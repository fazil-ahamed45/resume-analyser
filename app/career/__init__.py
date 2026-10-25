from flask import Blueprint

bp = Blueprint("career", __name__)

from app.career import routes
