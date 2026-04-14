
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/dados-corrida', methods=['GET', 'POST'])
def processar_corrida():

    if request.method == 'GET':
        return jsonify({
            "mensagem": "API de corrida funcionando!",
            "como_usar": "Envie um POST para esta rota contendo um corpo JSON",
            "exemplo_json": {
                "distancia": 10,
                "tempo": 20,
                "destino": "Praia"
            }
        })
    
    dados = request.json or {}
    
    distancia = dados.get('distancia')
    tempo = dados.get('tempo')
    destino = dados.get('destino')
    
    if distancia is None or tempo is None:
        return jsonify({"erro": "Dados incompletos"}), 400

    print(f"Viagem para: {destino} | Distância: {distancia} km | Tempo: {tempo} min")

    return jsonify({
        "status": "sucesso",
        "resumo": {
            "distancia": distancia,
            "tempo": tempo
        }
    })

@app.route('/')
def home():
    return "API Online"

if __name__ == '__main__':
    app.run(debug=True, port=5000)

