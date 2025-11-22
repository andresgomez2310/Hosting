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

from auth_routes import MANAGER_TOKEN
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

proyectos_blueprint = Blueprint("projects", __name__)
logger = logging.getLogger(__name__)

roble = RobleClient()


# =============================================================
#   TOKEN DEL MANAGER (YA NO USAMOS Authorization DEL REQUEST)
# =============================================================

def get_manager_token():
    if not MANAGER_TOKEN:
        logger.error("❌ No hay token activo en el Manager.")
        return None
    return MANAGER_TOKEN


# =============================================================
#   VERIFICAR USER_ID DESDE TOKEN
# =============================================================

def get_user_id():
    token = get_manager_token()
    if not token:
        return None

    base = os.getenv("ROBLE_URL", "https://roble-api.openlab.uninorte.edu.co")
    contract = os.getenv("ROBLE_CONTRACT", "hosting_adcce8f544")

    url = f"{base}/auth/{contract}/verify-token"

    try:
        r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
        if r.status_code != 200:
            return None

        data = r.json().get("user", {})
        return data.get("id") or data.get("_id")

    except:
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
        return jsonify({"error": "Faltan campos"}), 400

    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "Token inválido"}), 401

    new_project = {
        "user_id": user_id,
        "nombre": nombre,
        "repo_url": repo,
        "status": "pending",
        "container_id": None,
        "created_at": datetime.utcnow().isoformat(),
        "last_access": datetime.utcnow().isoformat()
    }

    proyecto = roble.create_record("proyectos", new_project, token)

    return jsonify({"success": True, "project": proyecto}), 201


# =============================================================
#   LISTAR MIS PROYECTOS
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
#   GET PROYECTO POR ID
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
