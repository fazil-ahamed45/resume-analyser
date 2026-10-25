import json
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    experience_level = db.Column(db.String(50), default="fresher", nullable=False)
    target_role = db.Column(db.String(100), default="Python Developer Intern", nullable=False)
    ai_consent = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships with cascading deletes for complete user cleanup
    resumes = db.relationship("Resume", backref="owner", cascade="all, delete-orphan", lazy="dynamic")
    analyses = db.relationship("ResumeAnalysis", backref="user", cascade="all, delete-orphan", lazy="dynamic")
    job_comparisons = db.relationship("JobComparison", backref="user", cascade="all, delete-orphan", lazy="dynamic")
    roadmap_items = db.relationship("RoadmapItem", backref="user", cascade="all, delete-orphan", lazy="dynamic")
    interview_sessions = db.relationship("InterviewSession", backref="user", cascade="all, delete-orphan", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"


class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), unique=True, nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # 'pdf' or 'docx'
    file_size = db.Column(db.Integer, nullable=False)
    raw_text = db.Column(db.Text, nullable=False, default="")
    _extracted_contact = db.Column("extracted_contact", db.Text, default="{}")
    _extracted_sections = db.Column("extracted_sections", db.Text, default="{}")
    is_scanned_pdf = db.Column(db.Boolean, default=False, nullable=False)
    target_role = db.Column(db.String(100), default="Python Developer Intern")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    analyses = db.relationship("ResumeAnalysis", backref="resume", cascade="all, delete-orphan", lazy="dynamic")
    job_comparisons = db.relationship("JobComparison", backref="resume", cascade="all, delete-orphan", lazy="dynamic")

    @property
    def extracted_contact(self):
        try:
            return json.loads(self._extracted_contact or "{}")
        except Exception:
            return {}

    @extracted_contact.setter
    def extracted_contact(self, val):
        self._extracted_contact = json.dumps(val if isinstance(val, dict) else {})

    @property
    def extracted_sections(self):
        try:
            return json.loads(self._extracted_sections or "{}")
        except Exception:
            return {}

    @extracted_sections.setter
    def extracted_sections(self, val):
        self._extracted_sections = json.dumps(val if isinstance(val, dict) else {})

    @property
    def latest_analysis(self):
        return self.analyses.order_by(ResumeAnalysis.created_at.desc()).first()

    def __repr__(self):
        return f"<Resume {self.id}: {self.original_filename}>"


class ResumeAnalysis(db.Model):
    __tablename__ = "resume_analyses"

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    target_role = db.Column(db.String(100), nullable=False)
    experience_level = db.Column(db.String(50), nullable=False)
    total_score = db.Column(db.Integer, nullable=False)
    _score_breakdown = db.Column("score_breakdown", db.Text, nullable=False, default="{}")
    _detected_skills = db.Column("detected_skills", db.Text, nullable=False, default="{}")
    _missing_sections = db.Column("missing_sections", db.Text, nullable=False, default="[]")
    _strengths = db.Column("strengths", db.Text, nullable=False, default="[]")
    _weaknesses = db.Column("weaknesses", db.Text, nullable=False, default="[]")
    _bullet_suggestions = db.Column("bullet_suggestions", db.Text, nullable=False, default="[]")
    _ai_suggestions = db.Column("ai_suggestions", db.Text, nullable=True, default="{}")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @property
    def score_breakdown(self):
        try:
            return json.loads(self._score_breakdown or "{}")
        except Exception:
            return {}

    @score_breakdown.setter
    def score_breakdown(self, val):
        self._score_breakdown = json.dumps(val)

    @property
    def detected_skills(self):
        try:
            return json.loads(self._detected_skills or "{}")
        except Exception:
            return {}

    @detected_skills.setter
    def detected_skills(self, val):
        self._detected_skills = json.dumps(val)

    @property
    def missing_sections(self):
        try:
            return json.loads(self._missing_sections or "[]")
        except Exception:
            return []

    @missing_sections.setter
    def missing_sections(self, val):
        self._missing_sections = json.dumps(val)

    @property
    def strengths(self):
        try:
            return json.loads(self._strengths or "[]")
        except Exception:
            return []

    @strengths.setter
    def strengths(self, val):
        self._strengths = json.dumps(val)

    @property
    def weaknesses(self):
        try:
            return json.loads(self._weaknesses or "[]")
        except Exception:
            return []

    @weaknesses.setter
    def weaknesses(self, val):
        self._weaknesses = json.dumps(val)

    @property
    def bullet_suggestions(self):
        try:
            return json.loads(self._bullet_suggestions or "[]")
        except Exception:
            return []

    @bullet_suggestions.setter
    def bullet_suggestions(self, val):
        self._bullet_suggestions = json.dumps(val)

    @property
    def ai_suggestions(self):
        try:
            return json.loads(self._ai_suggestions or "{}")
        except Exception:
            return {}

    @ai_suggestions.setter
    def ai_suggestions(self, val):
        self._ai_suggestions = json.dumps(val)

    def __repr__(self):
        return f"<ResumeAnalysis {self.id} for Resume {self.resume_id} - Score {self.total_score}>"


