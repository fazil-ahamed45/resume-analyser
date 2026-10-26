import os
from pathlib import Path
from flask import Flask, render_template, redirect, url_for
from flask_login import current_user
from config import config_by_name
from app.extensions import db, login_manager, csrf


def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Ensure upload directories exist (with fallback for read-only serverless environments like Vercel)
    try:
        upload_path = Path(app.config["UPLOAD_FOLDER"])
        upload_path.mkdir(parents=True, exist_ok=True)
    except OSError:
        fallback_upload = Path("/tmp/uploads")
        try:
            fallback_upload.mkdir(parents=True, exist_ok=True)
            app.config["UPLOAD_FOLDER"] = str(fallback_upload)
        except Exception:
            pass

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register Blueprints
    from app.auth import bp as auth_bp
    from app.dashboard import bp as dashboard_bp
    from app.resumes import bp as resumes_bp
    from app.analysis import bp as analysis_bp
    from app.career import bp as career_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(resumes_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(career_bp)

    # Landing page route
    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard.index"))
        return render_template("landing.html")

    # Custom Jinja Template Filters
    @app.template_filter("format_date")
    def format_date(dt, fmt="%b %d, %Y"):
        if not dt:
            return ""
        return dt.strftime(fmt)

    @app.template_filter("score_badge_class")
    def score_badge_class(score):
        if score >= 80:
            return "bg-success"
        elif score >= 60:
            return "bg-primary"
        elif score >= 45:
            return "bg-warning text-dark"
        else:
            return "bg-danger"

    @app.template_filter("category_badge")
    def category_badge(cat_name):
        colors = {
            "programming_languages": "bg-primary",
            "frameworks_libraries": "bg-info text-dark",
            "databases": "bg-success",
            "devops_cloud_tools": "bg-secondary",
            "concepts_methodologies": "bg-dark",
            "soft_skills": "bg-indigo text-white",
        }
        return colors.get(cat_name, "bg-secondary")

    # Error Handlers
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("errors/500.html"), 500

    return app
