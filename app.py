from flask import Flask, render_template
import requests

app = Flask(__name__)

API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImY4NmQ5OTU2OWQ0NzRiZGNiNDk2NzRmMDY0Y2EyYWQ2IiwiaCI6Im11cm11cjY0In0="

@app.route("/")
def home():
    alunoA = [-9.666, -35.735]
    alunoB = [-9.670, -35.750]
    faculdade = [-9.648, -35.708]

    distA = ((alunoA[0]-faculdade[0])**2 + (alunoA[1]-faculdade[1])**2)**0.5
    distB = ((alunoB[0]-faculdade[0])**2 + (alunoB[1]-faculdade[1])**2)**0.5

    if distA > distB:
        motorista, passageiro = alunoA, alunoB
        msg = "Motorista A busca o Aluno B"
    else:
        motorista, passageiro = alunoB, alunoA
        msg = "Motorista B busca o Aluno A"

    url = "https://api.openrouteservice.org/v2/directions/driving-car/geojson"
    headers = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }
    body = {
        "coordinates": [
            [motorista[1], motorista[0]], 
            [passageiro[1], passageiro[0]], 
            [faculdade[1], faculdade[0]]
        ]
    }

    response = requests.post(url, json=body, headers=headers)
    dados_rota = response.json()

    return render_template(
        "index.html", 
        rota_geojson=dados_rota, 
        mensagem=msg,
        pontoA=alunoA,
        pontoB=alunoB,
        faculdade=faculdade
    )

if __name__ == "__main__":
    app.run(debug=True)