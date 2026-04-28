from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import (
    init_db, popular_dados_exemplo,
    criar_usuario, criar_equipe, criar_organizacao, autenticar_usuario,
    validar_cadastro_usuario, validar_cadastro_equipe, validar_cadastro_organizacao,
    listar_campeonatos, buscar_campeonato, criar_campeonato,
    atualizar_status_campeonato, campeonatos_da_organizacao,
    buscar_partida, listar_partidas, criar_partida, finalizar_partida,
    convites_da_equipe, enviar_convite, responder_convite,
    campeonatos_da_equipe, inscrever_equipe,
    atletas_da_equipe, adicionar_atleta, remover_atleta,
    apostas_do_usuario, fazer_aposta,
)

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')

app.secret_key = 'bet404-secret-key-2026'

# Inicializa o banco na inicialização
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
        return render_template('index.html', usuario='Usuário', partidas=partidas)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cpf_cnpj = request.form.get('cpf', '').strip()
        senha    = request.form.get('password', '')
        tipo, obj = autenticar_usuario(cpf_cnpj, senha)
        if tipo:
            session['tipo']       = tipo
            session['usuario_id'] = obj['id']
            session['nome']       = obj['nome']
            flash('Login realizado com sucesso!', 'success')
            if tipo == 'equipe':
                return redirect(url_for('equipe_inicio'))
            elif tipo == 'organizacao':
                return redirect(url_for('organizacao_inicio'))
            else:
                return redirect(url_for('homepage'))
        flash('CPF/CNPJ ou senha inválidos.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        tipo             = request.form.get('tipo_conta')
        senha            = request.form.get('password', '')
        confirmar_senha  = request.form.get('confirmar_senha', '')

        if tipo == 'usuario':
            nome       = request.form.get('nome', '')
            cpf        = request.form.get('cpf', '')
            nascimento = request.form.get('nascimento', '')
            numero     = request.form.get('numero', '')
            email      = request.form.get('email', '')

            erros = validar_cadastro_usuario(nome, cpf, nascimento, numero, email, senha, confirmar_senha)
            if erros:
                for erro in erros:
                    flash(erro, 'error')
                return render_template('cadastro.html')

            ok, msg = criar_usuario(nome=nome, cpf=cpf, nascimento=nascimento,
                                    numero=numero, email=email, senha=senha)
            if ok:
                flash(msg, 'success')
                return redirect(url_for('login'))
            flash(msg, 'error')

        elif tipo == 'equipe':
            nome       = request.form.get('nome_equipe', '')
            cnpj       = request.form.get('cnpj', '')
            numero     = request.form.get('numero', '')
            email      = request.form.get('email', '')
            modalidade = request.form.get('modalidade', '')

            erros = validar_cadastro_equipe(nome, cnpj, email, senha, confirmar_senha, modalidade)
            if erros:
                for erro in erros:
                    flash(erro, 'error')
                return render_template('cadastro.html')

            ok, msg = criar_equipe(nome=nome, cnpj=cnpj, numero=numero,
                                   email=email, senha=senha, modalidade=modalidade)
            if ok:
                flash(msg, 'success')
                return redirect(url_for('login'))
            flash(msg, 'error')

        elif tipo == 'organizacao':
            nome        = request.form.get('nome_equipe', '')
            cnpj        = request.form.get('cnpj', '')
            numero      = request.form.get('numero', '')
            email       = request.form.get('email', '')
            modalidades = request.form.getlist('modalidades')

            erros = validar_cadastro_organizacao(nome, cnpj, email, senha, confirmar_senha, modalidades)
            if erros:
                for erro in erros:
                    flash(erro, 'error')
                return render_template('cadastro.html')

            ok, msg = criar_organizacao(nome=nome, cnpj=cnpj, numero=numero,
                                        email=email, senha=senha, modalidades=modalidades)
            if ok:
                flash(msg, 'success')
                return redirect(url_for('login'))
            flash(msg, 'error')

        else:
            flash('Selecione um tipo de conta.', 'error')

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
    return redirect(url_for('login'))

@app.route('/apostas')
def apostas():
    partidas_abertas     = listar_partidas(status='agendada')
    partidas_finalizadas = listar_partidas(status='finalizada')
    return render_template('comum/apostas.html',
        partidas_abertas=partidas_abertas,
        partidas_finalizadas=partidas_finalizadas)

@app.route('/apostas/fazer/<int:partida_id>', methods=['POST'])
def fazer_aposta_route(partida_id):
    if tipo_usuario() != 'usuario':
        flash('Apenas usuários comuns podem apostar.', 'error')
        return redirect(url_for('apostas'))
    equipe_id = request.form.get('equipe_vencedora_id', type=int)
    valor     = request.form.get('valor', type=float)
    ok, msg   = fazer_aposta(usuario_id(), partida_id, equipe_id, valor)
    flash(msg, 'success' if ok else 'error')
    return redirect(url_for('apostas'))

@app.route('/campeonatos/<int:id>')
def campeonato(id):
    camp = buscar_campeonato(id)
    if not camp:
        flash('Campeonato não encontrado.', 'error')
        return redirect(url_for('homepage'))
    tipo = tipo_usuario()
    if tipo == 'organizacao':
        if camp['status'] == 'futuro':
            return render_template('organizacao/campeonato-futuro.html', campeonato=camp)
        elif camp['status'] == 'ativo':
            return render_template('organizacao/campeonato-ativo.html', campeonato=camp)
        else:
            return render_template('organizacao/campeonato-passado.html', campeonato=camp)
    if tipo == 'equipe':
        inscrito = any(c['id'] == id for c in campeonatos_da_equipe(usuario_id()))
        return render_template('equipe/campeonato.html', campeonato=camp, campeonato_inscrito=inscrito)
    return render_template('comum/campeonato.html', campeonato=camp)

@app.route('/partidas/<int:id>')
def partida(id):
    p = buscar_partida(id)
    if not p:
        flash('Partida não encontrada.', 'error')
        return redirect(url_for('homepage'))
    if p['status'] == 'finalizada':
        return render_template('comum/partida-finalizada.html', partida=p)
    return render_template('comum/partida.html', partida=p)

@app.route('/equipe')
def equipe_inicio():
    return render_template('equipe/inicio.html')

@app.route('/equipe/conta')
def equipe_conta():
    return render_template('equipe/conta.html')

@app.route('/equipe/campeonatos')
def equipe_campeonatos():
    todos = listar_campeonatos(status='futuro')
    ids_inscritos = {c['id'] for c in campeonatos_da_equipe(usuario_id())} if tipo_usuario() == 'equipe' else set()
    return render_template('equipe/campeonatos.html', campeonatos=todos, ids_inscritos=ids_inscritos)

@app.route('/equipe/campeonatos/<int:id>')
def equipe_campeonato(id):
    camp     = buscar_campeonato(id)
    inscrito = tipo_usuario() == 'equipe' and any(c['id'] == id for c in campeonatos_da_equipe(usuario_id()))
    return render_template('equipe/campeonato.html', campeonato=camp, campeonato_inscrito=inscrito)

@app.route('/equipe/inscrever/<int:campeonato_id>', methods=['POST'])
def equipe_inscrever(campeonato_id):
    if tipo_usuario() != 'equipe':
        flash('Apenas equipes podem se inscrever.', 'error')
        return redirect(url_for('equipe_campeonatos'))
    inscrever_equipe(campeonato_id, usuario_id())
    flash('Inscrição realizada!', 'success')
    return redirect(url_for('equipe_campeonato', id=campeonato_id))

@app.route('/equipe/convites')
def equipe_convites():
    convites = convites_da_equipe(usuario_id()) if tipo_usuario() == 'equipe' else []
    return render_template('equipe/convites.html', convites=convites)

@app.route('/equipe/convites/<int:convite_id>/responder', methods=['POST'])
def responder_convite_route(convite_id):
    aceito = request.form.get('resposta') == 'aceitar'
    responder_convite(convite_id, aceito)
    flash('Convite ' + ('aceito' if aceito else 'recusado') + '.', 'success')
    return redirect(url_for('equipe_convites'))

@app.route('/equipe/<int:id>/subequipes')
def equipe_subequipes(id):
    atletas = atletas_da_equipe(id)
    return render_template('equipe/subequipes.html', tipo_categoria='peso', atletas=atletas)

@app.route('/equipe/<int:id>/atleta/adicionar', methods=['POST'])
def adicionar_atleta_route(id):
    adicionar_atleta(id, request.form.get('nome', ''), request.form.get('categoria', ''))
    flash('Atleta adicionado!', 'success')
    return redirect(url_for('equipe_subequipes', id=id))

@app.route('/equipe/atleta/<int:atleta_id>/remover', methods=['POST'])
def remover_atleta_route(atleta_id):
    eid = usuario_id()
    remover_atleta(atleta_id)
    flash('Atleta removido.', 'success')
    return redirect(url_for('equipe_subequipes', id=eid))

@app.route('/organizacao')
def organizacao_inicio():
    campeonatos = campeonatos_da_organizacao(usuario_id()) if tipo_usuario() == 'organizacao' else []
    return render_template('organizacao/inicio.html', campeonatos=campeonatos)

@app.route('/organizacao/novo-campeonato', methods=['GET', 'POST'])
def organizacao_novo_campeonato():
    if request.method == 'POST':
        criar_campeonato(
            organizacao_id=usuario_id(),
            nome=request.form.get('nome', ''),
            modalidade=request.form.get('modalidade', ''),
            data_inicio=request.form.get('data_inicio', ''),
            data_fim=request.form.get('data_fim', ''),
            max_participantes=request.form.get('max_participantes', 16, type=int),
            descricao=request.form.get('descricao', ''),
        )
        flash('Campeonato criado com sucesso!', 'success')
        return redirect(url_for('organizacao_inicio'))
    return render_template('organizacao/novo-campeonato.html')

@app.route('/organizacao/campeonato/<int:campeonato_id>/status', methods=['POST'])
def atualizar_campeonato_status(campeonato_id):
    novo = request.form.get('status', '')
    if novo in ('futuro', 'ativo', 'encerrado'):
        atualizar_status_campeonato(campeonato_id, novo)
        flash('Status atualizado.', 'success')
    return redirect(url_for('campeonato', id=campeonato_id))

@app.route('/organizacao/campeonato/<int:campeonato_id>/convidar', methods=['POST'])
def convidar_equipe(campeonato_id):
    equipe_id = request.form.get('equipe_id', type=int)
    if equipe_id:
        enviar_convite(campeonato_id, equipe_id)
        flash('Convite enviado!', 'success')
    return redirect(url_for('campeonato', id=campeonato_id))

@app.route('/historico')
def historico():
    tipo = tipo_usuario()
    if tipo == 'organizacao':
        todos = campeonatos_da_organizacao(usuario_id())
        encerrados = [c for c in todos if c['status'] == 'encerrado']
        return render_template('organizacao/historico.html', campeonatos=encerrados)
    elif tipo == 'equipe':
        todos    = campeonatos_da_equipe(usuario_id())
        passados = [c for c in todos if c['status'] == 'encerrado']
        return render_template('equipe/historico.html', campeonatos=passados)
    return redirect(url_for('homepage'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
