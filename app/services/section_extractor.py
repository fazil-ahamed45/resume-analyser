import re
from typing import Any
from app.services.skills_dictionary import (
    SKILLS_TAXONOMY,
    SKILL_ALIASES,
    get_all_canonical_skills,
    get_skill_category,
)

# Standard section header regex patterns
SECTION_PATTERNS = {
    "contact": r"(?i)^(?:contact(?:\s+information)?|personal\s+details)$",
    "education": r"(?i)^(?:education|academic\s+background|academics|qualifications)$",
    "experience": r"(?i)^(?:experience|work\s+experience|professional\s+experience|employment\s+history|internships?)$",
    "projects": r"(?i)^(?:projects?|academic\s+projects?|personal\s+projects?|technical\s+projects?)$",
    "skills": r"(?i)^(?:skills?|technical\s+skills?|core\s+competencies|technologies|tools\s+&\s+technologies)$",
    "certifications": r"(?i)^(?:certifications?|certificates?|licenses?|courses\s+&\s+certifications)$",
    "achievements": r"(?i)^(?:achievements?|awards?|honors?|extracurricular(?:\s+activities)?)$",
    "summary": r"(?i)^(?:summary|professional\s+summary|profile|about\s+me|career\s+objective)$",
}

STRONG_ACTION_VERBS = {
    "built", "developed", "created", "engineered", "implemented", "designed",
    "architected", "optimized", "accelerated", "reduced", "increased", "deployed",
    "integrated", "automated", "spearheaded", "orchestrated", "refactored", "migrated",
    "analyzed", "resolved", "collaborated", "managed", "led", "enhanced", "delivered"
}


def extract_contact_info(text: str) -> dict[str, Any]:
    """
    Extract contact details: email, phone, links (GitHub, LinkedIn, Portfolio).
    Never logs or exposes personal information outside user view.
    """
    contact = {
        "email": None,
        "phone": None,
        "github": None,
        "linkedin": None,
        "portfolio": None,
    }

    # Email
    email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b", text)
    if email_match:
        contact["email"] = email_match.group(0)

    # Phone: international or US/Indian formats
    phone_match = re.search(
        r"(?:(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\+?\d{10,13})",
        text,
    )
    if phone_match:
        contact["phone"] = phone_match.group(0).strip()

    # GitHub URL or handle
    github_match = re.search(r"(?:https?://)?(?:www\.)?github\.com/([A-Za-z0-9_-]+)", text, re.IGNORECASE)
    if github_match:
        contact["github"] = f"https://github.com/{github_match.group(1)}"

    # LinkedIn URL
    linkedin_match = re.search(r"(?:https?://)?(?:www\.)?linkedin\.com/in/([A-Za-z0-9_-]+)", text, re.IGNORECASE)
    if linkedin_match:
        contact["linkedin"] = f"https://linkedin.com/in/{linkedin_match.group(1)}"

    # Portfolio / Personal Website
    portfolio_match = re.search(
        r"(?:https?://)(?:[a-zA-Z0-9-]+\.)+(?:com|io|me|dev|app|org)(?:/[^\s]*)?",
        text,
        re.IGNORECASE,
    )
    if portfolio_match:
        url = portfolio_match.group(0)
        if "github.com" not in url and "linkedin.com" not in url:
            contact["portfolio"] = url

    return contact


def split_into_sections(raw_text: str) -> dict[str, str]:
    """
    Segment the raw text into distinct resume sections using header matching heuristics.
    """
    lines = [line.strip() for line in raw_text.split("\n")]
    sections: dict[str, list[str]] = {
        "summary": [],
        "education": [],
        "experience": [],
        "projects": [],
        "skills": [],
        "certifications": [],
        "achievements": [],
        "other": [],
    }

    current_section = "other"

    for line in lines:
        if not line:
            continue

        # Check if line matches a known section title
        matched_section = None
        # Clean line of punctuation like trailing colons or dashes
        clean_header = re.sub(r"[:\-_#=*]+$", "", line).strip()

        # Section headers are usually short (under 40 chars)
        if len(clean_header) < 40:
            for sec_name, pattern in SECTION_PATTERNS.items():
                if re.match(pattern, clean_header):
                    matched_section = sec_name
                    break

        if matched_section:
            current_section = matched_section
        else:
            sections[current_section].append(line)

    # Convert list of lines to strings
    result = {}
    for sec, sec_lines in sections.items():
        content = "\n".join(sec_lines).strip()
        if content:
            result[sec] = content

    return result


