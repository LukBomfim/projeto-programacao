from flask import Blueprint, request, jsonify
from config.firebase import db
from middlewares.auth_middleware import auth_required
from firebase_admin import firestore

apostas_bp = Blueprint("apostas", __name__)

@apostas_bp.route("/", methods=["POST"])
@auth_required
def apostar():
    data = request.json

    if not data or "valor" not in data or "partida_id" not in data:
        return jsonify({"error": "Dados inválidos"}), 400

    aposta = {
        "user_id": request.user["uid"],
        "valor": data["valor"],
        "partida_id": data["partida_id"],
        "created_at": firestore.SERVER_TIMESTAMP
    }

    db.collection("apostas").add(aposta)

    return jsonify({
        "success": True,
        "data": aposta
    })