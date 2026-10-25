"""
Resume-based interview preparation service generating role and skill-specific
technical questions, project deep-dives, and behavioral interview checklists.
Works 100% deterministically without requiring an external AI API key.
"""

import re
from typing import Any

TECHNICAL_QUESTION_BANK = {
    "Python": [
        {
            "question": "How do Python's memory management and garbage collection mechanisms work?",
            "category": "Technical Core",
            "outline": "Explain reference counting as the primary mechanism, followed by the generational garbage collector for cyclic references.",
            "key_concepts": ["reference counting", "garbage collection", "cycles", "memory management", "gil"]
        },
        {
            "question": "What is the difference between deepcopy and shallow copy in Python, and when would you use each?",
            "category": "Technical Core",
            "outline": "Contrast references to compound objects vs recursively copying child objects. Give an example with nested lists or dictionaries.",
            "key_concepts": ["shallow copy", "deep copy", "compound objects", "nested", "references", "mutability"]
        },
        {
            "question": "Explain Python generators, yield, and how they provide memory efficiency over standard lists.",
            "category": "Technical Core",
            "outline": "Define iterators and lazy evaluation. Contrast generator functions using 'yield' with list comprehensions for large datasets.",
            "key_concepts": ["generator", "yield", "lazy evaluation", "memory", "iterators", "next"]
        }
    ],
    "SQL": [
        {
            "question": "Explain the difference between INNER JOIN, LEFT JOIN, and FULL OUTER JOIN with real examples.",
            "category": "Technical Core",
            "outline": "Describe how rows with and without matches in right/left tables are handled, including NULL filling.",
            "key_concepts": ["inner join", "left join", "null", "foreign key", "unmatched rows"]
        },
        {
            "question": "How do database indexes improve query performance, and what are their trade-offs during write operations?",
            "category": "Technical Core",
            "outline": "Discuss B-Tree data structures, rapid search vs overhead on INSERT, UPDATE, and DELETE queries.",
            "key_concepts": ["index", "b-tree", "query performance", "insert", "write overhead", "lookup"]
        }
    ],
    "Flask": [
        {
            "question": "How does Flask handle request contexts, application contexts, and blueprint routing?",
            "category": "Technical Core",
            "outline": "Detail the distinction between current_app and request/session thread-local proxies, and how Blueprints modularize large apps.",
            "key_concepts": ["request context", "app context", "blueprints", "routing", "thread local"]
        }
    ],
    "Django": [
        {
            "question": "Walk through the Django request-response cycle from urls.py through middleware, views, and ORM to template/JSON.",
            "category": "Technical Core",
            "outline": "Trace WSGI handler -> Middleware stack -> URL resolution -> View execution -> ORM querying -> HTTP response.",
            "key_concepts": ["middleware", "urls", "view", "orm", "response", "wsgi"]
        }
    ],
    "Git": [
        {
            "question": "What is the difference between 'git merge' and 'git rebase', and in which team workflows would you choose each?",
            "category": "Technical Core",
            "outline": "Explain linear commit history vs true chronological branching. Discuss risks of rebasing public shared branches.",
            "key_concepts": ["rebase", "merge", "commit history", "fast-forward", "merge conflict"]
        }
    ],
    "Docker": [
        {
            "question": "Explain the difference between a Docker image and a Docker container, and how layer caching speeds up builds.",
            "category": "Technical Core",
            "outline": "Image is read-only template; container is running instance with writable layer. Layers are cached based on file hash changes.",
            "key_concepts": ["image", "container", "layer caching", "dockerfile", "writable layer"]
        }
    ],
    "REST API": [
        {
            "question": "What makes an API RESTful? Explain idempotency in HTTP methods (GET, POST, PUT, DELETE).",
            "category": "Technical Core",
            "outline": "Discuss statelessness, resource identification by URI, and how PUT/DELETE are idempotent while POST is not.",
            "key_concepts": ["idempotent", "stateless", "http methods", "post", "put", "status codes"]
        }
    ]
}

BEHAVIORAL_QUESTION_BANK = [
    {
        "question": "Tell me about a challenging technical bug or problem you encountered in a project. How did you diagnose and resolve it?",
        "category": "Behavioral / STAR Method",
        "outline": "Use the STAR method: Situation (the project), Task (what failed), Action (debugging tools, logs, hypothesis testing), Result (speedup or fix).",
        "key_concepts": ["situation", "task", "action", "result", "debug", "logs", "root cause", "solution"]
    },
    {
        "question": "Describe a situation where you had to quickly learn a new framework, library, or tool to finish a project.",
        "category": "Behavioral / STAR Method",
        "outline": "Explain your structured learning approach: official documentation, building a minimal prototype, asking questions, and meeting deadlines.",
        "key_concepts": ["documentation", "learning", "prototype", "adaptation", "deadline", "delivered"]
    },
    {
        "question": "How do you handle disagreement or constructive criticism during code reviews or team projects?",
        "category": "Behavioral / STAR Method",
        "outline": "Emphasize listening with an open mind, focusing on code quality and user impact rather than ego, and working toward consensus.",
        "key_concepts": ["feedback", "code review", "communication", "improvement", "collaboration", "standards"]
    }
]


