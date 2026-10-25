"""
Explainable 0-100 scoring engine with transparent, documented criteria.
Adapts to student / fresher level so candidates without 5+ years of full-time
experience are evaluated fairly on projects, skills, and execution quality.
"""

from typing import Any

# Role expectations for key target roles
ROLE_CORE_SKILLS = {
    "Python Developer Intern": {
        "required": ["Python", "SQL", "Git"],
        "recommended": ["Flask", "Django", "FastAPI", "PostgreSQL", "REST API", "Docker", "Pytest", "Data Structures & Algorithms"],
    },
    "Backend Developer Intern": {
        "required": ["Python", "SQL", "REST API", "Git"],
        "recommended": ["FastAPI", "Django", "PostgreSQL", "Redis", "Docker", "Linux", "Microservices", "Unit Testing"],
    },
    "Full Stack Developer Intern": {
        "required": ["JavaScript", "HTML5", "CSS3", "Git"],
        "recommended": ["Python", "React", "Node.js", "Flask", "PostgreSQL", "MongoDB", "REST API", "Tailwind CSS"],
    },
    "Data Analyst Intern": {
        "required": ["Python", "SQL", "Pandas"],
        "recommended": ["NumPy", "Scikit-Learn", "PostgreSQL", "MySQL", "Analytical Thinking", "Problem Solving", "Git"],
    },
    "QA Automation Intern": {
        "required": ["Python", "Unit Testing", "Git"],
        "recommended": ["Pytest", "Postman", "CI/CD", "Linux", "REST API", "Debugging", "Problem Solving"],
    },
    "Software Engineer Intern": {
        "required": ["Git", "Data Structures & Algorithms", "Object-Oriented Programming"],
        "recommended": ["Python", "SQL", "REST API", "Linux", "Problem Solving", "Docker", "Unit Testing"],
    }
}


def evaluate_section_completeness(sections: dict[str, str], contact: dict[str, Any]) -> dict[str, Any]:
    """
    Max: 25 points.
    Evaluates presence and substance of standard resume sections.
    """
    score = 0
    missing = []
    present = []
    tips = []

    # Education (6 points)
    if sections.get("education"):
        score += 6
        present.append("Education")
    else:
        missing.append("Education")
        tips.append("Add an Education section with your degree, college name, CGPA/percentage, and expected graduation.")

    # Skills (6 points)
    if sections.get("skills"):
        score += 6
        present.append("Skills")
    else:
        missing.append("Skills")
        tips.append("Include a dedicated Technical Skills section organized by Languages, Frameworks, and Tools.")

    # Projects (7 points) - Crucial for college students
    if sections.get("projects"):
        score += 7
        present.append("Projects")
    else:
        missing.append("Projects")
        tips.append("Add 2-3 technical projects showcasing real problem solving, tech stack, and GitHub links.")

    # Contact Details (4 points)
    has_email = bool(contact.get("email"))
    has_phone = bool(contact.get("phone"))
    if has_email and has_phone:
        score += 4
        present.append("Contact Information")
    elif has_email or has_phone:
        score += 2
        tips.append("Ensure both email and phone number are clearly visible in the header.")
    else:
        missing.append("Contact Details")
        tips.append("Add your email, phone number, and LinkedIn/GitHub links.")

    # Summary or Certifications or Experience (2 points)
    if sections.get("experience") or sections.get("certifications") or sections.get("summary"):
        score += 2
        present.append("Professional Profile / Experience / Certifications")
    else:
        tips.append("Add a concise summary or certifications section to round out your profile.")

    return {
        "score": min(score, 25),
        "max_score": 25,
        "present_sections": present,
        "missing_sections": missing,
        "tips": tips,
        "explanation": f"Found {len(present)} standard sections out of 5 expected areas."
    }


