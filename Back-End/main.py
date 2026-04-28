from flask import Flask, render_template, request, redirect, session, flash
from database import (
    init_db, popular_dados_exemplo,
    criar_usuario, criar_equipe, criar_organizacao, autenticar_usuario,
    listar_campeonatos, buscar_campeonato, criar_campeonato,
    campeonatos_da_organizacao,
    buscar_partida, listar_partidas,
    convites_da_equipe, responder_convite,
    campeonatos_da_equipe, inscrever_equipe,
    atletas_da_equipe,
    apostas_do_usuario, fazer_aposta,
)

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
app.secret_key = 'bet404-secret-key-2026'

init_db()
popular_dados_exemplo()


def tipo_usuario():
    return session.get('tipo')


def usuario_id():
    return session.get('usuario_id')


@app.route('/')
def homepage():
    tipo = tipo_usuario()
    if tipo == 'equipe':
        return render_template('equipe/inicio.html')
    elif tipo == 'organizacao':
        campeonatos = campeonatos_da_organizacao(usuario_id())
        return render_template('organizacao/inicio.html', campeonatos=campeonatos)
    else:
        partidas = listar_partidas(status='agendada')
        return render_template('index.html', usuario=session.get('nome', 'Usuário'), partidas=partidas)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cpf = request.form.get('cpf')
        senha = request.form.get('password')

        tipo, obj = autenticar_usuario(cpf, senha)

        if tipo:
            session['tipo'] = tipo
            session['usuario_id'] = obj['id']
            session['nome'] = obj['nome']

            if tipo == 'equipe':
                return redirect('/equipe')
            elif tipo == 'organizacao':
                return redirect('/organizacao')
            else:
                return redirect('/')

        flash('Login inválido')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        tipo = request.form.get('tipo_conta')
        senha = request.form.get('password')

        if tipo == 'usuario':
            ok, msg = criar_usuario(
                request.form.get('nome'),
                request.form.get('cpf'),
                request.form.get('nascimento'),
                request.form.get('numero'),
                request.form.get('email'),
                senha
            )

        elif tipo == 'equipe':
            ok, msg = criar_equipe(
                request.form.get('nome_equipe'),
                request.form.get('cnpj'),
                request.form.get('numero'),
                request.form.get('email'),
                senha,
                request.form.get('modalidade')
            )

        elif tipo == 'organizacao':
            ok, msg = criar_organizacao(
                request.form.get('nome_equipe'),
                request.form.get('cnpj'),
                request.form.get('numero'),
                request.form.get('email'),
                senha,
                request.form.getlist('modalidades')
            )

        flash(msg)
        return redirect('/login')

    return render_template('cadastro.html')


@app.route('/perfil')
def perfil():
    tipo = tipo_usuario()

    if tipo == 'usuario':
        apostas = apostas_do_usuario(usuario_id())
        return render_template('comum/conta.html', apostas=apostas)

    elif tipo == 'equipe':
        return render_template('equipe/conta.html')

    elif tipo == 'organizacao':
        return render_template('organizacao/conta.html')

    return redirect('/login')


@app.route('/historico')
def historico():
    tipo = tipo_usuario()

    if tipo == 'equipe':
        camps = campeonatos_da_equipe(usuario_id())
        return render_template('equipe/historico.html', campeonatos=camps)

    elif tipo == 'organizacao':
        camps = campeonatos_da_organizacao(usuario_id())
        return render_template('organizacao/historico.html', campeonatos=camps)

    return redirect('/')


@app.route('/apostas')
def apostas():
    abertas = listar_partidas(status='agendada')
    finalizadas = listar_partidas(status='finalizada')

    return render_template(
        'comum/apostas.html',
        partidas_abertas=abertas,
        partidas_finalizadas=finalizadas
    )


@app.route('/apostas/fazer/<int:partida_id>', methods=['POST'])
def fazer_aposta_route(partida_id):
    if tipo_usuario() != 'usuario':
        return redirect('/apostas')

    equipe_id = int(request.form.get('equipe_vencedora_id'))
    valor = float(request.form.get('valor'))

    ok, msg = fazer_aposta(usuario_id(), partida_id, equipe_id, valor)
    flash(msg)

    return redirect('/apostas')


@app.route('/campeonatos/<int:id>')
def campeonato(id):
    camp = buscar_campeonato(id)

    if not camp:
        return redirect('/')

    tipo = tipo_usuario()

    if tipo == 'organizacao':
        return render_template('organizacao/campeonato.html', campeonato=camp)

    if tipo == 'equipe':
        inscrito = any(c['id'] == id for c in campeonatos_da_equipe(usuario_id()))
        return render_template('equipe/campeonato.html', campeonato=camp, campeonato_inscrito=inscrito)

    return render_template('comum/campeonato.html', campeonato=camp)


@app.route('/partidas/<int:id>')
def partida(id):
    p = buscar_partida(id)

    if not p:
        return redirect('/')

    if p['status'] == 'finalizada':
        return render_template('comum/partida-finalizada.html', partida=p)

    return render_template('comum/partida.html', partida=p)


@app.route('/equipe')
def equipe_inicio():
    return render_template('equipe/inicio.html')


@app.route('/equipe/campeonatos')
def equipe_campeonatos():
    camps = listar_campeonatos(status='futuro')
    inscritos = campeonatos_da_equipe(usuario_id())

    return render_template('equipe/campeonatos.html', campeonatos=camps, inscritos=inscritos)


@app.route('/equipe/campeonatos/<int:id>')
def equipe_campeonato(id):
    camp = buscar_campeonato(id)
    inscrito = any(c['id'] == id for c in campeonatos_da_equipe(usuario_id()))

    return render_template('equipe/campeonato.html', campeonato=camp, campeonato_inscrito=inscrito)


@app.route('/equipe/inscrever/<int:id>', methods=['POST'])
def inscrever(id):
    inscrever_equipe(id, usuario_id())
    return redirect(f'/equipe/campeonatos/{id}')


@app.route('/equipe/convites')
def equipe_convites():
    convites = convites_da_equipe(usuario_id())
    return render_template('equipe/convites.html', convites=convites)


@app.route('/equipe/convites/<int:id>/responder', methods=['POST'])
def responder_convite_route(id):
    resposta = request.form.get('resposta') == 'aceitar'
    responder_convite(id, resposta)
    return redirect('/equipe/convites')


@app.route('/equipe/<int:id>/subequipes')
def equipe_subequipes(id):
    atletas = atletas_da_equipe(id)
    return render_template('equipe/subequipes.html', tipo_categoria='peso', atletas=atletas)


@app.route('/organizacao')
def organizacao_inicio():
    camps = campeonatos_da_organizacao(usuario_id())
    return render_template('organizacao/inicio.html', campeonatos=camps)


@app.route('/organizacao/novo', methods=['GET', 'POST'])
def novo_campeonato():
    if request.method == 'POST':
        criar_campeonato(
            usuario_id(),
            request.form.get('nome'),
            request.form.get('modalidade'),
            request.form.get('data_inicio'),
            request.form.get('data_fim'),
            int(request.form.get('max_participantes')),
            request.form.get('descricao')
        )
        return redirect('/organizacao')

    return render_template('organizacao/novo-campeonato.html')


if __name__ == '__main__':
    app.run(debug=True)