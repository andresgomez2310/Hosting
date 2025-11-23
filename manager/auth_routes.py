"""
Rutas de autenticación del Manager.
Se integran con Roble y actualizan el token global del Monitor.
"""

from flask import Blueprint, request, jsonify
import logging
from roble_client import RobleClient
from activity_monitor import monitor
MANAGER_TOKEN = None

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

auth_blueprint = Blueprint("auth", __name__)
logger = logging.getLogger(__name__)

roble = RobleClient()


# =============================================================
# =========================== LOGIN ============================
# =============================================================

@auth_blueprint.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        logger.info(f"LOGIN ATTEMPT: {email}")

        if not email or not password:
            return jsonify({"error": "Email y contraseña requeridos"}), 400

        auth = roble.login(email, password)

        # Tokens devueltos por Roble
        access = auth["accessToken"]
        refresh = auth["refreshToken"]
        user = auth.get("user")

        logger.info(f"LOGIN SUCCESS: {email}")

        return jsonify({
            "success": True,
            "accessToken": access,
            "refreshToken": refresh,
            "user": user
        }), 200

    except Exception as e:
        logger.error(f"Error en login: {e}")
        return jsonify({"error": "Credenciales incorrectas"}), 401


# =============================================================
# ============ APPLY TOKEN FROM FRONTEND ======================
# =============================================================

@auth_blueprint.route("/use_token", methods=["POST"])
def use_token():
    """
    El frontend nos envía el accessToken.
    - Lo activamos en el monitor.
    - Guardamos MANAGER_TOKEN para usarlo en otras rutas.
    """
    global MANAGER_TOKEN

    try:
        data = request.get_json() or {}
        token = data.get("accessToken") or data.get("token")

        if not token:
            return jsonify({"error": "accessToken requerido"}), 400

        # Guardar token global del Manager
        MANAGER_TOKEN = token
        logger.info("🔐 Manager recibió y guardó token correctamente.")

        # Activar monitor
        monitor.set_token(token)
        logger.info("🔐 Token aplicado correctamente al Monitor.")

        return jsonify({
            "success": True,
            "message": "Token aplicado al Manager",
            "accessToken": token
        }), 200

    except Exception as e:
        logger.error(f"Error aplicando token: {e}")
        return jsonify({"error": "No se pudo aplicar token"}), 400



# =============================================================
# =========================== SIGNUP ===========================
# =============================================================

@auth_blueprint.route("/signup", methods=["POST"])
def signup():
    try:
        data = request.get_json()

        email = data.get("email")
        password = data.get("password")
        name = data.get("name")

        logger.info(f"SIGNUP ATTEMPT: {email}")

        if not email or not password or not name:
            return jsonify({"error": "Email, contraseña y nombre requeridos"}), 400

        roble.signup_direct(email, password, name)

        logger.info(f"SIGNUP SUCCESS: {email}")

        return jsonify({
            "success": True,
            "message": "Usuario registrado exitosamente"
        }), 201

    except Exception as e:
        logger.error(f"Signup error: {e}")
        return jsonify({"error": "Error registrando usuario"}), 400


# =============================================================
# ============================ LOGOUT ==========================
# =============================================================

@auth_blueprint.route("/logout", methods=["POST"])
def logout():
    try:
        # Se toma el token activo del Monitor
        token = monitor.token
        if not token:
            return jsonify({"error": "Token inexistente"}), 400

        roble.logout(token)

        # Se desactiva en el Monitor
        monitor.token = None

        logger.info("LOGOUT SUCCESS")

        return jsonify({"success": True, "message": "Sesión cerrada"}), 200

    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({"error": "No se pudo cerrar sesión"}), 400


# =============================================================
# ====================== GET CURRENT USER ======================
# =============================================================

@auth_blueprint.route("/me", methods=["GET"])
def me():
    try:
        token = monitor.token
        if not token:
            return jsonify({"error": "Token requerido"}), 401

        user = roble.verify_token(token)
        logger.info(f"GET USER SUCCESS: {user.get('email', 'unknown')}")

        return jsonify({"success": True, "user": user}), 200

    except Exception as e:
        logger.error(f"Me error: {e}")
        return jsonify({"error": "Token inválido"}), 401


# =============================================================
# =========================== REFRESH ==========================
# =============================================================

@auth_blueprint.route("/refresh", methods=["POST"])
def refresh():
    try:
        data = request.get_json()
        refresh_token = data.get("refreshToken")

        logger.info(f"REFRESH ATTEMPT")

        if not refresh_token:
            return jsonify({"error": "refreshToken requerido"}), 400

        new_tokens = roble.refresh_token(refresh_token)

        new_access = new_tokens["accessToken"]
        monitor.set_token(new_access)

        logger.info("REFRESH SUCCESS")

        return jsonify({"accessToken": new_access}), 200

    except Exception as e:
        logger.error(f"Refresh error: {e}")
        return jsonify({"error": "No se pudo refrescar el token"}), 400


# =============================================================
# =========================== VERIFY ===========================
# =============================================================

@auth_blueprint.route("/verify", methods=["GET"])
def verify():
    try:
        token = monitor.token
        if not token:
            return jsonify({"valid": False}), 401

        user = roble.verify_token(token)
        logger.info("VERIFY SUCCESS")

        return jsonify({"valid": True, "user": user}), 200

    except Exception:
        return jsonify({"valid": False}), 401
