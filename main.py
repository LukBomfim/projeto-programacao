from flask import Flask, render_template, url_for

app = Flask(__name__, template_folder='frontend/templates', static_folder='frontend/static')

@app.route('/')
def homepage():
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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
