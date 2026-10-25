from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlsplit
from app.auth import bp
from app.auth.forms import LoginForm, RegisterForm, ProfileForm
from app.models import User
from app.extensions import db


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            full_name=form.full_name.data.strip(),
            email=form.email.data.lower().strip(),
            experience_level=form.experience_level.data,
            target_role=form.target_role.data,
            ai_consent=form.ai_consent.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash("Account created successfully! You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", title="Create Account", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid email or password. Please try again.", "danger")
            return redirect(url_for("auth.login"))

        login_user(user, remember=form.remember_me.data)
        flash(f"Welcome back, {user.full_name.split()[0]}!", "success")

        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc != "":
            next_page = url_for("dashboard.index")
        return redirect(next_page)

    return render_template("auth/login.html", title="Sign In", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("auth.login"))


@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm(obj=current_user)

    if form.validate_on_submit():
        # Check if password change is requested
        if form.new_password.data:
            if not form.current_password.data or not current_user.check_password(form.current_password.data):
                flash("Current password was incorrect. Password was not changed.", "danger")
                return render_template("auth/profile.html", title="Profile Settings", form=form)
            current_user.set_password(form.new_password.data)
            flash("Your password has been updated.", "success")

        current_user.full_name = form.full_name.data.strip()
        current_user.experience_level = form.experience_level.data
        current_user.target_role = form.target_role.data
        current_user.ai_consent = form.ai_consent.data

        db.session.commit()
        flash("Your profile preferences have been updated.", "success")
        return redirect(url_for("auth.profile"))

    return render_template("auth/profile.html", title="Profile Settings", form=form)
