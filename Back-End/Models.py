from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class UsuarioComum(db.Model):
    __tablename__ = 'usuarios'

    id         = db.Column(db.Integer, primary_key=True)
    nome       = db.Column(db.String(100), nullable=False)
    cpf        = db.Column(db.String(14), unique=True, nullable=False)
    data_nasc  = db.Column(db.Date)
    telefone   = db.Column(db.String(20))
    email      = db.Column(db.String(150), unique=True, nullable=False)
    senha_hash = db.Column(db.String(256), nullable=False)