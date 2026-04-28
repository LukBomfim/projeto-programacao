from flask import Blueprint, jsonify, request
from config.firebase import db
from middlewares.auth_middleware import auth_required

users_bp = Blueprint("users", __name__)

@users_bp.route("/me", methods=["GET"])
@auth_required
def me():
    uid = request.user["uid"]

    doc = db.collection("usuarios").document(uid).get()

    if not doc.exists:
        return jsonify({"error": "Usuário não encontrado"}), 404

    return jsonify(doc.to_dict())