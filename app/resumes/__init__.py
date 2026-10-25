from flask import Blueprint

bp = Blueprint("resumes", __name__)

from app.resumes import routes
