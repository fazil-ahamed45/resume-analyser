from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from app.auth.forms import TARGET_ROLE_CHOICES, EXPERIENCE_CHOICES


class ReanalyzeForm(FlaskForm):
    target_role = SelectField("Target Role", choices=TARGET_ROLE_CHOICES)
    experience_level = SelectField("Experience Level", choices=EXPERIENCE_CHOICES)
    submit = SubmitField("Re-calculate Score")
