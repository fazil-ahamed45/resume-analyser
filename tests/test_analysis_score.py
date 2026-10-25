from app.services.section_extractor import (
    extract_skills_with_evidence,
    split_into_sections,
    extract_contact_info,
    analyze_bullet_points,
)
from app.services.scoring_service import calculate_overall_resume_score


def test_skills_extraction_and_evidence():
    text = (
        "Experienced in Python and Flask development.\n"
        "Configured Docker containers and wrote SQL queries for PostgreSQL.\n"
        "Used Git for team collaboration and version control."
    )
    data = extract_skills_with_evidence(text)
    skills = data["all_skills"]

    assert "Python" in skills
    assert "Flask" in skills
    assert "Docker" in skills
    assert "SQL" in skills
    assert "PostgreSQL" in skills
    assert "Git" in skills

    # Check evidence snippet
    assert "Python" in data["evidence"]
    assert "Flask" in data["evidence"]["Python"] or "Python" in data["evidence"]["Python"]


def test_section_splitting():
    raw_resume = (
        "John Doe\njohn@example.com\n\n"
        "EDUCATION\n"
        "B.S. in Computer Science, 2025\n\n"
        "TECHNICAL SKILLS\n"
        "Python, Java, Git, Docker\n\n"
        "PROJECTS\n"
        "REST API Service\n"
        "- Engineered microservice handling 100 req/sec.\n"
    )
    sections = split_into_sections(raw_resume)
    assert "education" in sections
    assert "skills" in sections
    assert "projects" in sections
    assert "B.S. in Computer Science" in sections["education"]


def test_explainable_score_fresher_mode():
    raw_resume = (
        "Alice Candidate\nalice@example.com | +1 555-0100 | https://github.com/alice | https://linkedin.com/in/alice\n\n"
        "SUMMARY\n"
        "Motivated computer science undergraduate seeking a Python Developer Internship. Passionate about backend systems.\n\n"
        "EDUCATION\nB.E. in Computer Science and Engineering, State College of Engineering, Expected 2026, CGPA 8.8/10\n\n"
        "TECHNICAL SKILLS\nProgramming Languages: Python, SQL, JavaScript, HTML5, CSS3\n"
        "Frameworks & Libraries: Flask, Django, PostgreSQL, SQLite, Pytest, REST API\n"
        "Developer Tools: Git, GitHub, Docker, Linux, Postman\n\n"
        "PROJECTS\n"
        "Distributed Web App | Python, Flask, Docker, PostgreSQL\n"
        "- Engineered a full-stack job application tracker with Flask-Login and PostgreSQL database.\n"
        "- Optimized relational database queries reducing average API response times by 35%.\n"
        "- Deployed microservices using Docker containers and configured automated CI/CD workflows.\n\n"
        "RESTful Task Management API | Python, FastAPI, SQLite\n"
        "- Architected asynchronous CRUD endpoints handling 200+ requests per second with automated validation.\n"
        "- Implemented comprehensive unit test suite with Pytest achieving 92% statement coverage.\n"
    )
    contact = extract_contact_info(raw_resume)
    sections = split_into_sections(raw_resume)
    skills_data = extract_skills_with_evidence(raw_resume)
    bullet_data = analyze_bullet_points(sections)

    score_result = calculate_overall_resume_score(
        raw_text=raw_resume,
        sections=sections,
        contact=contact,
        detected_skills=skills_data["all_skills"],
        target_role="Python Developer Intern",
        experience_level="fresher",
        bullet_analysis=bullet_data,
    )

    total = score_result["total_score"]
    assert 0 <= total <= 100
    assert total >= 70  # Strong fresher resume with projects should score high

    breakdown = score_result["breakdown"]
    assert breakdown["section_completeness"]["score"] > 0
    assert breakdown["skills_relevance"]["score"] > 0
    assert breakdown["project_experience"]["score"] > 0
    assert breakdown["bullet_quality"]["score"] > 0
    assert breakdown["readability"]["score"] > 0
    assert "disclaimer" in score_result
