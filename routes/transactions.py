from flask import Blueprint, request, session, redirect, url_for, flash
from datetime import datetime
from database.connection import get_db

transactions_bp = Blueprint('transactions', __name__)

# --- Cash In Routes ---

@transactions_bp.route("/cash_in", methods=["POST"])
def cash_in():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    amount = float(request.form["amount"])
    description = request.form.get("description", "Cash In")
    txn_date = request.form.get("date", datetime.now().strftime("%Y-%m-%d"))
    
    txn_datetime = f"{txn_date} {datetime.now().strftime('%H:%M:%S')}"
    
    conn = get_db()
    conn.execute(
        "INSERT INTO incomes (user_id, amount, description, date) VALUES (?, ?, ?, ?)",
        (session["user_id"], amount, description, txn_datetime),
    )
    conn.commit()
    return redirect(url_for("dashboard.index"))


@transactions_bp.route("/incomes/<int:id>/edit", methods=["POST"])
def edit_income(id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
        
    amount = float(request.form["amount"])
    description = request.form["description"]
    txn_date = request.form["date"]
    
    # We maintain the existing time portion if possible, or append current time
    txn_datetime = f"{txn_date} {datetime.now().strftime('%H:%M:%S')}"

    conn = get_db()
    conn.execute(
        "UPDATE incomes SET amount=?, description=?, date=? WHERE id=? AND user_id=?",
        (amount, description, txn_datetime, id, session["user_id"])
    )
    conn.commit()
    return redirect(url_for("dashboard.index"))


@transactions_bp.route("/incomes/<int:id>/delete", methods=["POST"])
def delete_income(id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
        
    conn = get_db()
    conn.execute("DELETE FROM incomes WHERE id=? AND user_id=?", (id, session["user_id"]))
    conn.commit()
    return redirect(url_for("dashboard.index"))


# --- Expense Routes ---

@transactions_bp.route("/expenses/add", methods=["POST"])
def add_expense():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    category_id = request.form["category_id"]
    amount = float(request.form["amount"])
    description = request.form.get("description", "")
    txn_date = request.form.get("date", datetime.now().strftime("%Y-%m-%d"))

    txn_datetime = f"{txn_date} {datetime.now().strftime('%H:%M:%S')}"

    conn = get_db()
    conn.execute(
        "INSERT INTO expenses (user_id, category_id, amount, description, date) VALUES (?, ?, ?, ?, ?)",
        (session["user_id"], category_id, amount, description, txn_datetime),
    )
    conn.commit()
    return redirect(url_for("dashboard.index"))


@transactions_bp.route("/expenses/<int:id>/edit", methods=["POST"])
def edit_expense(id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
        
    category_id = request.form["category_id"]
    amount = float(request.form["amount"])
    description = request.form["description"]
    txn_date = request.form["date"]

    txn_datetime = f"{txn_date} {datetime.now().strftime('%H:%M:%S')}"

    conn = get_db()
    conn.execute(
        "UPDATE expenses SET category_id=?, amount=?, description=?, date=? WHERE id=? AND user_id=?",
        (category_id, amount, description, txn_datetime, id, session["user_id"])
    )
    conn.commit()
    return redirect(url_for("dashboard.index"))


@transactions_bp.route("/expenses/<int:id>/delete", methods=["POST"])
def delete_expense(id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
        
    conn = get_db()
    conn.execute("DELETE FROM expenses WHERE id=? AND user_id=?", (id, session["user_id"]))
    conn.commit()
    return redirect(url_for("dashboard.index"))
