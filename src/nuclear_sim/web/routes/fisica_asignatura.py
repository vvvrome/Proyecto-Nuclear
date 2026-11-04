from flask import Blueprint, abort, render_template


fisica_asignatura_bp = Blueprint(
    "fisica_asignatura",
    __name__,
    url_prefix="/fisica",
)


ASIGNATURAS = {
    "primero": {
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
    },
    "segundo": {
        "mecanica-y-ondas-i": {
            "codigo": "mecanica-y-ondas-i",
            "nombre": "Mecánica y Ondas I",
            "ects": 6,
        },
        "variable-compleja": {
            "codigo": "variable-compleja",
            "nombre": "Variable Compleja",
            "ects": 6,
        },
        "electromagnetismo-i": {
            "codigo": "electromagnetismo-i",
            "nombre": "Electromagnetismo I",
            "ects": 6,
        },
        "analisis-multivariante": {
            "codigo": "analisis-multivariante",
            "nombre": "Análisis Multivariante",
            "ects": 6,
        },
        "termodinamica": {
            "codigo": "termodinamica",
            "nombre": "Termodinámica",
            "ects": 6,
        },
        "mecanica-y-ondas-ii": {
            "codigo": "mecanica-y-ondas-ii",
            "nombre": "Mecánica y Ondas II",
            "ects": 6,
        },
        "ecuaciones-diferenciales": {
            "codigo": "ecuaciones-diferenciales",
            "nombre": "Ecuaciones diferenciales",
            "ects": 6,
        },
        "electromagnetismo-ii": {
            "codigo": "electromagnetismo-ii",
            "nombre": "Electromagnetismo II",
            "ects": 6,
        },
        "metodos-numericos": {
            "codigo": "metodos-numericos",
            "nombre": "Métodos Numéricos",
            "ects": 6,
        },
        "optica": {
            "codigo": "optica",
            "nombre": "Óptica",
            "ects": 6,
        },
    },
    "tercero": {
        "fisica-cuantica-i": {
            "codigo": "fisica-cuantica-i",
            "nombre": "Física Cuántica I",
            "ects": 6,
        },
        "base-de-datos": {
            "codigo": "base-de-datos",
            "nombre": "Base de Datos",
            "ects": 6,
        },
        "electronica": {
            "codigo": "electronica",
            "nombre": "Electrónica",
            "ects": 6,
        },
        "analisis-funcional": {
            "codigo": "analisis-funcional",
            "nombre": "Análisis Funcional",
            "ects": 6,
        },
        "fisica-estadistica": {
            "codigo": "fisica-estadistica",
            "nombre": "Física Estadística",
            "ects": 6,
        },
        "modelizacion-problemas-fisicos": {
            "codigo": "modelizacion-problemas-fisicos",
            "nombre": "Modelización de problemas físicos",
            "ects": 6,
        },
        "fundamentos-computacion-cuantica": {
            "codigo": "fundamentos-computacion-cuantica",
            "nombre": "Fundamentos de Computación Cuántica",
            "ects": 6,
        },
        "fisica-cuantica-ii": {
            "codigo": "fisica-cuantica-ii",
            "nombre": "Física Cuántica II",
            "ects": 6,
        },
        "estructura-de-la-materia": {
            "codigo": "estructura-de-la-materia",
            "nombre": "Estructura de la materia",
            "ects": 6,
        },
        "fisica-del-estado-solido": {
            "codigo": "fisica-del-estado-solido",
            "nombre": "Física del Estado Sólido",
            "ects": 6,
        },
    },
    "cuarto": {
        "ciencia-de-datos": {
            "codigo": "ciencia-de-datos",
            "nombre": "Ciencia de Datos",
            "ects": 6,
            "tipo": "obligatoria",
        },
        "mineria-de-datos": {
            "codigo": "mineria-de-datos",
            "nombre": "Minería de Datos",
            "ects": 6,
            "tipo": "obligatoria",
        },
        "introduccion-inteligencia-artificial": {
            "codigo": "introduccion-inteligencia-artificial",
            "nombre": "Introducción a la Inteligencia Artificial",
            "ects": 6,
            "tipo": "obligatoria",
        },
        "fisica-atomica-y-molecular": {
            "codigo": "fisica-atomica-y-molecular",
            "nombre": "Física Atómica y Molecular",
            "ects": 6,
            "tipo": "obligatoria",
        },
        "mecanica-cuantica": {
            "codigo": "mecanica-cuantica",
            "nombre": "Mecánica Cuántica",
            "ects": 6,
            "tipo": "obligatoria",
        },
        "practicas-academicas-externas-i": {
            "codigo": "practicas-academicas-externas-i",
            "nombre": "Prácticas Académicas Externas I",
            "ects": 6,
            "tipo": "practicas",
        },
        "introduccion-machine-learning": {
            "codigo": "introduccion-machine-learning",
            "nombre": "Introducción al Machine Learning",
            "ects": 6,
            "tipo": "optativa",
        },
        "metodologia-agile": {
            "codigo": "metodologia-agile",
            "nombre": "Metodología Agile para gestión de proyectos",
            "ects": 6,
            "tipo": "optativa",
        },
        "algoritmos-programacion-computacion-cuantica": {
            "codigo": "algoritmos-programacion-computacion-cuantica",
            "nombre": "Algoritmos y Programación en Computación Cuántica",
            "ects": 6,
            "tipo": "optativa",
        },
        "practicas-academicas-externas-ii": {
            "codigo": "practicas-academicas-externas-ii",
            "nombre": "Prácticas Académicas Externas II",
            "ects": 6,
            "tipo": "optativa_practicas",
        },
        "fisica-tierra-atmosfera": {
            "codigo": "fisica-tierra-atmosfera",
            "nombre": "Física de la Tierra y la Atmósfera",
            "ects": 6,
            "tipo": "optativa",
        },
        "astrofisica-cosmologia": {
            "codigo": "astrofisica-cosmologia",
            "nombre": "Astrofísica y Cosmología",
            "ects": 6,
            "tipo": "optativa",
        },
        "tecnologia-energia": {
            "codigo": "tecnologia-energia",
            "nombre": "Tecnología de la Energía",
            "ects": 6,
            "tipo": "optativa",
        },
        "big-data": {
            "codigo": "big-data",
            "nombre": "Big Data",
            "ects": 6,
            "tipo": "optativa",
        },
        "trabajo-fin-de-grado": {
            "codigo": "trabajo-fin-de-grado",
            "nombre": "Trabajo Fin de Grado",
            "ects": 6,
            "tipo": "tfg",
        },
    },
}


@fisica_asignatura_bp.get("/<curso>/<slug>/")
def index(curso: str, slug: str) -> str:
    cursos_validos = ASIGNATURAS.get(curso)

    if cursos_validos is None:
        abort(404)

    asignatura = cursos_validos.get(slug)

    if asignatura is None:
        abort(404)

    return render_template(
        "subject.html",
        area="fisica",
        course=curso,
        subject=asignatura,
        subject_slug=slug,
    )