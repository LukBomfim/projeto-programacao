from flask import Blueprint, request, jsonify
from services.challonge_service import criar_campeonato
from middlewares.auth_middleware import auth_required

camp_bp = Blueprint("campeonatos", __name__)

@camp_bp.route("/", methods=["POST"])
@auth_required
def criar():
    data = request.json

    if not data or "nome" not in data:
        return jsonify({"error": "Nome é obrigatório"}), 400

    camp = criar_campeonato(data["nome"])

    return jsonify({
        "success": True,
        "data": camp
    })