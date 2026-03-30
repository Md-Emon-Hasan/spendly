import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

def init_db():
    database_url = os.environ.get('DATABASE_URL')
    is_postgres = database_url is not None
    
    if is_postgres:
        try:
            import psycopg2
            from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
            print("Connecting to PostgreSQL...")
            if database_url.startswith("postgres://"):
                database_url = database_url.replace("postgres://", "postgresql://", 1)
            conn = psycopg2.connect(database_url)
            cur = conn.cursor()
            param_style = '%s'
            serial_type = 'SERIAL'
            timestamp_type = 'TIMESTAMP'
        except ImportError:
            print("Error: psycopg2 not installed. Cannot connect to PostgreSQL.")
            return
        except Exception as e:
            print(f"Error connecting to PostgreSQL: {e}")
            return
    else:
        print("Connecting to local SQLite...")
        # Get project root to find/create database folder
        basedir = os.path.abspath(os.path.dirname(__file__))
        db_path = os.path.join(basedir, 'database', 'spendly.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        param_style = '?'
        serial_type = 'INTEGER' # SQLITE uses INTEGER PRIMARY KEY for auto-inc
        timestamp_type = 'DATETIME'

    try:
        # Create Tables
        print("Creating tables...")
        
        # 1. Users
        cur.execute(f'''
            CREATE TABLE IF NOT EXISTS users (
                id {serial_type} PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            );
        ''')

        # 2. Categories
        cur.execute(f'''
            CREATE TABLE IF NOT EXISTS categories (
                id {serial_type} PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                icon VARCHAR(10) DEFAULT '📦',
                type VARCHAR(20) DEFAULT 'expense'
            );
        ''')

        # 3. Incomes
        cur.execute(f'''
            CREATE TABLE IF NOT EXISTS incomes (
                id {serial_type} PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                amount DECIMAL(15, 2) NOT NULL,
                description TEXT,
                date {timestamp_type} DEFAULT CURRENT_TIMESTAMP
            );
        ''')

        # 4. Expenses
        cur.execute(f'''
            CREATE TABLE IF NOT EXISTS expenses (
                id {serial_type} PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
                amount DECIMAL(15, 2) NOT NULL,
                description TEXT,
                date {timestamp_type} DEFAULT CURRENT_TIMESTAMP
            );
        ''')

        # 5. Budgets (Unified monthly and category budgets)
        cur.execute(f'''
            CREATE TABLE IF NOT EXISTS budgets (
                id {serial_type} PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
                amount DECIMAL(15, 2) NOT NULL,
                month VARCHAR(7) NOT NULL
            );
        ''')

        # 6. Goals
        cur.execute(f'''
            CREATE TABLE IF NOT EXISTS goals (
                id {serial_type} PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                name VARCHAR(255) NOT NULL,
                target_amount DECIMAL(15, 2) NOT NULL,
                current_amount DECIMAL(15, 2) DEFAULT 0,
                deadline DATE,
                created_at {timestamp_type} DEFAULT CURRENT_TIMESTAMP
            );
        ''')

        # 6a. Add created_at to existing goals table if missing
        try:
            if is_postgres:
                cur.execute('ALTER TABLE goals ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;')
            else:
                # SQLite doesn't support IF NOT EXISTS in ALTER TABLE.
                # Use a trick: check if column lives in the table info.
                cur.execute("PRAGMA table_info(goals)")
                columns = [c[1] for c in cur.fetchall()]
                if 'created_at' not in columns:
                    print("Adding 'created_at' to goals table (SQLite)...")
                    cur.execute("ALTER TABLE goals ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP")
        except Exception as e:
            print(f"Warning migrating goals table: {e}")

        # 7. Goal Fund History
        cur.execute(f'''
            CREATE TABLE IF NOT EXISTS goal_funds (
                id {serial_type} PRIMARY KEY,
                goal_id INTEGER REFERENCES goals(id) ON DELETE CASCADE,
                amount DECIMAL(15, 2) NOT NULL,
                added_at {timestamp_type} DEFAULT CURRENT_TIMESTAMP
            );
        ''')

        # Default Categories
        print("Inserting default categories...")
        categories = [
            ('Salary', '💰', 'income'),
            ('Freelance', '💻', 'income'),
            ('Gift', '🎁', 'income'),
            ('Other', '➕', 'income'),
            ('Food', '🍱', 'expense'),
            ('Transport', '🚗', 'expense'),
            ('Rent', '🏠', 'expense'),
            ('Utilities', '💡', 'expense'),
            ('Entertainment', '🎬', 'expense'),
            ('Health', '💊', 'expense'),
            ('Shopping', '🛍️', 'expense'),
            ('Education', '📚', 'expense'),
            ('Personal Care', '✨', 'expense'),
            ('Internet', '🌐', 'expense'),
            ('Bills', '🧾', 'expense'),
            ('Grocery', '🛒', 'expense'),
            ('Courier & Delivery', '🚚', 'expense'),
            ('Phone Bill', '📱', 'expense'),
            ('Savings', '🏦', 'expense'),
            ('Miscellaneous', '🧩', 'expense')
        ]
        
        for name, icon, cat_type in categories:
            query = f"SELECT id FROM categories WHERE name = {param_style} AND type = {param_style}"
            cur.execute(query, (name, cat_type))
            if not cur.fetchone():
                insert_query = f"INSERT INTO categories (name, icon, type) VALUES ({param_style}, {param_style}, {param_style})"
                cur.execute(insert_query, (name, icon, cat_type))

        conn.commit()
        cur.close()
        conn.close()
        print("Database initialized successfully!")

    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == "__main__":
    init_db()
