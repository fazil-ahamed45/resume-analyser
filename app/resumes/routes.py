from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.resumes import bp
from app.resumes.forms import ResumeUploadForm
from app.models import Resume, ResumeAnalysis, RoadmapItem
from app.extensions import db
from app.services.file_service import save_resume_file, get_resume_path, delete_resume_file, FileServiceError
from app.services.parser_service import extract_resume_text, ParserServiceError
from app.services.section_extractor import (
    extract_contact_info,
    split_into_sections,
    extract_skills_with_evidence,
    analyze_bullet_points,
)
from app.services.scoring_service import calculate_overall_resume_score
from app.services.roadmap_service import generate_roadmap_for_role
from app.services.ai_service import get_ai_resume_coach_feedback


@bp.route("/resumes/upload", methods=["GET", "POST"])
@login_required
def upload():
    form = ResumeUploadForm()
    # Prepopulate default role and experience from user profile if not set
    if request.method == "GET":
        form.target_role.data = current_user.target_role
        form.experience_level.data = current_user.experience_level

    if form.validate_on_submit():
        file = form.resume_file.data
        target_role = form.target_role.data
        experience_level = form.experience_level.data

        try:
            # 1. Secure file storage with server UUID
            orig_name, stored_name, file_size, file_type = save_resume_file(file)
            saved_path = get_resume_path(stored_name)

            # 2. Text extraction
            raw_text, is_scanned = extract_resume_text(saved_path, file_type)

            if is_scanned:
                flash(
                    "Warning: This PDF appears to be a scanned image or rasterized document without selectable text. "
                    "OCR is not enabled, so text-based analysis cannot detect your skills. Please upload a standard text-based PDF or DOCX file.",
                    "warning"
                )

            # 3. Section and contact extraction
            contact_info = extract_contact_info(raw_text)
            sections = split_into_sections(raw_text)

            # 4. Save Resume entity
            resume = Resume(
                user_id=current_user.id,
                original_filename=orig_name,
                stored_filename=stored_name,
                file_type=file_type,
                file_size=file_size,
                raw_text=raw_text,
                is_scanned_pdf=is_scanned,
                target_role=target_role,
            )
            resume.extracted_contact = contact_info
            resume.extracted_sections = sections
            db.session.add(resume)
            db.session.commit()

            # 5. Immediate automated analysis
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

            # Optional AI suggestions or deterministic fallback
            ai_data = get_ai_resume_coach_feedback(
                user_has_consented=current_user.ai_consent,
                target_role=target_role,
                detected_skills=skills_data["all_skills"],
                missing_skills=score_data["breakdown"]["skills_relevance"]["missing_required"],
                weak_bullets=bullet_data["weak_bullets"],
                sections=sections,
                raw_resume_text=raw_text,
            )

            analysis = ResumeAnalysis(
                resume_id=resume.id,
                user_id=current_user.id,
                target_role=target_role,
                experience_level=experience_level,
                total_score=score_data["total_score"],
            )
            analysis.score_breakdown = score_data["breakdown"]
            analysis.detected_skills = skills_data
            analysis.missing_sections = score_data["breakdown"]["section_completeness"]["missing_sections"]
            analysis.strengths = score_data["strengths"]
            analysis.weaknesses = score_data["weaknesses"]
            analysis.bullet_suggestions = score_data["actionable_tips"]
            analysis.ai_suggestions = ai_data

            db.session.add(analysis)

            # Generate initial roadmap milestones for user
            missing_skills = score_data["breakdown"]["skills_relevance"]["missing_required"]
            roadmap_items = generate_roadmap_for_role(missing_skills, target_role)
            for item in roadmap_items:
                # Avoid duplicates
                exists = RoadmapItem.query.filter_by(
                    user_id=current_user.id,
                    skill_name=item["skill_name"],
                    target_role=target_role
                ).first()
                if not exists:
                    new_item = RoadmapItem(
                        user_id=current_user.id,
                        target_role=target_role,
                        skill_name=item["skill_name"],
                        category=item.get("category", "Technical"),
                        priority=item.get("priority", "High"),
                        difficulty=item.get("difficulty", "Beginner"),
                        estimated_hours=item.get("estimated_hours", 10),
                        reason=item.get("reason", ""),
                        practice_task=item.get("practice_task", ""),
                        project_idea=item.get("project_idea", ""),
                        resource_title=item.get("resource_title", ""),
                        resource_url=item.get("resource_url", ""),
                    )
                    db.session.add(new_item)

            db.session.commit()

            flash(f"Resume '{orig_name}' successfully parsed and analyzed!", "success")
            return redirect(url_for("analysis.view", analysis_id=analysis.id))

        except (FileServiceError, ParserServiceError) as e:
            flash(str(e), "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"An unexpected error occurred while processing your resume: {e}", "danger")

    return render_template("resumes/upload.html", title="Upload Resume", form=form)


@bp.route("/resumes")
@login_required
def list_resumes():
    # User-isolated listing
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.created_at.desc()).all()
    return render_template("resumes/list.html", title="My Resumes", resumes=resumes)


@bp.route("/resumes/<int:resume_id>")
@login_required
def view_resume(resume_id):
    # Enforce strict user isolation
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    return render_template("resumes/view.html", title=f"Resume - {resume.original_filename}", resume=resume)


@bp.route("/resumes/<int:resume_id>/delete", methods=["POST"])
@login_required
def delete_resume(resume_id):
    # Enforce strict user isolation
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    stored_name = resume.stored_filename
    orig_name = resume.original_filename

    # Delete from DB (cascades to analyses and job comparisons)
    db.session.delete(resume)
    db.session.commit()

    # Delete physical file from disk outside public static
    delete_resume_file(stored_name)

    flash(f"Resume '{orig_name}' and all associated analyses have been permanently deleted.", "info")
    return redirect(url_for("resumes.list_resumes"))
