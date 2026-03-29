from flask import Blueprint, render_template, session, redirect, url_for
from datetime import datetime, timedelta
from database.connection import get_db

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

    # --- Categories ---
    categories = conn.execute("SELECT * FROM categories ORDER BY name").fetchall()

    # --- Recent expenses ---
    recent_expenses = conn.execute("""
        SELECT e.*, c.name as category_name, c.icon as category_icon
        FROM expenses e JOIN categories c ON e.category_id = c.id
        WHERE e.user_id = ? ORDER BY e.date DESC LIMIT 10
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
    )
