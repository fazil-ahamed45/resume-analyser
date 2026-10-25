from app.services.career_service import get_career_recommendations
from app.services.roadmap_service import generate_roadmap_for_role
from app.services.interview_service import (
    generate_interview_questions,
    evaluate_user_answer,
)
from app.models import RoadmapItem


def test_career_recommendations():
    skills = ["Python", "SQL", "Git", "Flask", "PostgreSQL", "Docker"]
    roles = get_career_recommendations(skills)

    assert len(roles) >= 4
    top_role = roles[0]
    assert top_role["fit_percentage"] > 70
    assert "matched_core" in top_role
    assert "intern_responsibilities" in top_role
    assert "why_recommended" in top_role


def test_roadmap_verified_urls():
    missing = ["Docker", "PostgreSQL", "Pytest"]
    roadmap = generate_roadmap_for_role(missing, "Python Developer Intern")

    assert len(roadmap) >= 3
    for item in roadmap:
        assert item["resource_url"].startswith("https://")
        assert len(item["practice_task"]) > 10
        assert len(item["project_idea"]) > 10


def test_roadmap_toggle_route(auth_client, registered_user, db_session):
    item = RoadmapItem(
        user_id=registered_user.id,
        target_role="Python Developer Intern",
        skill_name="Docker",
        priority="High",
        difficulty="Intermediate",
        estimated_hours=14,
        reason="Required for containers",
        practice_task="Write a Dockerfile",
        project_idea="Dockerized Web App",
        is_completed=False,
    )
    db_session.add(item)
    db_session.commit()

    # Toggle to complete
    res = auth_client.post(f"/career/roadmap/{item.id}/toggle", follow_redirects=True)
    assert res.status_code == 200

    updated = db_session.get(RoadmapItem, item.id)
    assert updated.is_completed is True


def test_interview_question_and_evaluation():
    questions = generate_interview_questions(
        detected_skills=["Python", "SQL"],
        target_role="Python Developer Intern",
        sections={"projects": "Built an online store with Python and SQLite"},
    )
    assert len(questions) >= 3

    # Test answer evaluation
    q = questions[0]
    good_answer = (
        "In Python, memory management is primarily handled by reference counting. "
        "When an object's reference count drops to zero, its memory is deallocated immediately. "
        "To handle cyclic references that reference counting cannot resolve, Python employs a generational "
        "garbage collector that scans cyclic objects and frees memory, preventing leaks in applications."
    )
    eval_res = evaluate_user_answer(
        question_text=q["question"],
        key_concepts=q["key_concepts"],
        user_answer=good_answer,
        category="Technical Core",
    )
    assert eval_res["score"] >= 70
    assert eval_res["grade"] in ("Good", "Excellent")
    assert len(eval_res["matched_concepts"]) > 0
