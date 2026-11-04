from flask import Blueprint, abort, render_template


fisica_asignatura_bp = Blueprint(
    "fisica_asignatura",
    __name__,
    url_prefix="/fisica/primero",
)


ASIGNATURAS = {
    "algebra-i": {
        "codigo": "algebra-i",
        "nombre": "Álgebra I",
        "ects": 6,
    },
    "analisis-i": {
        "codigo": "analisis-i",
        "nombre": "Análisis I",
        "ects": 6,
    },
    "fisica-i": {
        "codigo": "fisica-i",
        "nombre": "Física I",
        "ects": 6,
    },
    "programacion-i": {
        "codigo": "programacion-i",
        "nombre": "Programación I",
        "ects": 6,
    },
    "tecnicas-experimentales": {
        "codigo": "tecnicas-experimentales",
        "nombre": "Técnicas experimentales y análisis de datos",
        "ects": 6,
    },
    "algebra-ii": {
        "codigo": "algebra-ii",
        "nombre": "Álgebra II",
        "ects": 6,
    },
    "analisis-ii": {
        "codigo": "analisis-ii",
        "nombre": "Análisis II",
        "ects": 6,
    },
    "fisica-ii": {
        "codigo": "fisica-ii",
        "nombre": "Física II",
        "ects": 6,
    },
    "estadistica": {
        "codigo": "estadistica",
        "nombre": "Estadística",
        "ects": 6,
    },
    "programacion-ii": {
        "codigo": "programacion-ii",
        "nombre": "Programación II",
        "ects": 6,
    },
}


@fisica_asignatura_bp.get("/<slug>/")
def index(slug: str) -> str:
    asignatura = ASIGNATURAS.get(slug)

    if asignatura is None:
        abort(404)

    return render_template(
        "subject.html",
        area="fisica",
        course="primero",
        subject=asignatura,
        subject_slug=slug,
    )