class JobComparison(db.Model):
    __tablename__ = "job_comparisons"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    job_title = db.Column(db.String(150), nullable=False)
    company_name = db.Column(db.String(100), default="Target Company")
    job_description_raw = db.Column(db.Text, nullable=False)
    match_percentage = db.Column(db.Integer, nullable=False)
    _matched_skills = db.Column("matched_skills", db.Text, nullable=False, default="[]")
    _missing_required_skills = db.Column("missing_required_skills", db.Text, nullable=False, default="[]")
    _missing_preferred_skills = db.Column("missing_preferred_skills", db.Text, nullable=False, default="[]")
    _additional_skills = db.Column("additional_skills", db.Text, nullable=False, default="[]")
    _recommendations = db.Column("recommendations", db.Text, nullable=False, default="[]")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @property
    def matched_skills(self):
        try:
            return json.loads(self._matched_skills or "[]")
        except Exception:
            return []

    @matched_skills.setter
    def matched_skills(self, val):
        self._matched_skills = json.dumps(val)

    @property
    def missing_required_skills(self):
        try:
            return json.loads(self._missing_required_skills or "[]")
        except Exception:
            return []

    @missing_required_skills.setter
    def missing_required_skills(self, val):
        self._missing_required_skills = json.dumps(val)

    @property
    def missing_preferred_skills(self):
        try:
            return json.loads(self._missing_preferred_skills or "[]")
        except Exception:
            return []

    @missing_preferred_skills.setter
    def missing_preferred_skills(self, val):
        self._missing_preferred_skills = json.dumps(val)

    @property
    def additional_skills(self):
        try:
            return json.loads(self._additional_skills or "[]")
        except Exception:
            return []

    @additional_skills.setter
    def additional_skills(self, val):
        self._additional_skills = json.dumps(val)

    @property
    def recommendations(self):
        try:
            return json.loads(self._recommendations or "[]")
        except Exception:
            return []

    @recommendations.setter
    def recommendations(self, val):
        self._recommendations = json.dumps(val)

    def __repr__(self):
        return f"<JobComparison {self.id}: {self.job_title} ({self.match_percentage}%)>"


class RoadmapItem(db.Model):
    __tablename__ = "roadmap_items"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    target_role = db.Column(db.String(100), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), default="Technical")
    priority = db.Column(db.String(20), default="High")  # High, Medium, Low
    difficulty = db.Column(db.String(20), default="Beginner")  # Beginner, Intermediate, Advanced
    estimated_hours = db.Column(db.Integer, default=10)
    reason = db.Column(db.Text, nullable=False)
    practice_task = db.Column(db.Text, nullable=False)
    project_idea = db.Column(db.Text, nullable=False)
    resource_title = db.Column(db.String(200), nullable=True)
    resource_url = db.Column(db.String(500), nullable=True)
    is_completed = db.Column(db.Boolean, default=False, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<RoadmapItem {self.skill_name} ({'Done' if self.is_completed else 'Pending'})>"


class InterviewSession(db.Model):
    __tablename__ = "interview_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=True)
    target_role = db.Column(db.String(100), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), default="Technical")
    sample_outline = db.Column(db.Text, nullable=False)
    _key_concepts = db.Column("key_concepts", db.Text, default="[]")
    user_answer = db.Column(db.Text, nullable=True)
    self_assessment_score = db.Column(db.Integer, default=0)
    _feedback = db.Column("feedback", db.Text, default="{}")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @property
    def key_concepts(self):
        try:
            return json.loads(self._key_concepts or "[]")
        except Exception:
            return []

    @key_concepts.setter
    def key_concepts(self, val):
        self._key_concepts = json.dumps(val)

    @property
    def feedback(self):
        try:
            return json.loads(self._feedback or "{}")
        except Exception:
            return {}

    @feedback.setter
    def feedback(self, val):
        self._feedback = json.dumps(val)

    def __repr__(self):
        return f"<InterviewSession {self.id}: {self.question_type}>"
