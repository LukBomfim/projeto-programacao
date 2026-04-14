#Nathan Jhones

import sqlite3

conexao = sqlite3.connect("unimacar.db")
cursor =conexao.cursor()
cursor.execute("""
               CREATE TABLE IF NOT EXISTS usuarios (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                     nome TEXT, 
                        email TEXT, 
                        cpf TEXT, 
                        data_de_nascimento TEXT,
                        senha TEXT,
                        telefone TEXT,
                        avaliacao REAL, 
                        biografia TEXT,
                        universidade TEXT
                    
                   
                   )
                   """)

cursor.execute("""
               CREATE TABLE IF NOT EXISTS Caronas (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   motorista INTEGER,
                   passageiro INTEGER,
                   destino TEXT,
                   horario TEXT,
                   data TEXT
)
            """) 

def cadastrar_usuario(nome, email, cpf, data_de_nascimento, senha, telefone, avaliacao, biografia):
    cursor.execute("""
                   INSERT INTO usuarios (nome, email, cpf, data_de_nascimento, senha, telefone, avaliacao, biografia)
                   values (?, ?, ?, ?, ?, ?, ?, ?)
                   """, (nome, email, cpf, data_de_nascimento, senha, telefone, avaliacao, biografia))
    conexao.commit()

def buscar_usuario(id):
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (id,))
    return cursor.fetchone()

def buscar_caronas():
    cursor.execute("SELECT * FROM caronas")
    return cursor.fetchall()

def buscar_usuarios_login(email,senha):
    cursor.execute("SELECT * FROM usuarios WHERE email = ? AND senha = ?",(email,senha))
    return cursor.fetchone()
    
def cadastrar_carona(motorista, passageiro, destino, horario, data):
    cursor.execute("""
                   
                   INSERT INTO caronas (motorista, passageiro, destino, horario, data)
                   values (?, ?, ?, ?, ?)
                   
                    """, (motorista, passageiro, destino, horario, data))
    conexao.commit()