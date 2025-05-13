# -*- coding: utf-8 -*-
import sys
import os

# Adiciona o diretório src ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Blueprint, request, jsonify
from main import token_required # Import from main
from models.models import db, Viagem, Destino, Despesa, CategoriaDespesa, MeioPagamento
from datetime import datetime

viagem_bp = Blueprint("viagem_bp", __name__)

# --- Viagens Endpoints ---
@viagem_bp.route("/viagens", methods=["POST"])
@token_required
def create_viagem(current_user):
    data = request.get_json()
    if not data or not data.get("nome_viagem"):
        return jsonify({"message": "Nome da viagem é obrigatório"}), 400

    try:
        nova_viagem = Viagem(
            nome_viagem=data["nome_viagem"],
            data_inicio=datetime.strptime(data["data_inicio"], "%Y-%m-%d").date() if data.get("data_inicio") else None,
            data_fim=datetime.strptime(data["data_fim"], "%Y-%m-%d").date() if data.get("data_fim") else None,
            orcamento_total=data.get("orcamento_total"),
            usuario_id=current_user.id
        )
        db.session.add(nova_viagem)
        db.session.commit()
        return jsonify({
            "id": nova_viagem.id,
            "nome_viagem": nova_viagem.nome_viagem,
            "data_inicio": nova_viagem.data_inicio.isoformat() if nova_viagem.data_inicio else None,
            "data_fim": nova_viagem.data_fim.isoformat() if nova_viagem.data_fim else None,
            "orcamento_total": float(nova_viagem.orcamento_total) if nova_viagem.orcamento_total else None
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao criar viagem", "error": str(e)}), 500

@viagem_bp.route("/viagens", methods=["GET"])
@token_required
def get_viagens(current_user):
    viagens = Viagem.query.filter_by(usuario_id=current_user.id).all()
    output = []
    for viagem in viagens:
        viagem_data = {
            "id": viagem.id,
            "nome_viagem": viagem.nome_viagem,
            "data_inicio": viagem.data_inicio.isoformat() if viagem.data_inicio else None,
            "data_fim": viagem.data_fim.isoformat() if viagem.data_fim else None,
            "orcamento_total": float(viagem.orcamento_total) if viagem.orcamento_total else None
        }
        output.append(viagem_data)
    return jsonify(output), 200

@viagem_bp.route("/viagens/<int:id_viagem>", methods=["GET"])
@token_required
def get_viagem_by_id(current_user, id_viagem):
    viagem = Viagem.query.filter_by(id=id_viagem, usuario_id=current_user.id).first()
    if not viagem:
        return jsonify({"message": "Viagem não encontrada"}), 404
    
    viagem_data = {
        "id": viagem.id,
        "nome_viagem": viagem.nome_viagem,
        "data_inicio": viagem.data_inicio.isoformat() if viagem.data_inicio else None,
        "data_fim": viagem.data_fim.isoformat() if viagem.data_fim else None,
        "orcamento_total": float(viagem.orcamento_total) if viagem.orcamento_total else None,
        "destinos": [
            {
                "id": d.id, 
                "nome_cidade": d.nome_cidade,
                "data_chegada": d.data_chegada.isoformat() if d.data_chegada else None,
                "data_partida": d.data_partida.isoformat() if d.data_partida else None,
                "orcamento_destino": float(d.orcamento_destino) if d.orcamento_destino else None
            } for d in viagem.destinos
        ]
    }
    return jsonify(viagem_data), 200

@viagem_bp.route("/viagens/<int:id_viagem>", methods=["PUT"])
@token_required
def update_viagem(current_user, id_viagem):
    data = request.get_json()
    viagem = Viagem.query.filter_by(id=id_viagem, usuario_id=current_user.id).first()

    if not viagem:
        return jsonify({"message": "Viagem não encontrada"}), 404

    try:
        if "nome_viagem" in data: viagem.nome_viagem = data["nome_viagem"]
        if "data_inicio" in data: viagem.data_inicio = datetime.strptime(data["data_inicio"], "%Y-%m-%d").date() if data["data_inicio"] else None
        if "data_fim" in data: viagem.data_fim = datetime.strptime(data["data_fim"], "%Y-%m-%d").date() if data["data_fim"] else None
        if "orcamento_total" in data: viagem.orcamento_total = data["orcamento_total"]
        
        db.session.commit()
        return jsonify({"message": "Viagem atualizada com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao atualizar viagem", "error": str(e)}), 500

@viagem_bp.route("/viagens/<int:id_viagem>", methods=["DELETE"])
@token_required
def delete_viagem(current_user, id_viagem):
    viagem = Viagem.query.filter_by(id=id_viagem, usuario_id=current_user.id).first()
    if not viagem:
        return jsonify({"message": "Viagem não encontrada"}), 404
    
    try:
        db.session.delete(viagem)
        db.session.commit()
        return jsonify({"message": "Viagem deletada com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao deletar viagem", "error": str(e)}), 500

# TODO: Implementar endpoints para Destinos, Despesas, Categorias, Meios de Pagamento e Relatórios/Gráficos
# Os endpoints de Destino devem ser aninhados sob /viagens/<id_viagem>/destinos
# Os endpoints de Despesa devem ser aninhados sob /destinos/<id_destino>/despesas

