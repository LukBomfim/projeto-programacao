import sqlite3
import hashlib
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'bet404.db')


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # ── Usuário comum ────────────────────────────────────────────────────────
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuario (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nome        TEXT    NOT NULL,
            cpf         TEXT    NOT NULL UNIQUE,
            nascimento  TEXT    NOT NULL,
            numero      TEXT,
            email       TEXT    NOT NULL UNIQUE,
            senha_hash  TEXT    NOT NULL,
            saldo       REAL    NOT NULL DEFAULT 0.0,
            criado_em   TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    ''')

    # ── Equipe esportiva ─────────────────────────────────────────────────────
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipe (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nome        TEXT    NOT NULL,
            cnpj        TEXT    NOT NULL UNIQUE,
            numero      TEXT,
            email       TEXT    NOT NULL UNIQUE,
            senha_hash  TEXT    NOT NULL,
            modalidade  TEXT    NOT NULL,
            criado_em   TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    ''')

    # ── Organização ──────────────────────────────────────────────────────────
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS organizacao (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nome        TEXT    NOT NULL,
            cnpj        TEXT    NOT NULL UNIQUE,
            numero      TEXT,
            email       TEXT    NOT NULL UNIQUE,
            senha_hash  TEXT    NOT NULL,
            criado_em   TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    ''')

    # Modalidades que uma organização suporta (N:N)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS organizacao_modalidade (
            organizacao_id  INTEGER NOT NULL REFERENCES organizacao(id) ON DELETE CASCADE,
            modalidade      TEXT    NOT NULL,
            PRIMARY KEY (organizacao_id, modalidade)
        )
    ''')

    # ── Campeonato ───────────────────────────────────────────────────────────
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS campeonato (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            organizacao_id   INTEGER NOT NULL REFERENCES organizacao(id),
            nome             TEXT    NOT NULL,
            modalidade       TEXT    NOT NULL,
            data_inicio      TEXT    NOT NULL,
            data_fim         TEXT    NOT NULL,
            max_participantes INTEGER NOT NULL DEFAULT 16,
            descricao        TEXT,
            status           TEXT    NOT NULL DEFAULT 'futuro'
                             CHECK(status IN ('futuro', 'ativo', 'encerrado')),
            criado_em        TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    ''')

    # ── Inscrição de equipe em campeonato ────────────────────────────────────
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inscricao (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            campeonato_id   INTEGER NOT NULL REFERENCES campeonato(id) ON DELETE CASCADE,
            equipe_id       INTEGER NOT NULL REFERENCES equipe(id)     ON DELETE CASCADE,
            status          TEXT    NOT NULL DEFAULT 'pendente'
                            CHECK(status IN ('pendente', 'aceito', 'recusado')),
            inscrito_em     TEXT    NOT NULL DEFAULT (datetime('now')),
            UNIQUE (campeonato_id, equipe_id)
        )
    ''')

    # ── Convite (organização convida equipe) ─────────────────────────────────
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS convite (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            campeonato_id   INTEGER NOT NULL REFERENCES campeonato(id) ON DELETE CASCADE,
            equipe_id       INTEGER NOT NULL REFERENCES equipe(id)     ON DELETE CASCADE,
            status          TEXT    NOT NULL DEFAULT 'pendente'
                            CHECK(status IN ('pendente', 'aceito', 'recusado')),
            enviado_em      TEXT    NOT NULL DEFAULT (datetime('now')),
            UNIQUE (campeonato_id, equipe_id)
        )
    ''')

    # ── Partida ──────────────────────────────────────────────────────────────
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS partida (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            campeonato_id   INTEGER NOT NULL REFERENCES campeonato(id) ON DELETE CASCADE,
            equipe_a_id     INTEGER NOT NULL REFERENCES equipe(id),
            equipe_b_id     INTEGER NOT NULL REFERENCES equipe(id),
            data            TEXT    NOT NULL,
            resultado_a     INTEGER,
            resultado_b     INTEGER,
            status          TEXT    NOT NULL DEFAULT 'agendada'
                            CHECK(status IN ('agendada', 'em_andamento', 'finalizada')),
            criado_em       TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    ''')

    # ── Atleta / Subdivisão de equipe ────────────────────────────────────────
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS atleta (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            equipe_id       INTEGER NOT NULL REFERENCES equipe(id) ON DELETE CASCADE,
            nome            TEXT    NOT NULL,
            categoria       TEXT,
            foto_path       TEXT,
            disponivel      INTEGER NOT NULL DEFAULT 1,
            adicionado_em   TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    ''')

    # ── Aposta ───────────────────────────────────────────────────────────────
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aposta (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id      INTEGER NOT NULL REFERENCES usuario(id),
            partida_id      INTEGER NOT NULL REFERENCES partida(id),
            equipe_vencedora_id INTEGER REFERENCES equipe(id),
            valor           REAL    NOT NULL CHECK(valor > 0),
            odd             REAL    NOT NULL DEFAULT 1.0,
            resultado       TEXT    DEFAULT NULL
                            CHECK(resultado IN ('ganhou', 'perdeu', NULL)),
            apostado_em     TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    ''')

    conn.commit()
    conn.close()
    print(f"[DB] Banco de dados inicializado em: {DB_PATH}")


