import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

cred_path = os.getenv("FIREBASE_CREDENTIALS")

if not cred_path:
    raise ValueError("FIREBASE_CREDENTIALS não definido no .env")

cred_path = os.path.join(BASE_DIR, cred_path)

if not os.path.exists(cred_path):
    raise FileNotFoundError(f"Arquivo não encontrado: {cred_path}")

cred = credentials.Certificate(cred_path)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()