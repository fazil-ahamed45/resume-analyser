from app.services.ai_service import (
    generate_rule_based_coach_feedback,
    get_ai_resume_coach_feedback,
)


def test_deterministic_rule_based_coach():
    target_role = "Python Developer Intern"
    detected_skills = ["Python", "Flask", "SQL"]
    missing_skills = ["Docker", "PostgreSQL"]
    weak_bullets = [
        {"original": "Worked on a website with Python.", "issues": ["Starts with weak phrasing"]}
    ]
    sections = {"projects": "Website with Python"}

    res = generate_rule_based_coach_feedback(
        target_role, detected_skills, missing_skills, weak_bullets, sections
    )

    assert res["is_ai_generated"] is False
    assert "summary_recommendation" in res
    assert len(res["rewritten_bullets"]) > 0
    assert len(res["gap_explanations"]) > 0

    # Ensure rewritten bullet has an action verb
    rewritten = res["rewritten_bullets"][0]["suggestion"]
    assert any(verb in rewritten for verb in ["Architected", "Engineered", "Implemented", "Developed", "Optimized"])


def test_ai_coach_graceful_fallback_without_consent(app):
    with app.app_context():
        # User has NOT consented to external AI
        feedback = get_ai_resume_coach_feedback(
            user_has_consented=False,
            target_role="Backend Developer Intern",
            detected_skills=["Python", "SQL"],
            missing_skills=["Redis"],
            weak_bullets=[],
            sections={},
            raw_resume_text="Sample resume text",
        )
        assert feedback["is_ai_generated"] is False
        assert "Deterministic Rule-Based" in feedback["provider"]
