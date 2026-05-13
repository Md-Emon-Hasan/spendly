# Spendly

Spendly is a comprehensive personal finance and budgeting application built with Python and Flask. It empowers users to track their incomes and expenses, manage budgets, analyze their financial habits, and set achievable saving goals.

<p align="center">
  <img src="https://github.com/user-attachments/assets/5b916c70-9377-46b8-8a46-3c3b6c231bf3" width="100%" alt="Spendly Banner" />
</p>

## 🚀 Features

- **User Authentication**: Secure sign-up, login, and session management.
- **Dashboard Overview**: A quick glance at recent transactions, current balances, and quick stats.
- **Transaction Management**: Add, edit, and categorize daily incomes and expenses.
- **Budgeting**: Set and monitor monthly budgets for different categories.
- **Savings Goals**: Create financial goals and track your progress as you add funds to them.
- **Analytics & Insights**: Visualize spending patterns and income vs. expense ratios.
- **Data Export**: Export financial data for external use (e.g., CSV/Excel).

## 🛠️ Technology Stack

- **Backend Framework**: Python 3.11+, Flask
- **Database**: SQLite
- **Database Driver**: `psycopg2-binary`
- **Server**: Gunicorn (for production)
- **Static File Serving**: WhiteNoise
- **Testing**: Pytest, Pytest-Flask

## 📂 Project Structure

```text
spendly/
├── app/
│   ├── __init__.py          # App factory and blueprint registration
│   ├── config.py            # Environment configurations
│   ├── database/            # Database connection handlers
│   ├── routes/              # Flask Blueprints (auth, dashboard, analytics, etc.)
│   ├── static/              # CSS, JavaScript, and Images (served by WhiteNoise)
│   └── templates/           # Jinja2 HTML templates
├── database/                # Local SQLite DB storage (ignored in version control)
├── .env.example             # Example environment variables
├── init_db.py               # Database initialization and schema creation
├── render.yaml              # Render deployment configuration
├── requirements.txt         # Python dependencies
├── run.py                   # Local development server entry point
└── wsgi.py                  # Production WSGI entry point
```

## ⚙️ Local Development Setup

### 1. Clone the repository
Ensure you have Python 3.11+ installed on your machine.
```bash
git clone https://github.com/Md-Emon-Hasan/spendly.git
cd spendly
```

### 2. Create and activate a virtual environment
**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```
**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory. For local development, you only need to set a secret key (SQLite will be used by default if `DATABASE_URL` is omitted).

### 5. Initialize the Database
Run the database initialization script to create the required tables and default categories.
```bash
python init_db.py
```

### 6. Run the Application
Start the Flask development server:
```bash
python run.py
```
The application will be accessible at `http://127.0.0.1:5001`.

## 🗄️ Database Schema

The application uses a relational database model consisting of the following primary tables:
- **`users`**: Stores user credentials and profile information.
- **`categories`**: Defines default and custom categories for transactions (e.g., Food, Transport, Salary).
- **`incomes`**: Records user income entries.
- **`expenses`**: Records user expense entries mapped to categories.
- **`budgets`**: Stores monthly budget limits per category for each user.
- **`goals`**: Tracks user saving goals and deadlines.
- **`goal_funds`**: Logs the history of funds added to specific goals.

## 🧪 Testing

The project uses `pytest` for unit and integration testing. To run the test suite, ensure your virtual environment is active and run:
```bash
pytest
```

## **Author**

**Md Emon Hasan**

- Email: [emon.mlengineer@gmail.com](mailto:emon.mlengineer@gmail.com)
- LinkedIn: [md-emon-hasan](https://www.linkedin.com/in/md-emon-hasan-695483237/)
- GitHub: [Md-Emon-Hasan](https://github.com/Md-Emon-Hasan)
- Facebook: [Md-Emon-Hasan](https://www.facebook.com/mdemon.hasan2001/)
- WhatsApp: [+8801834363533](https://wa.me/8801834363533)

## 📝 License

This project is open-source and available under the MIT License.
