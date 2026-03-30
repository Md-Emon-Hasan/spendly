from flask import Flask, render_template, session, redirect, url_for
from .config import Config
from .database.connection import close_db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # --- Jinja Filters ---
    @app.template_filter('format_date')
    def format_date_filter(value):
        if not value:
            return ""
        if hasattr(value, 'strftime'):
            return value.strftime('%Y-%m-%d')
        # If it's a string, just take the date part
        return str(value).split(' ')[0]

    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.dashboard import dashboard_bp
    from .routes.analytics import analytics_bp
    from .routes.transactions import transactions_bp
    from .routes.budgets import budgets_bp
    from .routes.export import export_bp
    from .routes.goals import goals_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(budgets_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(goals_bp)

    @app.route("/")
    def landing():
        if "user_id" in session:
            return redirect(url_for("dashboard.index"))
        return render_template("landing.html")

    @app.route("/terms")
    def terms():
        return render_template("terms.html")

    app.teardown_appcontext(close_db)

    return app
