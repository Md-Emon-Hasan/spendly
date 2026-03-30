from flask import Blueprint, render_template, session, redirect, url_for
from datetime import datetime, timedelta
import calendar
from ..database.connection import get_db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route("/dashboard")
def index():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    uid = session["user_id"]
    conn = get_db()
    now = datetime.now()
    curr_month = now.strftime("%Y-%m")

    # --- Lifetime totals ---
    total_income = (conn.execute(
        "SELECT COALESCE(SUM(amount),0) as t FROM incomes WHERE user_id=?", (uid,)
    ).fetchone()["t"])

    total_expense = (conn.execute(
        "SELECT COALESCE(SUM(amount),0) as t FROM expenses WHERE user_id=?", (uid,)
    ).fetchone()["t"])

    lifetime_saved = total_income - total_expense

    # --- Current month ---
    cm_income = (conn.execute(
        "SELECT COALESCE(SUM(amount),0) as t FROM incomes WHERE user_id=? AND strftime('%Y-%m',date)=?",
        (uid, curr_month),
    ).fetchone()["t"])

    cm_expense = (conn.execute(
        "SELECT COALESCE(SUM(amount),0) as t FROM expenses WHERE user_id=? AND strftime('%Y-%m',date)=?",
        (uid, curr_month),
    ).fetchone()["t"])

    cm_saved = cm_income - cm_expense

    # --- Previous month ---
    first_of_month = now.replace(day=1)
    prev_month_date = first_of_month - timedelta(days=1)
    prev_month = prev_month_date.strftime("%Y-%m")

    pm_income = (conn.execute(
        "SELECT COALESCE(SUM(amount),0) as t FROM incomes WHERE user_id=? AND strftime('%Y-%m',date)=?",
        (uid, prev_month),
    ).fetchone()["t"])

    pm_expense = (conn.execute(
        "SELECT COALESCE(SUM(amount),0) as t FROM expenses WHERE user_id=? AND strftime('%Y-%m',date)=?",
        (uid, prev_month),
    ).fetchone()["t"])

    pm_saved = pm_income - pm_expense
    savings_diff = cm_saved - pm_saved

    # --- Advanced Budgets & Stats ---
    all_budgets = conn.execute(
        "SELECT category_id, amount FROM budgets WHERE user_id=? AND month=?",
        (uid, curr_month)
    ).fetchall()
    
    monthly_budget = 0
    cat_budgets = {}
    for b in all_budgets:
        if b['category_id'] is None:
            monthly_budget = b['amount']
        else:
            cat_budgets[b['category_id']] = b['amount']

    # Fetch spending grouped by category for current month
    cat_spending_query = conn.execute("""
        SELECT category_id, SUM(amount) as spent
        FROM expenses
        WHERE user_id=? AND strftime('%Y-%m', date)=?
        GROUP BY category_id
    """, (uid, curr_month)).fetchall()
    cat_spending_map = {r['category_id']: r['spent'] for r in cat_spending_query}
    
    days_in_month = calendar.monthrange(now.year, now.month)[1]
    current_day = now.day
    days_left = days_in_month - current_day + 1
    
    daily_average = cm_expense / current_day if current_day > 0 else 0
    projected_spend = daily_average * days_in_month
    
    if monthly_budget > 0:
        safe_to_spend_daily = max(0, (monthly_budget - cm_expense) / days_left)
        budget_used_percent = round(min(100, (cm_expense / monthly_budget) * 100), 1)
    else:
        safe_to_spend_daily = 0
        budget_used_percent = 0

    # --- Categories & Category Budgets ---
    categories = conn.execute("SELECT * FROM categories ORDER BY name").fetchall()
    
    detailed_cat_budgets = []
    for c in categories:
        cid = c['id']
        if cid in cat_budgets:
            budget_amt = cat_budgets[cid]
            spent_amt = cat_spending_map.get(cid, 0)
            percent = round(min(100, (spent_amt / budget_amt) * 100), 1) if budget_amt > 0 else 0
            detailed_cat_budgets.append({
                'id': cid,
                'name': c['name'],
                'icon': c['icon'],
                'budget': budget_amt,
                'spent': spent_amt,
                'percent': percent
            })

    # --- Recent expenses (reduced to 5) ---
    recent_expenses = conn.execute("""
        SELECT e.*, c.name as category_name, c.icon as category_icon
        FROM expenses e JOIN categories c ON e.category_id = c.id
        WHERE e.user_id = ? ORDER BY e.date DESC LIMIT 5
    """, (uid,)).fetchall()

    # --- Recent cash-ins ---
    recent_incomes = conn.execute(
        "SELECT * FROM incomes WHERE user_id=? ORDER BY date DESC LIMIT 5",
        (uid,),
    ).fetchall()

    # --- Category spending (current month) ---
    cat_spending = conn.execute("""
        SELECT c.name, c.icon, COALESCE(SUM(e.amount),0) as total
        FROM categories c LEFT JOIN expenses e ON c.id = e.category_id
            AND e.user_id = ? AND strftime('%Y-%m', e.date) = ?
        GROUP BY c.id HAVING total > 0
        ORDER BY total DESC
    """, (uid, curr_month)).fetchall()

    return render_template(
        "dashboard.html",
        total_income=total_income,
        total_expense=total_expense,
        lifetime_saved=lifetime_saved,
        balance=lifetime_saved,
        cm_income=cm_income,
        cm_expense=cm_expense,
        cm_saved=cm_saved,
        pm_saved=pm_saved,
        savings_diff=savings_diff,
        curr_month_savings=cm_saved,
        categories=categories,
        recent_expenses=recent_expenses,
        recent_incomes=recent_incomes,
        cat_spending=cat_spending,
        curr_month_label=now.strftime("%B %Y"),
        prev_month_label=prev_month_date.strftime("%B %Y"),
        current_date=now.strftime("%Y-%m-%d"),
        monthly_budget=monthly_budget,
        daily_average=daily_average,
        projected_spend=projected_spend,
        safe_to_spend_daily=safe_to_spend_daily,
        budget_used_percent=budget_used_percent,
        detailed_cat_budgets=detailed_cat_budgets,
    )
