# Spendly — Personal Finance Tracker

A clean, elegant personal finance tracker built with Flask. Track income, expenses, set savings goals, and understand your spending patterns — all from a beautiful light-themed dashboard.

## Features

- **Dashboard** — Financial health score, monthly stats, budget tracking, and recent transactions at a glance
- **Transaction History** — Filter by month, category, or type; live search across all records
- **Analytics** — 6-month income vs. expense trend chart, category breakdowns, day-of-week spending analysis
- **Savings Goals** — Create targets with deadlines, fund contributions, and track progress
- **Budget Control** — Set overall or per-category monthly budgets with real-time usage indicators
- **CSV Export** — Download your full transaction history at any time

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask |
| Database | SQLite (via raw SQL) |
| Frontend | Jinja2 templates, vanilla JS, custom CSS |
| Fonts | Plus Jakarta Sans (Google Fonts) |
| Deployment | Render (via `render.yaml`) |

## Design

The UI is built on a **Claude-inspired light design system**:

- **Palette** — Warm off-white backgrounds (`#faf9f7`), cream sidebar (`#f0ede7`), pure white cards
- **Accent** — Warm orange (`#c96a28`) for primary actions, active states, and highlights
- **Typography** — Plus Jakarta Sans with weights 400–900; generous letter-spacing and line-height
- **Components** — Tinted light stat cards (no dark gradients), soft shadows, warm borders (`#e8e3db`)
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

# Initialize the database
python init_db.py

# Run the development server
python run.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

### Windows Quick Start

```bat
run.bat
```

## Project Structure

```
spendly/
├── app/
│   ├── routes/          # Flask blueprints (dashboard, transactions, goals, analytics, auth, export)
│   ├── static/
│   │   ├── css/style.css   # Full design system
│   │   └── js/main.js      # Sidebar toggle, toasts, animations
│   └── templates/          # Jinja2 HTML templates
│       ├── base.html        # Shell with sidebar + navbar
│       ├── dashboard.html
│       ├── history.html
│       ├── analytics.html
│       ├── goals.html
│       ├── landing.html
│       ├── login.html
│       └── register.html
├── database/
│   └── spendly.db       # SQLite database
├── init_db.py           # Schema initialization
├── run.py               # Entry point
├── requirements.txt
└── render.yaml          # Render deployment config
```

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl + E` | Open Add Expense modal |
| `Ctrl + I` | Open Add Income modal |
| `Esc` | Close any open modal |

## Deployment

The app is configured for deployment on [Render](https://render.com) via `render.yaml`. Set `FLASK_SECRET_KEY` as an environment variable in your Render dashboard before deploying.

---

Built with care by Md Emon Hasan.
