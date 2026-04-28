from flask import Flask, render_template, request, redirect, url_for

app = Flask(
    __name__,
    template_folder='frontend/templates',
    static_folder='frontend/static'
)

tipo_usuario = 'organizacao'

@app.route('/')
def homepage():
    if tipo_usuario == 'equipe':
        return render_template('equipe/inicio.html')
    elif tipo_usuario == 'organizacao':
        return render_template('organizacao/inicio.html')
    else:
        return render_template('index.html', usuario='Usuário')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cpf = request.form.get('cpf')
        senha = request.form.get('password')
        if cpf == 'admin':
            return redirect(url_for('homepage'))
        elif cpf == 'equipe':
            return redirect(url_for('equipe_inicio'))
        elif cpf == 'org':
            return redirect(url_for('organizacao_inicio'))
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        tipo = request.form.get('tipo_conta')
        if tipo == 'usuario':
            return redirect(url_for('homepage'))
        elif tipo == 'equipe':
            return redirect(url_for('equipe_inicio'))
        elif tipo == 'organizacao':
            return redirect(url_for('organizacao_inicio'))
    return render_template('cadastro.html')

@app.route('/perfil')
def perfil():
    if tipo_usuario == 'comum':
        return render_template('comum/conta.html')
    elif tipo_usuario == 'equipe':
        return render_template('equipe/conta.html')
    elif tipo_usuario == 'organizacao':
        return render_template('organizacao/conta.html')

@app.route('/apostas')
def apostas():
    return render_template('comum/apostas.html')

@app.route('/campeonatos/<int:id>')
def campeonato(id):
    campeonato = {
        "nome": f"Campeonato {id}",
        "modalidade": "Futebol",
        "data": "2026-05-10",
        "descricao": "Descrição do campeonato"
    }
    if tipo_usuario == 'organizacao':
        if id == 1:
            return render_template('organizacao/campeonato-futuro.html', campeonato=campeonato)
        elif id == 2:
            return render_template('organizacao/campeonato-ativo.html', campeonato=campeonato)
        elif id == 3:
            return render_template('organizacao/campeonato-passado.html', campeonato=campeonato)
    if tipo_usuario == 'equipe':
        return render_template('equipe/campeonato.html', campeonato=campeonato)
    
    return render_template('comum/campeonato.html', campeonato=campeonato)

@app.route('/partidas/<int:id>')
def partida(id):
    partida = {
        "nome": f"Partida {id}",
        "modalidade": "Futebol",
        "data": "2026-05-10",
        "descricao": "Descrição da partida",
        "resultado": "2x1"
    }
    if id == 2:
        return render_template('comum/partida-finalizada.html', partida=partida)
    return render_template('comum/partida.html', partida=partida)

@app.route('/equipe')
def equipe_inicio():
    return render_template('equipe/inicio.html')

@app.route('/equipe/conta')
def equipe_conta():
    return render_template('equipe/conta.html')

@app.route('/equipe/campeonatos')
def equipe_campeonatos():
    return render_template('equipe/campeonatos.html')

@app.route('/equipe/campeonatos/<int:id>')
def equipe_campeonato(id):
    return render_template('equipe/campeonato.html', campeonato_inscrito=(id == 1))

@app.route('/equipe/convites')
def equipe_convites():
    return render_template('equipe/convites.html')

@app.route('/equipe/<int:id>/subequipes')
def equipe_subequipes(id):
    return render_template('equipe/subequipes.html', tipo_categoria='peso')

@app.route('/organizacao/novo-campeonato')
def organizacao_novo_campeonato():
    return render_template('organizacao/novo-campeonato.html')

@app.route('/historico')
def historico():
    if tipo_usuario == 'organizacao':
        return render_template('organizacao/historico.html')
    elif tipo_usuario == 'equipe':
        return render_template('equipe/historico.html')
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)