from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SelectField, SubmitField
from app.auth.forms import TARGET_ROLE_CHOICES, EXPERIENCE_CHOICES


class ResumeUploadForm(FlaskForm):
    resume_file = FileField(
        "Upload Resume (PDF or DOCX)",
        validators=[
            FileRequired(message="Please select a resume file to upload."),
            FileAllowed(["pdf", "docx"], message="Only PDF and DOCX files are allowed."),
        ],
    )
    target_role = SelectField("Target Internship / Role", choices=TARGET_ROLE_CHOICES, default="Python Developer Intern")
    experience_level = SelectField("Your Level", choices=EXPERIENCE_CHOICES, default="fresher")
    submit = SubmitField("Upload & Analyze")
