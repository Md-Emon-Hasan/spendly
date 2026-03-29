from flask import Flask, render_template, session, redirect, url_for
from database.connection import close_db

# Import Blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.analytics import analytics_bp
from routes.transactions import transactions_bp

app = Flask(__name__)
app.secret_key = "super_secret_bachelor_key_123"

# Register teardown function to close DB after request
app.teardown_appcontext(close_db)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(transactions_bp)

# Root Landing Route
@app.route("/")
def landing():
    if "user_id" in session:
        return redirect(url_for("dashboard.index"))
    return render_template("landing.html")

# Terms Route
@app.route("/terms")
def terms():
    return render_template("terms.html")

if __name__ == "__main__":
    app.run(debug=True, port=5001)
