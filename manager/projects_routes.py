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
from activity_monitor import monitor

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

proyectos_blueprint = Blueprint("projects", __name__)
logger = logging.getLogger(__name__)

roble = RobleClient()

# =============================================================
#   OBTENER TOKEN GLOBAL (del monitor)
# =============================================================

def get_manager_token():
    token = monitor.token
    if not token:
        logger.error("❌ No hay token activo en el Manager.")
    return token


# =============================================================
#   OBTENER USER_ID DE /auth/{contract}/verify-token
# =============================================================

def get_user_id():
    token = get_manager_token()
    if not token:
        return None

    base = os.getenv("ROBLE_URL", "https://roble-api.openlab.uninorte.edu.co")
    contract = os.getenv("ROBLE_CONTRACT", "pc2_394e10a6d2")  # contrato REAL

    url = f"{base}/auth/{contract}/verify-token"

    try:
        resp = requests.get(url, headers={"Authorization": f"Bearer {token}"})
        data = resp.json()

        logger.info(f"===== verify-token RESPONSE =====")
        logger.info(data)

        if not data.get("valid"):
            return None

        return data.get("user", {}).get("sub")

    except Exception as e:
        logger.error(f"Error en get_user_id(): {e}")
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
    rep_url = data.get("repo_url")

    if not nombre or not rep_url:
        return jsonify({"error": "Faltan campos requeridos"}), 400

    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "No se pudo obtener user_id"}), 401

    try:
        proyecto = roble.create_project(
            user_id=user_id,
            name=nombre,
            rep_url=rep_url,
            access_token=token
        )
    except Exception as e:
        logger.error(f"❌ Error creando proyecto: {e}")
        return jsonify({"error": str(e)}), 500

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
        return jsonify({"error": "No se pudo obtener user_id"}), 401

    try:
        proyectos = roble.read_records(
            "proyectos",
            filters={"user_id": user_id},
            access_token=token
        )
    except Exception as e:
        logger.error(f"❌ Error obteniendo proyectos: {e}")
        return jsonify({"error": "Error obteniendo proyectos"}), 500

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

    proyecto = roble.read_records(
        "proyectos",
        filters={"_id": project_id},
        access_token=token
    )

    if not proyecto or not proyecto[0].get("container_"):
        return jsonify({"error": "Contenedor no encontrado"}), 404

    cid = proyecto[0]["container_"]

    try:
        subprocess.check_call(["docker", "start", cid])
        roble.update_project_status(project_id, "running", cid, token)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =============================================================
#   STOP CONTAINER
# =============================================================

@proyectos_blueprint.route("/stop/<project_id>", methods=["POST"])
def stop_container(project_id):
    token = get_manager_token()
    if not token:
        return jsonify({"error": "Token requerido"}), 401

    proyecto = roble.read_records(
        "proyectos",
        filters={"_id": project_id},
        access_token=token
    )

    if not proyecto or not proyecto[0].get("container_"):
        return jsonify({"error": "Contenedor no encontrado"}), 404

    cid = proyecto[0]["container_"]

    try:
        subprocess.check_call(["docker", "stop", cid])
        roble.update_project_status(project_id, "stopped", cid, token)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =============================================================
#   LOGS DEL CONTENEDOR
# =============================================================

@proyectos_blueprint.route("/logs/<project_id>", methods=["GET"])
def logs_container(project_id):
    token = get_manager_token()
    if not token:
        return jsonify({"error": "Token requerido"}), 401

    proyecto = roble.read_records(
        "proyectos",
        filters={"_id": project_id},
        access_token=token
    )

    if not proyecto or not proyecto[0].get("container_"):
        return jsonify({"error": "Contenedor no encontrado"}), 404

    cid = proyecto[0]["container_"]

    try:
        logs = subprocess.check_output(["docker", "logs", cid], text=True)
        return jsonify({"success": True, "logs": logs})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
