"""
Personalized learning roadmap generator with verified, official resource URLs
and practical portfolio tasks tailored to bridge skill gaps.
"""

from typing import Any

# Verified authoritative resources directory
VERIFIED_RESOURCES = {
    "Python": {
        "title": "Official Python 3 Documentation & Tutorial",
        "url": "https://docs.python.org/3/tutorial/",
        "hours": 12,
        "difficulty": "Beginner",
        "task": "Build a command-line expense tracker with data persistence using JSON or SQLite.",
        "project": "Personal Finance CLI Tool with category summaries and monthly budget alerts."
    },
    "Flask": {
        "title": "Official Flask Quickstart & Tutorial",
        "url": "https://flask.palletsprojects.com/en/stable/quickstart/",
        "hours": 14,
        "difficulty": "Intermediate",
        "task": "Create a RESTful CRUD API with SQLite and authentication using Flask-Login.",
        "project": "Task and Habit Tracker Web App with user auth and SQLite backend."
    },
    "Django": {
        "title": "Official Django Tutorial",
        "url": "https://docs.djangoproject.com/en/stable/intro/tutorial01/",
        "hours": 20,
        "difficulty": "Intermediate",
        "task": "Build a multi-model blogging platform with admin panel and user comments.",
        "project": "E-Commerce or College Course Enrollment Portal with Django ORM."
    },
    "FastAPI": {
        "title": "Official FastAPI Tutorial - User Guide",
        "url": "https://fastapi.tiangolo.com/tutorial/",
        "hours": 12,
        "difficulty": "Intermediate",
        "task": "Build an asynchronous API with Pydantic request validation and auto-generated Swagger docs.",
        "project": "URL Shortener and Analytics API with rate limiting and automated docs."
    },
    "SQL": {
        "title": "SQLZoo Interactive SQL Tutorial",
        "url": "https://sqlzoo.net/",
        "hours": 10,
        "difficulty": "Beginner",
        "task": "Write complex multi-table JOINs, GROUP BY aggregations, and window functions.",
        "project": "Retail Sales Analysis database with optimized indexing and aggregation queries."
    },
    "PostgreSQL": {
        "title": "PostgreSQL Official Documentation",
        "url": "https://www.postgresql.org/docs/current/tutorial.html",
        "hours": 12,
        "difficulty": "Intermediate",
        "task": "Set up a local PostgreSQL database, create indexes, and connect via Python psycopg2/SQLAlchemy.",
        "project": "Multi-tenant Event Registration Database with ACID transactions."
    },
    "Git": {
        "title": "Pro Git Book (Free by Scott Chacon & Ben Straub)",
        "url": "https://git-scm.com/book/en/v2",
        "hours": 8,
        "difficulty": "Beginner",
        "task": "Practice branching, rebasing, resolving merge conflicts, and creating pull requests.",
        "project": "Open-source GitHub repository with feature branches, PR templates, and release tags."
    },
    "Docker": {
        "title": "Docker Official Getting Started Guide",
        "url": "https://docs.docker.com/get-started/",
        "hours": 14,
        "difficulty": "Intermediate",
        "task": "Write a multi-stage Dockerfile for a Python application and orchestrate with Docker Compose.",
        "project": "Containerized Flask + PostgreSQL + Redis application running via docker-compose."
    },
    "REST API": {
        "title": "MDN Web Docs: An Overview of HTTP and REST",
        "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview",
        "hours": 10,
        "difficulty": "Beginner",
        "task": "Design RESTful URL structures adhering to standard HTTP verbs, status codes, and JSON errors.",
        "project": "Book Review REST API with filtering, pagination, and JWT authentication."
    },
    "Pytest": {
        "title": "Official Pytest Documentation",
        "url": "https://docs.pytest.org/en/stable/getting-started.html",
        "hours": 8,
        "difficulty": "Beginner",
        "task": "Write unit and integration tests using pytest fixtures, parametrize, and test coverage tools.",
        "project": "Test suite with 90%+ code coverage for an existing Python library or API."
    },
    "Data Structures & Algorithms": {
        "title": "GeeksforGeeks Python Data Structures & Algorithms",
        "url": "https://www.geeksforgeeks.org/python-data-structures-and-algorithms/",
        "hours": 25,
        "difficulty": "Intermediate",
        "task": "Implement Linked Lists, Binary Search Trees, and Graph BFS/DFS from scratch in Python.",
        "project": "Pathfinding visualizer or custom LRU Cache implementation."
    },
    "CI/CD": {
        "title": "GitHub Actions Documentation: Quickstart",
        "url": "https://docs.github.com/en/actions/quickstart",
        "hours": 8,
        "difficulty": "Intermediate",
        "task": "Create a GitHub Actions workflow that runs pytest and flake8 on every push and PR.",
        "project": "Automated CI/CD pipeline running linting, test suites, and Docker builds on GitHub."
    },
    "Linux": {
        "title": "The Linux Command Line (LinuxCommand.org)",
        "url": "https://linuxcommand.org/tlcl.php",
        "hours": 10,
        "difficulty": "Beginner",
        "task": "Master file permissions, SSH key setup, grep, systemctl, and bash scripting.",
        "project": "Automated server backup and log analysis shell script."
    },
    "Pandas": {
        "title": "Official Pandas 10-Minute Tutorial",
        "url": "https://pandas.pydata.org/docs/user_guide/10min.html",
        "hours": 12,
        "difficulty": "Beginner",
        "task": "Perform data cleaning, handling missing values, pivoting, and grouping on real-world CSVs.",
        "project": "Exploratory Data Analysis (EDA) of job market trends using real Kaggle datasets."
    },
    "JavaScript": {
        "title": "MDN JavaScript Guide",
        "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide",
        "hours": 16,
        "difficulty": "Beginner",
        "task": "Master ES6+ syntax, Promises, async/await, and DOM manipulation without libraries.",
        "project": "Interactive Kanban task board with local storage persistence."
    },
    "React": {
        "title": "Official React Documentation (react.dev)",
        "url": "https://react.dev/learn",
        "hours": 18,
        "difficulty": "Intermediate",
        "task": "Build component state, custom hooks, and manage API fetch calls with loading and error states.",
        "project": "Job Tracker Dashboard consuming a REST backend with client-side filtering."
    }
}