# ── Helpers de senha ─────────────────────────────────────────────────────────

def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()


# ── CRUD: Usuário ─────────────────────────────────────────────────────────────

def criar_usuario(nome, cpf, nascimento, numero, email, senha):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO usuario (nome, cpf, nascimento, numero, email, senha_hash) VALUES (?,?,?,?,?,?)",
            (nome, cpf, nascimento, numero, email, hash_senha(senha))
        )
        conn.commit()
        return True, "Usuário cadastrado com sucesso."
    except sqlite3.IntegrityError as e:
        return False, "CPF ou e-mail já cadastrado."
    finally:
        conn.close()


def buscar_usuario_por_cpf(cpf):
    conn = get_connection()
    row = conn.execute("SELECT * FROM usuario WHERE cpf = ?", (cpf,)).fetchone()
    conn.close()
    return row


def autenticar_usuario(cpf_ou_cnpj, senha):
    """Retorna (tipo, objeto) ou (None, None)."""
    h = hash_senha(senha)
    conn = get_connection()
    u = conn.execute("SELECT * FROM usuario WHERE cpf = ? AND senha_hash = ?", (cpf_ou_cnpj, h)).fetchone()
    if u:
        conn.close()
        return 'usuario', u
    e = conn.execute("SELECT * FROM equipe WHERE cnpj = ? AND senha_hash = ?", (cpf_ou_cnpj, h)).fetchone()
    if e:
        conn.close()
        return 'equipe', e
    o = conn.execute("SELECT * FROM organizacao WHERE cnpj = ? AND senha_hash = ?", (cpf_ou_cnpj, h)).fetchone()
    if o:
        conn.close()
        return 'organizacao', o
    conn.close()
    return None, None


# ── CRUD: Equipe ──────────────────────────────────────────────────────────────

def criar_equipe(nome, cnpj, numero, email, senha, modalidade):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO equipe (nome, cnpj, numero, email, senha_hash, modalidade) VALUES (?,?,?,?,?,?)",
            (nome, cnpj, numero, email, hash_senha(senha), modalidade)
        )
        conn.commit()
        return True, "Equipe cadastrada com sucesso."
    except sqlite3.IntegrityError:
        return False, "CNPJ ou e-mail já cadastrado."
    finally:
        conn.close()


def buscar_equipe(equipe_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM equipe WHERE id = ?", (equipe_id,)).fetchone()
    conn.close()
    return row


# ── CRUD: Organização ─────────────────────────────────────────────────────────

def criar_organizacao(nome, cnpj, numero, email, senha, modalidades: list):
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO organizacao (nome, cnpj, numero, email, senha_hash) VALUES (?,?,?,?,?)",
            (nome, cnpj, numero, email, hash_senha(senha))
        )
        org_id = cur.lastrowid
        for m in modalidades:
            conn.execute(
                "INSERT INTO organizacao_modalidade (organizacao_id, modalidade) VALUES (?,?)",
                (org_id, m)
            )
        conn.commit()
        return True, "Organização cadastrada com sucesso."
    except sqlite3.IntegrityError:
        return False, "CNPJ ou e-mail já cadastrado."
    finally:
        conn.close()


