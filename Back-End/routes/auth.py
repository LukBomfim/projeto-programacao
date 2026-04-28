from flask import Blueprint, request, jsonify
from firebase_admin import auth
from config.firebase import db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json

    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Dados inválidos"}), 400

    try:
        user = auth.create_user(
            email=data["email"],
            password=data["password"]
        )

        db.collection("usuarios").document(user.uid).set({
            "nome": data.get("nome"),
            "tipo": data.get("tipo", "user")
        })

        return jsonify({
            "success": True,
            "uid": user.uid
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400