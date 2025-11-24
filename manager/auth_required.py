from functools import wraps
from flask import request, jsonify
from roble_client import RobleClient

roble = RobleClient()

def auth_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Leer token enviado por el usuario
        auth = request.headers.get("Authorization")

        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "Token requerido"}), 401

        token = auth.split(" ")[1]

        try:
            # Validar token con Roble
            user = roble.verify_token(token)
            request.user = user     # se guarda el usuario para la ruta
            request.token = token   # también guardamos el token
        except Exception:
            return jsonify({"error": "Token inválido"}), 401

        return f(*args, **kwargs)

    return wrapper
