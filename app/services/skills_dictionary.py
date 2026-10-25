"""
Extensible, curated technical and professional skills taxonomy
with category mappings and alias resolution for accurate detection.
"""

SKILLS_TAXONOMY = {
    "programming_languages": [
        "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go",
        "Rust", "Ruby", "PHP", "SQL", "HTML5", "CSS3", "Bash", "Shell",
        "Kotlin", "Swift", "Scala", "R", "Dart"
    ],
    "frameworks_libraries": [
        "Flask", "Django", "FastAPI", "React", "Node.js", "Express.js",
        "Vue.js", "Angular", "Next.js", "Spring Boot", "PyTorch", "TensorFlow",
        "Pandas", "NumPy", "Scikit-Learn", "Tailwind CSS", "Bootstrap",
        "jQuery", "Celery", "SQLAlchemy", "Redux", "Pytest", "Jest"
    ],
    "databases": [
        "PostgreSQL", "MySQL", "SQLite", "MongoDB", "Redis", "Cassandra",
        "DynamoDB", "Oracle", "Firebase", "Elasticsearch", "Neo4j", "MariaDB"
    ],
    "devops_cloud_tools": [
        "Git", "GitHub", "GitLab", "Docker", "Kubernetes", "AWS", "Azure",
        "Google Cloud", "Linux", "CI/CD", "GitHub Actions", "Jenkins",
        "Nginx", "Apache", "Postman", "Terraform", "Ansible", "Jira"
    ],
    "concepts_methodologies": [
        "REST API", "GraphQL", "Microservices", "Object-Oriented Programming",
        "Data Structures & Algorithms", "Agile", "Scrum", "Test-Driven Development",
        "MVC Architecture", "System Design", "Unit Testing", "Debugging"
    ],
    "soft_skills": [
        "Problem Solving", "Communication", "Team Collaboration", "Leadership",
        "Time Management", "Adaptability", "Critical Thinking", "Mentorship",
        "Presentation Skills", "Analytical Thinking"
    ]
}

# Aliases and variations map to canonical name
SKILL_ALIASES = {
    "py": "Python",
    "python3": "Python",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "c plus plus": "C++",
    "cpp": "C++",
    "c sharp": "C#",
    "c#": "C#",
    "golang": "Go",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "psql": "PostgreSQL",
    "mysql": "MySQL",
    "sqlite": "SQLite",
    "sqlite3": "SQLite",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "react": "React",
    "react.js": "React",
    "reactjs": "React",
    "node": "Node.js",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "express": "Express.js",
    "express.js": "Express.js",
    "expressjs": "Express.js",
    "vue": "Vue.js",
    "vue.js": "Vue.js",
    "vuejs": "Vue.js",
    "angular": "Angular",
    "angularjs": "Angular",
    "next": "Next.js",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "spring": "Spring Boot",
    "springboot": "Spring Boot",
    "html": "HTML5",
    "html5": "HTML5",
    "css": "CSS3",
    "css3": "CSS3",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "bootstrap": "Bootstrap",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "docker": "Docker",
    "aws": "AWS",
    "amazon web services": "AWS",
    "azure": "Azure",
    "microsoft azure": "Azure",
    "gcp": "Google Cloud",
    "google cloud platform": "Google Cloud",
    "google cloud": "Google Cloud",
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "rest": "REST API",
    "restful": "REST API",
    "rest api": "REST API",
    "rest apis": "REST API",
    "graphql": "GraphQL",
    "oop": "Object-Oriented Programming",
    "object-oriented": "Object-Oriented Programming",
    "object oriented programming": "Object-Oriented Programming",
    "dsa": "Data Structures & Algorithms",
    "data structures": "Data Structures & Algorithms",
    "algorithms": "Data Structures & Algorithms",
    "tdd": "Test-Driven Development",
    "test-driven development": "Test-Driven Development",
    "test driven development": "Test-Driven Development",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "continuous integration": "CI/CD",
    "github actions": "GitHub Actions",
    "gh actions": "GitHub Actions",
    "postman": "Postman",
    "scikit-learn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    "tf": "TensorFlow",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "sqlalchemy": "SQLAlchemy",
    "linux": "Linux",
    "bash": "Bash",
    "shell scripting": "Shell",
    "problem-solving": "Problem Solving",
    "problem solving": "Problem Solving",
    "teamwork": "Team Collaboration",
    "team collaboration": "Team Collaboration",
    "collaboration": "Team Collaboration",
    "communication": "Communication",
    "leadership": "Leadership",
    "time management": "Time Management",
    "critical thinking": "Critical Thinking",
    "agile": "Agile",
    "scrum": "Scrum",
    "microservices": "Microservices",
    "unit test": "Unit Testing",
    "unit tests": "Unit Testing",
    "unit testing": "Unit Testing"
}


def get_all_canonical_skills() -> set[str]:
    """Return set of all canonical skill names across categories."""
    canonical = set()
    for cat_skills in SKILLS_TAXONOMY.values():
        canonical.update(cat_skills)
    return canonical


def get_all_skill_patterns() -> dict[str, str]:
    """
    Return dictionary mapping all lowercased aliases and canonical skill names
    to their canonical representation for reliable matching.
    """
    mapping = {}
    # 1. Base canonical names
    for cat_skills in SKILLS_TAXONOMY.values():
        for s in cat_skills:
            mapping[s.lower()] = s
    # 2. Aliases (take precedence if explicit)
    for alias, canonical in SKILL_ALIASES.items():
        mapping[alias.lower()] = canonical
    return mapping


def get_skill_category(skill_name: str) -> str:
    """Return the category key for a canonical skill name."""
    for category, skills in SKILLS_TAXONOMY.items():
        if skill_name in skills:
            return category
    return "other"
