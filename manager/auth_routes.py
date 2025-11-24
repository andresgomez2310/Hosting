"""
Rutas de autenticación del Manager.
Se integran con Roble Auth REAL.
"""

from flask import Blueprint, request, jsonify
import logging
from roble_client import RobleClient
from activity_monitor import monitor

auth_blueprint = Blueprint("auth", __name__)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

roble = RobleClient()


# =============================================================
# =========================== SIGNUP ===========================
# =============================================================

@auth_blueprint.route("/signup-direct", methods=["POST"])
def signup_direct():
    try:
        data = request.get_json()

        email = data.get("email")
        password = data.get("password")
        name = data.get("name")

        if not email or not password or not name:
            return jsonify({"error": "Email, contraseña y nombre requeridos"}), 400

        result = roble.signup_direct(email, password, name)

        return jsonify({
            "success": True,
            "user": result["user"]
        }), 200

    except Exception as e:
        print("----- ERROR EN ROBLE -----")
        print("Error:", e)

        # 👇 ESTA ES LA LÍNEA IMPORTANTE
        try:
            print("Roble respondió:", e.response.text)
        except:
            pass

        return jsonify({"error": "Error registrando usuario"}), 400




# =============================================================
# ====================== VERIFY CODE ===========================
# =============================================================

@auth_blueprint.route("/verify_code", methods=["POST"])
def verify_code():
    """
    Verifica el código enviado al correo del usuario.
    """
    try:
        data = request.get_json()

        email = data.get("email")
        code = data.get("code")

        if not email or not code:
            return jsonify({"error": "Email y código requeridos"}), 400

        roble.verify_code(email, code)

        logger.info(f"EMAIL VERIFIED: {email}")

        return jsonify({
            "success": True,
            "message": "Cuenta verificada correctamente"
        }), 200

    except Exception as e:
        logger.error(f"Verify code error: {e}")
        return jsonify({"error": "Código incorrecto o expirado"}), 400


# =============================================================
# =========================== LOGIN ============================
# =============================================================

@auth_blueprint.route("/login", methods=["POST"])
def login():
    """
    Login REAL usando Roble Auth.
    """
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
        return jsonify({"error": "Credenciales incorrectas o usuario no verificado"}), 401


# =============================================================
# ============ APPLY TOKEN FROM FRONTEND ======================
# =============================================================

@auth_blueprint.route("/use_token", methods=["POST"])
def use_token():
    """
    Guardar el token enviado por el frontend y aplicarlo al monitor.
    """
    try:
        data = request.get_json() or {}
        token = data.get("accessToken") or data.get("token")

        if not token:
            return jsonify({"error": "accessToken requerido"}), 400

        monitor.set_token(token)
        logger.info("🔐 Token aplicado correctamente al Monitor.")

        return jsonify({
            "success": True,
            "message": "Token aplicado correctamente",
            "accessToken": token
        }), 200

    except Exception as e:
        logger.error(f"Error aplicando token: {e}")
        return jsonify({"error": "No se pudo aplicar token"}), 400


# =============================================================
# ============================ LOGOUT ==========================
# =============================================================

@auth_blueprint.route("/logout", methods=["POST"])
def logout():
    """
    Cerrar sesión llamando a Roble.
    """
    try:
        token = monitor.token
        if not token:
            return jsonify({"error": "Token inexistente"}), 400

        roble.logout(token)
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
    """
    Obtener datos del usuario autenticado.
    """
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
    """
    Refrescar accessToken usando refreshToken.
    """
    try:
        data = request.get_json()
        refresh_token = data.get("refreshToken")

        if not refresh_token:
            return jsonify({"error": "refreshToken requerido"}), 400

        new_tokens = roble.refresh_token(refresh_token)
        new_access = new_tokens["accessToken"]

        monitor.set_token(new_access)

        logger.info("REFRESH SUCCESS")

        return jsonify({"accessToken": new_access}), 200

    except Exception as e:
        logger.error(f"Refresh error: {e}")
        return jsonify({"error": "No se pudo refrescar"}), 400
