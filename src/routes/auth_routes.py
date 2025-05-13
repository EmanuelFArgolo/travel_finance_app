# -*- coding: utf-8 -*-
import sys
import os

# Adiciona o diretório src ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import jwt
import datetime

from models.models import db, Usuario
from main import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_DELTA_SECONDS # Import from main

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"message": "Username and password required"}), 400

    user = Usuario.query.filter_by(username=data["username"]).first()

    if not user or not check_password_hash(user.password_hash, data["password"]):
        return jsonify({"message": "Invalid credentials"}), 401

    token_payload = {
        "user_id": user.id,
        "username": user.username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXPIRATION_DELTA_SECONDS)
    }
    token = jwt.encode(token_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    return jsonify({"token": token}), 200

# Rota para criar o usuário admin se não existir (apenas para setup inicial, pode ser removida ou protegida depois)
@auth_bp.route("/setup_admin", methods=["POST"])
def setup_admin():
    if Usuario.query.filter_by(username="admin").first():
        return jsonify({"message": "Admin user already exists"}), 409
    
    # Em um cenário real, a senha viria de uma config segura ou input
    hashed_password = generate_password_hash("admin_password", method="pbkdf2:sha256")
    admin_user = Usuario(username="admin", password_hash=hashed_password)
    db.session.add(admin_user)
    db.session.commit()
    return jsonify({"message": "Admin user created successfully"}), 201

