import os
from flask import Blueprint, jsonify, send_file
import zipfile
from io import BytesIO

templates_blueprint = Blueprint("templates", __name__)

# Templates permitidos
TEMPLATE_MAP = {
    "flask": "Aplicación Flask",
    "static_template": "Sitio Web Estático",
    "template_react": "Aplicación React"
}

# Extensiones permitidas
ALLOWED_EXT = {".html", ".js", ".css", ".json", ".py", ".yml", ".yaml", ".md", ".txt"}


def read_files_recursive(base_path):
    result = {}

    for root, _, files in os.walk(base_path):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext not in ALLOWED_EXT:
                continue

            full_path = os.path.join(root, file)

            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except:
                continue

            rel_path = os.path.relpath(full_path, base_path)
            result[rel_path] = content

    return result


@templates_blueprint.route("/api/templates", methods=["GET"])
def listar_templates():
    templates_dir = os.path.join(os.getcwd(), "templates")

    templates = []

    for folder_name, pretty_name in TEMPLATE_MAP.items():
        folder_path = os.path.join(templates_dir, folder_name)

        if not os.path.isdir(folder_path):
            continue

        files = read_files_recursive(folder_path)

        templates.append({
            "name": pretty_name,
            "folder": folder_name,
            "files": files
        })

    return jsonify({"templates": templates})


# Descargar template como ZIP
def zip_directory(folder_path):
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zip_file.write(file_path, arcname)

    zip_buffer.seek(0)
    return zip_buffer


@templates_blueprint.route("/api/templates/<template_folder>/download", methods=["GET"])
def descargar_template(template_folder):
    base_dir = os.path.join(os.getcwd(), "templates", template_folder)

    if not os.path.isdir(base_dir):
        return jsonify({"error": "Template no encontrado"}), 404

    zip_data = zip_directory(base_dir)

    return send_file(
        zip_data,
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"{template_folder}.zip"
    )
