import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


def generate_pdf_report(
    candidate_name: str,
    email: str,
    target_role: str,
    experience_level: str,
    total_score: int,
    score_breakdown: dict,
    detected_skills: dict,
    strengths: list[str],
    weaknesses: list[str],
    actionable_tips: list[str],
    roadmap_items: list[dict] = None
) -> io.BytesIO:
    """
    Generate an executive PDF analysis report using ReportLab.
    Returns: BytesIO stream ready for Flask send_file.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Custom palette: Navy, Slate, Violet accents
    navy = colors.HexColor("#0F172A")
    blue = colors.HexColor("#2563EB")
    violet = colors.HexColor("#7C3AED")
    dark_gray = colors.HexColor("#334155")
    light_bg = colors.HexColor("#F8FAFC")
    border_color = colors.HexColor("#E2E8F0")

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=navy,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748B"),
    )

    h2_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=navy,
        spaceBefore=10,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=dark_gray,
    )

    bold_body = ParagraphStyle(
        "BodyDarkBold",
        parent=body_style,
        fontName="Helvetica-Bold",
    )

    elements = []

    # 1. Header Banner
    header_data = [
        [
            Paragraph("<b>CareerPilot AI</b> — Resume Analysis Audit", title_style),
            Paragraph(f"Score: <b>{total_score}/100</b>", ParagraphStyle(
                "ScoreHeader",
                fontName="Helvetica-Bold",
                fontSize=18,
                textColor=blue,
                alignment=TA_RIGHT
            ))
        ],
        [
            Paragraph(f"Candidate: <b>{candidate_name}</b> ({email}) | Target: <b>{target_role}</b> ({experience_level.title()})", subtitle_style),
            Paragraph(f"Generated: {datetime.utcnow().strftime('%b %d, %Y')}", ParagraphStyle(
                "DateHeader",
                fontName="Helvetica",
                fontSize=9,
                textColor=colors.HexColor("#64748B"),
                alignment=TA_RIGHT
            ))
        ]
    ]

    header_table = Table(header_data, colWidths=[380, 150])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=border_color, spaceBefore=4, spaceAfter=12))

    # 2. Executive Summary Score Breakdown Table
    elements.append(Paragraph("Score Component Breakdown", h2_style))

    breakdown_rows = [
        [
            Paragraph("<b>Assessment Component</b>", bold_body),
            Paragraph("<b>Points</b>", bold_body),
            Paragraph("<b>Evaluation & Rationale</b>", bold_body)
        ]
    ]

    components = [
        ("Section Completeness", score_breakdown.get("section_completeness", {})),
        ("Skills Alignment", score_breakdown.get("skills_relevance", {})),
        ("Project Evidence", score_breakdown.get("project_experience", {})),
        ("Bullet Point Quality", score_breakdown.get("bullet_quality", {})),
        ("Readability & Formatting", score_breakdown.get("readability", {})),
    ]

    for label, item in components:
        sc = item.get("score", 0)
        mx = item.get("max_score", 0)
        expl = item.get("explanation", "Standard review completed.")
        breakdown_rows.append([
            Paragraph(f"<b>{label}</b>", body_style),
            Paragraph(f"{sc}/{mx}", bold_body),
            Paragraph(expl, body_style)
        ])

    table = Table(breakdown_rows, colWidths=[150, 60, 320])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), light_bg),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    # 3. Detected Skills Summary
    elements.append(Paragraph("Detected Technical & Professional Skills", h2_style))
    cats = detected_skills.get("categorized", {})
    skill_rows = []
    for cat_name, skill_list in cats.items():
        if skill_list:
            formatted_cat = cat_name.replace("_", " ").title()
            skill_rows.append([
                Paragraph(f"<b>{formatted_cat}</b>", bold_body),
                Paragraph(", ".join(skill_list), body_style)
            ])

    if skill_rows:
        skills_table = Table(skill_rows, colWidths=[150, 380])
        skills_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, border_color),
            ('BACKGROUND', (0, 0), (0, -1), light_bg),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(skills_table)
    else:
        elements.append(Paragraph("No technical skills cataloged yet.", body_style))

    elements.append(Spacer(1, 12))

    # 4. Actionable Improvements & Strengths
    elements.append(Paragraph("Actionable Recommendations for Maximum Impact", h2_style))
    for i, tip in enumerate(actionable_tips[:5], 1):
        elements.append(Paragraph(f"<b>{i}.</b> {tip}", body_style))
        elements.append(Spacer(1, 3))

    elements.append(Spacer(1, 8))

    # 5. Roadmap Milestones if provided
    if roadmap_items:
        elements.append(Paragraph("Personalized Next-Step Learning Roadmap", h2_style))
        roadmap_rows = [
            [
                Paragraph("<b>Skill</b>", bold_body),
                Paragraph("<b>Priority</b>", bold_body),
                Paragraph("<b>Hands-on Practice Task</b>", bold_body)
            ]
        ]
        for item in roadmap_items[:4]:
            roadmap_rows.append([
                Paragraph(f"<b>{item.get('skill_name', '')}</b>", body_style),
                Paragraph(item.get("priority", "Medium"), body_style),
                Paragraph(item.get("practice_task", ""), body_style)
            ])
        rm_table = Table(roadmap_rows, colWidths=[120, 70, 340])
        rm_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), light_bg),
            ('GRID', (0, 0), (-1, -1), 0.5, border_color),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(rm_table)
        elements.append(Spacer(1, 12))

    # 6. Disclaimer Footer
    disclaimer_text = (
        "<b>Disclaimer:</b> This report was generated automatically by CareerPilot AI. "
        "The score is a heuristic benchmark based on student and entry-level criteria, not an official ATS vendor proprietary decision. "
        "User data is private and confidential."
    )
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(disclaimer_text, ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#94A3B8")
    )))

    doc.build(elements)
    buffer.seek(0)
    return buffer
