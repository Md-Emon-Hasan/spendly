from flask import Blueprint, render_template, request, session, redirect, url_for
from datetime import datetime
from database.connection import get_db

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

    cat_breakdown = conn.execute("""
        SELECT c.name, c.icon, COALESCE(SUM(e.amount),0) as total
        FROM categories c LEFT JOIN expenses e ON c.id = e.category_id
            AND e.user_id = ? AND strftime('%Y-%m', e.date) = ?
        GROUP BY c.id HAVING total > 0
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

    monthly_trend = []
    for m in all_months[:6]:
        m_in = conn.execute(
            "SELECT COALESCE(SUM(amount),0) as t FROM incomes WHERE user_id=? AND strftime('%Y-%m',date)=?",
            (uid, m),
        ).fetchone()["t"]
        m_out = conn.execute(
            "SELECT COALESCE(SUM(amount),0) as t FROM expenses WHERE user_id=? AND strftime('%Y-%m',date)=?",
            (uid, m),
        ).fetchone()["t"]
        try:
            label = datetime.strptime(m, "%Y-%m").strftime("%b %Y")
        except ValueError:
            label = m
        monthly_trend.append({
            "month": m, "label": label,
            "income": m_in, "expense": m_out, "saved": m_in - m_out,
        })

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
        monthly_trend=monthly_trend,
    )
