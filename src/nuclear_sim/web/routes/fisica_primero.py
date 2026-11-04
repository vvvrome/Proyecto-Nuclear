from flask import Blueprint, render_template


fisica_primero_bp = Blueprint(
    "fisica_primero",
    __name__,
    url_prefix="/fisica/primero",
)


@fisica_primero_bp.get("/")
def index() -> str:
    return render_template("fisica_primero.html")