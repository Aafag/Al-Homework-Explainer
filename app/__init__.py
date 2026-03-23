import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

from .config import Config
from .db import init_db
from .routes import api
from .services.gemini_service import GeminiService


def create_app() -> Flask:
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    init_db(app)
    app.gemini_service = GeminiService(
        api_key=app.config["GEMINI_API_KEY"],
        model=app.config["GEMINI_MODEL"],
        api_base=app.config["GEMINI_API_BASE"],
    )

    app.register_blueprint(api)

    @app.get("/")
    def index():
        return jsonify({"message": "AI Homework Explainer backend is running."})

    return app

