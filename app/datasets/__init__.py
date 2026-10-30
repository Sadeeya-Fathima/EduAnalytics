from flask import Blueprint

datasets_bp = Blueprint("datasets", __name__, url_prefix="/datasets")

from app.datasets import routes
