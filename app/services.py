"""Shared helpers used across routes."""
from datetime import datetime


def process_recurring(conn, uid):
    """Auto-post any active recurring rules that are due this month.

    A rule posts once per calendar month, on or after its day_of_month.
    Returns the number of transactions posted.
    """
    now = datetime.now()
    curr_month = now.strftime("%Y-%m")
    today = now.day

    rules = conn.execute(
        "SELECT * FROM recurring WHERE user_id=? AND active=1", (uid,)
    ).fetchall()

    posted = 0
    for r in rules:
        if (r["last_posted"] or "") == curr_month:
            continue
        day = min(max(int(r["day_of_month"] or 1), 1), 28)
        if today < day:
            continue

        txn_date = f"{curr_month}-{day:02d} 09:00:00"
        note = (r["description"] or "").strip()

        if r["type"] == "income":
            label = note or "Recurring income"
            conn.execute(
                "INSERT INTO incomes (user_id, amount, description, date) VALUES (?, ?, ?, ?)",
                (uid, r["amount"], f"{label} (recurring)", txn_date),
            )
        else:
            label = note or "Recurring expense"
            conn.execute(
                "INSERT INTO expenses (user_id, category_id, amount, description, date) VALUES (?, ?, ?, ?, ?)",
                (uid, r["category_id"], r["amount"], f"{label} (recurring)", txn_date),
            )

        conn.execute(
            "UPDATE recurring SET last_posted=? WHERE id=?", (curr_month, r["id"])
        )
        posted += 1

    if posted:
        conn.commit()
    return posted
