import os
import sys
import shutil
from pathlib import Path

# Add project root directory to Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Detect Vercel Serverless environment and set up writable /tmp storage
if os.environ.get("VERCEL"):
    os.environ.setdefault("FLASK_ENV", "production")
    
    # Use /tmp for file uploads (only writable directory in AWS Lambda/Vercel)
    os.environ.setdefault("UPLOAD_FOLDER", "/tmp/uploads")
    try:
        Path("/tmp/uploads").mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

    # Use /tmp for SQLite database if no external database URL is configured
    if not os.environ.get("DATABASE_URL"):
        tmp_db = Path("/tmp/careerpilot.db")
        os.environ["DATABASE_URL"] = f"sqlite:///{tmp_db}"
        
        # Copy bundled instance/careerpilot.db to /tmp if available
        bundled_db = ROOT_DIR / "instance" / "careerpilot.db"
        if bundled_db.exists() and not tmp_db.exists():
            try:
                shutil.copyfile(bundled_db, tmp_db)
            except Exception:
                pass

from app import create_app
from app.extensions import db

env = os.environ.get("FLASK_ENV", "production")
app = create_app(env)

# Ensure database tables exist
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        app.logger.warning(f"Database table setup notice: {e}")
