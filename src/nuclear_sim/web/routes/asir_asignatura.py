from flask import Blueprint, abort, render_template


asir_asignatura_bp = Blueprint(
    "asir_asignatura",
    __name__,
    url_prefix="/asir/primero",
)


ASIGNATURAS = {
    "m00377": {
        "codigo": "M00377",
        "nombre": "Administración de sistemas gestores de bases de datos",
    },
    "m00374": {
        "codigo": "M00374",
        "nombre": "Administración de sistemas operativos",
    },
    "m00376": {
        "codigo": "M00376",
        "nombre": "Implantación de aplicaciones web",
    },
    "m00378": {
        "codigo": "M00378",
        "nombre": "Seguridad y alta disponibilidad",
    },
    "m00375": {
        "codigo": "M00375",
        "nombre": "Servicios de red e internet",
    },
    "m00179": {
        "codigo": "M00179",
        "nombre": "Inglés profesional (GS)",
    },
    "m01710": {
        "codigo": "M01710",
        "nombre": "Itinerario personal para la empleabilidad II",
    },
    "m01665": {
        "codigo": "M01665",
        "nombre": "Digitalización aplicada a los sectores productivos (GS)",
    },
    "m01708": {
        "codigo": "M01708",
        "nombre": "Sostenibilidad aplicada al sistema productivo",
    },
    "mocmo-ii": {
        "codigo": "MOCMO II",
        "nombre": "Módulo profesional optativo II - Ciberseguridad",
    },
    "m00379": {
        "codigo": "M00379",
        "nombre": "Proyecto intermodular de administración de sistemas informáticos en red",
    },
}


@asir_asignatura_bp.get("/<slug>/")
def index(slug: str) -> str:
    asignatura = ASIGNATURAS.get(slug)

    if asignatura is None:
        abort(404)

    return render_template(
        "subject.html",
        area="asir",
        course="primero",
        subject=asignatura,
        subject_slug=slug,
    )