from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, Optional


class JobMatchForm(FlaskForm):
    resume_id = SelectField("Select Resume for Comparison", coerce=int, validators=[DataRequired()])
    job_title = StringField("Target Job / Internship Title", validators=[DataRequired(), Length(max=150)])
    company_name = StringField("Company Name (Optional)", validators=[Optional(), Length(max=100)])
    job_description = TextAreaField(
        "Paste Job or Internship Description",
        validators=[
            DataRequired(),
            Length(min=50, message="Please paste a complete job description (at least 50 characters)."),
        ],
    )
    submit = SubmitField("Compare & Match Skills")


class InterviewAnswerForm(FlaskForm):
    question_text = HiddenField("Question", validators=[DataRequired()])
    key_concepts = HiddenField("Key Concepts", validators=[DataRequired()])
    category = HiddenField("Category", validators=[DataRequired()])
    user_answer = TextAreaField(
        "Type Your Interview Answer",
        validators=[
            DataRequired(message="Please enter your answer before evaluating."),
            Length(min=10, message="Please provide a more complete answer (at least 10 words)."),
        ],
    )
    submit = SubmitField("Evaluate Answer")
