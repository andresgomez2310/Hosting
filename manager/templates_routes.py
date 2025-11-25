from flask import Blueprint, jsonify
import os

# Crear el blueprint para los templates
templates_bp = Blueprint('templates_bp', __name__)

# Ruta para obtener los templates
@templates_bp.route('/api/templates', methods=['GET'])
def get_templates():
    # Definir las rutas de los templates en tu proyecto
    templates = [
        {
            "name": "Template React",
            "description": "Template React básico, usa CDN",
            "url": "/templates/template_react",  # Ruta donde estará el template React
            "code": read_template_code("template_react/public/index.html")  # Leer el código de index.html para React
        },
        {
            "name": "Template Flask",
            "description": "Template Flask para backend con Python",
            "url": "/templates/flask",  # Ruta donde estará el template Flask
            "code": read_template_code("flask/app.py")  # Leer el código de app.py para Flask
        },
        {
            "name": "Template Estático",
            "description": "Template HTML estático con Nginx",
            "url": "/templates/static_template",  # Ruta donde estará el template Estático
            "code": read_template_code("static_template/index.html")  # Leer el código de index.html para Estático
        }
    ]
    
    return jsonify({"templates": templates})


def read_template_code(file_path):
    try:
        # Abrir y leer el archivo del template
        with open(os.path.join("templates", file_path), "r") as file:
            return file.read()  # Retornar el contenido del archivo como string
    except FileNotFoundError:
        return "Archivo no encontrado"  # Manejar si no se encuentra el archivo
