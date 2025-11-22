"""
Rutas de autenticación para el servicio Manager.
Integran RobleClient y sincronizan el token del usuario.
"""

from flask import Blueprint, request, jsonify
from roble_client import RobleClient
from activity_monitor import monitor
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

auth_blueprint = Blueprint("auth", __name__)
logger = logging.getLogger(__name__)
roble = RobleClient()

# ===========================
# TOKEN GLOBAL DEL MANAGER
# ===========================
MANAGER_TOKEN = None


# ===========================
# LOGIN
# ===========================

@auth_blueprint.route("/login", methods=["POST"])
def login():
    """
    Inicia sesión contra Roble.
    """
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email y contraseña requeridos"}), 400

        logger.info(f"LOGIN ATTEMPT: {email}")
        auth = roble.login(email, password)
        user = auth.get("user")

        logger.info(f"LOGIN SUCCESS: {email}")

        return jsonify({
            "success": True,
            "accessToken": auth["accessToken"],
            "refreshToken": auth["refreshToken"],
            "user": user
        }), 200

    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"error": "Credenciales incorrectas"}), 401


# ===========================
# use_token → ACTIVA EL TOKEN EN EL MANAGER
# ===========================

@auth_blueprint.route("/use_token", methods=["POST"])
def use_token():
    """
    Recibe el token del usuario desde el frontend
    y lo guarda en el Manager para todas las rutas.
    """
    global MANAGER_TOKEN

    try:
        data = request.get_json()
        token = data.get("accessToken") or data.get("token")

        if not token:
            return jsonify({"error": "accessToken requerido"}), 400

        MANAGER_TOKEN = token  # 🔥 Token guardado

        monitor.set_token(token)  # Se lo pasamos al monitor también

        logger.info("🔐 Manager recibió y guardó token correctamente.")

        return jsonify({
            "success": True,
            "message": "Token aplicado al Manager",
            "accessToken": token
        }), 200

    except Exception as e:
        logger.error(f"Error aplicando token: {e}")
        return jsonify({"error": "No se pudo aplicar token"}), 400


# ===========================
# SIGNUP
# ===========================

@auth_blueprint.route("/signup", methods=["POST"])
def signup():
    try:
        data = request.get_json()

        email = data.get("email")
        password = data.get("password")
        name = data.get("name")

        if not email or not password or not name:
            return jsonify({"error": "Email, contraseña y nombre requeridos"}), 400

        roble.signup_direct(email, password, name)
        logger.info(f"SIGNUP SUCCESS: {email}")

        return jsonify({"success": True, "message": "Usuario creado"}), 201

    except Exception as e:
        logger.error(f"Signup error: {e}")
        return jsonify({"error": "Error creando usuario"}), 400


# ===========================
# LOGOUT
# ===========================

@auth_blueprint.route("/logout", methods=["POST"])
def logout():
    global MANAGER_TOKEN
    try:
        if MANAGER_TOKEN:
            roble.logout(MANAGER_TOKEN)

        MANAGER_TOKEN = None
        monitor.set_token(None)

        logger.info("LOGOUT SUCCESS.")

        return jsonify({"success": True, "message": "Sesión cerrada"}), 200

    except Exception:
        return jsonify({"error": "No se pudo cerrar sesión"}), 400


# ===========================
# VERIFICAR
# ===========================

@auth_blueprint.route("/verify", methods=["GET"])
def verify():
    try:
        global MANAGER_TOKEN
        if not MANAGER_TOKEN:
            return jsonify({"valid": False}), 401

        user = roble.verify_token(MANAGER_TOKEN)

        return jsonify({"valid": True, "user": user}), 200

    except Exception:
        return jsonify({"valid": False}), 401
