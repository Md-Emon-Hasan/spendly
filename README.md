# Spendly — Personal Finance Tracker

A clean, elegant personal finance tracker built with Flask. Track income and expenses, set savings goals, automate recurring transactions, and understand your spending patterns — all from a warm, light-themed interface.

## Features

- **Home** — Personalized overview: lifetime balance, this-month income/expense/savings, quick actions, a goals snapshot, and a recent-activity feed
- **Dashboard** — Your monthly control center: financial health score, monthly stats, overall & per-category budget tracking with a "safe to spend" projection, and recent income/expense tables with inline edit & delete
- **Transactions** — Full income & expense ledger with live search and filters (month, type, category, date range, amount range); edit or delete any record
- **Analytics** — Dual gradient **trend charts** (4-month and current-month) plotting income, expense, and savings; **two spending-split donuts** (last 4 months and running month); category breakdown, day-of-week spending, top expenses, and lifetime totals
- **Savings Goals** — Create targets with deadlines, add or withdraw funds, and track contribution history per goal
- **Budgets** — Set an overall monthly budget or per-category limits with real-time usage indicators and over-budget alerts
- **Recurring Transactions** — Define monthly income/expenses (e.g. salary, rent) that auto-post on a chosen day
- **Settings** — Manage your profile and recurring rules, plus a danger zone to reset data or delete your account
- **CSV Export** — Download your full transaction history at any time

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask 3.1 |
| Database | SQLite (local) · PostgreSQL (production) via raw SQL |
| Auth | Werkzeug password hashing, server-side sessions |
| Frontend | Jinja2 templates, vanilla JS, custom CSS |
| Static files | WhiteNoise |
| Fonts | Source Serif 4 (headings) + Inter (body), via Google Fonts |
| Deployment | Render + Gunicorn (via `render.yaml`) |

## Design

The UI is built on a **Claude-inspired light design system**:

- **Palette** — Warm cream backgrounds (`#f5f4ee`), white cards, soft warm borders
- **Accent** — Claude coral (`#d97757`) for primary actions, active states, and highlights; muted sage for success, brick red for danger
- **Typography** — **Source Serif 4** for large display headings, **Inter** for body and UI text
- **Components** — Tinted light stat cards (no dark gradients), soft shadows, flat primary buttons
- **Charts** — SVG, client-rendered: vibrant multi-hue gradient area waves for trends and donut breakdowns, all tuned to the light theme
- **Animations** — Smooth fill-bar animations, staggered card entrances, modal slide-in

## Getting Started

### Prerequisites

- Python 3.9+
- pip

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd spendly

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Initialize the database (creates schema + seeds default categories)
python init_db.py

# Run the development server
python run.py
```

Open [http://localhost:5001](http://localhost:5001) in your browser.

### Windows Quick Start

```bat
run.bat
```

## Project Structure

```
spendly/
├── app/
│   ├── __init__.py          # App factory, blueprint registration, schema bootstrap
│   ├── config.py            # Configuration (secret key, DB settings)
│   ├── services.py          # Recurring-transaction processing
│   ├── database/
│   │   └── connection.py    # DB connection + schema helpers (SQLite/Postgres)
│   ├── routes/              # Flask blueprints
│   │   ├── auth.py            # Register, login, logout
│   │   ├── home.py            # Overview page
│   │   ├── dashboard.py       # Monthly dashboard
│   │   ├── transactions.py    # Add/edit/delete + transaction ledger
│   │   ├── budgets.py         # Budget setting
│   │   ├── goals.py           # Goals + fund add/withdraw
│   │   ├── recurring.py       # Recurring rules
│   │   ├── analytics.py       # Trends, breakdowns, insights
│   │   ├── account.py         # Settings, reset, delete account
│   │   └── export.py          # CSV export
│   ├── static/
│   │   ├── css/style.css      # Full design system
│   │   └── js/main.js         # Sidebar toggle, toasts, animations
│   └── templates/             # Jinja2 HTML templates
│       ├── base.html           # Shell with sidebar (auth) / navbar (public)
│       ├── home.html
│       ├── dashboard.html
│       ├── history.html        # Transactions page
│       ├── analytics.html
│       ├── goals.html
│       ├── account.html        # Settings
│       ├── landing.html
│       ├── login.html
│       ├── register.html
│       └── terms.html
├── database/
│   └── spendly.db           # SQLite database
├── init_db.py               # Schema initialization + category seed
├── run.py                   # Entry point (port 5001)
├── run.bat                  # Windows quick-start
├── requirements.txt
└── render.yaml              # Render deployment config
```

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl + E` | Open Add Expense modal |
| `Ctrl + I` | Open Add Income modal |
| `Esc` | Close any open modal |

## Deployment

The app is configured for deployment on [Render](https://render.com) via `render.yaml`, served by Gunicorn. Configure these environment variables in the Render dashboard:

- `SECRET_KEY` — Flask session signing key
- `DATABASE_URL` — PostgreSQL connection string (when present, the app uses Postgres; otherwise it falls back to local SQLite)

---

Built with care by Md Emon Hasan.
