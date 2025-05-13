# -*- coding: utf-8 -*-
import sys
import os

# Adiciona o diretório src ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Blueprint, request, jsonify
from main import token_required # Import from main
from models.models import db, Viagem, Destino
from datetime import datetime

destino_bp = Blueprint("destino_bp", __name__)

# --- Destinos Endpoints (aninhados sob /api/viagens/<id_viagem>/destinos) ---
@destino_bp.route("/viagens/<int:id_viagem>/destinos", methods=["POST"])
@token_required
def create_destino(current_user, id_viagem):
    data = request.get_json()
    if not data or not data.get("nome_cidade"):
        return jsonify({"message": "Nome da cidade é obrigatório"}), 400

    viagem = Viagem.query.filter_by(id=id_viagem, usuario_id=current_user.id).first()
    if not viagem:
        return jsonify({"message": "Viagem não encontrada"}), 404

    try:
        novo_destino = Destino(
            nome_cidade=data["nome_cidade"],
            data_chegada=datetime.strptime(data["data_chegada"], "%Y-%m-%d").date() if data.get("data_chegada") else None,
            data_partida=datetime.strptime(data["data_partida"], "%Y-%m-%d").date() if data.get("data_partida") else None,
            orcamento_destino=data.get("orcamento_destino"),
            viagem_id=id_viagem
        )
        db.session.add(novo_destino)
        db.session.commit()
        return jsonify({
            "id": novo_destino.id,
            "nome_cidade": novo_destino.nome_cidade,
            "data_chegada": novo_destino.data_chegada.isoformat() if novo_destino.data_chegada else None,
            "data_partida": novo_destino.data_partida.isoformat() if novo_destino.data_partida else None,
            "orcamento_destino": float(novo_destino.orcamento_destino) if novo_destino.orcamento_destino else None,
            "viagem_id": novo_destino.viagem_id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao criar destino", "error": str(e)}), 500

@destino_bp.route("/viagens/<int:id_viagem>/destinos", methods=["GET"])
@token_required
def get_destinos_por_viagem(current_user, id_viagem):
    viagem = Viagem.query.filter_by(id=id_viagem, usuario_id=current_user.id).first()
    if not viagem:
        return jsonify({"message": "Viagem não encontrada"}), 404

    destinos = Destino.query.filter_by(viagem_id=id_viagem).all()
    output = []
    for destino in destinos:
        destino_data = {
            "id": destino.id,
            "nome_cidade": destino.nome_cidade,
            "data_chegada": destino.data_chegada.isoformat() if destino.data_chegada else None,
            "data_partida": destino.data_partida.isoformat() if destino.data_partida else None,
            "orcamento_destino": float(destino.orcamento_destino) if destino.orcamento_destino else None
        }
        output.append(destino_data)
    return jsonify(output), 200

@destino_bp.route("/destinos/<int:id_destino>", methods=["GET"])
@token_required
def get_destino_by_id(current_user, id_destino):
    # Verificar se o destino pertence a uma viagem do usuário atual
    destino = Destino.query.join(Viagem).filter(Destino.id == id_destino, Viagem.usuario_id == current_user.id).first()
    if not destino:
        return jsonify({"message": "Destino não encontrado"}), 404
    
    destino_data = {
        "id": destino.id,
        "nome_cidade": destino.nome_cidade,
        "data_chegada": destino.data_chegada.isoformat() if destino.data_chegada else None,
        "data_partida": destino.data_partida.isoformat() if destino.data_partida else None,
        "orcamento_destino": float(destino.orcamento_destino) if destino.orcamento_destino else None,
        "viagem_id": destino.viagem_id,
        "despesas": [
            {
                "id": d.id,
                "descricao": d.descricao,
                "valor": float(d.valor),
                "data": d.data.isoformat(),
                "observacoes": d.observacoes,
                "categoria_id": d.categoria_id,
                "meio_pagamento_id": d.meio_pagamento_id
            } for d in destino.despesas
        ]
    }
    return jsonify(destino_data), 200

@destino_bp.route("/destinos/<int:id_destino>", methods=["PUT"])
@token_required
def update_destino(current_user, id_destino):
    data = request.get_json()
    destino = Destino.query.join(Viagem).filter(Destino.id == id_destino, Viagem.usuario_id == current_user.id).first()

    if not destino:
        return jsonify({"message": "Destino não encontrado"}), 404

    try:
        if "nome_cidade" in data: destino.nome_cidade = data["nome_cidade"]
        if "data_chegada" in data: destino.data_chegada = datetime.strptime(data["data_chegada"], "%Y-%m-%d").date() if data["data_chegada"] else None
        if "data_partida" in data: destino.data_partida = datetime.strptime(data["data_partida"], "%Y-%m-%d").date() if data["data_partida"] else None
        if "orcamento_destino" in data: destino.orcamento_destino = data["orcamento_destino"]
        
        db.session.commit()
        return jsonify({"message": "Destino atualizado com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao atualizar destino", "error": str(e)}), 500

@destino_bp.route("/destinos/<int:id_destino>", methods=["DELETE"])
@token_required
def delete_destino(current_user, id_destino):
    destino = Destino.query.join(Viagem).filter(Destino.id == id_destino, Viagem.usuario_id == current_user.id).first()
    if not destino:
        return jsonify({"message": "Destino não encontrado"}), 404
    
    try:
        db.session.delete(destino)
        db.session.commit()
        return jsonify({"message": "Destino deletado com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao deletar destino", "error": str(e)}), 500

