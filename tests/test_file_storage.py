from io import BytesIO

import pytest
from werkzeug.datastructures import FileStorage
from nuclear_sim.web.file_storage import (
    delete_file,
    get_storage_path,
    is_allowed_file,
    list_files,
    save_file,
)


def test_allowed_file_extension():
    assert is_allowed_file("apuntes.pdf")
    assert is_allowed_file("documento.docx")
    assert is_allowed_file("datos.xlsx")


def test_disallowed_file_extension():
    assert not is_allowed_file("archivo.exe")
    assert not is_allowed_file("script.py")


def test_get_storage_path_creates_directory(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "nuclear_sim.web.file_storage.BASE_STORAGE",
        tmp_path,
    )

    path = get_storage_path(
        "fisica",
        "primero",
        "algebra-i",
        "apuntes",
    )

    assert path.exists()
    assert path.is_dir()


def test_save_file(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "nuclear_sim.web.file_storage.BASE_STORAGE",
        tmp_path,
    )

    file = FileStorage(
        stream=BytesIO(b"contenido de prueba"),
        filename="apuntes.pdf",
    )

    filename = save_file(
        file,
        "fisica",
        "primero",
        "algebra-i",
        "apuntes",
    )

    assert filename == "apuntes.pdf"

    saved_file = (
        tmp_path
        / "fisica"
        / "primero"
        / "algebra-i"
        / "apuntes"
        / "apuntes.pdf"
    )

    assert saved_file.exists()
    assert saved_file.read_bytes() == b"contenido de prueba"


def test_save_file_rejects_invalid_extension(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "nuclear_sim.web.file_storage.BASE_STORAGE",
        tmp_path,
    )

    file = FileStorage(
        stream=BytesIO(b"contenido"),
        filename="malware.exe",
    )

    with pytest.raises(ValueError):
        save_file(
            file,
            "fisica",
            "primero",
            "algebra-i",
            "apuntes",
        )


def test_list_files(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "nuclear_sim.web.file_storage.BASE_STORAGE",
        tmp_path,
    )

    file = FileStorage(
        stream=BytesIO(b"uno"),
        filename="uno.pdf",
    )

    save_file(
        file,
        "fisica",
        "primero",
        "algebra-i",
        "apuntes",
    )

    file = FileStorage(
        stream=BytesIO(b"dos"),
        filename="dos.pdf",
    )

    save_file(
        file,
        "fisica",
        "primero",
        "algebra-i",
        "apuntes",
    )

    files = list_files(
        "fisica",
        "primero",
        "algebra-i",
        "apuntes",
    )

    assert files == ["dos.pdf", "uno.pdf"]

def test_delete_file(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "nuclear_sim.web.file_storage.BASE_STORAGE",
        tmp_path,
    )

    file = FileStorage(
        stream=BytesIO(b"contenido"),
        filename="apuntes.pdf",
    )

    save_file(
        file,
        "fisica",
        "primero",
        "algebra-i",
        "apuntes",
    )

    delete_file(
        "fisica",
        "primero",
        "algebra-i",
        "apuntes",
        "apuntes.pdf",
    )

    files = list_files(
        "fisica",
        "primero",
        "algebra-i",
        "apuntes",
    )

    assert files == []

def test_get_storage_path_rejects_path_traversal():
    with pytest.raises(ValueError):
        get_storage_path(
            "../fisica",
            "primero",
            "algebra-i",
            "resumen",
        )


def test_get_storage_path_rejects_invalid_identifier():
    with pytest.raises(ValueError):
        get_storage_path(
            "fisica",
            "primero",
            "algebra_i",
            "resumen",
        )


def test_get_storage_path_rejects_uppercase_identifier():
    with pytest.raises(ValueError):
        get_storage_path(
            "Fisica",
            "primero",
            "algebra-i",
            "resumen",
        )


def test_get_storage_path_rejects_nested_path():
    with pytest.raises(ValueError):
        get_storage_path(
            "fisica",
            "../primero",
            "algebra-i",
            "resumen",
        )
