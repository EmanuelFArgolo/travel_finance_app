# -*- coding: utf-8 -*-
import sys
import os

# Adiciona o diretório src ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Blueprint, request, jsonify
from sqlalchemy import func, extract
from main import token_required # Import from main
from models.models import db, Viagem, Destino, Despesa, CategoriaDespesa
from datetime import datetime

relatorio_bp = Blueprint("relatorio_bp", __name__)

# --- Relatórios e Gráficos Endpoints ---
@relatorio_bp.route("/viagens/<int:id_viagem>/relatorio/geral", methods=["GET"])
@token_required
def get_relatorio_geral(current_user, id_viagem):
    viagem = Viagem.query.filter_by(id=id_viagem, usuario_id=current_user.id).first()
    if not viagem:
        return jsonify({"message": "Viagem não encontrada"}), 404

    query_despesas = Despesa.query.join(Destino).filter(Destino.viagem_id == id_viagem)

    # Filtros opcionais
    data_inicio_str = request.args.get("data_inicio")
    data_fim_str = request.args.get("data_fim")
    id_destino_str = request.args.get("id_destino")
    meio_pagamento_id_str = request.args.get("meio_pagamento_id")
    categoria_id_str = request.args.get("categoria_id")

    if data_inicio_str:
        query_despesas = query_despesas.filter(Despesa.data >= datetime.strptime(data_inicio_str, "%Y-%m-%d").date())
    if data_fim_str:
        query_despesas = query_despesas.filter(Despesa.data <= datetime.strptime(data_fim_str, "%Y-%m-%d").date())
    if id_destino_str:
        query_despesas = query_despesas.filter(Despesa.destino_id == int(id_destino_str))
    if meio_pagamento_id_str:
        query_despesas = query_despesas.filter(Despesa.meio_pagamento_id == int(meio_pagamento_id_str))
    if categoria_id_str:
        query_despesas = query_despesas.filter(Despesa.categoria_id == int(categoria_id_str))

    total_gasto = query_despesas.with_entities(func.sum(Despesa.valor)).scalar() or 0
    
    despesas_por_categoria = query_despesas.join(CategoriaDespesa)\
        .group_by(CategoriaDespesa.nome)\
        .with_entities(CategoriaDespesa.nome, func.sum(Despesa.valor).label("total"))\
        .all()
    
    despesas_por_destino_q = db.session.query(
            Destino.nome_cidade, 
            func.sum(Despesa.valor).label("total_gasto_destino")
        ).join(Despesa, Despesa.destino_id == Destino.id)\
        .filter(Destino.viagem_id == id_viagem)
    
    if data_inicio_str: despesas_por_destino_q = despesas_por_destino_q.filter(Despesa.data >= datetime.strptime(data_inicio_str, "%Y-%m-%d").date())
    if data_fim_str: despesas_por_destino_q = despesas_por_destino_q.filter(Despesa.data <= datetime.strptime(data_fim_str, "%Y-%m-%d").date())
    if id_destino_str: despesas_por_destino_q = despesas_por_destino_q.filter(Destino.id == int(id_destino_str))
    if meio_pagamento_id_str: despesas_por_destino_q = despesas_por_destino_q.filter(Despesa.meio_pagamento_id == int(meio_pagamento_id_str))
    if categoria_id_str: despesas_por_destino_q = despesas_por_destino_q.filter(Despesa.categoria_id == int(categoria_id_str))
    
    despesas_por_destino = despesas_por_destino_q.group_by(Destino.nome_cidade).all()

    relatorio = {
        "viagem_id": id_viagem,
        "nome_viagem": viagem.nome_viagem,
        "orcamento_total_viagem": float(viagem.orcamento_total) if viagem.orcamento_total else None,
        "total_gasto_geral": float(total_gasto),
        "saldo_geral": (float(viagem.orcamento_total) - float(total_gasto)) if viagem.orcamento_total else None,
        "despesas_por_categoria": [{ "categoria": cat, "total": float(tot) } for cat, tot in despesas_por_categoria],
        "despesas_por_destino": [{ "destino": dest, "total": float(tot) } for dest, tot in despesas_por_destino],
        "filtros_aplicados": {
            "data_inicio": data_inicio_str,
            "data_fim": data_fim_str,
            "id_destino": id_destino_str,
            "meio_pagamento_id": meio_pagamento_id_str,
            "categoria_id": categoria_id_str
        }
    }
    return jsonify(relatorio), 200

@relatorio_bp.route("/viagens/<int:id_viagem>/grafico/despesas_por_categoria", methods=["GET"])
@token_required
def get_grafico_despesas_por_categoria(current_user, id_viagem):
    viagem = Viagem.query.filter_by(id=id_viagem, usuario_id=current_user.id).first()
    if not viagem:
        return jsonify({"message": "Viagem não encontrada"}), 404

    query_despesas = Despesa.query.join(Destino).filter(Destino.viagem_id == id_viagem)
    
    data_inicio_str = request.args.get("data_inicio")
    data_fim_str = request.args.get("data_fim")
    id_destino_str = request.args.get("id_destino")

    if data_inicio_str: query_despesas = query_despesas.filter(Despesa.data >= datetime.strptime(data_inicio_str, "%Y-%m-%d").date())
    if data_fim_str: query_despesas = query_despesas.filter(Despesa.data <= datetime.strptime(data_fim_str, "%Y-%m-%d").date())
    if id_destino_str: query_despesas = query_despesas.filter(Despesa.destino_id == int(id_destino_str))

    resultado = query_despesas.join(CategoriaDespesa)\
        .group_by(CategoriaDespesa.nome)\
        .with_entities(CategoriaDespesa.nome, func.sum(Despesa.valor).label("total"))\
        .order_by(func.sum(Despesa.valor).desc())\
        .all()
    
    dados_grafico = [{ "name": cat, "value": float(tot) } for cat, tot in resultado]
    return jsonify(dados_grafico), 200

@relatorio_bp.route("/viagens/<int:id_viagem>/grafico/despesas_por_dia", methods=["GET"])
@token_required
def get_grafico_despesas_por_dia(current_user, id_viagem):
    viagem = Viagem.query.filter_by(id=id_viagem, usuario_id=current_user.id).first()
    if not viagem:
        return jsonify({"message": "Viagem não encontrada"}), 404

    query_despesas = Despesa.query.join(Destino).filter(Destino.viagem_id == id_viagem)

    data_inicio_str = request.args.get("data_inicio")
    data_fim_str = request.args.get("data_fim")
    id_destino_str = request.args.get("id_destino")

    if data_inicio_str: query_despesas = query_despesas.filter(Despesa.data >= datetime.strptime(data_inicio_str, "%Y-%m-%d").date())
    if data_fim_str: query_despesas = query_despesas.filter(Despesa.data <= datetime.strptime(data_fim_str, "%Y-%m-%d").date())
    if id_destino_str: query_despesas = query_despesas.filter(Despesa.destino_id == int(id_destino_str))
    
    resultado = query_despesas.group_by(Despesa.data)\
        .with_entities(Despesa.data, func.sum(Despesa.valor).label("total"))\
        .order_by(Despesa.data.asc())\
        .all()

    dados_grafico = [{ "date": data.isoformat(), "value": float(total) } for data, total in resultado]
    return jsonify(dados_grafico), 200

