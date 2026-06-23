from flask import Blueprint, render_template, session, redirect, url_for
from datetime import datetime
from ..database.connection import get_db
from ..services import process_recurring

home_bp = Blueprint('home', __name__)


@home_bp.route("/home")
def index():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    uid = session["user_id"]
    conn = get_db()
    process_recurring(conn, uid)

    now = datetime.now()
    curr_month = now.strftime("%Y-%m")
    hour = now.hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    total_income = conn.execute(
        "SELECT COALESCE(SUM(amount),0) as t FROM incomes WHERE user_id=?", (uid,)
    ).fetchone()["t"]
    total_expense = conn.execute(
        "SELECT COALESCE(SUM(amount),0) as t FROM expenses WHERE user_id=?", (uid,)
    ).fetchone()["t"]
    balance = total_income - total_expense

    cm_income = conn.execute(
        "SELECT COALESCE(SUM(amount),0) as t FROM incomes WHERE user_id=? AND strftime('%Y-%m',date)=?",
        (uid, curr_month),
    ).fetchone()["t"]
    cm_expense = conn.execute(
        "SELECT COALESCE(SUM(amount),0) as t FROM expenses WHERE user_id=? AND strftime('%Y-%m',date)=?",
        (uid, curr_month),
    ).fetchone()["t"]
    cm_saved = cm_income - cm_expense

    budget_row = conn.execute(
        "SELECT amount FROM budgets WHERE user_id=? AND category_id IS NULL AND month=?",
        (uid, curr_month),
    ).fetchone()
    monthly_budget = float(budget_row["amount"]) if budget_row and budget_row["amount"] is not None else 0.0
    budget_used_percent = round(min(100, (cm_expense / monthly_budget) * 100), 1) if monthly_budget > 0 else 0

    # Goals snapshot
    goals = conn.execute(
        "SELECT * FROM goals WHERE user_id=? ORDER BY id DESC", (uid,)
    ).fetchall()
    goals_data = []
    for g in goals:
        target = float(g["target_amount"] or 0)
        current = float(g["current_amount"] or 0)
        progress = min(100, (current / target * 100)) if target > 0 else 0
        goals_data.append({
            "name": g["name"], "current": current, "target": target, "progress": progress,
        })
    top_goals = goals_data[:3]

    # Recent activity (5 most recent of either kind)
    recent_exp = conn.execute("""
        SELECT e.date, c.name as label, c.icon as icon, e.amount, 'expense' as kind
        FROM expenses e LEFT JOIN categories c ON e.category_id = c.id
        WHERE e.user_id=? ORDER BY e.date DESC LIMIT 5
    """, (uid,)).fetchall()
    recent_inc = conn.execute("""
        SELECT date, description as label, '💰' as icon, amount, 'income' as kind
        FROM incomes WHERE user_id=? ORDER BY date DESC LIMIT 5
    """, (uid,)).fetchall()
    recent = sorted([dict(r) for r in recent_exp] + [dict(r) for r in recent_inc],
                    key=lambda x: x["date"], reverse=True)[:6]

    return render_template(
        "home.html",
        greeting=greeting,
        curr_month_label=now.strftime("%B %Y"),
        balance=balance,
        cm_income=cm_income,
        cm_expense=cm_expense,
        cm_saved=cm_saved,
        monthly_budget=monthly_budget,
        budget_used_percent=budget_used_percent,
        top_goals=top_goals,
        goal_count=len(goals_data),
        recent=recent,
    )