def generate_roadmap_for_role(
    missing_skills: list[str],
    target_role: str = "Python Developer Intern"
) -> list[dict[str, Any]]:
    """
    Generate tailored learning milestones based on detected skill gaps.
    If few skills are missing, provides advanced portfolio milestones for the target role.
    """
    milestones = []
    
    # Priority sorting: if skill is missing, add it
    for i, skill in enumerate(missing_skills):
        info = VERIFIED_RESOURCES.get(skill)
        priority = "High" if i < 3 else "Medium"
        if info:
            milestones.append({
                "skill_name": skill,
                "category": "Technical Gap",
                "priority": priority,
                "difficulty": info["difficulty"],
                "estimated_hours": info["hours"],
                "reason": f"Required or heavily preferred for {target_role} roles.",
                "practice_task": info["task"],
                "project_idea": info["project"],
                "resource_title": info["title"],
                "resource_url": info["url"],
            })

    # If the candidate has almost all skills or missing list is small, add advanced role milestones
    if len(milestones) < 3:
        fallback_skills = ["Docker", "Pytest", "CI/CD", "Data Structures & Algorithms"]
        for skill in fallback_skills:
            if skill not in [m["skill_name"] for m in milestones]:
                info = VERIFIED_RESOURCES.get(skill)
                if info:
                    milestones.append({
                        "skill_name": skill,
                        "category": "Portfolio Enhancement",
                        "priority": "Medium",
                        "difficulty": info["difficulty"],
                        "estimated_hours": info["hours"],
                        "reason": f"Elevates your portfolio for competitive {target_role} applications.",
                        "practice_task": info["task"],
                        "project_idea": info["project"],
                        "resource_title": info["title"],
                        "resource_url": info["url"],
                    })
            if len(milestones) >= 4:
                break

    return milestones
