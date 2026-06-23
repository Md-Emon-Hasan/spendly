from flask import Blueprint, render_template, request, session, redirect, url_for
from datetime import datetime
from ..database.connection import get_db

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route("/analytics")
def index():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    uid = session["user_id"]
    conn = get_db()

    income_months = conn.execute(
        "SELECT DISTINCT strftime('%Y-%m', date) as m FROM incomes WHERE user_id=?", (uid,)
    ).fetchall()
    expense_months = conn.execute(
        "SELECT DISTINCT strftime('%Y-%m', date) as m FROM expenses WHERE user_id=?", (uid,)
    ).fetchall()

    all_months = sorted(
        set(r["m"] for r in income_months) | set(r["m"] for r in expense_months),
        reverse=True,
    )

    selected = request.args.get("month", datetime.now().strftime("%Y-%m"))

    sm_income = conn.execute(
        "SELECT COALESCE(SUM(amount),0) as t FROM incomes WHERE user_id=? AND strftime('%Y-%m',date)=?",
        (uid, selected),
    ).fetchone()["t"]

    sm_expense = conn.execute(
        "SELECT COALESCE(SUM(amount),0) as t FROM expenses WHERE user_id=? AND strftime('%Y-%m',date)=?",
        (uid, selected),
    ).fetchone()["t"]

    sm_saved = sm_income - sm_expense

    # Month-over-Month (MoM) calculation
    selected_dt = datetime.strptime(selected, "%Y-%m")
    if selected_dt.month == 1:
        prev_month_str = f"{selected_dt.year - 1}-12"
    else:
        prev_month_str = f"{selected_dt.year}-{selected_dt.month - 1:02d}"

    pm_expense = conn.execute(
        "SELECT COALESCE(SUM(amount),0) as t FROM expenses WHERE user_id=? AND strftime('%Y-%m',date)=?",
        (uid, prev_month_str),
    ).fetchone()["t"]
    
    mom_change_percent = 0
    if pm_expense > 0:
        mom_change_percent = ((sm_expense - pm_expense) / pm_expense) * 100
    elif sm_expense > 0:
        mom_change_percent = 100

    cat_breakdown = conn.execute("""
        SELECT c.name, c.icon, COALESCE(SUM(e.amount),0) as total
        FROM categories c LEFT JOIN expenses e ON c.id = e.category_id
            AND e.user_id = ? AND strftime('%Y-%m', e.date) = ?
        GROUP BY c.id, c.name, c.icon HAVING COALESCE(SUM(e.amount),0) > 0
        ORDER BY total DESC
    """, (uid, selected)).fetchall()

    max_cat_amount = max((r["total"] for r in cat_breakdown), default=1)

    total_income = conn.execute(
        "SELECT COALESCE(SUM(amount),0) as t FROM incomes WHERE user_id=?", (uid,)
    ).fetchone()["t"]

    total_expense = conn.execute(
        "SELECT COALESCE(SUM(amount),0) as t FROM expenses WHERE user_id=?", (uid,)
    ).fetchone()["t"]

    total_transactions = conn.execute(
        "SELECT COUNT(*) as c FROM expenses WHERE user_id=?", (uid,)
    ).fetchone()["c"]

    total_cashins = conn.execute(
        "SELECT COUNT(*) as c FROM incomes WHERE user_id=?", (uid,)
    ).fetchone()["c"]

    # --- 4-Month trend (selected month + previous 3), gradient area chart ---
    def _month_shift(ym, delta):
        y, mo = int(ym[:4]), int(ym[5:7])
        total = y * 12 + (mo - 1) + delta
        return f"{total // 12}-{total % 12 + 1:02d}"

    months4 = [_month_shift(selected, d) for d in (-3, -2, -1, 0)]
    trend_months = []
    for m in months4:
        m_in = conn.execute(
            "SELECT COALESCE(SUM(amount),0) as t FROM incomes WHERE user_id=? AND strftime('%Y-%m',date)=?",
            (uid, m),
        ).fetchone()["t"]
        m_out = conn.execute(
            "SELECT COALESCE(SUM(amount),0) as t FROM expenses WHERE user_id=? AND strftime('%Y-%m',date)=?",
            (uid, m),
        ).fetchone()["t"]
        try:
            label = datetime.strptime(m, "%Y-%m").strftime("%b")
        except ValueError:
            label = m
        trend_months.append({
            "month": m, "label": label,
            "income": m_in, "expense": m_out, "saved": m_in - m_out,
        })

    ### Behavioral Analytics (Phase 2) ###
    
    # 1. Top 3 Expenses
    top_expenses = conn.execute("""
        SELECT e.description, e.amount, c.icon, c.name, e.date
        FROM expenses e
        LEFT JOIN categories c ON e.category_id = c.id
        WHERE e.user_id = ? AND strftime('%Y-%m', e.date) = ?
        ORDER BY e.amount DESC
        LIMIT 3
    """, (uid, selected)).fetchall()

    # 2. Day of Week Analysis (0=Sunday ... 6=Saturday)
    dow_expenses = conn.execute("""
        SELECT strftime('%w', date) as dow, SUM(amount) as total
        FROM expenses
        WHERE user_id = ? AND strftime('%Y-%m', date) = ?
        GROUP BY strftime('%w', date)
    """, (uid, selected)).fetchall()
    
    dow_map = {"0": "Sun", "1": "Mon", "2": "Tue", "3": "Wed", "4": "Thu", "5": "Fri", "6": "Sat"}
    
    dow_data = [{"dow": dow_map[str(i)], "total": 0} for i in range(7)]
    for x in dow_expenses:
        dow_data[int(x["dow"])]["total"] = x["total"]
        
    highest_dow = max(dow_data, key=lambda x: x["total"]) if sm_expense > 0 else None

    ### Budget Usage ###
    budget_row = conn.execute(
        "SELECT amount FROM budgets WHERE user_id=? AND category_id IS NULL AND month=?",
        (uid, selected)
    ).fetchone()
    monthly_budget = budget_row["amount"] if budget_row else 0
    budget_used_percent = round(min(100, (sm_expense / monthly_budget) * 100), 1) if monthly_budget > 0 else 0

    # --- This-month daily trend (income + expense per day) for the 1-month area chart ---
    import calendar as _cal
    daily_exp_rows = conn.execute("""
        SELECT strftime('%d', date) as d, SUM(amount) as total
        FROM expenses
        WHERE user_id=? AND strftime('%Y-%m', date)=?
        GROUP BY strftime('%d', date)
    """, (uid, selected)).fetchall()
    daily_exp_map = {str(r["d"]): float(r["total"]) for r in daily_exp_rows}
    daily_inc_rows = conn.execute("""
        SELECT strftime('%d', date) as d, SUM(amount) as total
        FROM incomes
        WHERE user_id=? AND strftime('%Y-%m', date)=?
        GROUP BY strftime('%d', date)
    """, (uid, selected)).fetchall()
    daily_inc_map = {str(r["d"]): float(r["total"]) for r in daily_inc_rows}
    try:
        sel_dt = datetime.strptime(selected, "%Y-%m")
        days_in_sel = _cal.monthrange(sel_dt.year, sel_dt.month)[1]
    except ValueError:
        days_in_sel = 31
    trend_days = []
    for d in range(1, days_in_sel + 1):
        di = daily_inc_map.get(f"{d:02d}", 0)
        de = daily_exp_map.get(f"{d:02d}", 0)
        trend_days.append({"day": d, "income": di, "expense": de, "saved": di - de})

    # Category breakdown for the running (selected) month donut
    cat_donut = [{"name": r["name"], "icon": r["icon"], "total": float(r["total"])} for r in cat_breakdown]

    # Category breakdown aggregated over the last 4 months, for the second donut
    _ph = ",".join("?" * len(months4))
    donut_4m_rows = conn.execute(f"""
        SELECT c.name, c.icon, COALESCE(SUM(e.amount),0) as total
        FROM categories c JOIN expenses e ON c.id = e.category_id
        WHERE e.user_id = ? AND strftime('%Y-%m', e.date) IN ({_ph})
        GROUP BY c.id, c.name, c.icon HAVING COALESCE(SUM(e.amount),0) > 0
        ORDER BY total DESC
    """, (uid, *months4)).fetchall()
    donut_4m = [{"name": r["name"], "icon": r["icon"], "total": float(r["total"])} for r in donut_4m_rows]

    try:
        range_4m_label = datetime.strptime(months4[0], "%Y-%m").strftime("%b") + " – " + \
            datetime.strptime(months4[-1], "%Y-%m").strftime("%b %Y")
    except ValueError:
        range_4m_label = "Last 4 months"

    try:
        selected_label = datetime.strptime(selected, "%Y-%m").strftime("%B %Y")
    except ValueError:
        selected_label = selected

    return render_template(
        "analytics.html",
        all_months=all_months,
        selected=selected,
        selected_label=selected_label,
        sm_income=sm_income,
        sm_expense=sm_expense,
        sm_saved=sm_saved,
        cat_breakdown=cat_breakdown,
        max_cat_amount=max_cat_amount,
        total_income=total_income,
        total_expense=total_expense,
        lifetime_saved=total_income - total_expense,
        total_transactions=total_transactions,
        total_cashins=total_cashins,
        trend_months=trend_months,
        trend_days=trend_days,
        range_4m_label=range_4m_label,
        mom_change_percent=mom_change_percent,
        top_expenses=top_expenses,
        dow_data=dow_data,
        highest_dow=highest_dow,
        monthly_budget=monthly_budget,
        budget_used_percent=budget_used_percent,
        cat_donut=cat_donut,
        donut_4m=donut_4m,
    )
