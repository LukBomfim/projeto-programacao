from flask import Flask, render_template, url_for

app = Flask(__name__, template_folder='frontend/templates', static_folder='frontend/static')

@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)