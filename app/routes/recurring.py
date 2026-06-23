from flask import Blueprint, request, session, redirect, url_for, flash
from ..database.connection import get_db

recurring_bp = Blueprint('recurring', __name__)


@recurring_bp.route("/recurring/add", methods=["POST"])
def add():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    uid = session["user_id"]
    rtype = request.form.get("type", "expense")
    if rtype not in ("income", "expense"):
        rtype = "expense"

    try:
        amount = float(request.form.get("amount", 0))
    except (TypeError, ValueError):
        amount = 0
    if amount <= 0:
        flash('Enter an amount greater than zero.', 'error')
        return redirect(url_for("account.index"))

    try:
        day = min(max(int(request.form.get("day_of_month", 1)), 1), 28)
    except (TypeError, ValueError):
        day = 1

    description = request.form.get("description", "").strip()
    category_id = request.form.get("category_id") or None
    if rtype == "income":
        category_id = None

    conn = get_db()
    conn.execute(
        """INSERT INTO recurring (user_id, type, category_id, amount, description, day_of_month, active)
           VALUES (?, ?, ?, ?, ?, ?, 1)""",
        (uid, rtype, category_id, amount, description, day),
    )
    conn.commit()
    flash('Recurring transaction added.', 'success')
    return redirect(url_for("account.index"))


@recurring_bp.route("/recurring/<int:id>/toggle", methods=["POST"])
def toggle(id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    uid = session["user_id"]
    conn = get_db()
    row = conn.execute("SELECT active FROM recurring WHERE id=? AND user_id=?", (id, uid)).fetchone()
    if row:
        new_state = 0 if row["active"] else 1
        conn.execute("UPDATE recurring SET active=? WHERE id=? AND user_id=?", (new_state, id, uid))
        conn.commit()
    return redirect(url_for("account.index"))


@recurring_bp.route("/recurring/<int:id>/delete", methods=["POST"])
def delete(id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    uid = session["user_id"]
    conn = get_db()
    conn.execute("DELETE FROM recurring WHERE id=? AND user_id=?", (id, uid))
    conn.commit()
    flash('Recurring transaction removed.', 'info')
    return redirect(url_for("account.index"))
