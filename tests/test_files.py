from io import BytesIO

from nuclear_sim.web.app import create_app
from nuclear_sim.web.file_storage import save_file
from werkzeug.datastructures import FileStorage


def test_download_file_returns_200(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "nuclear_sim.web.file_storage.BASE_STORAGE",
        tmp_path,
    )

    app = create_app()
    client = app.test_client()

    save_file(
        FileStorage(
            stream=BytesIO(b"contenido de prueba"),
            filename="documento.txt",
        ),
        "fisica",
        "cuarto",
        "astrofisica-cosmologia",
        "documentacion",
    )

    response = client.get(
        "/files/download",
        query_string={
            "area": "fisica",
            "course": "cuarto",
            "subject": "astrofisica-cosmologia",
            "category": "documentacion",
            "filename": "documento.txt",
        },
    )

    assert response.status_code == 200
    assert response.data == b"contenido de prueba"


def test_download_file_returns_404_for_missing_file(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "nuclear_sim.web.file_storage.BASE_STORAGE",
        tmp_path,
    )

    app = create_app()
    client = app.test_client()

    response = client.get(
        "/files/download",
        query_string={
            "area": "fisica",
            "course": "cuarto",
            "subject": "astrofisica-cosmologia",
            "category": "documentacion",
            "filename": "no-existe.txt",
        },
    )

    assert response.status_code == 404


def test_download_file_rejects_path_traversal(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "nuclear_sim.web.file_storage.BASE_STORAGE",
        tmp_path,
    )

    app = create_app()
    client = app.test_client()

    response = client.get(
        "/files/download",
        query_string={
            "area": "fisica",
            "course": "cuarto",
            "subject": "astrofisica-cosmologia",
            "category": "documentacion",
            "filename": "../../archivo.txt",
        },
    )

    assert response.status_code != 200

def test_download_file_cannot_access_file_outside_storage(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        "nuclear_sim.web.file_storage.BASE_STORAGE",
        tmp_path / "academic_files",
    )

    outside_file = tmp_path / "secret.txt"
    outside_file.write_bytes(b"contenido privado")

    app = create_app()
    client = app.test_client()

    response = client.get(
        "/files/download",
        query_string={
            "area": "fisica",
            "course": "cuarto",
            "subject": "astrofisica-cosmologia",
            "category": "documentacion",
            "filename": "../../secret.txt",
        },
    )

    assert response.status_code != 200
    assert response.data != b"contenido privado"

def test_view_txt_file_returns_content(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "nuclear_sim.web.file_storage.BASE_STORAGE",
        tmp_path,
    )

    app = create_app()
    client = app.test_client()

    save_file(
        FileStorage(
            stream=BytesIO(b"contenido del archivo"),
            filename="notas.txt",
        ),
        "fisica",
        "cuarto",
        "astrofisica-cosmologia",
        "documentacion",
    )

    response = client.get(
        "/files/view",
        query_string={
            "area": "fisica",
            "course": "cuarto",
            "subject": "astrofisica-cosmologia",
            "category": "documentacion",
            "filename": "notas.txt",
        },
    )

    assert response.status_code == 200
    assert b"contenido del archivo" in response.data


def test_view_missing_file_returns_404(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "nuclear_sim.web.file_storage.BASE_STORAGE",
        tmp_path,
    )

    app = create_app()
    client = app.test_client()

    response = client.get(
        "/files/view",
        query_string={
            "area": "fisica",
            "course": "cuarto",
            "subject": "astrofisica-cosmologia",
            "category": "documentacion",
            "filename": "no-existe.txt",
        },
    )

    assert response.status_code == 404


def test_view_file_cannot_access_file_outside_storage(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        "nuclear_sim.web.file_storage.BASE_STORAGE",
        tmp_path / "academic_files",
    )

    outside_file = tmp_path / "secret.txt"
    outside_file.write_bytes(b"contenido privado")

    app = create_app()
    client = app.test_client()

    response = client.get(
        "/files/view",
        query_string={
            "area": "fisica",
            "course": "cuarto",
            "subject": "astrofisica-cosmologia",
            "category": "documentacion",
            "filename": "../../secret.txt",
        },
    )

    assert response.status_code != 200
    assert b"contenido privado" not in response.data

