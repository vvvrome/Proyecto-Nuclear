from flask import Blueprint, render_template


fisica_bp = Blueprint("fisica", __name__, url_prefix="/fisica")


@fisica_bp.get("/")
def index() -> str:
    return render_template("fisica.html")