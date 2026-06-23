from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from ..database.connection import get_db

account_bp = Blueprint('account', __name__)


@account_bp.route("/account")
def index():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    uid = session["user_id"]
    conn = get_db()

    user = conn.execute("SELECT name, email FROM users WHERE id=?", (uid,)).fetchone()
    categories = conn.execute("SELECT * FROM categories ORDER BY name").fetchall()

    recurring = conn.execute("""
        SELECT r.*, c.name as category_name, c.icon as category_icon
        FROM recurring r LEFT JOIN categories c ON r.category_id = c.id
        WHERE r.user_id=? ORDER BY r.type, r.day_of_month
    """, (uid,)).fetchall()

    # Counts for the reset summary
    counts = {
        "expenses": conn.execute("SELECT COUNT(*) as c FROM expenses WHERE user_id=?", (uid,)).fetchone()["c"],
        "incomes": conn.execute("SELECT COUNT(*) as c FROM incomes WHERE user_id=?", (uid,)).fetchone()["c"],
        "goals": conn.execute("SELECT COUNT(*) as c FROM goals WHERE user_id=?", (uid,)).fetchone()["c"],
        "budgets": conn.execute("SELECT COUNT(*) as c FROM budgets WHERE user_id=?", (uid,)).fetchone()["c"],
    }

    return render_template("account.html", user=user, categories=categories,
                           recurring=recurring, counts=counts)


def _delete_user_data(conn, uid):
    """Remove all of a user's financial data (keeps the account)."""
    conn.execute("""
        DELETE FROM goal_funds WHERE goal_id IN (SELECT id FROM goals WHERE user_id=?)
    """, (uid,))
    conn.execute("DELETE FROM goals WHERE user_id=?", (uid,))
    conn.execute("DELETE FROM expenses WHERE user_id=?", (uid,))
    conn.execute("DELETE FROM incomes WHERE user_id=?", (uid,))
    conn.execute("DELETE FROM budgets WHERE user_id=?", (uid,))
    conn.execute("DELETE FROM recurring WHERE user_id=?", (uid,))


@account_bp.route("/account/reset", methods=["POST"])
def reset_data():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if request.form.get("confirm") != "RESET":
        flash('Type RESET to confirm clearing your data.', 'error')
        return redirect(url_for("account.index"))

    uid = session["user_id"]
    conn = get_db()
    _delete_user_data(conn, uid)
    conn.commit()
    flash('All your transactions, goals and budgets have been cleared.', 'success')
    return redirect(url_for("account.index"))


@account_bp.route("/account/delete", methods=["POST"])
def delete_account():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if request.form.get("confirm") != "DELETE":
        flash('Type DELETE to confirm removing your account.', 'error')
        return redirect(url_for("account.index"))

    uid = session["user_id"]
    conn = get_db()
    _delete_user_data(conn, uid)
    conn.execute("DELETE FROM users WHERE id=?", (uid,))
    conn.commit()
    session.clear()
    flash('Your account and all data have been permanently deleted.', 'info')
    return redirect(url_for("landing"))
