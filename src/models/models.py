# -*- coding: utf-8 -*-
import sys
import os

# Adiciona o diretório src ao sys.path para permitir importações absolutas
# Isso é crucial para que o Flask encontre os módulos corretamente
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'Usuario'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    viagens = db.relationship('Viagem', backref='usuario', lazy=True)
    categorias_despesa = db.relationship('CategoriaDespesa', backref='usuario', lazy=True)
    meios_pagamento = db.relationship('MeioPagamento', backref='usuario', lazy=True)

    def __repr__(self):
        return f'<Usuario {self.username}>'

class Viagem(db.Model):
    __tablename__ = 'Viagem'
    id = db.Column(db.Integer, primary_key=True)
    nome_viagem = db.Column(db.String(255), nullable=False)
    data_inicio = db.Column(db.Date, nullable=True)
    data_fim = db.Column(db.Date, nullable=True)
    orcamento_total = db.Column(db.Numeric(10, 2), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('Usuario.id'), nullable=False)

    destinos = db.relationship('Destino', backref='viagem', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Viagem {self.nome_viagem}>'

class Destino(db.Model):
    __tablename__ = 'Destino'
    id = db.Column(db.Integer, primary_key=True)
    nome_cidade = db.Column(db.String(100), nullable=False)
    data_chegada = db.Column(db.Date, nullable=True)
    data_partida = db.Column(db.Date, nullable=True)
    orcamento_destino = db.Column(db.Numeric(10, 2), nullable=True)
    viagem_id = db.Column(db.Integer, db.ForeignKey('Viagem.id'), nullable=False)

    despesas = db.relationship('Despesa', backref='destino', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Destino {self.nome_cidade}>'

class CategoriaDespesa(db.Model):
    __tablename__ = 'CategoriaDespesa'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('Usuario.id'), nullable=False)
    # Adicionar unique=True se o nome da categoria deve ser único por usuário
    # db.UniqueConstraint('nome', 'usuario_id', name='uq_categoria_usuario')

    despesas = db.relationship('Despesa', backref='categoria', lazy=True)

    def __repr__(self):
        return f'<CategoriaDespesa {self.nome}>'

class MeioPagamento(db.Model):
    __tablename__ = 'MeioPagamento'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('Usuario.id'), nullable=False)
    # Adicionar unique=True se o nome do meio de pagamento deve ser único por usuário
    # db.UniqueConstraint('nome', 'usuario_id', name='uq_meiopagamento_usuario')

    despesas = db.relationship('Despesa', backref='meio_pagamento', lazy=True)

    def __repr__(self):
        return f'<MeioPagamento {self.nome}>'

class Despesa(db.Model):
    __tablename__ = 'Despesa'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(255), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    data = db.Column(db.Date, nullable=False)
    observacoes = db.Column(db.Text, nullable=True)
    destino_id = db.Column(db.Integer, db.ForeignKey('Destino.id'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('CategoriaDespesa.id'), nullable=True)
    meio_pagamento_id = db.Column(db.Integer, db.ForeignKey('MeioPagamento.id'), nullable=True)

    def __repr__(self):
        return f'<Despesa {self.descricao} - {self.valor}>'

