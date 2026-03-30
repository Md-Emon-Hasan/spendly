import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def init_db():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("Error: DATABASE_URL not found in environment.")
        return

    # Fix for newer SQLAlchemy/psycopg2 versions
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    try:
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()

        # Create Tables
        print("Creating tables...")
        
        # 1. Users
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            );
        ''')

        # 2. Categories
        cur.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                icon VARCHAR(10) DEFAULT '📦',
                type VARCHAR(20) DEFAULT 'expense'
            );
        ''')

        # 3. Incomes
        cur.execute('''
            CREATE TABLE IF NOT EXISTS incomes (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                amount DECIMAL(15, 2) NOT NULL,
                description TEXT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')

        # 4. Expenses
        cur.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
                amount DECIMAL(15, 2) NOT NULL,
                description TEXT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')

        # 5. Budgets (Unified monthly and category budgets)
        cur.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
                amount DECIMAL(15, 2) NOT NULL,
                month VARCHAR(7) NOT NULL
            );
        ''')

        # 6. Goals
        cur.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                name VARCHAR(255) NOT NULL,
                target_amount DECIMAL(15, 2) NOT NULL,
                current_amount DECIMAL(15, 2) DEFAULT 0,
                deadline DATE
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
            cur.execute("SELECT id FROM categories WHERE name = %s AND type = %s", (name, cat_type))
            if not cur.fetchone():
                cur.execute("INSERT INTO categories (name, icon, type) VALUES (%s, %s, %s)", (name, icon, cat_type))

        conn.commit()
        cur.close()
        conn.close()
        print("Database initialized successfully!")

    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == "__main__":
    init_db()
