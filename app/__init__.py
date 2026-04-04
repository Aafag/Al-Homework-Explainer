from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, send_from_directory
from flask_cors import CORS

from .db import init_db
from .routes import api
from .services.gemini_service import GeminiService


def create_app(config_overrides: dict | None = None) -> Flask:
    project_root = Path(__file__).resolve().parent.parent
    frontend_dir = project_root / "frontend"
    load_dotenv(project_root / ".env")
    from .config import Config

    app = Flask(
        __name__,
        static_folder=str(frontend_dir),
        static_url_path="",
    )
    app.config.from_object(Config)
    if config_overrides:
        app.config.update(config_overrides)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    app.db_conn = None
    app.gemini_service = None

    if app.config["INIT_EXTERNAL_SERVICES"]:
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
        return app.send_static_file("index.html")

    @app.get("/<path:path>")
    def static_proxy(path: str):
        asset_path = frontend_dir / path
        if asset_path.is_file():
            return send_from_directory(frontend_dir, path)

        return app.send_static_file("index.html")

    return app
