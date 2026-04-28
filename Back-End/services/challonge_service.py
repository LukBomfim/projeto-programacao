import requests
import os

from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("CHALLONGE_API_KEY")
USERNAME = os.getenv("CHALLONGE_USERNAME")

BASE_URL = "https://api.challonge.com/v1"

def criar_campeonato(nome):
    url = f"{BASE_URL}/tournaments.json"

    data = {
        "api_key": API_KEY,
        "tournament[name]": nome,
        "tournament[url]": nome.lower().replace(" ", "_"),
        "tournament[tournament_type]": "single elimination"
    }

    response = requests.post(url, data=data)

    if response.status_code != 200:
        return {"error": response.text}
    return response.json()

if not API_KEY:
    raise Exception("CHALLONGE_API_KEY não definida no .env")