def extract_skills_with_evidence(raw_text: str) -> dict[str, Any]:
    """
    Identify skills across categories, with exact snippet evidence from the text.
    Returns:
    {
        "categorized": { "programming_languages": ["Python", ...], ... },
        "all_skills": ["Python", "Flask", ...],
        "evidence": { "Python": "Built a scalable REST API using Python and Flask..." },
        "total_count": 12
    }
    """
    categorized: dict[str, list[str]] = {cat: [] for cat in SKILLS_TAXONOMY}
    all_found = set()
    evidence: dict[str, str] = {}

    lines = raw_text.split("\n")
    lower_text = raw_text.lower()

    # Search for canonical skills and aliases
    for alias_or_name, canonical in SKILL_ALIASES.items():
        # Word boundary pattern
        # Special regex handling for characters like +, #, .
        escaped = re.escape(alias_or_name)
        pattern = rf"(?<!\w){escaped}(?!\w)"
        
        match = re.search(pattern, lower_text)
        if match and canonical not in all_found:
            all_found.add(canonical)
            cat = get_skill_category(canonical)
            if cat in categorized:
                categorized[cat].append(canonical)
            else:
                categorized.setdefault("other", []).append(canonical)

            # Find evidence sentence/line containing the skill
            for line in lines:
                if re.search(pattern, line.lower()):
                    trimmed = line.strip()
                    if len(trimmed) > 15:
                        evidence[canonical] = trimmed[:160] + ("..." if len(trimmed) > 160 else "")
                        break
            if canonical not in evidence:
                evidence[canonical] = f"Mentioned in resume context."

    # Also directly check canonical skills that might not have an explicit alias
    for cat, skill_list in SKILLS_TAXONOMY.items():
        for skill in skill_list:
            if skill not in all_found:
                escaped = re.escape(skill)
                pattern = rf"(?<!\w){escaped}(?!\w)"
                if re.search(pattern, raw_text, re.IGNORECASE):
                    all_found.add(skill)
                    categorized[cat].append(skill)
                    for line in lines:
                        if re.search(pattern, line, re.IGNORECASE):
                            trimmed = line.strip()
                            if len(trimmed) > 15:
                                evidence[skill] = trimmed[:160] + ("..." if len(trimmed) > 160 else "")
                                break
                    if skill not in evidence:
                        evidence[skill] = f"Identified in resume content."

    # Sort skills alphabetically
    for cat in categorized:
        categorized[cat] = sorted(list(set(categorized[cat])))

    return {
        "categorized": categorized,
        "all_skills": sorted(list(all_found)),
        "evidence": evidence,
        "total_count": len(all_found),
    }


def analyze_bullet_points(sections: dict[str, str]) -> dict[str, Any]:
    """
    Examine bullet points in Projects and Experience sections:
    - Verifies presence of strong action verbs
    - Checks for quantitative metrics/numbers (e.g., %, 50+, 2x, 500ms)
    - Detects vague or overly short bullet points (< 30 characters)
    """
    combined_text = "\n".join([
        sections.get("projects", ""),
        sections.get("experience", "")
    ])

    lines = [l.strip() for l in combined_text.split("\n") if l.strip()]
    bullet_lines = []
    for line in lines:
        # Match lines starting with bullet symbols or dashes or numbered lists
        clean = re.sub(r"^[\s\u2022\u25cf\u25cb\u25aa\u25ab\-*•\d+.)]+", "", line).strip()
        if len(clean) > 10:
            bullet_lines.append(clean)

    action_verb_count = 0
    metric_count = 0
    weak_bullets = []
    strong_bullets = []

    # Regex for metrics (percentages, numbers, multipliers, times)
    metric_pattern = re.compile(r"\b(?:\d+[%kKmM]?|\$\d+|\d+\+|\d+x|\d+\s*(?:percent|users|ms|seconds|minutes|hours|days|requests))\b")

    for bullet in bullet_lines:
        first_word = bullet.split()[0].lower().rstrip(":,.-") if bullet.split() else ""
        has_action_verb = first_word in STRONG_ACTION_VERBS
        has_metric = bool(metric_pattern.search(bullet))

        if has_action_verb:
            action_verb_count += 1
        if has_metric:
            metric_count += 1

        if not has_action_verb or not has_metric:
            if len(weak_bullets) < 5:
                issue = []
                if not has_action_verb:
                    issue.append("Begins with weak phrasing instead of a strong action verb")
                if not has_metric:
                    issue.append("Lacks quantifiable impact or metrics")
                weak_bullets.append({
                    "original": bullet,
                    "issues": issue
                })
        else:
            if len(strong_bullets) < 5:
                strong_bullets.append(bullet)

    total_bullets = max(len(bullet_lines), 1)

    return {
        "total_bullets": len(bullet_lines),
        "action_verb_percentage": round((action_verb_count / total_bullets) * 100),
        "metric_percentage": round((metric_count / total_bullets) * 100),
        "weak_bullets": weak_bullets,
        "strong_bullets": strong_bullets,
    }
