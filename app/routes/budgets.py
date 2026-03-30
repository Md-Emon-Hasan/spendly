from flask import Blueprint, request, session, redirect, url_for
from ..database.connection import get_db

budgets_bp = Blueprint('budgets', __name__)

@budgets_bp.route("/budgets/set", methods=["POST"])
def set_budget():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    amount = float(request.form.get("amount", 0))
    category_id = request.form.get("category_id")
    if not category_id:
        category_id = None
        
    month = request.form.get("month")
    if not month:
        from datetime import datetime
        month = datetime.now().strftime("%Y-%m")
        
    conn = get_db()
    
    # Check if budget exists for this month, if so update, else insert.
    # Note: SQLite ON CONFLICT index on multiple columns with a NULL requires the category_id constraint.
    # We will just do a DELETE then INSERT to avoid ON CONFLICT issues with NULL.
    if category_id is None:
        conn.execute('''
            DELETE FROM budgets WHERE user_id=? AND category_id IS NULL AND month=?
        ''', (session["user_id"], month))
    else:
        conn.execute('''
            DELETE FROM budgets WHERE user_id=? AND category_id=? AND month=?
        ''', (session["user_id"], category_id, month))
        
    conn.execute('''
        INSERT INTO budgets (user_id, category_id, amount, month)
        VALUES (?, ?, ?, ?)
    ''', (session["user_id"], category_id, amount, month))
    conn.commit()
    conn.commit()
    
    return redirect(url_for("dashboard.index"))
