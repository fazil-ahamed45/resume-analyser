import json
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from app.career import bp
from app.career.forms import JobMatchForm, InterviewAnswerForm
from app.models import Resume, ResumeAnalysis, JobComparison, RoadmapItem, InterviewSession
from app.extensions import db
from app.services.section_extractor import extract_skills_with_evidence
from app.services.job_matcher import compare_resume_to_job
from app.services.career_service import get_career_recommendations
from app.services.interview_service import (
    generate_interview_questions,
    evaluate_user_answer,
)


@bp.route("/career/match", methods=["GET", "POST"])
@login_required
def job_match():
    form = JobMatchForm()
    user_resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.created_at.desc()).all()
    form.resume_id.choices = [(r.id, f"{r.original_filename} ({r.target_role})") for r in user_resumes]

    if not user_resumes:
        flash("Please upload a resume first before matching against job descriptions.", "info")
        return redirect(url_for("resumes.upload"))

    latest_comparison = None

    if form.validate_on_submit():
        resume_id = form.resume_id.data
        # Ensure resume belongs to current user
        resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()

        skills_data = extract_skills_with_evidence(resume.raw_text)
        candidate_skills = skills_data["all_skills"]

        job_title = form.job_title.data.strip()
        company = form.company_name.data.strip() if form.company_name.data else "Target Employer"
        raw_jd = form.job_description.data.strip()

        comparison_results = compare_resume_to_job(
            resume_skills=candidate_skills,
            job_description_raw=raw_jd,
            job_title=job_title,
        )

        # Save record
        comp = JobComparison(
            user_id=current_user.id,
            resume_id=resume.id,
            job_title=job_title,
            company_name=company,
            job_description_raw=raw_jd,
            match_percentage=comparison_results["match_percentage"],
        )
        comp.matched_skills = comparison_results["matched_skills"]
        comp.missing_required_skills = comparison_results["missing_required_skills"]
        comp.missing_preferred_skills = comparison_results["missing_preferred_skills"]
        comp.additional_skills = comparison_results["additional_skills"]
        comp.recommendations = comparison_results["recommendations"]

        db.session.add(comp)
        db.session.commit()

        flash(f"Comparison complete! Calculated match: {comp.match_percentage}%", "success")
        latest_comparison = comp

    return render_template(
        "career/job_match.html",
        title="Job Description Matcher",
        form=form,
        comparison=latest_comparison,
        has_resumes=bool(user_resumes),
    )


@bp.route("/career/match/history")
@login_required
def job_match_history():
    # User-isolated history
    comparisons = (
        JobComparison.query.filter_by(user_id=current_user.id)
        .order_by(JobComparison.created_at.desc())
        .all()
    )
    return render_template("career/job_match_history.html", title="Job Match History", comparisons=comparisons)


@bp.route("/career/match/<int:comparison_id>")
@login_required
def view_comparison(comparison_id):
    # Enforce strict user isolation
    comparison = JobComparison.query.filter_by(id=comparison_id, user_id=current_user.id).first_or_404()
    resume = Resume.query.filter_by(id=comparison.resume_id, user_id=current_user.id).first_or_404()

    form = JobMatchForm()
    user_resumes = Resume.query.filter_by(user_id=current_user.id).all()
    form.resume_id.choices = [(r.id, r.original_filename) for r in user_resumes]
    form.resume_id.data = resume.id
    form.job_title.data = comparison.job_title
    form.company_name.data = comparison.company_name
    form.job_description.data = comparison.job_description_raw

    return render_template(
        "career/job_match.html",
        title=f"Match: {comparison.job_title} ({comparison.match_percentage}%)",
        form=form,
        comparison=comparison,
        has_resumes=True,
    )


@bp.route("/career/match/<int:comparison_id>/delete", methods=["POST"])
@login_required
def delete_comparison(comparison_id):
    # Enforce strict user isolation
    comp = JobComparison.query.filter_by(id=comparison_id, user_id=current_user.id).first_or_404()
    db.session.delete(comp)
    db.session.commit()
    flash("Job comparison record deleted.", "info")
    return redirect(url_for("career.job_match_history"))


