# -*- coding: utf-8 -*-
import sys
import os

# Adiciona o diretório src ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt # PyJWT
import datetime
from functools import wraps

# Import models and db from the correct location
from models.models import db, Usuario, Viagem, Destino, CategoriaDespesa, MeioPagamento, Despesa

# Placeholder for JWT secret key - MUST BE CHANGED AND KEPT SECRET
# For a real application, use a strong, randomly generated key stored in environment variables
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key-for-dev")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DELTA_SECONDS = 3600  # 1 hour

# --- Authentication Decorator ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            try:
                token = auth_header.split(" ")[1] # Bearer <token>
            except IndexError:
                return jsonify({"message": "Bearer token malformed"}), 401

        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            data = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            current_user = Usuario.query.filter_by(id=data["user_id"]).first()
            if not current_user:
                return jsonify({"message": "User not found"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Token is invalid!"}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

# --- Main Application Setup ---
def create_app(config_name="default"):
    app = Flask(__name__)

    # --- Database Configuration ---
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "travel_finance.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY

    db.init_app(app)

    # --- Blueprints --- 
    from routes.auth_routes import auth_bp
    from routes.viagem_routes import viagem_bp
    from routes.destino_routes import destino_bp
    from routes.despesa_routes import despesa_bp
    from routes.dropdown_routes import dropdown_bp
    from routes.relatorio_routes import relatorio_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(viagem_bp, url_prefix="/api")
    app.register_blueprint(destino_bp, url_prefix="/api") # Note: aninhamento real é feito nas rotas do blueprint
    app.register_blueprint(despesa_bp, url_prefix="/api") # Note: aninhamento real é feito nas rotas do blueprint
    app.register_blueprint(dropdown_bp, url_prefix="/api")
    app.register_blueprint(relatorio_bp, url_prefix="/api")

    with app.app_context():
        db.create_all()
        if not Usuario.query.filter_by(username="admin").first():
            hashed_password = generate_password_hash("admin_password", method="pbkdf2:sha256")
            admin_user = Usuario(username="admin", password_hash=hashed_password)
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user created with username 'admin' and password 'admin_password'")
        else:
            print("Admin user already exists.")

    @app.route("/")
    def index():
        return "Flask Backend is running!"

    return app

if __name__ == "__main__":
    app = create_app()
    # É recomendado usar variáveis de ambiente para FLASK_APP e FLASK_DEBUG
    # Ex: export FLASK_APP=src/main.py && export FLASK_DEBUG=1 && flask run
    app.run(host="0.0.0.0", port=5000, debug=True)

