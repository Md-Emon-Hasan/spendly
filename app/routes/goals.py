from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..database.connection import get_db
from datetime import datetime

goals_bp = Blueprint('goals', __name__)

@goals_bp.route('/goals')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    uid = session['user_id']
    conn = get_db()
    
    # Fetch user's goals
    goals = conn.execute("SELECT * FROM goals WHERE user_id = ?", (uid,)).fetchall()
    
    # Calculate progress % for UX
    goals_data = []
    for g in goals:
        progress = 0
        if g['target_amount'] > 0:
            progress = min(100, (g['current_amount'] / g['target_amount']) * 100)
        
        goal_dict = dict(g)
        goal_dict['progress'] = progress
        goals_data.append(goal_dict)
        
    curr_month = datetime.now().strftime("%Y-%m")
    
    # Get budget info
    budget_row = conn.execute(
        "SELECT amount FROM budgets WHERE user_id=? AND category_id IS NULL AND month=?",
        (uid, curr_month)
    ).fetchone()
    monthly_budget = budget_row["amount"] if budget_row else 0
    
    # Get total spent this month
    cm_expense_row = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) as spent FROM expenses WHERE user_id=? AND strftime('%Y-%m', date)=?",
        (uid, curr_month)
    ).fetchone()
    cm_expense = cm_expense_row['spent']
    budget_used_percent = round(min(100, (cm_expense / monthly_budget) * 100), 1) if monthly_budget > 0 else 0
        
    return render_template('goals.html', goals=goals_data, monthly_budget=monthly_budget, cm_expense=cm_expense, budget_used_percent=budget_used_percent)

@goals_bp.route('/goals/add', methods=['POST'])
def add_goal():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    uid = session['user_id']
    name = request.form.get('name')
    target_amount = float(request.form.get('target_amount', 0))
    deadline = request.form.get('deadline') or None
    
    conn = get_db()
    conn.execute(
        "INSERT INTO goals (user_id, name, target_amount, deadline) VALUES (?, ?, ?, ?)",
        (uid, name, target_amount, deadline)
    )
    conn.commit()
    
    flash('Goal created successfully!', 'success')
    return redirect(url_for('goals.index'))

@goals_bp.route('/goals/<int:id>/add_funds', methods=['POST'])
def add_funds(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    uid = session['user_id']
    amount = float(request.form.get('amount', 0))
    
    conn = get_db()
    # verify ownership
    goal = conn.execute("SELECT * FROM goals WHERE id=? AND user_id=?", (id, uid)).fetchone()
    if goal:
        new_amt = float(goal['current_amount']) + amount
        conn.execute("UPDATE goals SET current_amount = ? WHERE id = ?", (new_amt, id))
        conn.commit()
        flash(f'Added {amount} to {goal["name"]}!', 'success')
    return redirect(url_for('goals.index'))

@goals_bp.route('/goals/<int:id>/delete', methods=['POST'])
def delete_goal(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    uid = session['user_id']
    conn = get_db()
    conn.execute("DELETE FROM goals WHERE id=? AND user_id=?", (id, uid))
    conn.commit()
    flash('Goal deleted!', 'success')
    return redirect(url_for('goals.index'))
