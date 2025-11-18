"""
Rutas para la gestión de proyectos y control de contenedores.
Integran creación, consulta y manejo de contenedores Docker asociados.
"""

from flask import Blueprint, request, jsonify
from roble_client import RobleClient
import logging
import subprocess
import requests
import os

proyectos_blueprint = Blueprint("projects", __name__)
logger = logging.getLogger(__name__)

roble = RobleClient()


# =============================================================
# ==================== OBTENER TOKEN ===========================
# =============================================================

def get_token():
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return None
    return auth.split(" ")[1]


# =============================================================
# ======= OBTENER USER_ID REAL DESDE ROBLE (CORREGIDO) =========
# =============================================================

def get_user_id_from_token(token):
    """
    Roble NO usa /me, usa /verify-token.
    """

    base = os.getenv("ROBLE_URL", "https://roble-api.openlab.uninorte.edu.co")
    contract = os.getenv("ROBLE_CONTRACT", "hosting_adcce8f544")

    url = f"{base}/auth/{contract}/verify-token"

    try:
        r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
        if r.status_code != 200:
            logger.error(f"verify-token error: {r.text}")
            return None

        data = r.json().get("user", {})

        # Roble puede devolver "id" o "_id"
        return data.get("id") or data.get("_id") or None

    except Exception as e:
        logger.error(f"Error en verify-token: {e}")
        return None


# =============================================================
# ==================== CREAR PROYECTO ==========================
# =============================================================

@proyectos_blueprint.route("/create", methods=["POST"])
def crear_proyecto():
    try:
        token = get_token()
        if not token:
            return jsonify({"error": "Token requerido"}), 401

        data = request.get_json()
        nombre = data.get("nombre")
        repo = data.get("repo_url")

        if not nombre or not repo:
            return jsonify({"error": "Faltan campos requeridos"}), 400

        # Obtener ID del usuario desde Roble (corregido)
        user_id = get_user_id_from_token(token)
        if not user_id:
            return jsonify({"error": "Token inválido"}), 401

        proyecto = roble.create_project(user_id, nombre, repo, token)

        return jsonify({
            "success": True,
            "project": proyecto
        }), 201

    except Exception as e:
        logger.error(f"Error creando proyecto: {e}")
        return jsonify({"error": "Error creando proyecto"}), 400


# =============================================================
# ==================== LISTAR PROYECTOS ========================
# =============================================================

@proyectos_blueprint.route("/mine", methods=["GET"])
def mis_proyectos():
    try:
        token = get_token()
        if not token:
            return jsonify({"error": "Token requerido"}), 401

        user_id = get_user_id_from_token(token)
        if not user_id:
            return jsonify({"error": "Token inválido"}), 401

        proyectos = roble.get_user_projects(user_id, token)

        return jsonify({"projects": proyectos}), 200

    except Exception as e:
        logger.error(f"Error al listar proyectos: {e}")
        return jsonify({"error": "Error obteniendo proyectos"}), 400


# =============================================================
# ==================== DETALLE DE PROYECTO =====================
# =============================================================

@proyectos_blueprint.route("/<project_id>", methods=["GET"])
def obtener_proyecto(project_id):
    try:
        token = get_token()
        if not token:
            return jsonify({"error": "Token requerido"}), 401

        proyecto = roble.read_records(
            "proyectos",
            filters={"_id": project_id},
            access_token=token
        )

        if not proyecto:
            return jsonify({"error": "Proyecto no encontrado"}), 404

        return jsonify({"project": proyecto[0]}), 200

    except Exception as e:
        logger.error(f"Error consultando proyecto: {e}")
        return jsonify({"error": "Error consultando proyecto"}), 400


# =============================================================
# =============== FUNCIONES AUXILIARES CONTENEDORES ============
# =============================================================

def get_container(project_id, token):
    container = roble.read_records(
        "containers",
        filters={"project_id": project_id},
        access_token=token
    )
    return container[0] if container else None


# =============================================================
# ==================== INICIAR CONTENEDOR ======================
# =============================================================

@proyectos_blueprint.route("/start/<project_id>", methods=["POST"])
def start_container(project_id):
    try:
        token = get_token()
        if not token:
            return jsonify({"error": "Token requerido"}), 401

        container = get_container(project_id, token)
        if not container:
            return jsonify({"error": "Contenedor no encontrado"}), 404

        cid = container.get("container_id")

        subprocess.check_call(["docker", "start", cid])

        roble.update_project_status(project_id, "running", cid, token)

        return jsonify({"success": True, "message": "Contenedor iniciado"}), 200

    except subprocess.CalledProcessError:
        return jsonify({"error": "Error iniciando contenedor (Docker)"}), 500

    except Exception as e:
        return jsonify({"error": f"No se pudo iniciar: {e}"}), 400


# =============================================================
# ===================== DETENER CONTENEDOR =====================
# =============================================================

@proyectos_blueprint.route("/stop/<project_id>", methods=["POST"])
def stop_container(project_id):
    try:
        token = get_token()
        if not token:
            return jsonify({"error": "Token requerido"}), 401

        container = get_container(project_id, token)
        if not container:
            return jsonify({"error": "Contenedor no encontrado"}), 404

        cid = container.get("container_id")

        subprocess.check_call(["docker", "stop", cid])

        roble.update_project_status(project_id, "stopped", cid, token)

        return jsonify({"success": True, "message": "Contenedor detenido"}), 200

    except subprocess.CalledProcessError:
        return jsonify({"error": "Error deteniendo contenedor"}), 500

    except Exception as e:
        return jsonify({"error": f"No se pudo detener: {e}"}), 400


# =============================================================
# ===================== REINICIAR CONTENEDOR ===================
# =============================================================

@proyectos_blueprint.route("/restart/<project_id>", methods=["POST"])
def restart_container(project_id):
    try:
        token = get_token()
        if not token:
            return jsonify({"error": "Token requerido"}), 401

        container = get_container(project_id, token)
        if not container:
            return jsonify({"error": "Contenedor no encontrado"}), 404

        cid = container.get("container_id")

        subprocess.check_call(["docker", "restart", cid])

        roble.update_project_status(project_id, "running", cid, token)

        return jsonify({"success": True, "message": "Contenedor reiniciado"}), 200

    except subprocess.CalledProcessError:
        return jsonify({"error": "Error reiniciando contenedor"}), 500

    except Exception as e:
        return jsonify({"error": f"No se pudo reiniciar: {e}"}), 400


# =============================================================
# ======================= LOGS CONTENEDOR ======================
# =============================================================

@proyectos_blueprint.route("/logs/<project_id>", methods=["GET"])
def container_logs(project_id):
    try:
        token = get_token()
        if not token:
            return jsonify({"error": "Token requerido"}), 401

        container = get_container(project_id, token)
        if not container:
            return jsonify({"error": "Contenedor no encontrado"}), 404

        cid = container.get("container_id")

        logs = subprocess.check_output(["docker", "logs", cid], text=True)

        return jsonify({
            "success": True,
            "logs": logs
        }), 200

    except subprocess.CalledProcessError:
        return jsonify({"error": "Error obteniendo logs"}), 500

    except Exception as e:
        return jsonify({"error": f"No se pudieron obtener logs: {e}"}), 400
