from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)

from nuclear_sim.web.file_storage import (
    delete_file,
    get_storage_path,
    list_files,
    save_file,
)


files_bp = Blueprint(
    "files",
    __name__,
    url_prefix="/files",
)


def _redirect_to_return_url(default_endpoint="dashboard.index"):
    return_url = request.form.get("return_url")

    if return_url and return_url.startswith("/") and not return_url.startswith("//"):
        return redirect(return_url)

    return redirect(url_for(default_endpoint))


@files_bp.post("/upload")
def upload_file():
    uploaded_file = request.files.get("file")

    area = request.form.get("area")
    course = request.form.get("course")
    subject = request.form.get("subject")
    category = request.form.get("category")

    if uploaded_file is None:
        return _redirect_to_return_url()

    if not all([area, course, subject, category]):
        flash("Faltan datos de ubicación.", "error")
        return _redirect_to_return_url()

    try:
        save_file(
            uploaded_file,
            area,
            course,
            subject,
            category,
        )
    except ValueError as error:
        flash(str(error), "error")
        return _redirect_to_return_url()

    flash("Archivo subido correctamente.", "success")

    return _redirect_to_return_url()


@files_bp.get("/list")
def get_file_list():
    area = request.args.get("area")
    course = request.args.get("course")
    subject = request.args.get("subject")
    category = request.args.get("category")

    if not all([area, course, subject, category]):
        return jsonify({"error": "Faltan datos de ubicación"}), 400

    files = list_files(
        area,
        course,
        subject,
        category,
    )

    return jsonify(files)


@files_bp.get("/download")
def download_file():
    area = request.args.get("area")
    course = request.args.get("course")
    subject = request.args.get("subject")
    category = request.args.get("category")
    filename = request.args.get("filename")

    if not all([area, course, subject, category, filename]):
        return "Faltan datos del archivo", 400

    storage_path = get_storage_path(
        area,
        course,
        subject,
        category,
    )

    file_path = storage_path / filename

    if not file_path.exists() or not file_path.is_file():
        return "Archivo no encontrado", 404

    return send_file(
        file_path.resolve(),
        as_attachment=True,
        download_name=filename,
    )


@files_bp.get("/view")
def view_file():
    area = request.args.get("area")
    course = request.args.get("course")
    subject = request.args.get("subject")
    category = request.args.get("category")
    filename = request.args.get("filename")

    if not all([area, course, subject, category, filename]):
        return "Faltan datos del archivo", 400

    storage_path = get_storage_path(
        area,
        course,
        subject,
        category,
    )

    file_path = storage_path / filename

    if not file_path.exists() or not file_path.is_file():
        return "Archivo no encontrado", 404

    extension = file_path.suffix.lower()

    if extension == ".txt":
        content = file_path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        return render_template(
            "file_viewer.html",
            filename=filename,
            content=content,
            file_type="text",
        )

    if extension == ".pdf":
        return send_file(
            file_path.resolve(),
            as_attachment=False,
        )

    if extension in {".png", ".jpg", ".jpeg"}:
        return send_file(
            file_path.resolve(),
            as_attachment=False,
        )

    return send_file(
        file_path.resolve(),
        as_attachment=True,
        download_name=filename,
    )


@files_bp.post("/delete")
def delete_uploaded_file():
    area = request.form.get("area")
    course = request.form.get("course")
    subject = request.form.get("subject")
    category = request.form.get("category")
    filename = request.form.get("filename")

    if not all([area, course, subject, category, filename]):
        flash("Faltan datos del archivo.", "error")
        return _redirect_to_return_url()

    try:
        delete_file(
            area,
            course,
            subject,
            category,
            filename,
        )
    except (ValueError, FileNotFoundError) as error:
        flash(str(error), "error")
        return _redirect_to_return_url()

    flash("Archivo eliminado correctamente.", "success")

    return _redirect_to_return_url()