# ── CRUD: Campeonato ──────────────────────────────────────────────────────────

def criar_campeonato(organizacao_id, nome, modalidade, data_inicio, data_fim, max_participantes, descricao):
    conn = get_connection()
    conn.execute(
        '''INSERT INTO campeonato
           (organizacao_id, nome, modalidade, data_inicio, data_fim, max_participantes, descricao)
           VALUES (?,?,?,?,?,?,?)''',
        (organizacao_id, nome, modalidade, data_inicio, data_fim, max_participantes, descricao)
    )
    conn.commit()
    conn.close()


def listar_campeonatos(status=None):
    conn = get_connection()
    if status:
        rows = conn.execute("SELECT * FROM campeonato WHERE status = ? ORDER BY data_inicio", (status,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM campeonato ORDER BY data_inicio").fetchall()
    conn.close()
    return rows


def buscar_campeonato(campeonato_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM campeonato WHERE id = ?", (campeonato_id,)).fetchone()
    conn.close()
    return row


def atualizar_status_campeonato(campeonato_id, status):
    conn = get_connection()
    conn.execute("UPDATE campeonato SET status = ? WHERE id = ?", (status, campeonato_id))
    conn.commit()
    conn.close()


def campeonatos_da_organizacao(organizacao_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM campeonato WHERE organizacao_id = ? ORDER BY data_inicio DESC",
        (organizacao_id,)
    ).fetchall()
    conn.close()
    return rows


# ── CRUD: Convite ─────────────────────────────────────────────────────────────

def enviar_convite(campeonato_id, equipe_id):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO convite (campeonato_id, equipe_id) VALUES (?,?)",
            (campeonato_id, equipe_id)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def convites_da_equipe(equipe_id):
    conn = get_connection()
    rows = conn.execute('''
        SELECT c.*, camp.nome AS campeonato_nome, camp.modalidade, camp.data_inicio
        FROM convite c
        JOIN campeonato camp ON camp.id = c.campeonato_id
        WHERE c.equipe_id = ? AND c.status = 'pendente'
    ''', (equipe_id,)).fetchall()
    conn.close()
    return rows


def responder_convite(convite_id, aceito: bool):
    status = 'aceito' if aceito else 'recusado'
    conn = get_connection()
    conn.execute("UPDATE convite SET status = ? WHERE id = ?", (status, convite_id))
    conn.commit()
    conn.close()


# ── CRUD: Inscrição ───────────────────────────────────────────────────────────

def inscrever_equipe(campeonato_id, equipe_id):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO inscricao (campeonato_id, equipe_id) VALUES (?,?)",
            (campeonato_id, equipe_id)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def campeonatos_da_equipe(equipe_id):
    conn = get_connection()
    rows = conn.execute('''
        SELECT camp.*, i.status AS status_inscricao
        FROM inscricao i
        JOIN campeonato camp ON camp.id = i.campeonato_id
        WHERE i.equipe_id = ?
        ORDER BY camp.data_inicio DESC
    ''', (equipe_id,)).fetchall()
    conn.close()
    return rows


# ── CRUD: Partida ─────────────────────────────────────────────────────────────

def criar_partida(campeonato_id, equipe_a_id, equipe_b_id, data):
    conn = get_connection()
    conn.execute(
        "INSERT INTO partida (campeonato_id, equipe_a_id, equipe_b_id, data) VALUES (?,?,?,?)",
        (campeonato_id, equipe_a_id, equipe_b_id, data)
    )
    conn.commit()
    conn.close()


def buscar_partida(partida_id):
    conn = get_connection()
    row = conn.execute('''
        SELECT p.*,
               ea.nome AS equipe_a_nome,
               eb.nome AS equipe_b_nome,
               camp.nome AS campeonato_nome,
               camp.modalidade
        FROM partida p
        JOIN equipe ea   ON ea.id = p.equipe_a_id
        JOIN equipe eb   ON eb.id = p.equipe_b_id
        JOIN campeonato camp ON camp.id = p.campeonato_id
        WHERE p.id = ?
    ''', (partida_id,)).fetchone()
    conn.close()
    return row


def listar_partidas(status=None):
    conn = get_connection()
    if status:
        rows = conn.execute('''
            SELECT p.*, ea.nome AS equipe_a_nome, eb.nome AS equipe_b_nome, camp.modalidade
            FROM partida p
            JOIN equipe ea ON ea.id = p.equipe_a_id
            JOIN equipe eb ON eb.id = p.equipe_b_id
            JOIN campeonato camp ON camp.id = p.campeonato_id
            WHERE p.status = ?
            ORDER BY p.data
        ''', (status,)).fetchall()
    else:
        rows = conn.execute('''
            SELECT p.*, ea.nome AS equipe_a_nome, eb.nome AS equipe_b_nome, camp.modalidade
            FROM partida p
            JOIN equipe ea ON ea.id = p.equipe_a_id
            JOIN equipe eb ON eb.id = p.equipe_b_id
            JOIN campeonato camp ON camp.id = p.campeonato_id
            ORDER BY p.data
        ''').fetchall()
    conn.close()
    return rows


def finalizar_partida(partida_id, resultado_a, resultado_b):
    conn = get_connection()
    conn.execute(
        "UPDATE partida SET resultado_a=?, resultado_b=?, status='finalizada' WHERE id=?",
        (resultado_a, resultado_b, partida_id)
    )
    conn.commit()
    conn.close()


# ── CRUD: Atleta ──────────────────────────────────────────────────────────────

def adicionar_atleta(equipe_id, nome, categoria, foto_path=None):
    conn = get_connection()
    conn.execute(
        "INSERT INTO atleta (equipe_id, nome, categoria, foto_path) VALUES (?,?,?,?)",
        (equipe_id, nome, categoria, foto_path)
    )
    conn.commit()
    conn.close()


def atletas_da_equipe(equipe_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM atleta WHERE equipe_id = ? ORDER BY nome",
        (equipe_id,)
    ).fetchall()
    conn.close()
    return rows


def remover_atleta(atleta_id):
    conn = get_connection()
    conn.execute("DELETE FROM atleta WHERE id = ?", (atleta_id,))
    conn.commit()
    conn.close()


# ── CRUD: Aposta ──────────────────────────────────────────────────────────────

def fazer_aposta(usuario_id, partida_id, equipe_vencedora_id, valor, odd=1.0):
    conn = get_connection()
    saldo = conn.execute("SELECT saldo FROM usuario WHERE id = ?", (usuario_id,)).fetchone()['saldo']
    if saldo < valor:
        conn.close()
        return False, "Saldo insuficiente."
    conn.execute(
        "INSERT INTO aposta (usuario_id, partida_id, equipe_vencedora_id, valor, odd) VALUES (?,?,?,?,?)",
        (usuario_id, partida_id, equipe_vencedora_id, valor, odd)
    )
    conn.execute("UPDATE usuario SET saldo = saldo - ? WHERE id = ?", (valor, usuario_id))
    conn.commit()
    conn.close()
    return True, "Aposta registrada."


def apostas_do_usuario(usuario_id):
    conn = get_connection()
    rows = conn.execute('''
        SELECT a.*, p.data AS partida_data, p.status AS partida_status,
               ea.nome AS equipe_a_nome, eb.nome AS equipe_b_nome,
               ev.nome AS equipe_apostada_nome,
               camp.modalidade
        FROM aposta a
        JOIN partida p    ON p.id = a.partida_id
        JOIN equipe ea    ON ea.id = p.equipe_a_id
        JOIN equipe eb    ON eb.id = p.equipe_b_id
        LEFT JOIN equipe ev ON ev.id = a.equipe_vencedora_id
        JOIN campeonato camp ON camp.id = p.campeonato_id
        WHERE a.usuario_id = ?
        ORDER BY a.apostado_em DESC
    ''', (usuario_id,)).fetchall()
    conn.close()
    return rows


# ── Dados de exemplo ──────────────────────────────────────────────────────────

def popular_dados_exemplo():
    """Insere dados de demonstração se o banco estiver vazio."""
    conn = get_connection()
    if conn.execute("SELECT COUNT(*) FROM usuario").fetchone()[0] > 0:
        conn.close()
        return

    # Usuário comum
    conn.execute(
        "INSERT INTO usuario (nome, cpf, nascimento, numero, email, senha_hash, saldo) VALUES (?,?,?,?,?,?,?)",
        ("João Silva", "111.111.111-11", "1990-05-15", "(11)91111-1111",
         "joao@email.com", hash_senha("123456"), 500.0)
    )

    # Equipe
    conn.execute(
        "INSERT INTO equipe (nome, cnpj, numero, email, senha_hash, modalidade) VALUES (?,?,?,?,?,?)",
        ("Equipe Dragões", "11.111.111/0001-01", "(11)93333-3333",
         "dragoes@email.com", hash_senha("123456"), "Futebol")
    )
    conn.execute(
        "INSERT INTO equipe (nome, cnpj, numero, email, senha_hash, modalidade) VALUES (?,?,?,?,?,?)",
        ("Equipe Fênix", "22.222.222/0001-02", "(11)94444-4444",
         "fenix@email.com", hash_senha("123456"), "Futebol")
    )

    # Organização
    conn.execute(
        "INSERT INTO organizacao (nome, cnpj, numero, email, senha_hash) VALUES (?,?,?,?,?)",
        ("Liga Nacional", "33.333.333/0001-03", "(11)95555-5555",
         "liga@email.com", hash_senha("123456"))
    )
    conn.execute(
        "INSERT INTO organizacao_modalidade (organizacao_id, modalidade) VALUES (1,'Futebol'),(1,'Basquete')"
    )

    # Campeonato
    conn.execute(
        '''INSERT INTO campeonato (organizacao_id, nome, modalidade, data_inicio, data_fim,
           max_participantes, descricao, status)
           VALUES (1,'Copa bet404','Futebol','2026-05-10','2026-06-10',16,'Grande campeonato nacional','futuro')'''
    )
    conn.execute(
        '''INSERT INTO campeonato (organizacao_id, nome, modalidade, data_inicio, data_fim,
           max_participantes, descricao, status)
           VALUES (1,'Liga Verão','Futebol','2026-04-01','2026-04-30',8,'Liga em andamento','ativo')'''
    )
    conn.execute(
        '''INSERT INTO campeonato (organizacao_id, nome, modalidade, data_inicio, data_fim,
           max_participantes, descricao, status)
           VALUES (1,'Torneio Inverno 2025','Futebol','2025-07-01','2025-08-01',8,'Encerrado','encerrado')'''
    )

    # Inscrições
    conn.execute("INSERT INTO inscricao (campeonato_id, equipe_id, status) VALUES (2,1,'aceito')")
    conn.execute("INSERT INTO inscricao (campeonato_id, equipe_id, status) VALUES (2,2,'aceito')")

    # Convite
    conn.execute("INSERT INTO convite (campeonato_id, equipe_id) VALUES (1,1)")

    # Partida
    conn.execute(
        "INSERT INTO partida (campeonato_id, equipe_a_id, equipe_b_id, data, status) VALUES (2,1,2,'2026-04-20','agendada')"
    )
    conn.execute(
        '''INSERT INTO partida (campeonato_id, equipe_a_id, equipe_b_id, data,
           resultado_a, resultado_b, status)
           VALUES (3,1,2,'2025-07-15',2,1,'finalizada')'''
    )

    # Atletas
    conn.execute("INSERT INTO atleta (equipe_id, nome, categoria, disponivel) VALUES (1,'Carlos Alves','Atacante',1)")
    conn.execute("INSERT INTO atleta (equipe_id, nome, categoria, disponivel) VALUES (1,'Pedro Lima','Goleiro',1)")

    # Aposta
    conn.execute(
        "INSERT INTO aposta (usuario_id, partida_id, equipe_vencedora_id, valor, odd) VALUES (1,1,1,50.0,1.8)"
    )

    conn.commit()
    conn.close()
    print("[DB] Dados de exemplo inseridos.")


if __name__ == '__main__':
    init_db()
    popular_dados_exemplo()
    print("[DB] Pronto!")
