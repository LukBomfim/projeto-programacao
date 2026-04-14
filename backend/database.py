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
                        TELEFONE TEXT,
                        AVALIACAO REAL, 
                        BIOGRAFIA TEXT,
                        
                    
                   
                   )
                   """)

cursor.execute("""
               CREATE TABLE IF NOT EXISTS Caronas (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   Motorista INTEGER,
                   Passageiro INTEGER,
                   Destino TEXT,
                   Horario TEXT
)
            """) 

def cadastrar_usuario(nome, email, cpf, data_de_nascimento, senha, telefone, avaliacao, biografia):
    cursor.execute("""
                   INSERT INTO usuarios (nome, email, cpf, data_de_nascimento, senha, telefone, avaliacao, biografia)
                   values (?, ?, ?, ?, ?, ?, ?, ?)
                   """, (nome, email, cpf, data_de_nascimento, senha, telefone, avaliacao, biografia))

def buscar_usuario(id):
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (id,))
    return cursor.fetchone()

def buscar_caronas():
    cursor.execute("SELECT * FROM caronas")
    return cursor.fetchall()