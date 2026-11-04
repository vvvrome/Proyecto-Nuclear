from flask import Blueprint, render_template

from nuclear_sim.web.routes.asir_asignatura import ASIGNATURAS


asir_bp = Blueprint(
    "asir",
    __name__,
    url_prefix="/asir",
)


@asir_bp.get("/")
def index() -> str:
    return render_template(
        "asir.html",
        asignaturas=ASIGNATURAS,
    )