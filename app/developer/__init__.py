from flask import Blueprint

developer_bp = Blueprint("developer", __name__, url_prefix="/developer")

from app.developer import routes
