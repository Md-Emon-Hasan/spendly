import sqlite3
import os

# Point to spendly.db in the parent 'database' folder
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'spendly.db')

def migrate():
    print(f"Connecting to database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    
    print("Creating goals table...")
    conn.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            target_amount REAL NOT NULL,
            current_amount REAL DEFAULT 0,
            deadline TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Goals migration complete.")

if __name__ == "__main__":
    migrate()
