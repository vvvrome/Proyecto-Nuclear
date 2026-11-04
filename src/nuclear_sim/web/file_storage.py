from pathlib import Path
import re

from werkzeug.utils import secure_filename


BASE_STORAGE = Path("data/academic_files")

ALLOWED_EXTENSIONS = {
    "pdf",
    "doc",
    "docx",
    "ppt",
    "pptx",
    "xls",
    "xlsx",
    "txt",
    "png",
    "jpg",
    "jpeg",
    "zip",
}

IDENTIFIER_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def is_allowed_file(filename: str) -> bool:
    if "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS


def _validate_identifier(value: str) -> str:
    if not isinstance(value, str) or not IDENTIFIER_PATTERN.fullmatch(value):
        raise ValueError("Identificador de ruta no válido")

    return value


def get_storage_path(
    area: str,
    course: str,
    subject: str,
    category: str,
) -> Path:
    area = _validate_identifier(area)
    course = _validate_identifier(course)
    subject = _validate_identifier(subject)
    category = _validate_identifier(category)

    path = BASE_STORAGE / area / course / subject / category
    path.mkdir(parents=True, exist_ok=True)

    return path


def save_file(
    file,
    area: str,
    course: str,
    subject: str,
    category: str,
) -> str:
    filename = secure_filename(file.filename)

    if not filename:
        raise ValueError("Nombre de archivo no válido")

    if not is_allowed_file(filename):
        raise ValueError("Tipo de archivo no permitido")

    storage_path = get_storage_path(
        area,
        course,
        subject,
        category,
    )

    file.save(storage_path / filename)

    return filename


def list_files(
    area: str,
    course: str,
    subject: str,
    category: str,
) -> list[str]:
    storage_path = get_storage_path(
        area,
        course,
        subject,
        category,
    )

    return sorted(
        file.name
        for file in storage_path.iterdir()
        if file.is_file()
    )


def delete_file(
    area: str,
    course: str,
    subject: str,
    category: str,
    filename: str,
) -> None:
    filename = secure_filename(filename)

    if not filename:
        raise ValueError("Nombre de archivo no válido")

    storage_path = get_storage_path(
        area,
        course,
        subject,
        category,
    )

    file_path = storage_path / filename

    if not file_path.exists() or not file_path.is_file():
        raise FileNotFoundError("El archivo no existe")

    file_path.unlink()
