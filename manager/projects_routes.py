"""
Rutas para gestión de proyectos y contenedores.
"""

from flask import Blueprint, request, jsonify
from roble_client import RobleClient

import logging
import subprocess
import requests
import os
from datetime import datetime
from activity_monitor import monitor  # ← el token ahora viene del monitor

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

proyectos_blueprint = Blueprint("projects", __name__)
logger = logging.getLogger(__name__)

roble = RobleClient()


# =============================================================
#   TOKEN GLOBAL DEL MANAGER — SIEMPRE VIENE DEL MONITOR
# =============================================================

def get_manager_token():
    token = monitor.token
    if not token:
        logger.error("❌ No hay token activo en el Manager.")
    return token


# =============================================================
#   OBTENER USER_ID REAL DESDE TOKEN
# =============================================================

def get_user_id():
    token = get_manager_token()
    if not token:
        return None

    base = os.getenv("ROBLE_URL", "https://roble-api.openlab.uninorte.edu.co")
    contract = os.getenv("ROBLE_CONTRACT", "pc2_394e10a6d2")   # ⚡ tu contrato correcto

    url = f"{base}/auth/{contract}/verify-token"

    try:
        r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
        if r.status_code != 200:
            logger.error(f"verify-token error: {r.text}")
            return None

        data = r.json().get("user", {})
        return data.get("id") or data.get("_id")

    except Exception as e:
        logger.error(f"Error verificando token: {e}")
        return None


# =============================================================
#   CREAR PROYECTO
# =============================================================

@proyectos_blueprint.route("/create", methods=["POST"])
def crear_proyecto():
    token = get_manager_token()
    if not token:
        return jsonify({"error": "Token requerido"}), 401

    data = request.get_json()
    nombre = data.get("nombre")
    repo = data.get("repo_url")

    if not nombre or not repo:
        return jsonify({"error": "Faltan campos requeridos"}), 400

    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "Token inválido"}), 401

    nuevo_registro = {
        "user_id": user_id,
        "nombre": nombre,
        "repo_url": repo,
        "status": "pending",
        "container_id": None,
        "created_at": datetime.utcnow().isoformat(),
        "last_access": datetime.utcnow().isoformat()
    }

    proyecto = roble.create_record("proyectos", nuevo_registro, token)

    return jsonify({"success": True, "project": proyecto}), 201


# =============================================================
#   LISTAR PROYECTOS DEL USUARIO
# =============================================================

@proyectos_blueprint.route("/mine", methods=["GET"])
def mis_proyectos():
    token = get_manager_token()
    if not token:
        return jsonify({"error": "Token requerido"}), 401

    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "Token inválido"}), 401

    proyectos = roble.read_records(
        "proyectos",
        filters={"user_id": user_id},
        access_token=token
    )

    return jsonify({"projects": proyectos}), 200


# =============================================================
#   OBTENER PROYECTO POR ID
# =============================================================

@proyectos_blueprint.route("/<project_id>", methods=["GET"])
def get_project(project_id):
    token = get_manager_token()
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


# =============================================================
#   OBTENER CONTENEDOR ASOCIADO
# =============================================================

def get_container(project_id, token):
    cont = roble.read_records(
        "containers",
        filters={"project_id": project_id},
        access_token=token
    )
    return cont[0] if cont else None


# =============================================================
#   START CONTAINER
# =============================================================

@proyectos_blueprint.route("/start/<project_id>", methods=["POST"])
def start_container(project_id):
    token = get_manager_token()
    if not token:
        return jsonify({"error": "Token requerido"}), 401

    container = get_container(project_id, token)
    if not container:
        return jsonify({"error": "Contenedor no encontrado"}), 404

    cid = container["container_id"]

    try:
        subprocess.check_call(["docker", "start", cid])

        roble.update_record(
            "proyectos",
            project_id,
            {"status": "running"},
            token
        )

        return jsonify({"success": True, "message": "Contenedor iniciado"}), 200

    except Exception as e:
        return jsonify({"error": f"Error iniciando contenedor: {e}"}), 500


# =============================================================
#   STOP CONTAINER
# =============================================================

@proyectos_blueprint.route("/stop/<project_id>", methods=["POST"])
def stop_container(project_id):
    token = get_manager_token()
    if not token:
        return jsonify({"error": "Token requerido"}), 401

    container = get_container(project_id, token)
    if not container:
        return jsonify({"error": "Contenedor no encontrado"}), 404

    cid = container["container_id"]

    try:
        subprocess.check_call(["docker", "stop", cid])

        roble.update_record(
            "proyectos",
            project_id,
            {"status": "stopped"},
            token
        )

        return jsonify({"success": True, "message": "Contenedor detenido"}), 200

    except Exception as e:
        return jsonify({"error": f"Error deteniendo contenedor: {e}"}), 500


# =============================================================
#   RESTART CONTAINER
# =============================================================

@proyectos_blueprint.route("/restart/<project_id>", methods=["POST"])
def restart_container(project_id):
    token = get_manager_token()
    if not token:
        return jsonify({"error": "Token requerido"}), 401

    container = get_container(project_id, token)
    if not container:
        return jsonify({"error": "Contenedor no encontrado"}), 404

    cid = container["container_id"]

    try:
        subprocess.check_call(["docker", "restart", cid])

        roble.update_record(
            "proyectos",
            project_id,
            {"status": "running"},
            token
        )

        return jsonify({"success": True, "message": "Contenedor reiniciado"}), 200

    except Exception as e:
        return jsonify({"error": f"Error reiniciando contenedor: {e}"}), 500


# =============================================================
#   LOGS DEL CONTENEDOR
# =============================================================

@proyectos_blueprint.route("/logs/<project_id>", methods=["GET"])
def logs_container(project_id):
    token = get_manager_token()
    if not token:
        return jsonify({"error": "Token requerido"}), 401

    container = get_container(project_id, token)
    if not container:
        return jsonify({"error": "Contenedor no encontrado"}), 404

    cid = container["container_id"]

    try:
        logs = subprocess.check_output(["docker", "logs", cid], text=True)

        return jsonify({"success": True, "logs": logs}), 200

    except Exception as e:
        return jsonify({"error": f"No se pudieron obtener logs: {e}"}), 500
