from flask import Blueprint, render_template


tfg_asir_bp = Blueprint(
    "tfg_asir",
    __name__,
    url_prefix="/asir/tfg",
)


@tfg_asir_bp.get("/")
def index() -> str:
    return render_template("tfg_asir.html")