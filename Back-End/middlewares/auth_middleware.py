from functools import wraps
from flask import request, jsonify
from firebase_admin import auth

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"error": "Token obrigatório"}), 401

        try:
            decoded = auth.verify_id_token(token)
            request.user = decoded
        except Exception:
            return jsonify({"error": "Token inválido"}), 401

        return f(*args, **kwargs)
    return decorated