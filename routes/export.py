from flask import Blueprint, session, redirect, url_for, Response
from database.connection import get_db
import csv
import io

export_bp = Blueprint('export', __name__)

@export_bp.route("/export/transactions")
def export_transactions():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
        
    conn = get_db()
    uid = session["user_id"]
    
    expenses = conn.execute("""
        SELECT e.date, c.name as category, e.amount, e.description, 'Expense' as type
        FROM expenses e JOIN categories c ON e.category_id = c.id
        WHERE e.user_id = ?
    """, (uid,)).fetchall()
    
    incomes = conn.execute("""
        SELECT date, 'Income' as category, amount, description, 'Income' as type
        FROM incomes WHERE user_id = ?
    """, (uid,)).fetchall()
    
    all_txns = sorted(expenses + incomes, key=lambda x: x["date"], reverse=True)
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Type', 'Category', 'Description', 'Amount'])
    
    for row in all_txns:
        writer.writerow([row["date"], row["type"], row["category"], row["description"], f"{row['amount']:.2f}"])
        
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=spendly_transactions.csv"}
    )
