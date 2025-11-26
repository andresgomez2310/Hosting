from flask import Flask, jsonify, send_from_directory, abort
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
        ],
        "repo": "https://github.com/Znake-G/flask-template.git"
    },
    "static_template": {
        "title": "Sitio Web Estático",
        "description": "Template HTML/CSS/JS sencillo.",
        "allowed": [
            "Dockerfile",
            "docker-compose.yml",
            "index.html"
        ],
        "repo": "https://github.com/Znake-G/static-template.git"
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
        ],
        "repo": "https://github.com/Znake-G/react_template.git"
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


# Preview estático de templates (sin docker extra)
@app.route("/preview/<folder>/", defaults={"path": "index.html"})
@app.route("/preview/<folder>/<path:path>")
def preview_template(folder, path):
	"""
	Serve a preview for a template folder located at manager/templates/<folder>/
	Search order: build, dist, public, root. If requested file exists serve it,
	otherwise return index.html (SPA support). If no index.html found, render
	a minimal HTML listing files + repo link.
	"""
	base_dir = os.path.join(os.path.dirname(__file__), "templates", folder)
	candidates = ["build", "dist", "public", ""]  # order to check
	for c in candidates:
		root = os.path.join(base_dir, c) if c else base_dir
		index_file = os.path.join(root, "index.html")
		if os.path.isdir(root) and os.path.exists(index_file):
			# if requested path exists, serve it; else serve index.html
			requested = os.path.join(root, path)
			if os.path.exists(requested) and os.path.isfile(requested):
				return send_from_directory(root, path)
			return send_from_directory(root, "index.html")

	# Si llegamos aquí: no hay index en los lugares esperados.
	# Si el folder existe, listar archivos y mostrar enlace al repo si existe.
	if os.path.isdir(base_dir):
		# construir listado simple
		items = []
		for root_dir, dirs, files in os.walk(base_dir):
			rel = os.path.relpath(root_dir, base_dir)
			for f in files:
				items.append(os.path.join(rel if rel != "." else "", f))
		# obtener repo si está definido en TEMPLATE_INFO
		repo = TEMPLATE_INFO.get(folder, {}).get("repo", "")
		html = ["<html><head><meta charset='utf-8'><title>Preview - {}</title></head><body>".format(folder)]
		html.append("<h1>Preview mínimo: {}</h1>".format(folder))
		if repo:
			html.append('<p>Repo: <a href="{}" target="_blank" rel="noopener noreferrer">{}</a></p>'.format(repo, repo))
		if items:
			html.append("<h3>Archivos:</h3><ul>")
			for it in sorted(items):
				html.append("<li>{}</li>".format(it))
			html.append("</ul>")
		else:
			html.append("<p>No hay archivos detectados en este template.</p>")
		html.append("</body></html>")
		return ("".join(html), 200, {"Content-Type": "text/html; charset=utf-8"})

	# no se encontró el template
	abort(404)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
