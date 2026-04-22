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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)