# CareerPilot AI — Resume Analyzer & Career Assistant

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask%203.1-black.svg)](https://flask.palletsprojects.com/)
[![Tests](https://img.shields.io/badge/Tests-25%20Passed-brightgreen.svg)](https://docs.pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**CareerPilot AI** is a production-minded web application designed for college students and job seekers applying for full-stack and backend software engineering internships. It bridges the gap between academic resumes and real-world hiring criteria through **explainable 0–100 scoring**, **job description skill matching**, **career path fit discovery**, and **personalized learning roadmaps**.

Unlike black-box ATS checkers that claim proprietary scoring or guarantee hiring results, CareerPilot AI uses transparent, documented evaluation criteria adapted to student and fresher experience levels, prioritizing projects, technical depth, and quantifiable bullet points over missing corporate employment history.

---

## 🌟 Key Features

### 1. Secure Resume Upload & Multi-Format Parsing
- **PDF & DOCX Support**: High-fidelity text extraction using `PyMuPDF` (for PDFs) and `python-docx` (for DOCX).
- **Security by Design**: Validates file magic bytes (signatures), limits uploads to 5 MB, and assigns cryptographically secure UUID filenames (`uuid.uuid4().hex`) stored outside public static directories.
- **Scanned PDF Detection**: Automatically detects rasterized/scanned documents without selectable text and alerts the candidate.
- **Isolated User Deletion**: Deleting a resume safely purges the physical file from the server disk and cascades through all associated database records.

### 2. Transparent & Explainable 0–100 Resume Scoring
Scored using five documented, configurable criteria designed to avoid penalizing college freshers:
- **Section Completeness (25 pts)**: Education, Skills, Projects, Contact, and Experience/Certifications.
- **Skills Relevance (30 pts)**: Aligned against target role curricula (Python Developer, Backend Developer, Full Stack, Data Analyst, QA, etc.).
- **Project & Evidence Depth (20 pts)**: Student-friendly scoring emphasizing GitHub links, multi-model complexity, and practical code evidence.
- **Bullet Point Quality (15 pts)**: Automated analysis of strong past-tense action verbs (*Architected, Engineered, Optimized*) and measurable metrics (*%, ms, users, requests*).
- **Readability & Formatting (10 pts)**: Word count density checks (ideal 400–900 words) and contact accessibility.
- *Includes a clear disclaimer that scores are heuristic benchmarks, not proprietary ATS vendor guarantees.*

### 3. Job Description Matcher
- Paste any real internship or job posting.
- Automatic extraction of required vs. preferred skills using a curated taxonomy of 70+ technical and soft skills.
- Interactive **Chart.js** donut chart visualization with weighted match percentage (75% required / 25% preferred).
- Pinpoints matched skills (green), missing critical requirements (red), and bonus advantages (amber) with tailored advice.
- Saves comparisons to SQLite with full history review and deletion controls.

### 4. Career Role Recommendations
- Evaluates student skills against 6 entry-level roles:
  1. **Python Developer Intern**
  2. **Backend Developer Intern**
  3. **Full Stack Developer Intern**
  4. **Data Analyst Intern**
  5. **QA Automation Intern**
  6. **DevOps & Cloud Intern**
- Explains *why* the role is recommended, highlights core gaps, and summarizes typical daily intern responsibilities.

### 5. Personalized Learning Roadmap
- Generates prioritized technical milestones (High, Medium, Low) bridging candidate-specific skill gaps.
- Includes hands-on practice exercises, resume-worthy project ideas, and **100% verified official documentation links** (Python Docs, Flask, Docker, PostgreSQL, Pytest, MDN).
- Interactive AJAX milestone checkboxes to check off mastered skills and track completion progress.

### 6. Resume-Based Interview Practice
- Generates 5 tailored technical, project deep-dive, and behavioral questions directly from the candidate's parsed projects and detected skills.
- Interactive answer studio with sample outlines.
- Rubric-based evaluation grading concept coverage, depth, quantifiable metrics, and **STAR method structure** (Situation, Task, Action, Result).
- Runs 100% locally without external dependencies.

### 7. AI Resume Coach with Deterministic Fallback
- Configurable LLM API (Google Gemini 2.5 Flash via `google-genai` SDK or OpenAI).
- **Prompt Injection Defense**: Resume text and job descriptions are wrapped in untrusted data tags `<resume_text>` with strict system constraints.
- **Fact Integrity**: AI prompt explicitly forbids fabricating unearned degrees, companies, or fake metrics.
- **Consent Gate**: External API calls require explicit user opt-in consent (`ai_consent=True`).
- **Deterministic Rule Fallback**: If no API key is provided or if network errors occur, the application transparently serves local heuristic suggestions.

### 8. Downloadable PDF Analysis Report
- High-contrast, executive PDF report generated via `ReportLab`.
- Includes candidate header, overall score badge, component audit table, cataloged skills taxonomy, actionable improvement points, and learning milestones.

---

## 🏗️ Architecture & Database Relationships

### Technology Stack
- **Backend**: Python 3.11+ / 3.13, Flask 3.1, Flask-SQLAlchemy 3.1, Flask-Login 0.6, Flask-WTF 1.3
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla ES6+), Bootstrap 5.3, Bootstrap Icons, Chart.js 4.4
- **Database**: SQLite (SQLAlchemy ORM with Foreign Keys, Cascading Deletes, and Indexes)
- **Document Parsing**: PyMuPDF (`pymupdf`), `python-docx`
- **PDF Generation**: ReportLab 5.1
- **Testing**: `pytest 9.1` (25 automated tests)
- **AI Integration**: Optional Google Gemini official SDK (`google-genai`) with local rule-based fallback

### Project Structure
```
careerpilot-ai/
├── app/
│   ├── __init__.py               # Application factory & Jinja filters
│   ├── extensions.py             # SQLAlchemy, LoginManager, CSRFProtect
│   ├── models.py                 # User, Resume, ResumeAnalysis, JobComparison, RoadmapItem, InterviewSession
│   ├── auth/                     # Authentication routes & forms (Login, Register, Profile)
│   ├── dashboard/                # Candidate overview metrics & quick shortcuts
│   ├── resumes/                  # Upload, document inspection, parsing & delete routes
│   ├── analysis/                 # Scoring view, radar chart, history & PDF export
│   ├── career/                   # Job matcher, role discovery, roadmap & interview prep
│   ├── services/
│   │   ├── file_service.py       # Signature validation, UUID generation, cleanup
│   │   ├── parser_service.py     # PyMuPDF & python-docx extraction, scanned document check
│   │   ├── skills_dictionary.py  # Curated taxonomy & alias resolution
│   │   ├── section_extractor.py  # Contact info, resume sections & bullet point analysis
│   │   ├── scoring_service.py    # 0-100 explainable scoring model
│   │   ├── job_matcher.py        # Job description extraction & match percentage
│   │   ├── career_service.py     # Role recommendation engine
│   │   ├── roadmap_service.py    # Personalized roadmap with verified links
│   │   ├── interview_service.py  # Question bank & STAR answer evaluator
│   │   ├── report_service.py     # ReportLab executive PDF generator
│   │   └── ai_service.py         # LLM integration & deterministic rule-based fallback
│   ├── static/
│   │   ├── css/custom.css        # Modern Navy & Slate SaaS design system
│   │   └── js/main.js            # Chart.js renderers, AJAX toggles, interview switcher
│   └── templates/                # Jinja2 templates (Base, Auth, Dashboard, Career, Errors)
├── tests/
│   ├── conftest.py               # Fixtures, test client, sample PDF/DOCX generators
│   ├── test_auth.py              # Auth, registration, session, route security
│   ├── test_upload_parser.py     # File validation, size, signature, parsing
│   ├── test_analysis_score.py    # Section splitting, skills extraction, 0-100 scoring
│   ├── test_job_matching.py      # JD skill extraction, match %, DB persistence
│   ├── test_career_roadmap.py    # Role recommendations, roadmap toggle, interview
│   ├── test_ai_fallback.py       # Deterministic fallback without API keys
│   ├── test_report_pdf.py        # ReportLab PDF creation & download endpoint
│   └── test_isolation_security.py# Cross-user isolation & physical file cleanup
├── instance/                     # SQLite database & secure upload storage
├── .env.example                  # Environment configuration template
├── .gitignore                    # Git ignore rules for virtualenvs, DBs, uploads
├── config.py                     # Dev, Testing, Production configurations
├── pytest.ini                    # Pytest configuration
├── requirements.txt              # Pinned dependencies
├── run.py                        # Entry point & CLI database commands
└── README.md                     # Comprehensive documentation
```

### Database Schema (Entity-Relationship Overview)
- **User (1) ────< (N) Resume**: Cascades on delete. Each user owns isolated resumes.
- **User (1) ────< (N) ResumeAnalysis**: Scored audits linked to both User and Resume.
- **Resume (1) ──< (N) ResumeAnalysis**: Cascades on delete.
- **Resume (1) ──< (N) JobComparison**: Job comparisons saved against specific resumes.
- **User (1) ────< (N) RoadmapItem**: Personalized learning milestones tracked per user.
- **User (1) ────< (N) InterviewSession**: Interview self-assessment logs.

*All endpoints enforce ownership (`user_id=current_user.id`) to prevent cross-user ID tampering.*

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11, 3.12, or 3.13
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/careerpilot-ai.git
cd careerpilot-ai
```

### 2. Create and Activate Virtual Environment
**On Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**On Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Default development settings are preconfigured. To test optional external AI suggestions, add your Google Gemini API key:
```ini
AI_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
```
*(If left blank, CareerPilot AI uses its deterministic rule engine with zero external calls.)*

### 5. Initialize the Database
```bash
python -m flask --app run.py init-db
```
*(Or simply start the application; SQLite tables are automatically verified on launch.)*

### 6. Run the Application
```bash
python run.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Automated Testing

CareerPilot AI includes a comprehensive test suite covering authentication, file validation, text extraction, scoring formulas, job matching, cross-user isolation, AI fallback, and PDF generation.

Run all tests with:
```bash
python -m pytest -v
```

### Test Results
```
tests/test_ai_fallback.py::test_deterministic_rule_based_coach PASSED             [  4%]
tests/test_ai_fallback.py::test_ai_coach_graceful_fallback_without_consent PASSED  [  8%]
tests/test_analysis_score.py::test_skills_extraction_and_evidence PASSED          [ 12%]
tests/test_analysis_score.py::test_section_splitting PASSED                       [ 16%]
tests/test_analysis_score.py::test_explainable_score_fresher_mode PASSED          [ 20%]
tests/test_auth.py::test_user_registration PASSED                                 [ 24%]
tests/test_auth.py::test_duplicate_email_registration_fails PASSED                [ 28%]
tests/test_auth.py::test_login_success_and_logout PASSED                          [ 32%]
tests/test_auth.py::test_login_invalid_password PASSED                            [ 36%]
tests/test_auth.py::test_protected_routes_redirect_unauthenticated PASSED          [ 40%]
tests/test_career_roadmap.py::test_career_recommendations PASSED                  [ 44%]
tests/test_career_roadmap.py::test_roadmap_verified_urls PASSED                   [ 48%]
tests/test_career_roadmap.py::test_roadmap_toggle_route PASSED                    [ 52%]
tests/test_career_roadmap.py::test_interview_question_and_evaluation PASSED      [ 56%]
tests/test_isolation_security.py::test_user_data_isolation_and_id_tampering PASSED[ 60%]
tests/test_isolation_security.py::test_resume_deletion_cleans_up_files_and_cascades PASSED [ 64%]
tests/test_job_matching.py::test_job_skill_extraction PASSED                      [ 68%]
tests/test_job_matching.py::test_compare_resume_to_job PASSED                     [ 72%]
tests/test_job_matching.py::test_job_match_route_flow PASSED                      [ 76%]
tests/test_report_pdf.py::test_pdf_report_generation PASSED                       [ 80%]
tests/test_report_pdf.py::test_download_pdf_endpoint PASSED                       [ 84%]
tests/test_upload_parser.py::test_upload_valid_pdf PASSED                         [ 88%]
tests/test_upload_parser.py::test_upload_valid_docx PASSED                        [ 92%]
tests/test_upload_parser.py::test_upload_disallowed_extension PASSED              [ 96%]
tests/test_upload_parser.py::test_upload_corrupted_magic_bytes_pdf PASSED         [100%]

============================= 25 passed in 4.42s ==============================
```

---

## 🔒 Security & Privacy Practices

1. **User Data Isolation**: Every database query filters by `user_id=current_user.id` or verifies record ownership before rendering, preventing ID parameter tampering.
2. **Safe File Handling**: Uploaded files are assigned random UUID filenames (`32-hex-chars.pdf`) and stored outside the public `static/` directory in `instance/uploads/`.
3. **Magic Byte Verification**: Verifies PDF (`%PDF-`) and DOCX OpenXML ZIP signatures before saving.
4. **Output Escaping & CSRF**: All forms are protected by Flask-WTF CSRF tokens; Jinja2 autoescaping prevents XSS.
5. **Secure Session Settings**: Configured with `SESSION_COOKIE_HTTPONLY=True`, `SESSION_COOKIE_SAMESITE="Lax"`, and production HTTPS flags.
6. **Privacy First AI**: Resume contents are never transmitted to external APIs unless the user explicitly checks the opt-in disclosure box (`ai_consent=True`).

---

## 📋 Feature Verification Checklist

| Feature | Status | Automated Test Coverage |
| :--- | :--- | :--- |
| User Registration & Login | ✅ Implemented | `test_auth.py` |
| Password Hashing (Werkzeug) | ✅ Implemented | `test_auth.py` |
| Route Protection | ✅ Implemented | `test_auth.py` |
| PDF Parsing (PyMuPDF) | ✅ Implemented | `test_upload_parser.py` |
| DOCX Parsing (python-docx) | ✅ Implemented | `test_upload_parser.py` |
| Scanned PDF Detection | ✅ Implemented | `test_upload_parser.py` |
| File Type & Size Validation | ✅ Implemented | `test_upload_parser.py` |
| Skills Extraction & Evidence | ✅ Implemented | `test_analysis_score.py` |
| 0–100 Explainable Scoring | ✅ Implemented | `test_analysis_score.py` |
| Student / Fresher Adaptation | ✅ Implemented | `test_analysis_score.py` |
| Action Verb & Metric Audit | ✅ Implemented | `test_analysis_score.py` |
| Job Description Matcher | ✅ Implemented | `test_job_matching.py` |
| Career Recommendations | ✅ Implemented | `test_career_roadmap.py` |
| Interactive Roadmap Tracking | ✅ Implemented | `test_career_roadmap.py` |
| Interview Prep & STAR Grading | ✅ Implemented | `test_career_roadmap.py` |
| Deterministic AI Fallback | ✅ Implemented | `test_ai_fallback.py` |
| User Data Isolation (Anti-Tamper) | ✅ Implemented | `test_isolation_security.py` |
| Resume Deletion & File Cleanup | ✅ Implemented | `test_isolation_security.py` |
| Downloadable PDF Report | ✅ Implemented | `test_report_pdf.py` |
| Custom 403, 404, 500 Pages | ✅ Implemented | Manual & Route Verified |

---

## 🚢 Production Deployment

For production deployment (e.g., Ubuntu VPS, Render, Railway, or AWS EC2):

1. **Set Environment Variables**:
   ```ini
   FLASK_ENV=production
   DEBUG=False
   SECRET_KEY=use-a-strong-32-byte-random-key
   SESSION_COOKIE_SECURE=True
   DATABASE_URL=sqlite:////var/data/careerpilot.db  # or PostgreSQL URL
   ```
2. **Run with Gunicorn**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 "run:app"
   ```
3. **Nginx Reverse Proxy**: Terminate SSL (HTTPS) at Nginx, set maximum body size (`client_max_body_size 5M;`), and proxy requests to `http://127.0.0.1:8000`.

---

## 🐙 GitHub Publishing Instructions

To push this project to your GitHub account:

```bash
# 1. Initialize git repository
git init

# 2. Add files (respects .gitignore, excluding .venv and uploaded resumes)
git add .

# 3. Commit
git commit -m "Initial commit: CareerPilot AI - Resume Analyzer & Career Assistant"

# 4. Create repository on GitHub and link remote
git branch -M main
git remote add origin https://github.com/your-username/careerpilot-ai.git

# 5. Push to GitHub
git push -u origin main
```

---

## 💼 Resume Project Description (For Your Internship Resume)

Use these honest, achievement-focused bullet points on your own resume under **Projects**:

### **CareerPilot AI — Resume Analyzer & Career Assistant**
*Tech Stack: Python, Flask, SQLAlchemy, SQLite, PyMuPDF, python-docx, ReportLab, Chart.js, Bootstrap 5, Pytest*

- Engineered a full-stack career platform empowering CS students to analyze resumes against internship postings with an explainable 0–100 scoring model across 5 dimensions.
- Built multi-format document extraction pipelines utilizing `PyMuPDF` and `python-docx`, with automated scanned document detection and magic byte verification.
- Developed a job description matching engine parsing required vs. preferred competencies against a curated 70+ technical skill taxonomy, generating gap diagnostics and verified resource roadmaps.
- Designed an interactive interview studio evaluating technical and behavioral responses against semantic rubrics, keyword density, and STAR narrative frameworks.
- Implemented user data isolation, CSRF protection, UUID-based file storage outside public web directories, and a 25-test automated test suite achieving 100% pass rate.
