from app.services.job_matcher import compare_resume_to_job, extract_skills_from_job_text
from app.models import JobComparison


def test_job_skill_extraction():
    jd = """
    Required Qualifications:
    - Proficiency in Python, SQL, and Git
    - Knowledge of REST API design and relational databases
    
    Preferred Skills:
    - Experience with Docker, Kubernetes, and Redis
    - Prior exposure to FastAPI or Django
    """
    extracted = extract_skills_from_job_text(jd)
    assert "Python" in extracted["required"]
    assert "SQL" in extracted["required"]
    assert "Git" in extracted["required"]
    assert "Docker" in extracted["preferred"]
    assert "Kubernetes" in extracted["preferred"]


def test_compare_resume_to_job():
    candidate_skills = ["Python", "SQL", "Git", "Flask"]
    jd = """
    We are seeking a Python Intern.
    Requirements: Python, SQL, Git, and Docker.
    Nice to have: Redis and AWS.
    """
    res = compare_resume_to_job(candidate_skills, jd, job_title="Python Intern")

    assert res["match_percentage"] > 0
    assert "Python" in res["matched_skills"]
    assert "SQL" in res["matched_skills"]
    assert "Git" in res["matched_skills"]
    assert "Docker" in res["missing_required_skills"]
    assert "Redis" in res["missing_preferred_skills"]
    assert len(res["recommendations"]) > 0


def test_job_match_route_flow(auth_client, registered_user, db_session):
    # Create a resume in DB for the user
    from app.models import Resume
    resume = Resume(
        user_id=registered_user.id,
        original_filename="test.pdf",
        stored_filename="test_uuid.pdf",
        file_type="pdf",
        file_size=1024,
        raw_text="Python developer with SQL, Git, and Flask project experience.",
        target_role="Python Developer Intern",
    )
    db_session.add(resume)
    db_session.commit()

    res = auth_client.post(
        "/career/match",
        data={
            "resume_id": resume.id,
            "job_title": "Backend Engineering Intern",
            "company_name": "Tech Corp",
            "job_description": "We require Python, SQL, Git, and Docker. Experience with REST APIs is preferred.",
        },
        follow_redirects=True,
    )
    assert res.status_code == 200
    assert b"Comparison complete" in res.data
    assert b"Backend Engineering Intern" in res.data

    comp = JobComparison.query.filter_by(job_title="Backend Engineering Intern").first()
    assert comp is not None
    assert comp.match_percentage > 50
