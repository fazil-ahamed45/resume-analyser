import io
from app.services.report_service import generate_pdf_report
from app.models import Resume, ResumeAnalysis


def test_pdf_report_generation():
    breakdown = {
        "section_completeness": {"score": 25, "max_score": 25, "explanation": "All sections present"},
        "skills_relevance": {"score": 26, "max_score": 30, "explanation": "High skill alignment"},
        "project_experience": {"score": 18, "max_score": 20, "explanation": "Solid projects"},
        "bullet_quality": {"score": 12, "max_score": 15, "explanation": "Good action verbs"},
        "readability": {"score": 10, "max_score": 10, "explanation": "Clear format"},
    }
    detected_skills = {
        "categorized": {
            "programming_languages": ["Python", "SQL"],
            "frameworks_libraries": ["Flask", "FastAPI"],
        }
    }
    strengths = ["Strong core language foundation", "Clean formatting"]
    weaknesses = ["Add more metrics to bullet points"]
    tips = ["Add GitHub links to projects", "Quantify database optimizations"]

    pdf_stream = generate_pdf_report(
        candidate_name="Alice Candidate",
        email="alice@example.com",
        target_role="Python Developer Intern",
        experience_level="Fresher",
        total_score=85,
        score_breakdown=breakdown,
        detected_skills=detected_skills,
        strengths=strengths,
        weaknesses=weaknesses,
        actionable_tips=tips,
        roadmap_items=[{"skill_name": "Docker", "priority": "High", "practice_task": "Write Dockerfile"}],
    )

    assert isinstance(pdf_stream, io.BytesIO)
    content = pdf_stream.getvalue()
    assert len(content) > 1000
    assert content.startswith(b"%PDF-")


def test_download_pdf_endpoint(auth_client, registered_user, db_session):
    resume = Resume(
        user_id=registered_user.id,
        original_filename="audit_resume.pdf",
        stored_filename="audit_uuid.pdf",
        file_type="pdf",
        file_size=2048,
        raw_text="Python and SQL skills",
        target_role="Python Developer Intern",
    )
    db_session.add(resume)
    db_session.commit()

    analysis = ResumeAnalysis(
        resume_id=resume.id,
        user_id=registered_user.id,
        target_role="Python Developer Intern",
        experience_level="fresher",
        total_score=82,
    )
    analysis.score_breakdown = {
        "section_completeness": {"score": 20, "max_score": 25, "explanation": "Good"},
        "skills_relevance": {"score": 24, "max_score": 30, "explanation": "High"},
        "project_experience": {"score": 16, "max_score": 20, "explanation": "Deep"},
        "bullet_quality": {"score": 12, "max_score": 15, "explanation": "Strong"},
        "readability": {"score": 10, "max_score": 10, "explanation": "Clear"},
    }
    analysis.detected_skills = {"categorized": {"programming_languages": ["Python"]}}
    analysis.strengths = ["Solid technical background"]
    analysis.weaknesses = ["Include more metrics"]
    analysis.bullet_suggestions = ["Quantify achievements"]
    db_session.add(analysis)
    db_session.commit()

    res = auth_client.get(f"/analysis/{analysis.id}/report.pdf")
    assert res.status_code == 200
    assert res.mimetype == "application/pdf"
    assert b"%PDF-" in res.data