def evaluate_skills_relevance(detected_skills: list[str], target_role: str) -> dict[str, Any]:
    """
    Max: 30 points.
    Matches candidate skills against target role curriculum and job market expectations.
    """
    profile = ROLE_CORE_SKILLS.get(target_role, ROLE_CORE_SKILLS["Software Engineer Intern"])
    req = set(profile["required"])
    rec = set(profile["recommended"])
    detected_set = set(detected_skills)

    matched_req = req.intersection(detected_set)
    matched_rec = rec.intersection(detected_set)

    # 15 points for required skills
    req_score = round((len(matched_req) / max(len(req), 1)) * 15)
    # 15 points for recommended skills
    rec_score = round((len(matched_rec) / max(len(rec), 1)) * 15)

    total_score = min(req_score + rec_score, 30)

    missing_req = list(req - detected_set)
    missing_rec = list(rec - detected_set)

    tips = []
    if missing_req:
        tips.append(f"Essential missing skills for {target_role}: {', '.join(missing_req)}.")
    if missing_rec:
        tips.append(f"High-impact skills to acquire: {', '.join(missing_rec[:4])}.")

    return {
        "score": total_score,
        "max_score": 30,
        "matched_required": list(matched_req),
        "missing_required": missing_req,
        "matched_recommended": list(matched_rec),
        "missing_recommended": missing_rec,
        "tips": tips,
        "explanation": f"Matched {len(matched_req)}/{len(req)} core skills and {len(matched_rec)}/{len(rec)} recommended skills for '{target_role}'."
    }


def evaluate_project_and_experience_evidence(
    sections: dict[str, str], experience_level: str
) -> dict[str, Any]:
    """
    Max: 20 points.
    Fresher-friendly: If experience_level is 'fresher' or 'student', weight heavily
    on Project depth, repo links, and technical implementation.
    """
    score = 0
    tips = []
    has_proj = bool(sections.get("projects"))
    has_exp = bool(sections.get("experience"))

    proj_text = sections.get("projects", "")
    exp_text = sections.get("experience", "")

    is_fresher = experience_level.lower() in ("fresher", "student", "intern", "entry-level")

    if is_fresher:
        # Fresher criteria: 16 points for Projects, 4 points for any internship or coursework
        if has_proj:
            score += 10
            # Check length/depth of projects
            words = len(proj_text.split())
            if words > 100:
                score += 4
            if "github.com" in proj_text.lower() or "demo" in proj_text.lower() or "http" in proj_text.lower():
                score += 2
            else:
                tips.append("Add live demo or GitHub repository URLs to your project descriptions.")
        else:
            tips.append("For student/fresher resumes, projects are the #1 hiring signal. Add 2+ substantial projects.")

        if has_exp:
            score += 4
        else:
            # If no formal experience, but projects are comprehensive (200+ words), award the 4 points
            if len(proj_text.split()) > 200:
                score += 4
            else:
                tips.append("Consider adding college technical team, open-source contribution, or hackathon participation.")
    else:
        # Experienced criteria
        if has_exp:
            score += 12
            if len(exp_text.split()) > 150:
                score += 4
        else:
            tips.append("Highlight your professional work history and internship experience with bullet points.")

        if has_proj:
            score += 4
        else:
            tips.append("Include relevant side projects demonstrating continuous learning.")

    score = min(score, 20)

    return {
        "score": score,
        "max_score": 20,
        "is_fresher_mode": is_fresher,
        "tips": tips,
        "explanation": "Evaluated using student-friendly scoring emphasizing project depth, links, and technical evidence."
        if is_fresher
        else "Evaluated based on professional experience and technical project records."
    }


def evaluate_bullet_point_quality(bullet_analysis: dict[str, Any]) -> dict[str, Any]:
    """
    Max: 15 points.
    Evaluates action verbs (8 pts) and metrics/quantifiable outcomes (7 pts).
    """
    action_pct = bullet_analysis.get("action_verb_percentage", 0)
    metric_pct = bullet_analysis.get("metric_percentage", 0)

    # Action verbs score (up to 8 points)
    action_score = round((action_pct / 100) * 8)

    # Metrics score (up to 7 points)
    metric_score = round((metric_pct / 100) * 7)

    total_score = min(action_score + metric_score, 15)

    tips = []
    if action_pct < 60:
        tips.append("Start each bullet point with a past-tense action verb (e.g., 'Architected', 'Implemented', 'Optimized').")
    if metric_pct < 40:
        tips.append("Quantify your accomplishments with numbers, speedups, percentages, or active users (e.g., 'reduced API response time by 35%').")

    return {
        "score": total_score,
        "max_score": 15,
        "action_verb_percentage": action_pct,
        "metric_percentage": metric_pct,
        "weak_bullets": bullet_analysis.get("weak_bullets", []),
        "strong_bullets": bullet_analysis.get("strong_bullets", []),
        "tips": tips,
        "explanation": f"{action_pct}% of bullets start with strong action verbs; {metric_pct}% contain measurable metrics."
    }


