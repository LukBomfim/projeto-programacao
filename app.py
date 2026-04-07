from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)


ORS_KEY = 'eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImY4NmQ5OTU2OWQ0NzRiZGNiNDk2NzRmMDY0Y2EyYWQ2IiwiaCI6Im11cm11cjY0In0='

MOTORISTAS = {
    "carlos": {"nome": "Carlos (Uno)", "coords": [-35.714, -9.666]}, #ponta verde
    "ana": {"nome": "Ana (Onix)", "coords": [-35.761, -9.582]}, #santa lucia
    "bruno": {"nome": "Bruno (Gol)", "coords": [-35.729, -9.555]} #biu
}


FACULDADE_COORDS = [-35.703, -9.633] #unima

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/gerar_rota", methods=['POST'])
def gerar_rota():
    dados = request.json
    moto_id = dados.get('motorista')
    lat_p = float(dados.get('lat'))
    lng_p = float(dados.get('lng'))

    
    ponto_motorista = MOTORISTAS[moto_id]['coords']
    ponto_embarque = [lng_p, lat_p]
    ponto_destino = FACULDADE_COORDS

    
    corpo = {
        "coordinates": [ponto_motorista, ponto_embarque, ponto_destino]
    }

    url = "https://api.openrouteservice.org/v2/directions/driving-car/geojson"
    headers = {
        'Authorization': ORS_KEY,
        'Content-Type': 'application/json'
    }

    try:
        r = requests.post(url, json=corpo, headers=headers)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)