def test_list_files_returns_files(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "nuclear_sim.web.file_storage.BASE_STORAGE",
        tmp_path,
    )

    app = create_app()
    client = app.test_client()

    save_file(
        FileStorage(
            stream=BytesIO(b"uno"),
            filename="uno.txt",
        ),
        "fisica",
        "cuarto",
        "astrofisica-cosmologia",
        "documentacion",
    )

    save_file(
        FileStorage(
            stream=BytesIO(b"dos"),
            filename="dos.txt",
        ),
        "fisica",
        "cuarto",
        "astrofisica-cosmologia",
        "documentacion",
    )

    response = client.get(
        "/files/list",
        query_string={
            "area": "fisica",
            "course": "cuarto",
            "subject": "astrofisica-cosmologia",
            "category": "documentacion",
        },
    )

    assert response.status_code == 200
    assert response.get_json() == ["dos.txt", "uno.txt"]


def test_list_files_requires_location_data():
    app = create_app()
    client = app.test_client()

    response = client.get("/files/list")

    assert response.status_code == 400


def test_upload_file_returns_success(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "nuclear_sim.web.file_storage.BASE_STORAGE",
        tmp_path,
    )

    app = create_app()
    client = app.test_client()

    response = client.post(
        "/files/upload",
        data={
            "area": "fisica",
            "course": "cuarto",
            "subject": "astrofisica-cosmologia",
            "category": "documentacion",
            "return_url": "/fisica/cuarto/astrofisica-cosmologia/",
            "file": (
                BytesIO(b"contenido"),
                "documentacion.txt",
            ),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/fisica/cuarto/astrofisica-cosmologia/"
    )

    saved_file = (
        tmp_path
        / "fisica"
        / "cuarto"
        / "astrofisica-cosmologia"
        / "documentacion"
        / "documentacion.txt"
    )

    assert saved_file.exists()
    assert saved_file.read_bytes() == b"contenido"


def test_delete_file_returns_success(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "nuclear_sim.web.file_storage.BASE_STORAGE",
        tmp_path,
    )

    app = create_app()
    client = app.test_client()

    save_file(
        FileStorage(
            stream=BytesIO(b"contenido"),
            filename="documentacion.txt",
        ),
        "fisica",
        "cuarto",
        "astrofisica-cosmologia",
        "documentacion",
    )

    response = client.post(
        "/files/delete",
        data={
            "area": "fisica",
            "course": "cuarto",
            "subject": "astrofisica-cosmologia",
            "category": "documentacion",
            "filename": "documentacion.txt",
            "return_url": "/fisica/cuarto/astrofisica-cosmologia/",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/fisica/cuarto/astrofisica-cosmologia/"
    )

    assert not (
        tmp_path
        / "fisica"
        / "cuarto"
        / "astrofisica-cosmologia"
        / "documentacion"
        / "documentacion.txt"
    ).exists()

def test_upload_file_rejects_invalid_extension(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "nuclear_sim.web.file_storage.BASE_STORAGE",
        tmp_path,
    )

    app = create_app()
    client = app.test_client()

    response = client.post(
        "/files/upload",
        data={
            "area": "fisica",
            "course": "cuarto",
            "subject": "astrofisica-cosmologia",
            "category": "documentacion",
            "return_url": "/fisica/cuarto/astrofisica-cosmologia/",
            "file": (
                BytesIO(b"contenido"),
                "malware.exe",
            ),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/fisica/cuarto/astrofisica-cosmologia/"
    )


def test_upload_file_without_location_returns_redirect():
    app = create_app()
    client = app.test_client()

    response = client.post(
        "/files/upload",
        data={
            "return_url": "/fisica/cuarto/",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/fisica/cuarto/")


def test_return_url_rejects_external_redirect():
    app = create_app()
    client = app.test_client()

    response = client.post(
        "/files/upload",
        data={
            "return_url": "//example.com",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_delete_missing_file_returns_redirect(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "nuclear_sim.web.file_storage.BASE_STORAGE",
        tmp_path,
    )

    app = create_app()
    client = app.test_client()

    response = client.post(
        "/files/delete",
        data={
            "area": "fisica",
            "course": "cuarto",
            "subject": "astrofisica-cosmologia",
            "category": "documentacion",
            "filename": "no-existe.txt",
            "return_url": "/fisica/cuarto/",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/fisica/cuarto/")