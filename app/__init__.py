import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

from .db import init_db
from .routes import api
from .services.gemini_service import GeminiService


def create_app() -> Flask:
    project_root = Path(__file__).resolve().parent.parent
    load_dotenv(project_root / ".env")
    from .config import Config

    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    init_db(app)
    app.gemini_service = GeminiService(
        api_key=app.config["GEMINI_API_KEY"],
        model=app.config["GEMINI_MODEL"],
        api_base=app.config["GEMINI_API_BASE"],
        auth_mode=app.config["GEMINI_AUTH_MODE"],
        vertex_access_token=app.config["VERTEX_ACCESS_TOKEN"],
        vertex_project_id=app.config["VERTEX_PROJECT_ID"],
        vertex_location=app.config["VERTEX_LOCATION"],
        vertex_use_project_endpoint=app.config["VERTEX_USE_PROJECT_ENDPOINT"],
    )

    app.register_blueprint(api)

    @app.get("/")
    def index():
        return jsonify({"message": "AI Homework Explainer backend is running."})

    return app
