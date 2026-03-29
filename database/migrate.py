import sqlite3
import os

DATABASE = os.path.join(os.path.dirname(__file__), "spendly.db")

def migrate():
    conn = sqlite3.connect(DATABASE)
    print("Running migration...")
    
    # Budgets Table
    # user_id connects to users table
    # category_id (optional) for category-specific budgets, NULL means global monthly budget
    # month format is 'YYYY-MM'
    conn.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category_id INTEGER,
            amount REAL NOT NULL,
            month TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE,
            UNIQUE(user_id, category_id, month)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Migration successful: budgets table created.")

if __name__ == "__main__":
    migrate()
