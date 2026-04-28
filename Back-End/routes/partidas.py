from flask import Blueprint, jsonify
from config.firebase import db
from middlewares.auth_middleware import auth_required

partidas_bp = Blueprint("partidas", __name__)

@partidas_bp.route("/", methods=["GET"])
@auth_required
def listar():
    docs = db.collection("partidas").stream()
    partidas = [doc.to_dict() for doc in docs]
    return jsonify(partidas)