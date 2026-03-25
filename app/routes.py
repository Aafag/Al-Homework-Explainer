from datetime import datetime, timezone

from bson import ObjectId
from flask import Blueprint, current_app, jsonify, request
from pymongo import DESCENDING
from pymongo.errors import PyMongoError
from requests import RequestException

api = Blueprint("api", __name__, url_prefix="/api")


def gemini_error_response(exc: RequestException) -> tuple:
    status_code = getattr(getattr(exc, "response", None), "status_code", None)

    if status_code == 401:
        return jsonify(
            {
                "error": (
                    "Gemini authentication failed. Check GEMINI_AUTH_MODE and credentials "
                    "(GEMINI_KEY/GEMINI_API_KEY or OAuth token/ADC)."
                )
            }
        ), 502
    if status_code == 403:
        return jsonify({"error": "Gemini API access denied for this key or model."}), 502
    if status_code == 429:
        return jsonify({"error": "Gemini API quota exceeded. Try again later."}), 502

    return jsonify({"error": "Gemini API request failed."}), 502


def serialize_question(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "question": doc["question"],
        "explanation": doc["explanation"],
        "created_at": doc["created_at"].isoformat(),
    }


@api.get("/health")
def health() -> tuple:
    return jsonify({"status": "ok"}), 200


@api.post("/questions")
def create_question() -> tuple:
    body = request.get_json(silent=True) or {}
    question = (body.get("question") or "").strip()

    if not question:
        return jsonify({"error": "Question is required."}), 400

    max_len = current_app.config["MAX_QUESTION_LENGTH"]
    if len(question) > max_len:
        return jsonify({"error": f"Question must be at most {max_len} characters."}), 400

    try:
        explanation = current_app.gemini_service.generate_explanation(question)
    except RequestException as exc:
        status_code = getattr(getattr(exc, "response", None), "status_code", None)
        current_app.logger.error("Gemini API request failed with status code: %s", status_code)
        return gemini_error_response(exc)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 502

    doc = {
        "question": question,
        "explanation": explanation,
        "created_at": datetime.now(timezone.utc),
    }

    try:
        result = current_app.questions_collection.insert_one(doc)
    except PyMongoError as exc:
        return jsonify({"error": f"Database write failed: {exc}"}), 500

    doc["_id"] = result.inserted_id
    return jsonify(serialize_question(doc)), 201


@api.get("/questions")
def get_questions() -> tuple:
    try:
        limit = int(request.args.get("limit", 20))
    except ValueError:
        return jsonify({"error": "limit must be an integer."}), 400

    limit = max(1, min(limit, 100))

    try:
        docs = (
            current_app.questions_collection.find({}, limit=limit)
            .sort("created_at", DESCENDING)
        )
        items = [serialize_question(doc) for doc in docs]
    except PyMongoError as exc:
        return jsonify({"error": f"Database read failed: {exc}"}), 500

    return jsonify(items), 200


@api.get("/questions/<question_id>")
def get_question(question_id: str) -> tuple:
    if not ObjectId.is_valid(question_id):
        return jsonify({"error": "Invalid question ID."}), 400

    try:
        doc = current_app.questions_collection.find_one({"_id": ObjectId(question_id)})
    except PyMongoError as exc:
        return jsonify({"error": f"Database read failed: {exc}"}), 500

    if not doc:
        return jsonify({"error": "Question not found."}), 404

    return jsonify(serialize_question(doc)), 200