def generate_interview_questions(
    detected_skills: list[str],
    target_role: str,
    sections: dict[str, str]
) -> list[dict[str, Any]]:
    """
    Select 4-6 targeted interview questions combining candidate's top technical skills,
    a project deep-dive question, and behavioral questions.
    """
    selected_questions = []

    # 1. Technical questions based on candidate's detected skills
    for skill in detected_skills:
        if skill in TECHNICAL_QUESTION_BANK:
            for q in TECHNICAL_QUESTION_BANK[skill]:
                if q not in selected_questions:
                    selected_questions.append(q)
                    break
        if len(selected_questions) >= 3:
            break

    # If few skills matched in technical bank, ensure Python and SQL defaults
    if len(selected_questions) < 2:
        for q in TECHNICAL_QUESTION_BANK["Python"][:1] + TECHNICAL_QUESTION_BANK["SQL"][:1]:
            if q not in selected_questions:
                selected_questions.append(q)

    # 2. Project Deep-Dive question
    proj_text = sections.get("projects", "")
    proj_title = "one of your featured projects"
    # Try to grab first project name from section
    if proj_text:
        first_line = proj_text.split("\n")[0].strip()
        if len(first_line) > 3 and len(first_line) < 50:
            proj_title = f"your project '{first_line}'"

    selected_questions.append({
        "question": f"Walk me through the architecture and design decisions behind {proj_title}. What trade-offs did you make?",
        "category": "Project Deep-Dive",
        "outline": "Explain: 1) Problem statement, 2) Tech stack justification, 3) Architecture diagram in words, 4) Biggest bottleneck encountered.",
        "key_concepts": ["architecture", "database schema", "trade-offs", "scalability", "bottleneck", "tech stack"]
    })

    # 3. Behavioral question
    selected_questions.append(BEHAVIORAL_QUESTION_BANK[0])
    selected_questions.append(BEHAVIORAL_QUESTION_BANK[1])

    return selected_questions[:5]


def evaluate_user_answer(
    question_text: str,
    key_concepts: list[str],
    user_answer: str,
    category: str
) -> dict[str, Any]:
    """
    Transparent rule-based answer evaluator assessing structure, completeness,
    keyword density, and STAR method markers.
    """
    ans = user_answer.strip()
    words = ans.split()
    word_count = len(words)

    if word_count < 20:
        return {
            "score": 30,
            "grade": "Needs Expansion",
            "word_count": word_count,
            "matched_concepts": [],
            "missing_concepts": key_concepts,
            "feedback": "Your answer is too brief. In a real technical interview, provide context, rationale, and concrete examples."
        }

    # Concept matching with intelligent stem support
    lower_ans = ans.lower()
    matched = []
    missing = []
    for concept in key_concepts:
        c_lower = concept.lower()
        is_matched = False
        if c_lower in lower_ans:
            is_matched = True
        else:
            # Check word root stems (e.g. 'cycle' for 'cycles', 'collect' for 'collection')
            tokens = [t for t in re.split(r"\W+", c_lower) if len(t) >= 4]
            if tokens and all(t[:4] in lower_ans for t in tokens):
                is_matched = True

        if is_matched:
            matched.append(concept)
        else:
            missing.append(concept)

    # Score calculation
    concept_ratio = len(matched) / max(len(key_concepts), 1)
    base_score = 45 + round(concept_ratio * 40)

    # Structure bonuses
    bonus = 0
    feedback_notes = []

    # Depth bonus for detailed responses (> 35 words)
    if word_count >= 35:
        bonus += 10
        feedback_notes.append("Strong explanatory depth.")

    # Check for metrics or quantifiable impact
    if re.search(r"\b(?:\d+%|\d+\s*(?:ms|seconds|users|times|requests))\b", ans):
        bonus += 5
        feedback_notes.append("Good inclusion of specific metrics/outcomes.")

    # Check for behavioral structure
    if "behavioral" in category.lower() or "star" in category.lower():
        has_star = any(w in lower_ans for w in ["situation", "task", "action", "result", "problem", "solution", "outcome"])
        if has_star:
            bonus += 10
            feedback_notes.append("Follows a structured narrative framework.")
        else:
            feedback_notes.append("Tip: Explicitly structure behavioral answers using the STAR method (Situation, Task, Action, Result).")

    final_score = min(base_score + bonus, 100)

    if matched:
        feedback_notes.append(f"Successfully discussed key concepts: {', '.join(matched)}.")
    if missing:
        feedback_notes.append(f"Could be strengthened by mentioning: {', '.join(missing[:3])}.")

    grade = "Excellent" if final_score >= 85 else ("Good" if final_score >= 70 else "Fair")

    return {
        "score": final_score,
        "grade": grade,
        "word_count": word_count,
        "matched_concepts": matched,
        "missing_concepts": missing,
        "feedback": " ".join(feedback_notes)
    }
