import sqlite3
from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify, request
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


def serialize_question(row) -> dict:
    return {
        "id": str(row["id"]),
        "question": row["question"],
        "explanation": row["explanation"],
        "created_at": row["created_at"],
    }


def get_db() -> sqlite3.Connection:
    return current_app.db_conn


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

    created_at = datetime.now(timezone.utc).isoformat()

    try:
        db = get_db()
        cursor = db.execute(
            "INSERT INTO questions (question, explanation, created_at) VALUES (?, ?, ?)",
            (question, explanation, created_at),
        )
        db.commit()
        row_id = cursor.lastrowid
    except sqlite3.Error as exc:
        return jsonify({"error": f"Database write failed: {exc}"}), 500

    return jsonify({
        "id": str(row_id),
        "question": question,
        "explanation": explanation,
        "created_at": created_at,
    }), 201


@api.get("/questions")
def get_questions() -> tuple:
    try:
        limit = int(request.args.get("limit", 20))
    except ValueError:
        return jsonify({"error": "limit must be an integer."}), 400

    limit = max(1, min(limit, 100))

    try:
        db = get_db()
        rows = db.execute(
            "SELECT * FROM questions ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        items = [serialize_question(row) for row in rows]
    except sqlite3.Error as exc:
        return jsonify({"error": f"Database read failed: {exc}"}), 500

    return jsonify(items), 200


@api.get("/questions/<question_id>")
def get_question(question_id: str) -> tuple:
    try:
        row_id = int(question_id)
    except ValueError:
        return jsonify({"error": "Invalid question ID."}), 400

    try:
        db = get_db()
        row = db.execute(
            "SELECT * FROM questions WHERE id = ?", (row_id,)
        ).fetchone()
    except sqlite3.Error as exc:
        return jsonify({"error": f"Database read failed: {exc}"}), 500

    if not row:
        return jsonify({"error": "Question not found."}), 404

    return jsonify(serialize_question(row)), 200
