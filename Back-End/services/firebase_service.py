def criar_usuario(data):
    ref = db.collection("usuarios").add(data)
    return {
        "id": ref[1].id,
        "data": data
    }