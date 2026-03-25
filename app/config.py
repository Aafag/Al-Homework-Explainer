import os


class Config:
    MONGODB_URI = os.getenv("MONGODB_URI", "")
    MONGODB_DB = os.getenv("MONGODB_DB", "ai_homework_explainer")

    GEMINI_API_KEY = os.getenv("GEMINI_KEY") or os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
    GEMINI_API_BASE = os.getenv("GEMINI_API_BASE", "https://aiplatform.googleapis.com/v1")
    GEMINI_AUTH_MODE = os.getenv("GEMINI_AUTH_MODE", "auto").lower()

    VERTEX_ACCESS_TOKEN = os.getenv("VERTEX_ACCESS_TOKEN", "")
    VERTEX_PROJECT_ID = os.getenv("VERTEX_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT", "")
    VERTEX_LOCATION = os.getenv("VERTEX_LOCATION", "us-central1")
    VERTEX_USE_PROJECT_ENDPOINT = os.getenv("VERTEX_USE_PROJECT_ENDPOINT", "0") == "1"

    MAX_QUESTION_LENGTH = int(os.getenv("MAX_QUESTION_LENGTH", "2000"))
