import re
from typing import Any
from app.services.skills_dictionary import (
    SKILLS_TAXONOMY,
    get_all_skill_patterns,
    get_all_canonical_skills,
)


def extract_skills_from_job_text(job_text: str) -> dict[str, list[str]]:
    """
    Separate job text into required vs preferred sections where possible,
    and extract all relevant technical and soft skills using the unified taxonomy.
    """
    required_skills = set()
    preferred_skills = set()
    all_job_skills = set()

    lower_text = job_text.lower()
    lines = lower_text.split("\n")

    in_preferred_section = False
    in_required_section = False

    preferred_keywords = ["preferred", "nice to have", "plus", "bonus", "desirable", "good to have"]
    required_keywords = ["required", "must have", "qualifications", "requirements", "minimum qualifications", "what you need"]

    skill_patterns = get_all_skill_patterns()

    # Categorize lines
    for line in lines:
        stripped = line.strip()
        if any(kw in stripped for kw in preferred_keywords):
            in_preferred_section = True
            in_required_section = False
        elif any(kw in stripped for kw in required_keywords):
            in_required_section = True
            in_preferred_section = False

        # Extract skills in this line
        for pattern_str, canonical in skill_patterns.items():
            pattern = rf"(?<!\w){re.escape(pattern_str)}(?!\w)"
            if re.search(pattern, stripped):
                all_job_skills.add(canonical)
                if in_preferred_section:
                    preferred_skills.add(canonical)
                else:
                    required_skills.add(canonical)

    # In case no explicit section headers were found, treat all detected as required
    if not required_skills and not preferred_skills:
        for pattern_str, canonical in skill_patterns.items():
            pattern = rf"(?<!\w){re.escape(pattern_str)}(?!\w)"
            if re.search(pattern, lower_text):
                required_skills.add(canonical)
                all_job_skills.add(canonical)

    # Ensure required and preferred don't overlap
    preferred_skills = preferred_skills - required_skills

    return {
        "required": sorted(list(required_skills)),
        "preferred": sorted(list(preferred_skills)),
        "all_skills": sorted(list(all_job_skills)),
    }


def compare_resume_to_job(
    resume_skills: list[str],
    job_description_raw: str,
    job_title: str = "Internship Position"
) -> dict[str, Any]:
    """
    Calculate match percentage and categorize skill overlaps.
    """
    extracted_job = extract_skills_from_job_text(job_description_raw)
    job_required = set(extracted_job["required"])
    job_preferred = set(extracted_job["preferred"])
    cand_skills = set(resume_skills)

    matched_required = list(job_required.intersection(cand_skills))
    missing_required = list(job_required - cand_skills)

    matched_preferred = list(job_preferred.intersection(cand_skills))
    missing_preferred = list(job_preferred - cand_skills)

    all_matched = sorted(list(set(matched_required + matched_preferred)))
    additional_skills = sorted(list(cand_skills - set(extracted_job["all_skills"])))

    # Compute transparent weighted score:
    # 75% weight on required skills, 25% on preferred skills (or 100% on required if no preferred)
    if job_required and job_preferred:
        req_ratio = len(matched_required) / len(job_required)
        pref_ratio = len(matched_preferred) / len(job_preferred)
        match_pct = round((req_ratio * 75) + (pref_ratio * 25))
    elif job_required:
        req_ratio = len(matched_required) / len(job_required)
        match_pct = round(req_ratio * 100)
    elif job_preferred:
        pref_ratio = len(matched_preferred) / len(job_preferred)
        match_pct = round(pref_ratio * 100)
    else:
        # Fallback if no specific skills found in description
        match_pct = 50

    match_pct = max(0, min(100, match_pct))

    # Recommendations
    recommendations = []
    if missing_required:
        recommendations.append(
            f"High Priority: Add evidence or projects covering missing required skills: {', '.join(missing_required[:5])}."
        )
    if missing_preferred:
        recommendations.append(
            f"Bonus Impact: Demonstrating knowledge in {', '.join(missing_preferred[:4])} will elevate your candidacy."
        )
    if all_matched:
        recommendations.append(
            f"Tailor Your Resume: Ensure your matched skills ({', '.join(all_matched[:4])}) are prominently mentioned in project bullet points."
        )
    if not recommendations:
        recommendations.append("Your resume skills align closely with this job description! Ensure your accomplishments are quantified.")

    return {
        "job_title": job_title,
        "match_percentage": match_pct,
        "matched_skills": all_matched,
        "matched_required": sorted(matched_required),
        "matched_preferred": sorted(matched_preferred),
        "missing_required_skills": sorted(missing_required),
        "missing_preferred_skills": sorted(missing_preferred),
        "additional_skills": additional_skills[:12],
        "recommendations": recommendations,
        "disclaimer": "This comparison is an automated keyword and taxonomy match. It does not reflect an official employer hiring decision."
    }