def evaluate_readability_formatting(raw_text: str, contact: dict[str, Any]) -> dict[str, Any]:
    """
    Max: 10 points.
    Checks resume word count, contact availability, and line consistency.
    """
    score = 10
    tips = []
    words = len(raw_text.split())

    if words < 180:
        score -= 4
        tips.append("Resume is too brief (< 180 words). Expand your project descriptions, tools, and technical details.")
    elif words > 1400:
        score -= 3
        tips.append("Resume is somewhat verbose (> 1400 words). Strive for a concise 1-page format for entry-level roles.")

    if not contact.get("email"):
        score -= 2
        tips.append("Ensure your primary email is clearly reachable.")

    if not contact.get("github") and not contact.get("linkedin"):
        score -= 2
        tips.append("Add links to your active GitHub and LinkedIn profiles.")

    score = max(score, 0)

    return {
        "score": score,
        "max_score": 10,
        "word_count": words,
        "tips": tips,
        "explanation": f"Word count is {words} words. Structure and contact indicators were reviewed."
    }


def calculate_overall_resume_score(
    raw_text: str,
    sections: dict[str, str],
    contact: dict[str, Any],
    detected_skills: list[str],
    target_role: str,
    experience_level: str,
    bullet_analysis: dict[str, Any]
) -> dict[str, Any]:
    """
    Compute total explainable 0-100 score and construct complete audit breakdown.
    """
    sec_eval = evaluate_section_completeness(sections, contact)
    skills_eval = evaluate_skills_relevance(detected_skills, target_role)
    exp_eval = evaluate_project_and_experience_evidence(sections, experience_level)
    bullet_eval = evaluate_bullet_point_quality(bullet_analysis)
    read_eval = evaluate_readability_formatting(raw_text, contact)

    total_score = (
        sec_eval["score"]
        + skills_eval["score"]
        + exp_eval["score"]
        + bullet_eval["score"]
        + read_eval["score"]
    )

    # Synthesize strengths & weaknesses
    strengths = []
    weaknesses = []

    if sec_eval["score"] >= 20:
        strengths.append("Strong section structure containing essential college resume components.")
    else:
        weaknesses.append("Resume is missing standard sections (see Section Breakdown).")

    if skills_eval["score"] >= 22:
        strengths.append(f"High technical alignment with entry-level {target_role} expectations.")
    else:
        weaknesses.append(f"Gaps identified in core skills for {target_role}.")

    if bullet_eval["score"] >= 11:
        strengths.append("Effective bullet points featuring action verbs and clear project contributions.")
    else:
        weaknesses.append("Bullet points could be sharpened with stronger verbs and quantifiable impact.")

    if exp_eval["score"] >= 16:
        strengths.append("Compelling project portfolio demonstrating practical implementation skills.")

    all_actionable_tips = (
        sec_eval["tips"]
        + skills_eval["tips"]
        + exp_eval["tips"]
        + bullet_eval["tips"]
        + read_eval["tips"]
    )

    return {
        "total_score": total_score,
        "target_role": target_role,
        "experience_level": experience_level,
        "breakdown": {
            "section_completeness": sec_eval,
            "skills_relevance": skills_eval,
            "project_experience": exp_eval,
            "bullet_quality": bullet_eval,
            "readability": read_eval,
        },
        "strengths": strengths,
        "weaknesses": weaknesses,
        "actionable_tips": all_actionable_tips[:6],
        "disclaimer": "This score is an explainable heuristic generated by CareerPilot AI algorithms based on entry-level hiring criteria. It is not an official proprietary score from any specific ATS software."
    }
