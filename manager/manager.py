from flask import Flask, jsonify, request
from flask_cors import CORS
from templates_routes import templates_blueprint
from auth_routes import auth_blueprint
from projects_routes import proyectos_blueprint
import os
import shutil
import tempfile
import subprocess
import docker

app = Flask(__name__)
CORS(app)
client = docker.from_env()

NGINX_CONF_DIR = os.environ.get("NGINX_CONF", "/nginx-conf/projects")
NETWORK_NAME = os.environ.get("DOCKER_NETWORK", "hosting_net")
IMAGE_PREFIX = "roble_proj_"
CONTAINER_PREFIX = "roble_proj_"
PROXY_CONTAINER = os.environ.get("PROXY_CONTAINER", "proxy")

# recursos por proyecto (pueden venir de .env)
PROJECT_CPU = float(os.environ.get("PROJECT_CPU", "0.5"))
PROJECT_MEM = os.environ.get("PROJECT_MEM", "512m")

os.makedirs(NGINX_CONF_DIR, exist_ok=True)

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

def write_nginx_conf(project_key, server_name, container_name):
	# escribe server block por proyecto en la carpeta montada
	conf = f"""server {{
    listen 80;
    server_name {server_name};

    location / {{
        proxy_pass http://{container_name}:80$request_uri;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}"""
	path = os.path.join(NGINX_CONF_DIR, f"{project_key}.conf")
	with open(path, "w") as f:
		f.write(conf)
	return path

def remove_nginx_conf(project_key):
	path = os.path.join(NGINX_CONF_DIR, f"{project_key}.conf")
	if os.path.exists(path):
		os.remove(path)

def reload_proxy():
	try:
		proxy = client.containers.get(PROXY_CONTAINER)
		res = proxy.exec_run(["nginx", "-s", "reload"])
		return res.exit_code == 0
	except Exception:
		return False

def build_and_run(project_key, image_tag, repo_url):
	tmpdir = tempfile.mkdtemp(prefix="roble_")
	try:
		subprocess.check_call(["git", "clone", repo_url, tmpdir])

		# detecta build de node o copia dist
		if os.path.exists(os.path.join(tmpdir, "package.json")):
			dockerfile = """FROM node:16 AS build
WORKDIR /app
COPY . .
RUN npm install --silent && npm run build --silent

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
"""
		else:
			src = "dist" if os.path.isdir(os.path.join(tmpdir, "dist")) else "."
			dockerfile = f"FROM nginx:alpine\nCOPY {src} /usr/share/nginx/html\n"

		with open(os.path.join(tmpdir, "Dockerfile"), "w") as f:
			f.write(dockerfile)

		image, _ = client.images.build(path=tmpdir, tag=image_tag)

		try:
			existing = client.containers.get(CONTAINER_PREFIX + project_key)
			existing.remove(force=True)
		except docker.errors.NotFound:
			pass

		nano_cpus = int(PROJECT_CPU * 1_000_000_000)

		container = client.containers.run(
			image=image_tag,
			name=CONTAINER_PREFIX + project_key,
			detach=True,
			network=NETWORK_NAME,
			restart_policy={"Name": "unless-stopped"},
			nano_cpus=nano_cpus,
			mem_limit=PROJECT_MEM
		)
		return container.id
	finally:
		shutil.rmtree(tmpdir, ignore_errors=True)

@app.route("/projects", methods=["POST"])
def create_project():
    data = request.get_json() or {}
    name = data.get("name")
    repo = data.get("repo")
    user = data.get("user", "user")
    if not name or not repo:
        return jsonify({"error": "name and repo required"}), 400
    project_key = f"{user}_{name}"
    container_name = CONTAINER_PREFIX + project_key
    image_tag = IMAGE_PREFIX + project_key
    server_name = f"{name}.{user}.localhost"
    try:
        client.containers.get(container_name)
        return jsonify({"error": "project already exists"}), 409
    except docker.errors.NotFound:
        pass
    try:
        build_and_run(project_key, image_tag, repo)
        write_nginx_conf(project_key, server_name, container_name)
        reload_proxy()
        return jsonify({"ok": True, "name": project_key, "server": server_name}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/projects/<project_key>", methods=["DELETE"])
def delete_project(project_key):
    container_name = CONTAINER_PREFIX + project_key
    image_tag = IMAGE_PREFIX + project_key
    try:
        try:
            cont = client.containers.get(container_name)
            cont.remove(force=True)
        except docker.errors.NotFound:
            pass
        try:
            client.images.remove(image=image_tag, force=True)
        except docker.errors.ImageNotFound:
            pass
        remove_nginx_conf(project_key)
        reload_proxy()
        return jsonify({"ok": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/projects/<project_key>/rebuild", methods=["POST"])
def rebuild_project(project_key):
    data = request.get_json() or {}
    repo = data.get("repo")
    if not repo:
        return jsonify({"error": "repo required"}), 400
    try:
        try:
            cont = client.containers.get(CONTAINER_PREFIX + project_key)
            cont.remove(force=True)
        except docker.errors.NotFound:
            pass
        build_and_run(project_key, IMAGE_PREFIX + project_key, repo)
        reload_proxy()
        return jsonify({"ok": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# NEW: importar el monitor y exponer endpoints para usar/verificar token
from activity_monitor import monitor as activity_monitor

# NEW endpoint: recibir token desde frontend y entregarlo al monitor
@app.route("/auth/use_token", methods=["POST"])
def use_token():
    data = request.get_json() or {}
    token = data.get("token")
    if not token:
        return jsonify({"error": "token required"}), 400
    try:
        activity_monitor.set_token(token)
        return jsonify({"ok": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# NEW endpoint: estado del monitor (útil para debug)
@app.route("/auth/monitor", methods=["GET"])
def monitor_status():
    try:
        status = {
            "running": getattr(activity_monitor, "running", False),
            "has_token": bool(getattr(activity_monitor, "token", None))
        }
        return jsonify(status), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
	return jsonify({"status": "manager running"})

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000)
