# -*- coding: utf-8 -*-
import sys
import os

# Adiciona o diretório src ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Blueprint, request, jsonify
from main import token_required # Import from main
from models.models import db, Viagem, Destino, Despesa, CategoriaDespesa, MeioPagamento
from datetime import datetime

despesa_bp = Blueprint("despesa_bp", __name__)

# --- Despesas Endpoints (aninhados sob /api/destinos/<id_destino>/despesas) ---
@despesa_bp.route("/destinos/<int:id_destino>/despesas", methods=["POST"])
@token_required
def create_despesa(current_user, id_destino):
    data = request.get_json()
    if not data or not data.get("descricao") or data.get("valor") is None or not data.get("data"):
        return jsonify({"message": "Descrição, valor e data são obrigatórios"}), 400

    # Verificar se o destino pertence a uma viagem do usuário atual
    destino = Destino.query.join(Viagem).filter(Destino.id == id_destino, Viagem.usuario_id == current_user.id).first()
    if not destino:
        return jsonify({"message": "Destino não encontrado ou não pertence ao usuário"}), 404
    
    # Validar categoria_id se fornecido
    categoria = None
    if data.get("categoria_id"):
        categoria = CategoriaDespesa.query.filter_by(id=data["categoria_id"], usuario_id=current_user.id).first()
        if not categoria:
            return jsonify({"message": "Categoria não encontrada ou não pertence ao usuário"}), 400

    # Validar meio_pagamento_id se fornecido
    meio_pagamento = None
    if data.get("meio_pagamento_id"):
        meio_pagamento = MeioPagamento.query.filter_by(id=data["meio_pagamento_id"], usuario_id=current_user.id).first()
        if not meio_pagamento:
            return jsonify({"message": "Meio de pagamento não encontrado ou não pertence ao usuário"}), 400

    try:
        nova_despesa = Despesa(
            descricao=data["descricao"],
            valor=data["valor"],
            data=datetime.strptime(data["data"], "%Y-%m-%d").date(),
            observacoes=data.get("observacoes"),
            destino_id=id_destino,
            categoria_id=data.get("categoria_id"),
            meio_pagamento_id=data.get("meio_pagamento_id")
        )
        db.session.add(nova_despesa)
        db.session.commit()
        return jsonify({
            "id": nova_despesa.id,
            "descricao": nova_despesa.descricao,
            "valor": float(nova_despesa.valor),
            "data": nova_despesa.data.isoformat(),
            "observacoes": nova_despesa.observacoes,
            "destino_id": nova_despesa.destino_id,
            "categoria_id": nova_despesa.categoria_id,
            "meio_pagamento_id": nova_despesa.meio_pagamento_id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao criar despesa", "error": str(e)}), 500

@despesa_bp.route("/destinos/<int:id_destino>/despesas", methods=["GET"])
@token_required
def get_despesas_por_destino(current_user, id_destino):
    destino = Destino.query.join(Viagem).filter(Destino.id == id_destino, Viagem.usuario_id == current_user.id).first()
    if not destino:
        return jsonify({"message": "Destino não encontrado ou não pertence ao usuário"}), 404

    # Filtros opcionais
    query = Despesa.query.filter_by(destino_id=id_destino)
    if request.args.get("data_inicio"):
        query = query.filter(Despesa.data >= datetime.strptime(request.args.get("data_inicio"), "%Y-%m-%d").date())
    if request.args.get("data_fim"):
        query = query.filter(Despesa.data <= datetime.strptime(request.args.get("data_fim"), "%Y-%m-%d").date())
    if request.args.get("categoria_id"):
        query = query.filter(Despesa.categoria_id == int(request.args.get("categoria_id")))
    if request.args.get("meio_pagamento_id"):
        query = query.filter(Despesa.meio_pagamento_id == int(request.args.get("meio_pagamento_id")))
    
    despesas = query.order_by(Despesa.data.desc()).all()
    output = []
    for despesa in despesas:
        despesa_data = {
            "id": despesa.id,
            "descricao": despesa.descricao,
            "valor": float(despesa.valor),
            "data": despesa.data.isoformat(),
            "observacoes": despesa.observacoes,
            "categoria_id": despesa.categoria_id,
            "categoria_nome": despesa.categoria.nome if despesa.categoria else None, # Adicionado nome da categoria
            "meio_pagamento_id": despesa.meio_pagamento_id,
            "meio_pagamento_nome": despesa.meio_pagamento.nome if despesa.meio_pagamento else None # Adicionado nome do meio de pagamento
        }
        output.append(despesa_data)
    return jsonify(output), 200

@despesa_bp.route("/despesas/<int:id_despesa>", methods=["GET"])
@token_required
def get_despesa_by_id(current_user, id_despesa):
    despesa = Despesa.query.join(Destino).join(Viagem).filter(Despesa.id == id_despesa, Viagem.usuario_id == current_user.id).first()
    if not despesa:
        return jsonify({"message": "Despesa não encontrada"}), 404
    
    despesa_data = {
        "id": despesa.id,
        "descricao": despesa.descricao,
        "valor": float(despesa.valor),
        "data": despesa.data.isoformat(),
        "observacoes": despesa.observacoes,
        "destino_id": despesa.destino_id,
        "categoria_id": despesa.categoria_id,
        "meio_pagamento_id": despesa.meio_pagamento_id
    }
    return jsonify(despesa_data), 200

@despesa_bp.route("/despesas/<int:id_despesa>", methods=["PUT"])
@token_required
def update_despesa(current_user, id_despesa):
    data = request.get_json()
    despesa = Despesa.query.join(Destino).join(Viagem).filter(Despesa.id == id_despesa, Viagem.usuario_id == current_user.id).first()

    if not despesa:
        return jsonify({"message": "Despesa não encontrada"}), 404

    try:
        if "descricao" in data: despesa.descricao = data["descricao"]
        if "valor" in data: despesa.valor = data["valor"]
        if "data" in data: despesa.data = datetime.strptime(data["data"], "%Y-%m-%d").date() if data["data"] else None
        if "observacoes" in data: despesa.observacoes = data["observacoes"]
        if "categoria_id" in data:
            if data["categoria_id"] is None:
                despesa.categoria_id = None
            else:
                categoria = CategoriaDespesa.query.filter_by(id=data["categoria_id"], usuario_id=current_user.id).first()
                if not categoria:
                    return jsonify({"message": "Categoria inválida"}), 400
                despesa.categoria_id = data["categoria_id"]
        if "meio_pagamento_id" in data:
            if data["meio_pagamento_id"] is None:
                despesa.meio_pagamento_id = None
            else:
                meio_pagamento = MeioPagamento.query.filter_by(id=data["meio_pagamento_id"], usuario_id=current_user.id).first()
                if not meio_pagamento:
                    return jsonify({"message": "Meio de pagamento inválido"}), 400
                despesa.meio_pagamento_id = data["meio_pagamento_id"]
        
        db.session.commit()
        return jsonify({"message": "Despesa atualizada com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao atualizar despesa", "error": str(e)}), 500

@despesa_bp.route("/despesas/<int:id_despesa>", methods=["DELETE"])
@token_required
def delete_despesa(current_user, id_despesa):
    despesa = Despesa.query.join(Destino).join(Viagem).filter(Despesa.id == id_despesa, Viagem.usuario_id == current_user.id).first()
    if not despesa:
        return jsonify({"message": "Despesa não encontrada"}), 404
    
    try:
        db.session.delete(despesa)
        db.session.commit()
        return jsonify({"message": "Despesa deletada com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao deletar despesa", "error": str(e)}), 500

