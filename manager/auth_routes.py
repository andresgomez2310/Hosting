"""
Rutas de autenticación para el servicio Manager.
Integran el RobleClient para login, registro, refresh y validación.
"""

from flask import Blueprint, request, jsonify
import logging
from roble_client import RobleClient
from activity_monitor import monitor  # 🔥 IMPORTANTE: traer el monitor real

auth_blueprint = Blueprint("auth", __name__)
logger = logging.getLogger(__name__)

roble = RobleClient()

# =============================================================
# =========================== LOGIN ============================
# =============================================================

@auth_blueprint.route("/login", methods=["POST"])
def login():
    """
    Inicia sesión con email + password usando Roble.
    """
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email y contraseña requeridos"}), 400

        auth = roble.login(email, password)
        user = auth.get("user")

        return jsonify({
            "success": True,
            "accessToken": auth["accessToken"],
            "refreshToken": auth["refreshToken"],
            "user": user
        }), 200

    except Exception as e:
        logger.error(f"Error en login: {e}")
        return jsonify({"error": "Credenciales incorrectas"}), 401


# =============================================================
# ======== Permitir al frontend activar el Monitor ============
# =============================================================

@auth_blueprint.route("/use_token", methods=["POST"])
def use_token():
    """
    El frontend nos envía el accessToken.
    - Lo activamos en el monitor.
    - Devolvemos confirmación y el token (importante para frontend).
    """
    try:
        data = request.get_json()

        # Aceptar ambos formatos por seguridad:
        token = data.get("accessToken") or data.get("token")

        if not token:
            return jsonify({"error": "accessToken requerido"}), 400

        # Activar monitor
        monitor.set_token(token)

        # Confirmar al frontend
        return jsonify({
            "success": True,
            "message": "Token aplicado al monitor",
            "accessToken": token
        }), 200

    except Exception as e:
        logger.error(f"Error aplicando token al monitor: {e}")
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

        if not email or not password or not name:
            return jsonify({"error": "Email, contraseña y nombre requeridos"}), 400

        roble.signup_direct(email, password, name)

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
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            return jsonify({"error": "Token requerido"}), 401

        token = token.split(" ")[1]
        roble.logout(token)

        return jsonify({"success": True, "message": "Sesión cerrada"}), 200

    except Exception:
        return jsonify({"error": "No se pudo cerrar sesión"}), 400


# =============================================================
# ========================== GET USER ==========================
# =============================================================

@auth_blueprint.route("/me", methods=["GET"])
def me():
    try:
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            return jsonify({"error": "Token requerido"}), 401

        token = token.split(" ")[1]
        user = roble.verify_token(token)

        return jsonify({"success": True, "user": user}), 200

    except Exception:
        return jsonify({"error": "Token inválido"}), 401


# =============================================================
# =========================== REFRESH ==========================
# =============================================================

@auth_blueprint.route("/refresh", methods=["POST"])
def refresh():
    try:
        data = request.get_json()
        refresh_token = data.get("refreshToken")

        if not refresh_token:
            return jsonify({"error": "refreshToken requerido"}), 400

        new_tokens = roble.refresh_token(refresh_token)
        return jsonify({"accessToken": new_tokens["accessToken"]}), 200

    except Exception:
        return jsonify({"error": "No se pudo refrescar el token"}), 400


# =============================================================
# =========================== VERIFY ===========================
# =============================================================

@auth_blueprint.route("/verify", methods=["GET"])
def verify():
    try:
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            return jsonify({"valid": False}), 401

        token = token.split(" ")[1]
        user = roble.verify_token(token)

        return jsonify({"valid": True, "user": user}), 200

    except Exception:
        return jsonify({"valid": False}), 401
