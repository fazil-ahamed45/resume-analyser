"""
Career recommendations service matching candidate skills against
entry-level tech roles with transparent fit calculations and gap analysis.
"""

from typing import Any

ROLE_PROFILES = [
    {
        "role": "Python Developer Intern",
        "description": "Develop backend scripts, web scrapers, data pipelines, or web applications with Flask/Django.",
        "core_skills": ["Python", "SQL", "Git"],
        "bonus_skills": ["Flask", "Django", "FastAPI", "PostgreSQL", "Docker", "Pytest", "REST API", "Data Structures & Algorithms"],
        "intern_responsibilities": "Write clean Python code, build REST endpoints, write unit tests, and collaborate with Git.",
        "difficulty": "Moderate",
    },
    {
        "role": "Backend Developer Intern",
        "description": "Design and build server-side logic, database schemas, authentication, and REST/GraphQL APIs.",
        "core_skills": ["Python", "SQL", "REST API", "Git"],
        "bonus_skills": ["FastAPI", "Django", "PostgreSQL", "Redis", "Docker", "Linux", "Microservices", "Unit Testing"],
        "intern_responsibilities": "Implement database migrations, build API endpoints, optimize queries, and integrate caching.",
        "difficulty": "Moderate",
    },
    {
        "role": "Full Stack Developer Intern",
        "description": "Build end-to-end web features connecting interactive web frontends to database-backed backends.",
        "core_skills": ["JavaScript", "HTML5", "CSS3", "Git"],
        "bonus_skills": ["Python", "React", "Node.js", "Flask", "PostgreSQL", "MongoDB", "REST API", "Tailwind CSS"],
        "intern_responsibilities": "Create responsive UI components, connect frontend to API endpoints, and fix cross-browser bugs.",
        "difficulty": "Moderate to High",
    },
    {
        "role": "Data Analyst Intern",
        "description": "Collect, clean, visualize data, and extract actionable business insights from relational databases.",
        "core_skills": ["Python", "SQL", "Pandas"],
        "bonus_skills": ["NumPy", "Scikit-Learn", "PostgreSQL", "MySQL", "Analytical Thinking", "Problem Solving", "Git"],
        "intern_responsibilities": "Clean messy datasets, write complex SQL aggregations, build dashboards, and present findings.",
        "difficulty": "Moderate",
    },
    {
        "role": "QA Automation Intern",
        "description": "Develop automated test suites, test API contracts, and verify software reliability and performance.",
        "core_skills": ["Python", "Unit Testing", "Git"],
        "bonus_skills": ["Pytest", "Postman", "CI/CD", "Linux", "REST API", "Debugging", "Problem Solving"],
        "intern_responsibilities": "Write automated test scripts, perform regression testing, identify edge cases, and report bug tickets.",
        "difficulty": "Accessible",
    },
    {
        "role": "DevOps & Cloud Intern",
        "description": "Automate build and deployment pipelines, containerize applications, and maintain cloud environments.",
        "core_skills": ["Git", "Linux", "Docker"],
        "bonus_skills": ["CI/CD", "GitHub Actions", "AWS", "Kubernetes", "Bash", "Terraform", "Nginx", "Python"],
        "intern_responsibilities": "Set up CI/CD workflows, build Docker images, configure web servers, and monitor services.",
        "difficulty": "Advanced",
    }
]


def get_career_recommendations(detected_skills: list[str]) -> list[dict[str, Any]]:
    """
    Evaluate candidate skills against each role profile, calculating match %
    and identifying matched vs missing skills.
    """
    candidate_skills_set = set(detected_skills)
    recommendations = []

    for profile in ROLE_PROFILES:
        core = set(profile["core_skills"])
        bonus = set(profile["bonus_skills"])

        matched_core = core.intersection(candidate_skills_set)
        missing_core = core - candidate_skills_set

        matched_bonus = bonus.intersection(candidate_skills_set)
        missing_bonus = bonus - candidate_skills_set

        # Score calculation: 65% for core skills, 35% for bonus skills
        core_score = (len(matched_core) / len(core)) * 65
        bonus_score = (len(matched_bonus) / len(bonus)) * 35
        fit_percentage = round(core_score + bonus_score)

        # Why recommended text
        why_parts = []
        if matched_core:
            why_parts.append(f"Strong foundation in core skills: {', '.join(sorted(matched_core))}.")
        if matched_bonus:
            why_parts.append(f"Valuable secondary skills: {', '.join(sorted(matched_bonus)[:3])}.")

        why_text = " ".join(why_parts) if why_parts else "You possess foundational concepts transferable to this role."

        recommendations.append({
            "role": profile["role"],
            "description": profile["description"],
            "difficulty": profile["difficulty"],
            "intern_responsibilities": profile["intern_responsibilities"],
            "fit_percentage": fit_percentage,
            "matched_core": sorted(list(matched_core)),
            "missing_core": sorted(list(missing_core)),
            "matched_bonus": sorted(list(matched_bonus)),
            "missing_bonus": sorted(list(missing_bonus)),
            "why_recommended": why_text,
            "next_steps": f"Prioritize learning {', '.join(sorted(missing_core))}" if missing_core else "Build a capstone project demonstrating your end-to-end skills.",
        })

    # Sort descending by fit percentage
    recommendations.sort(key=lambda r: r["fit_percentage"], reverse=True)
    return recommendations
