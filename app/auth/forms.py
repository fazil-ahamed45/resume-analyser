from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional
from app.models import User

EXPERIENCE_CHOICES = [
    ("fresher", "Fresher / College Student"),
    ("1-2_years", "1 - 2 Years (Early Career)"),
    ("student", "Current Undergraduate / Intern"),
]

TARGET_ROLE_CHOICES = [
    ("Python Developer Intern", "Python Developer Intern"),
    ("Backend Developer Intern", "Backend Developer Intern"),
    ("Full Stack Developer Intern", "Full Stack Developer Intern"),
    ("Data Analyst Intern", "Data Analyst Intern"),
    ("QA Automation Intern", "QA Automation Intern"),
    ("Software Engineer Intern", "Software Engineer Intern"),
]


class LoginForm(FlaskForm):
    email = StringField("Email Address", validators=[DataRequired(), Email(), Length(max=150)])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Keep me logged in")
    submit = SubmitField("Sign In")


class RegisterForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField("Email Address", validators=[DataRequired(), Email(), Length(max=150)])
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8, message="Password must be at least 8 characters long."),
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
    )
    experience_level = SelectField("Experience Level", choices=EXPERIENCE_CHOICES, default="fresher")
    target_role = SelectField("Target Role", choices=TARGET_ROLE_CHOICES, default="Python Developer Intern")
    ai_consent = BooleanField("I agree to optional external AI processing of resume snippets when enabled")
    submit = SubmitField("Create Account")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower().strip()).first():
            raise ValidationError("An account with this email address already exists.")


class ProfileForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=100)])
    experience_level = SelectField("Experience Level", choices=EXPERIENCE_CHOICES)
    target_role = SelectField("Target Role", choices=TARGET_ROLE_CHOICES)
    ai_consent = BooleanField("Enable optional external AI processing")
    current_password = PasswordField("Current Password (required only if updating password)", validators=[Optional()])
    new_password = PasswordField(
        "New Password",
        validators=[
            Optional(),
            Length(min=8, message="New password must be at least 8 characters."),
        ],
    )
    confirm_new_password = PasswordField(
        "Confirm New Password",
        validators=[
            EqualTo("new_password", message="New passwords must match."),
        ],
    )
    submit = SubmitField("Update Profile")
