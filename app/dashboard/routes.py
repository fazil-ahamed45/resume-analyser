from flask import render_template
from flask_login import login_required, current_user
from app.dashboard import bp
from app.models import Resume, ResumeAnalysis, JobComparison, RoadmapItem


@bp.route("/dashboard")
@login_required
def index():
    # User-isolated queries
    user_resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.created_at.desc()).all()
    user_analyses = ResumeAnalysis.query.filter_by(user_id=current_user.id).order_by(ResumeAnalysis.created_at.desc()).all()
    user_comparisons = JobComparison.query.filter_by(user_id=current_user.id).order_by(JobComparison.created_at.desc()).all()
    user_roadmap = RoadmapItem.query.filter_by(user_id=current_user.id).all()

    total_resumes = len(user_resumes)
    avg_score = (
        round(sum(a.total_score for a in user_analyses) / len(user_analyses))
        if user_analyses
        else 0
    )
    latest_analysis = user_analyses[0] if user_analyses else None
    latest_comparison = user_comparisons[0] if user_comparisons else None

    completed_milestones = sum(1 for m in user_roadmap if m.is_completed)
    total_milestones = len(user_roadmap)
    roadmap_progress = (
        round((completed_milestones / total_milestones) * 100)
        if total_milestones > 0
        else 0
    )

    return render_template(
        "dashboard/index.html",
        title="Candidate Dashboard",
        total_resumes=total_resumes,
        avg_score=avg_score,
        latest_analysis=latest_analysis,
        latest_comparison=latest_comparison,
        recent_analyses=user_analyses[:5],
        user_resumes=user_resumes[:5],
        user_comparisons=user_comparisons[:3],
        completed_milestones=completed_milestones,
        total_milestones=total_milestones,
        roadmap_progress=roadmap_progress,
    )
