import sqlite3

DATABASE = "database/spendly.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()

    # Enable foreign keys
    conn.execute('PRAGMA foreign_keys = ON;')

    # Users
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Categories
    conn.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            icon TEXT DEFAULT '💸'
        )
    ''')

    # Expenses
    conn.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')

    # Incomes (Cash In)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS incomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')

    # Budgets
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

    # Goals
    conn.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            target_amount REAL NOT NULL,
            current_amount REAL DEFAULT 0,
            deadline TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')

    # Bachelor-oriented categories
    categories = [
        ("Food & Snacks", "🍛"),
        ("Rent & Housing", "🏠"),
        ("Utilities & Bills", "💡"),
        ("Internet & WiFi", "📶"),
        ("Mobile Recharge", "📱"),
        ("Transportation & Rides", "🚌"),
        ("Health & Pharmacy", "💊"),
        ("Laundry", "👔"),
        ("Haircut & Grooming", "💈"),
        ("Gym & Fitness", "🏋️"),
        ("Education & Books", "📚"),
        ("Entertainment & Subscriptions", "🎬"),
        ("Shopping & Clothing", "🛍️"),
        ("Tea & Coffee", "☕"),
        ("Tiffin & Mess", "🍱"),
        ("Courier & Delivery", "📦"),
        ("Gifts & Donations", "🎁"),
        ("Others", "📌"),
    ]
    for name, icon in categories:
        conn.execute("INSERT OR IGNORE INTO categories (name, icon) VALUES (?, ?)", (name, icon))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
