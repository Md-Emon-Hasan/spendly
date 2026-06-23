from flask import Blueprint, request, session, redirect, url_for, flash
from datetime import datetime
from ..database.connection import get_db

transactions_bp = Blueprint('transactions', __name__)


def _apply_range(query, params, date_col, filter_month, date_from, date_to, amt_min, amt_max):
    """Append shared month / date-range / amount-range filters to a query."""
    if filter_month:
        query += f" AND strftime('%Y-%m', {date_col}) = ?"
        params.append(filter_month)
    if date_from:
        query += f" AND {date_col} >= ?"
        params.append(date_from)
    if date_to:
        query += f" AND {date_col} <= ?"
        params.append(date_to + " 23:59:59")
    if amt_min is not None:
        query += " AND amount >= ?"
        params.append(amt_min)
    if amt_max is not None:
        query += " AND amount <= ?"
        params.append(amt_max)
    return query, params

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
    flash(f"Income of ৳{amount:.2f} added successfully!", "success")
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
    flash("Income updated.", "success")
    return redirect(url_for("dashboard.index"))


@transactions_bp.route("/incomes/<int:id>/delete", methods=["POST"])
def delete_income(id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
        
    conn = get_db()
    conn.execute("DELETE FROM incomes WHERE id=? AND user_id=?", (id, session["user_id"]))
    conn.commit()
    flash("Income deleted.", "info")
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
    flash(f"Expense of ৳{amount:.2f} recorded!", "success")
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
    flash("Expense updated.", "success")
    return redirect(url_for("dashboard.index"))


@transactions_bp.route("/expenses/<int:id>/delete", methods=["POST"])
def delete_expense(id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
        
    conn = get_db()
    conn.execute("DELETE FROM expenses WHERE id=? AND user_id=?", (id, session["user_id"]))
    conn.commit()
    flash("Expense deleted.", "info")
    return redirect(url_for("dashboard.index"))

# --- History / All Transactions Route ---

@transactions_bp.route("/history")
def history():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
        
    uid = session["user_id"]
    conn = get_db()
    
    filter_month = request.args.get("month", "")
    filter_cat = request.args.get("category_id", "")
    filter_type = request.args.get("type", "")
    date_from = request.args.get("date_from", "")
    date_to = request.args.get("date_to", "")
    amount_min = request.args.get("amount_min", "")
    amount_max = request.args.get("amount_max", "")
    q = request.args.get("q", "").strip()

    def _num(val):
        try:
            return float(val)
        except (TypeError, ValueError):
            return None

    amt_min = _num(amount_min)
    amt_max = _num(amount_max)

    expenses = []
    if not filter_type or filter_type == "expense":
        query = "SELECT e.id, e.date, c.name as category_name, c.icon as category_icon, e.amount, e.description, 'expense' as txn_type, e.category_id FROM expenses e JOIN categories c ON e.category_id = c.id WHERE e.user_id = ?"
        params = [uid]
        if filter_cat:
            query += " AND e.category_id = ?"
            params.append(filter_cat)
        # Search matches note OR category name for expenses
        if q:
            query += " AND (LOWER(e.description) LIKE ? OR LOWER(c.name) LIKE ?)"
            params.extend([f"%{q.lower()}%", f"%{q.lower()}%"])
        query, params = _apply_range(query, params, "e.date", filter_month, date_from, date_to, amt_min, amt_max)
        expenses_raw = conn.execute(query, params).fetchall()
        expenses = [dict(r) for r in expenses_raw]

    incomes = []
    if (not filter_type or filter_type == "income") and not filter_cat:
        query = "SELECT id, date, 'Income' as category_name, '💰' as category_icon, amount, description, 'income' as txn_type, NULL as category_id FROM incomes WHERE user_id = ?"
        params = [uid]
        if q:
            query += " AND LOWER(description) LIKE ?"
            params.append(f"%{q.lower()}%")
        query, params = _apply_range(query, params, "date", filter_month, date_from, date_to, amt_min, amt_max)
        incomes_raw = conn.execute(query, params).fetchall()
        incomes = [dict(r) for r in incomes_raw]

    all_txns = sorted(expenses + incomes, key=lambda x: x["date"], reverse=True)
    categories = conn.execute("SELECT * FROM categories ORDER BY name").fetchall()

    # Get distinct months
    income_months = conn.execute("SELECT DISTINCT strftime('%Y-%m', date) as m FROM incomes WHERE user_id=?", (uid,)).fetchall()
    expense_months = conn.execute("SELECT DISTINCT strftime('%Y-%m', date) as m FROM expenses WHERE user_id=?", (uid,)).fetchall()
    all_months = sorted(set(r["m"] for r in income_months) | set(r["m"] for r in expense_months), reverse=True)

    total_in = sum(t["amount"] for t in all_txns if t["txn_type"] == "income")
    total_out = sum(t["amount"] for t in all_txns if t["txn_type"] == "expense")

    from flask import render_template
    return render_template("history.html", transactions=all_txns, categories=categories,
                           filter_month=filter_month, filter_cat=filter_cat, filter_type=filter_type,
                           date_from=date_from, date_to=date_to, amount_min=amount_min,
                           amount_max=amount_max, q=q, all_months=all_months,
                           total_in=total_in, total_out=total_out, result_count=len(all_txns))
