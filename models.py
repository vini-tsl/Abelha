from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    cpf = db.Column(db.String(14), unique=True)
    tipo_usuario = db.Column(db.String(20), default='Participante')
    matricula = db.Column(db.String(12))
    senha = db.Column(db.String(200), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Usuario {self.nome}>'

class Evidencia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    anotacoes = db.Column(db.Text)
    foto = db.Column(db.String(200))
    video = db.Column(db.String(200))
    audio = db.Column(db.String(200))
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    usuario = db.relationship('Usuario', backref=db.backref('evidencias', lazy=True))

    def __repr__(self):
        return f'<Evidencia {self.id}>'

class EstadoColmeia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    especie = db.Column(db.String(100))
    peso = db.Column(db.Float)
    contagem_abelhas = db.Column(db.Integer)
    observacoes = db.Column(db.Text)
    estado = db.Column(db.String(20), default='normal')
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    usuario = db.relationship('Usuario', backref=db.backref('estados_colmeia', lazy=True))

    def __repr__(self):
        return f'<EstadoColmeia {self.id}>'

class CapturaAbelha(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    observacao = db.Column(db.Text, nullable=False)
    data_captura = db.Column(db.DateTime, default=datetime.utcnow)
    
    usuario = db.relationship('Usuario', backref=db.backref('capturas', lazy=True))

    def __repr__(self):
        return f'<CapturaAbelha {self.id}>'

class SaudeAbelha(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    nivel_atividade = db.Column(db.Integer)
    presenca_alimento = db.Column(db.Integer)
    abelhas_visiveis = db.Column(db.Integer)
    pregas_problemas = db.Column(db.Text)
    observacoes_gerais = db.Column(db.Text)
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    usuario = db.relationship('Usuario', backref=db.backref('registros_saude', lazy=True))

    def __repr__(self):
        return f'<SaudeAbelha {self.id}>'

class ProducaoMel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    quantidade = db.Column(db.Float, nullable=False)
    data_colheita = db.Column(db.Date, nullable=False)
    observacoes = db.Column(db.Text)
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    usuario = db.relationship('Usuario', backref=db.backref('producoes_mel', lazy=True))

    def __repr__(self):
        return f'<ProducaoMel {self.id}>'