@bp.route("/career/recommendations")
@login_required
def recommendations():
    # Fetch user's latest resume or analysis
    latest_resume = (
        Resume.query.filter_by(user_id=current_user.id)
        .order_by(Resume.created_at.desc())
        .first()
    )

    detected_skills = []
    if latest_resume:
        skills_data = extract_skills_with_evidence(latest_resume.raw_text)
        detected_skills = skills_data["all_skills"]

    roles_data = get_career_recommendations(detected_skills)

    return render_template(
        "career/recommendations.html",
        title="Role Recommendations",
        roles=roles_data,
        detected_skills=detected_skills,
        has_resume=bool(latest_resume),
    )


@bp.route("/career/roadmap")
@login_required
def roadmap():
    user_items = (
        RoadmapItem.query.filter_by(user_id=current_user.id)
        .order_by(RoadmapItem.is_completed.asc(), RoadmapItem.priority.asc())
        .all()
    )

    completed = [i for i in user_items if i.is_completed]
    pending = [i for i in user_items if not i.is_completed]

    total = len(user_items)
    progress_pct = round((len(completed) / total * 100)) if total > 0 else 0

    return render_template(
        "career/roadmap.html",
        title="Personalized Learning Roadmap",
        pending_items=pending,
        completed_items=completed,
        total_count=total,
        completed_count=len(completed),
        progress_pct=progress_pct,
    )


@bp.route("/career/roadmap/<int:item_id>/toggle", methods=["POST"])
@login_required
def toggle_roadmap_item(item_id):
    # Enforce strict user isolation
    item = RoadmapItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    item.is_completed = not item.is_completed
    item.completed_at = datetime.utcnow() if item.is_completed else None
    db.session.commit()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({
            "success": True,
            "item_id": item.id,
            "is_completed": item.is_completed,
            "status": "Completed" if item.is_completed else "Pending"
        })

    flash(f"Milestone '{item.skill_name}' marked as {'completed' if item.is_completed else 'pending'}!", "success")
    return redirect(url_for("career.roadmap"))


@bp.route("/career/interview", methods=["GET", "POST"])
@login_required
def interview():
    latest_resume = (
        Resume.query.filter_by(user_id=current_user.id)
        .order_by(Resume.created_at.desc())
        .first()
    )

    detected_skills = []
    sections = {}
    target_role = current_user.target_role

    if latest_resume:
        skills_data = extract_skills_with_evidence(latest_resume.raw_text)
        detected_skills = skills_data["all_skills"]
        sections = latest_resume.extracted_sections
        target_role = latest_resume.target_role

    generated_questions = generate_interview_questions(
        detected_skills=detected_skills,
        target_role=target_role,
        sections=sections,
    )

    form = InterviewAnswerForm()
    evaluation_result = None

    if form.validate_on_submit():
        q_text = form.question_text.data
        concepts = json.loads(form.key_concepts.data) if form.key_concepts.data else []
        cat = form.category.data
        ans = form.user_answer.data.strip()

        evaluation_result = evaluate_user_answer(
            question_text=q_text,
            key_concepts=concepts,
            user_answer=ans,
            category=cat,
        )

        # Save session record
        session_record = InterviewSession(
            user_id=current_user.id,
            resume_id=latest_resume.id if latest_resume else None,
            target_role=target_role,
            question_text=q_text,
            question_type=cat,
            sample_outline=form.question_text.data,
            user_answer=ans,
            self_assessment_score=evaluation_result["score"],
        )
        session_record.key_concepts = concepts
        session_record.feedback = evaluation_result
        db.session.add(session_record)
        db.session.commit()

        flash(f"Answer evaluated! Score: {evaluation_result['score']}/100 ({evaluation_result['grade']})", "info")

    return render_template(
        "career/interview.html",
        title="Resume-Based Interview Practice",
        questions=generated_questions,
        form=form,
        evaluation=evaluation_result,
        target_role=target_role,
        has_resume=bool(latest_resume),
    )
