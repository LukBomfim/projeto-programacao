from flask import Flask, render_template, url_for

app = Flask(__name__, template_folder='frontend/templates', static_folder='frontend/static')

@app.route('/')
def homepage():
    tipo_usuario = 'equipe'
    if tipo_usuario == 'equipe':
        return render_template('equipe/inicio.html')
    if tipo_usuario == 'organizador':
        return render_template('organizador/inicio.html')
    else:
        return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@app.route('/campeonatos/<int:id>')
def campeonato(id):
    return render_template('comum/campeonato.html', campeonato='')

@app.route('/partidas/<int:id>')
def partida(id):

    if id == 1:
        return render_template('comum/partida.html', partida='Partida Exemplo')
    elif id == 2:
        return render_template('comum/partida-finalizada.html', partida='Partida Exemplo 2')

@app.route('/apostas')
def apostas():
    return render_template('comum/apostas.html')

@app.route('/equipe/campeonatos/<int:id>')
def equipe_campeonato(id):
    if id == 1:
        return render_template('equipe/campeonato.html', campeonato_inscrito=True)
    elif id == 2:
        return render_template('equipe/campeonato.html', campeonato_inscrito=False)

@app.route('/equipe/campeonatos')
def equipe_campeonatos():
    return render_template('equipe/campeonatos.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
