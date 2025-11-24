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
# TOKEN GLOBAL (siempre viene del monitor)
# =============================================================

def get_manager_token():
    token = monitor.token
    if not token:
        logger.error("❌ No hay token activo en el Manager.")
    return token


# =============================================================
# OBTENER USER ID DESDE verify-token  (sub)
# =============================================================

def get_user_id():
    token = get_manager_token()
    if not token:
        return None

    try:
        data = roble.verify_token(token)
        user = data.get("user", {})
        return user.get("sub")     # <-- ID real del usuario
    except Exception as e:
        logger.error(f"Error get_user_id(): {e}")
        return None


# =============================================================
# CREAR PROYECTO
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
# LISTAR PROYECTOS DEL USUARIO
# =============================================================

@proyectos_blueprint.route("/mine", methods=["GET"])
def mis_proyectos():
    token = get_manager_token()
    if not token:
        return jsonify({"error": "Token requerido"}), 401

    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "Token inválido"}), 401

    try:
        proyectos = roble.read_records(
            "proyectos",
            filters={"user_id": user_id},
            access_token=token
        )
        return jsonify({"projects": proyectos}), 200

    except Exception as e:
        logger.error(f"❌ Error obteniendo proyectos: {e}")
        return jsonify({"error": "No se pudieron obtener los proyectos"}), 500



# =============================================================
# OBTENER PROYECTO POR ID
# =============================================================

@proyectos_blueprint.route("/<project_id>", methods=["GET"])
def get_project(project_id):
    token = get_manager_token()
    if not token:
        return jsonify({"error": "Token requerido"}), 401

    try:
        rows = roble.read_records("proyectos", token)
        match = [p for p in rows if p.get("_id") == project_id]

        if not match:
            return jsonify({"error": "Proyecto no encontrado"}), 404

        return jsonify({"project": match[0]}), 200

    except Exception as e:
        logger.error(f"❌ Error leyendo proyecto: {e}")
        return jsonify({"error": "No se pudo obtener el proyecto"}), 500


# =============================================================
# OBTENER CONTENEDOR ASOCIADO
# =============================================================

def get_container(project_id, token):
    rows = roble.read_records("containers", token)
    match = [c for c in rows if c.get("project_id") == project_id]
    return match[0] if match else None


# =============================================================
# START CONTAINER
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
        return jsonify({"success": True, "message": "Contenedor iniciado"}), 200
    except Exception as e:
        return jsonify({"error": f"Error iniciando contenedor: {e}"}), 500


# =============================================================
# STOP CONTAINER
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
        return jsonify({"success": True, "message": "Contenedor detenido"}), 200
    except Exception as e:
        return jsonify({"error": f"Error deteniendo contenedor: {e}"}), 500


# =============================================================
# LOGS CONTAINER
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
