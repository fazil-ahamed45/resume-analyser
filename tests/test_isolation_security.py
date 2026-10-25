from app.models import Resume, ResumeAnalysis, JobComparison
from app.services.file_service import get_resume_path


def test_user_data_isolation_and_id_tampering(client, registered_user, second_user, db_session):
    # Create a resume owned by User A (Alice)
    alice_resume = Resume(
        user_id=registered_user.id,
        original_filename="alice_confidential.pdf",
        stored_filename="alice_secret_123.pdf",
        file_type="pdf",
        file_size=2048,
        raw_text="Alice confidential resume details",
        target_role="Python Developer Intern",
    )
    db_session.add(alice_resume)
    db_session.commit()

    alice_analysis = ResumeAnalysis(
        resume_id=alice_resume.id,
        user_id=registered_user.id,
        target_role="Python Developer Intern",
        experience_level="fresher",
        total_score=85,
    )
    alice_analysis.score_breakdown = {}
    alice_analysis.detected_skills = {}
    db_session.add(alice_analysis)
    db_session.commit()

    # Now login as User B (Bob)
    client.post(
        "/login",
        data={"email": "bob@example.com", "password": "Secret5678!"},
        follow_redirects=True,
    )

    # Bob tries to view Alice's resume by ID tampering
    res = client.get(f"/resumes/{alice_resume.id}")
    assert res.status_code == 404

    # Bob tries to view Alice's analysis by ID tampering
    res = client.get(f"/analysis/{alice_analysis.id}")
    assert res.status_code == 404

    # Bob tries to download Alice's PDF report
    res = client.get(f"/analysis/{alice_analysis.id}/report.pdf")
    assert res.status_code == 404

    # Bob tries to delete Alice's resume
    res = client.post(f"/resumes/{alice_resume.id}/delete")
    assert res.status_code == 404
    # Verify Alice's resume still exists
    assert db_session.get(Resume, alice_resume.id) is not None


def test_resume_deletion_cleans_up_files_and_cascades(auth_client, registered_user, db_session, sample_pdf_bytes):
    # Upload a resume through the endpoint so physical file is written
    import io
    data = {
        "resume_file": (io.BytesIO(sample_pdf_bytes), "deletion_test.pdf"),
        "target_role": "Python Developer Intern",
        "experience_level": "fresher",
    }
    auth_client.post("/resumes/upload", data=data, content_type="multipart/form-data", follow_redirects=True)

    resume = Resume.query.filter_by(original_filename="deletion_test.pdf").first()
    assert resume is not None
    resume_id = resume.id
    stored_name = resume.stored_filename
    file_path = get_resume_path(stored_name)
    assert file_path.exists()

    # Verify analysis exists
    analysis = ResumeAnalysis.query.filter_by(resume_id=resume_id).first()
    assert analysis is not None

    # Delete resume via endpoint
    del_res = auth_client.post(f"/resumes/{resume_id}/delete", follow_redirects=True)
    assert del_res.status_code == 200

    # Verify DB record deleted
    assert db_session.get(Resume, resume_id) is None
    # Verify cascade deleted analysis
    assert db_session.get(ResumeAnalysis, analysis.id) is None
    # Verify physical file was deleted from disk
    assert not file_path.exists()
