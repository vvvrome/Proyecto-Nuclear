from flask import Blueprint, abort, render_template

from nuclear_sim.web.routes.fisica_asignatura import ASIGNATURAS


fisica_curso_bp = Blueprint(
    "fisica_curso",
    __name__,
    url_prefix="/fisica",
)


CURSOS = {
    "primero": "1.º Curso",
    "segundo": "2.º Curso",
    "tercero": "3.º Curso",
    "cuarto": "4.º Curso",
}


@fisica_curso_bp.get("/<curso>/")
def index(curso: str) -> str:
    asignaturas = ASIGNATURAS.get(curso)

    if asignaturas is None:
        abort(404)

    return render_template(
        "fisica_curso.html",
        curso=curso,
        nombre_curso=CURSOS[curso],
        asignaturas=asignaturas,
    )
