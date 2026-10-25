from flask import render_template, redirect, url_for, flash, request, send_file, abort
from flask_login import login_required, current_user
from app.analysis import bp
from app.analysis.forms import ReanalyzeForm
from app.models import Resume, ResumeAnalysis, RoadmapItem
from app.extensions import db
from app.services.section_extractor import (
    extract_skills_with_evidence,
    analyze_bullet_points,
)
from app.services.scoring_service import calculate_overall_resume_score
from app.services.ai_service import get_ai_resume_coach_feedback
from app.services.report_service import generate_pdf_report


@bp.route("/analysis/<int:analysis_id>")
@login_required
def view(analysis_id):
    # Enforce strict user isolation
    analysis = ResumeAnalysis.query.filter_by(id=analysis_id, user_id=current_user.id).first_or_404()
    resume = Resume.query.filter_by(id=analysis.resume_id, user_id=current_user.id).first_or_404()

    form = ReanalyzeForm()
    form.target_role.data = analysis.target_role
    form.experience_level.data = analysis.experience_level

    return render_template(
        "analysis/results.html",
        title=f"Analysis: {analysis.target_role} ({analysis.total_score}/100)",
        analysis=analysis,
        resume=resume,
        form=form,
    )


@bp.route("/analysis/history")
@login_required
def history():
    # User-isolated history
    analyses = (
        ResumeAnalysis.query.filter_by(user_id=current_user.id)
        .order_by(ResumeAnalysis.created_at.desc())
        .all()
    )
    return render_template("analysis/history.html", title="Analysis History", analyses=analyses)


@bp.route("/analysis/<int:analysis_id>/delete", methods=["POST"])
@login_required
def delete(analysis_id):
    # Enforce strict user isolation
    analysis = ResumeAnalysis.query.filter_by(id=analysis_id, user_id=current_user.id).first_or_404()
    db.session.delete(analysis)
    db.session.commit()
    flash("Analysis record deleted successfully.", "info")
    return redirect(url_for("analysis.history"))


@bp.route("/analysis/reanalyze/<int:resume_id>", methods=["POST"])
@login_required
def reanalyze(resume_id):
    # Enforce strict user isolation
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    form = ReanalyzeForm()

    if form.validate_on_submit():
        target_role = form.target_role.data
        experience_level = form.experience_level.data

        raw_text = resume.raw_text
        contact_info = resume.extracted_contact
        sections = resume.extracted_sections

        skills_data = extract_skills_with_evidence(raw_text)
        bullet_data = analyze_bullet_points(sections)

        score_data = calculate_overall_resume_score(
            raw_text=raw_text,
            sections=sections,
            contact=contact_info,
            detected_skills=skills_data["all_skills"],
            target_role=target_role,
            experience_level=experience_level,
            bullet_analysis=bullet_data,
        )

        ai_data = get_ai_resume_coach_feedback(
            user_has_consented=current_user.ai_consent,
            target_role=target_role,
            detected_skills=skills_data["all_skills"],
            missing_skills=score_data["breakdown"]["skills_relevance"]["missing_required"],
            weak_bullets=bullet_data["weak_bullets"],
            sections=sections,
            raw_resume_text=raw_text,
        )

        new_analysis = ResumeAnalysis(
            resume_id=resume.id,
            user_id=current_user.id,
            target_role=target_role,
            experience_level=experience_level,
            total_score=score_data["total_score"],
        )
        new_analysis.score_breakdown = score_data["breakdown"]
        new_analysis.detected_skills = skills_data
        new_analysis.missing_sections = score_data["breakdown"]["section_completeness"]["missing_sections"]
        new_analysis.strengths = score_data["strengths"]
        new_analysis.weaknesses = score_data["weaknesses"]
        new_analysis.bullet_suggestions = score_data["actionable_tips"]
        new_analysis.ai_suggestions = ai_data

        db.session.add(new_analysis)
        db.session.commit()

        flash(f"New score calculated for {target_role}: {score_data['total_score']}/100", "success")
        return redirect(url_for("analysis.view", analysis_id=new_analysis.id))

    flash("Invalid re-analysis submission.", "danger")
    return redirect(url_for("resumes.view_resume", resume_id=resume.id))


@bp.route("/analysis/<int:analysis_id>/report.pdf")
@login_required
def download_pdf(analysis_id):
    # Enforce strict user isolation
    analysis = ResumeAnalysis.query.filter_by(id=analysis_id, user_id=current_user.id).first_or_404()
    resume = Resume.query.filter_by(id=analysis.resume_id, user_id=current_user.id).first_or_404()
    user_roadmap = RoadmapItem.query.filter_by(user_id=current_user.id, target_role=analysis.target_role).all()

    roadmap_dicts = [
        {
            "skill_name": item.skill_name,
            "priority": item.priority,
            "practice_task": item.practice_task,
        }
        for item in user_roadmap
    ]

    pdf_stream = generate_pdf_report(
        candidate_name=current_user.full_name,
        email=current_user.email,
        target_role=analysis.target_role,
        experience_level=analysis.experience_level,
        total_score=analysis.total_score,
        score_breakdown=analysis.score_breakdown,
        detected_skills=analysis.detected_skills,
        strengths=analysis.strengths,
        weaknesses=analysis.weaknesses,
        actionable_tips=analysis.bullet_suggestions,
        roadmap_items=roadmap_dicts,
    )

    clean_role = analysis.target_role.replace(" ", "_").lower()
    filename = f"CareerPilot_{clean_role}_Analysis.pdf"

    return send_file(
        pdf_stream,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )
