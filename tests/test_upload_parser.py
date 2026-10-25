import io
from app.models import Resume, ResumeAnalysis
from app.services.file_service import get_resume_path


def test_upload_valid_pdf(auth_client, sample_pdf_bytes, db_session):
    data = {
        "resume_file": (io.BytesIO(sample_pdf_bytes), "alice_resume.pdf"),
        "target_role": "Python Developer Intern",
        "experience_level": "fresher",
    }
    res = auth_client.post("/resumes/upload", data=data, content_type="multipart/form-data", follow_redirects=True)
    assert res.status_code == 200

    # Verify DB record created
    resume = Resume.query.filter_by(original_filename="alice_resume.pdf").first()
    assert resume is not None
    assert resume.file_type == "pdf"
    assert "Python" in resume.raw_text
    assert "Flask" in resume.raw_text
    assert resume.extracted_contact.get("email") == "alice@example.com"

    # Verify physical file stored with UUID filename
    path = get_resume_path(resume.stored_filename)
    assert path.exists()
    assert path.name.endswith(".pdf")

    # Verify automated analysis was created
    analysis = ResumeAnalysis.query.filter_by(resume_id=resume.id).first()
    assert analysis is not None
    assert analysis.total_score > 0


def test_upload_valid_docx(auth_client, sample_docx_bytes, db_session):
    data = {
        "resume_file": (io.BytesIO(sample_docx_bytes), "bob_resume.docx"),
        "target_role": "Backend Developer Intern",
        "experience_level": "fresher",
    }
    res = auth_client.post("/resumes/upload", data=data, content_type="multipart/form-data", follow_redirects=True)
    assert res.status_code == 200

    resume = Resume.query.filter_by(original_filename="bob_resume.docx").first()
    assert resume is not None
    assert resume.file_type == "docx"
    assert "Django" in resume.raw_text
    assert "PostgreSQL" in resume.raw_text


def test_upload_disallowed_extension(auth_client):
    data = {
        "resume_file": (io.BytesIO(b"Hello world"), "resume.txt"),
        "target_role": "Python Developer Intern",
        "experience_level": "fresher",
    }
    res = auth_client.post("/resumes/upload", data=data, content_type="multipart/form-data", follow_redirects=True)
    assert b"Only PDF and DOCX files are allowed" in res.data


def test_upload_corrupted_magic_bytes_pdf(auth_client):
    # A file named .pdf but containing plain non-PDF garbage
    fake_pdf = b"NOT_A_REAL_PDF_HEADER_JUST_GARBAGE"
    data = {
        "resume_file": (io.BytesIO(fake_pdf), "fake.pdf"),
        "target_role": "Python Developer Intern",
        "experience_level": "fresher",
    }
    res = auth_client.post("/resumes/upload", data=data, content_type="multipart/form-data", follow_redirects=True)
    assert b"does not match a valid PDF document" in res.data
