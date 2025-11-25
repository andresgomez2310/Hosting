from flask import Flask, jsonify
from flask_cors import CORS
from templates_routes import templates_blueprint
from auth_routes import auth_blueprint
from projects_routes import proyectos_blueprint
import os

app = Flask(__name__)
CORS(app)

# Registrar blueprints
app.register_blueprint(auth_blueprint, url_prefix="/auth")
app.register_blueprint(proyectos_blueprint, url_prefix="/projects")
app.register_blueprint(templates_blueprint)

@app.get("/")
def home():
    return {"message": "Hosting Manager API running"}

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "message": "Manager funcionando correctamente"
    }



# 🎨 Nombres bonitos
TEMPLATE_INFO = {
    "flask": {
        "title": "Aplicación Flask",
        "description": "Template base para aplicaciones Python usando Flask.",
        "allowed": [
            "Dockerfile",
            "docker-compose.yml",
            "app.py",
            "requirements.txt"
        ]
    },
    "static_template": {
        "title": "Sitio Web Estático",
        "description": "Template HTML/CSS/JS sencillo.",
        "allowed": [
            "Dockerfile",
            "docker-compose.yml",
            "index.html"
        ]
    },
    "template_react": {
        "title": "Aplicación React",
        "description": "Template de aplicación creada con React.",
        "allowed": [
            "Dockerfile",
            "package.json",
            "package-lock.json",
            "public/index.html",
            "src/App.js",
            "src/App.css",
            "src/index.js",
            "src/index.css"
        ]
    }
}

VALID_TEMPLATES = list(TEMPLATE_INFO.keys())


@app.route("/api/templates", methods=["GET"])
def get_templates():

    base_path = "/app/templates"
    result = []

    for folder in VALID_TEMPLATES:
        template_path = os.path.join(base_path, folder)
        template = TEMPLATE_INFO[folder]

        files = {}

        # Recorrer archivos permitidos únicamente
        for allowed in template["allowed"]:
            abs_path = os.path.join(template_path, allowed)

            if not os.path.exists(abs_path):
                continue

            try:
                with open(abs_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except:
                content = "(Archivo binario o ilegible)"

            files[allowed] = content

        result.append({
            "id": folder,
            "title": template["title"],
            "description": template["description"],
            "files": files
        })

    return jsonify({"templates": result})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
