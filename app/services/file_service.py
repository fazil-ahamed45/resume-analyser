import os
import uuid
import zipfile
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {"pdf", "docx"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


class FileServiceError(Exception):
    """Custom exception for file validation and storage errors."""
    pass


def allowed_file(filename: str) -> bool:
    """Check if the filename has an allowed extension."""
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def get_file_extension(filename: str) -> str:
    """Safely return lowercased extension."""
    return filename.rsplit(".", 1)[1].lower() if "." in filename else ""


def validate_file_content(file_storage, declared_ext: str) -> bool:
    """
    Validate magic bytes / structure to verify the file is genuinely PDF or DOCX,
    preventing disguised malicious files.
    """
    header = file_storage.read(16)
    file_storage.seek(0)  # Rewind pointer

    if declared_ext == "pdf":
        return header.startswith(b"%PDF-")
    elif declared_ext == "docx":
        # DOCX is an OpenXML ZIP archive starting with PK (0x50 0x4B 0x03 0x04)
        if not header.startswith(b"PK\x03\x04"):
            return False
        # Further verify by reading zip content without extracting
        try:
            with zipfile.ZipFile(file_storage) as z:
                # OpenXML DOCX files contain '[Content_Types].xml' and 'word/document.xml'
                names = z.namelist()
                has_content_types = "[Content_Types].xml" in names
                has_word_dir = any(name.startswith("word/") for name in names)
                file_storage.seek(0)
                return has_content_types and has_word_dir
        except Exception:
            file_storage.seek(0)
            return False
    return False


def save_resume_file(file_storage) -> tuple[str, str, int, str]:
    """
    Validates and saves an uploaded resume file using a server-generated UUID filename.
    Returns: (original_filename, stored_filename, file_size, file_type)
    """
    if not file_storage or not file_storage.filename:
        raise FileServiceError("No file selected for upload.")

    original_filename = secure_filename(file_storage.filename)
    if not original_filename:
        original_filename = "resume_document"

    if not allowed_file(original_filename):
        raise FileServiceError("Unsupported file type. Please upload a PDF or DOCX file.")

    ext = get_file_extension(original_filename)

    # Check file size by reading stream length safely
    file_storage.seek(0, os.SEEK_END)
    file_size = file_storage.tell()
    file_storage.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise FileServiceError("File exceeds the maximum allowed size of 5 MB.")

    if file_size == 0:
        raise FileServiceError("Uploaded file is empty (0 bytes).")

    # Content signature verification
    if not validate_file_content(file_storage, ext):
        raise FileServiceError(
            f"The file content does not match a valid {ext.upper()} document. Please check the file."
        )

    # Ensure upload directory exists
    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Generate safe random UUID filename
    stored_filename = f"{uuid.uuid4().hex}.{ext}"
    target_path = upload_dir / stored_filename

    # Save to disk
    file_storage.save(str(target_path))

    return original_filename, stored_filename, file_size, ext


def get_resume_path(stored_filename: str) -> Path:
    """Return the absolute path for a stored resume file."""
    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    return upload_dir / stored_filename


def delete_resume_file(stored_filename: str) -> bool:
    """Safely delete a resume file from disk."""
    try:
        path = get_resume_path(stored_filename)
        if path.exists() and path.is_file():
            path.unlink()
            return True
    except Exception as e:
        current_app.logger.error(f"Error deleting resume file {stored_filename}: {e}")
    return False
