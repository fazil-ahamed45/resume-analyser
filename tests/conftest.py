import io
import pytest
import pymupdf as fitz
import docx  # python-docx
from app import create_app
from app.extensions import db as _db
from app.models import User, Resume, ResumeAnalysis


@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    return app


@pytest.fixture(scope="function")
def db_session(app):
    with app.app_context():
        _db.create_all()
        yield _db.session
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app, db_session):
    return app.test_client()


@pytest.fixture
def registered_user(db_session):
    user = User(
        full_name="Alice Candidate",
        email="alice@example.com",
        experience_level="fresher",
        target_role="Python Developer Intern",
        ai_consent=False,
    )
    user.set_password("Secret1234!")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def second_user(db_session):
    user = User(
        full_name="Bob Unauthorized",
        email="bob@example.com",
        experience_level="fresher",
        target_role="Backend Developer Intern",
        ai_consent=False,
    )
    user.set_password("Secret5678!")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def auth_client(client, registered_user):
    client.post(
        "/login",
        data={"email": "alice@example.com", "password": "Secret1234!"},
        follow_redirects=True,
    )
    return client


@pytest.fixture
def second_auth_client(client, second_user):
    client.post(
        "/login",
        data={"email": "bob@example.com", "password": "Secret5678!"},
        follow_redirects=True,
    )
    return client


@pytest.fixture
def sample_pdf_bytes():
    """Create a minimal real PDF with selectable text using PyMuPDF."""
    doc = fitz.open()
    page = doc.new_page()
    text = (
        "Alice Candidate\nalice@example.com | +1 555-0199\n"
        "https://github.com/alice-dev | https://linkedin.com/in/alice-dev\n\n"
        "EDUCATION\nB.E. in Computer Science, State University, 2026, CGPA 8.8\n\n"
        "TECHNICAL SKILLS\nProgramming Languages: Python, SQL, JavaScript, HTML5, CSS3\n"
        "Frameworks & Tools: Flask, Git, Docker, PostgreSQL, REST API, Pytest\n\n"
        "PROJECTS\n"
        "Career Tracker Web App | Python, Flask, SQLite\n"
        "- Engineered a full-stack job application tracker with Flask-Login and SQLite.\n"
        "- Implemented RESTful APIs reducing data retrieval times by 40%.\n"
        "- Deployed using Docker container with automated GitHub Actions CI/CD pipeline.\n"
    )
    page.insert_text((50, 72), text, fontsize=10)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


@pytest.fixture
def sample_docx_bytes():
    """Create a minimal real DOCX document with python-docx."""
    doc = docx.Document()
    doc.add_heading("Bob Candidate", 0)
    doc.add_paragraph("bob@example.com | +1 555-0288 | https://github.com/bob-dev")
    doc.add_heading("Education", level=1)
    doc.add_paragraph("B.Tech in Information Technology, 2025")
    doc.add_heading("Skills", level=1)
    doc.add_paragraph("Python, Django, PostgreSQL, Git, Linux, Docker, REST API")
    doc.add_heading("Projects", level=1)
    doc.add_paragraph("Built an e-commerce backend handling 500 requests per minute.")

    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio.read()
