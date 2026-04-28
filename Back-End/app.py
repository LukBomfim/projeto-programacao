import os , main
from flask import Flask
from routes.auth import auth_bp
from routes.campeonatos import camp_bp
from routes.partidas import partidas_bp
from routes.apostas import apostas_bp
from dotenv import load_dotenv
from routes.users import users_bp
app = Flask(__name__)

load_dotenv()

CHALLONGE_API_KEY = os.getenv("CHALLONGE_API_KEY")
CHALLONGE_USERNAME = os.getenv("CHALLONGE_USERNAME")

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(camp_bp, url_prefix="/api/campeonatos")
app.register_blueprint(partidas_bp, url_prefix="/api/partidas")
app.register_blueprint(apostas_bp, url_prefix="/api/apostas")
app.register_blueprint(users_bp, url_prefix="/api/users")

@app.route("/")
def home():
    return {"msg": "API rodando"}

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)