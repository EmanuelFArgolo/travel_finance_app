# -*- coding: utf-8 -*-
import sys
import os

# Adiciona o diretório src ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Blueprint, request, jsonify
from main import token_required # Import from main
from models.models import db, CategoriaDespesa, MeioPagamento

dropdown_bp = Blueprint("dropdown_bp", __name__)

# --- Categorias de Despesa Endpoints ---
@dropdown_bp.route("/categorias", methods=["POST"])
@token_required
def create_categoria(current_user):
    data = request.get_json()
    if not data or not data.get("nome"):
        return jsonify({"message": "Nome da categoria é obrigatório"}), 400

    # Verificar se já existe uma categoria com o mesmo nome para este usuário
    existente = CategoriaDespesa.query.filter_by(nome=data["nome"], usuario_id=current_user.id).first()
    if existente:
        return jsonify({"message": f"Categoria \'{data['nome']}\' já existe."}), 409

    try:
        nova_categoria = CategoriaDespesa(
            nome=data["nome"],
            usuario_id=current_user.id
        )
        db.session.add(nova_categoria)
        db.session.commit()
        return jsonify({"id": nova_categoria.id, "nome": nova_categoria.nome}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao criar categoria", "error": str(e)}), 500

@dropdown_bp.route("/categorias", methods=["GET"])
@token_required
def get_categorias(current_user):
    categorias = CategoriaDespesa.query.filter_by(usuario_id=current_user.id).order_by(CategoriaDespesa.nome).all()
    output = []
    for categoria in categorias:
        categoria_data = {"id": categoria.id, "nome": categoria.nome}
        output.append(categoria_data)
    return jsonify(output), 200

@dropdown_bp.route("/categorias/<int:id_categoria>", methods=["PUT"])
@token_required
def update_categoria(current_user, id_categoria):
    data = request.get_json()
    categoria = CategoriaDespesa.query.filter_by(id=id_categoria, usuario_id=current_user.id).first()

    if not categoria:
        return jsonify({"message": "Categoria não encontrada"}), 404
    
    if not data or not data.get("nome"):
        return jsonify({"message": "Nome da categoria é obrigatório para atualização"}), 400

    # Verificar se o novo nome já existe para outra categoria do mesmo usuário
    novo_nome = data["nome"]
    if novo_nome != categoria.nome:
        existente = CategoriaDespesa.query.filter_by(nome=novo_nome, usuario_id=current_user.id).first()
        if existente:
            return jsonify({"message": f"Categoria \'{novo_nome}\' já existe."}), 409

    try:
        categoria.nome = novo_nome
        db.session.commit()
        return jsonify({"id": categoria.id, "nome": categoria.nome, "message": "Categoria atualizada com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao atualizar categoria", "error": str(e)}), 500

@dropdown_bp.route("/categorias/<int:id_categoria>", methods=["DELETE"])
@token_required
def delete_categoria(current_user, id_categoria):
    categoria = CategoriaDespesa.query.filter_by(id=id_categoria, usuario_id=current_user.id).first()
    if not categoria:
        return jsonify({"message": "Categoria não encontrada"}), 404
    
    # Verificar se a categoria está em uso por alguma despesa
    if categoria.despesas:
        return jsonify({"message": "Categoria não pode ser deletada pois está em uso por despesas."}), 400

    try:
        db.session.delete(categoria)
        db.session.commit()
        return jsonify({"message": "Categoria deletada com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao deletar categoria", "error": str(e)}), 500

# --- Meios de Pagamento Endpoints ---
@dropdown_bp.route("/meios_pagamento", methods=["POST"])
@token_required
def create_meio_pagamento(current_user):
    data = request.get_json()
    if not data or not data.get("nome"):
        return jsonify({"message": "Nome do meio de pagamento é obrigatório"}), 400

    existente = MeioPagamento.query.filter_by(nome=data["nome"], usuario_id=current_user.id).first()
    if existente:
        return jsonify({"message": f"Meio de pagamento \'{data['nome']}\' já existe."}), 409

    try:
        novo_meio_pagamento = MeioPagamento(
            nome=data["nome"],
            usuario_id=current_user.id
        )
        db.session.add(novo_meio_pagamento)
        db.session.commit()
        return jsonify({"id": novo_meio_pagamento.id, "nome": novo_meio_pagamento.nome}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao criar meio de pagamento", "error": str(e)}), 500

@dropdown_bp.route("/meios_pagamento", methods=["GET"])
@token_required
def get_meios_pagamento(current_user):
    meios_pagamento = MeioPagamento.query.filter_by(usuario_id=current_user.id).order_by(MeioPagamento.nome).all()
    output = []
    for mp in meios_pagamento:
        mp_data = {"id": mp.id, "nome": mp.nome}
        output.append(mp_data)
    return jsonify(output), 200

@dropdown_bp.route("/meios_pagamento/<int:id_meio_pagamento>", methods=["PUT"])
@token_required
def update_meio_pagamento(current_user, id_meio_pagamento):
    data = request.get_json()
    meio_pagamento = MeioPagamento.query.filter_by(id=id_meio_pagamento, usuario_id=current_user.id).first()

    if not meio_pagamento:
        return jsonify({"message": "Meio de pagamento não encontrado"}), 404

    if not data or not data.get("nome"):
        return jsonify({"message": "Nome do meio de pagamento é obrigatório para atualização"}), 400

    novo_nome = data["nome"]
    if novo_nome != meio_pagamento.nome:
        existente = MeioPagamento.query.filter_by(nome=novo_nome, usuario_id=current_user.id).first()
        if existente:
            return jsonify({"message": f"Meio de pagamento \'{novo_nome}\' já existe."}), 409

    try:
        meio_pagamento.nome = novo_nome
        db.session.commit()
        return jsonify({"id": meio_pagamento.id, "nome": meio_pagamento.nome, "message": "Meio de pagamento atualizado com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao atualizar meio de pagamento", "error": str(e)}), 500

@dropdown_bp.route("/meios_pagamento/<int:id_meio_pagamento>", methods=["DELETE"])
@token_required
def delete_meio_pagamento(current_user, id_meio_pagamento):
    meio_pagamento = MeioPagamento.query.filter_by(id=id_meio_pagamento, usuario_id=current_user.id).first()
    if not meio_pagamento:
        return jsonify({"message": "Meio de pagamento não encontrado"}), 404

    if meio_pagamento.despesas:
        return jsonify({"message": "Meio de pagamento não pode ser deletado pois está em uso por despesas."}), 400

    try:
        db.session.delete(meio_pagamento)
        db.session.commit()
        return jsonify({"message": "Meio de pagamento deletado com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao deletar meio de pagamento", "error": str(e)}), 500

