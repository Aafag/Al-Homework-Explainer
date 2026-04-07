from datetime import datetime, timedelta, timezone

from bson import ObjectId
from requests import HTTPError

from app import create_app
from app.db import DatabaseError


class DummyResponse:
    def __init__(self, status_code):
        self.status_code = status_code


class FakeGeminiService:
    def generate_explanation(self, question):
        return f"## Explanation\n\nThis is a guided explanation for: {question}"


class FailingGeminiService:
    def __init__(self, status_code):
        self.status_code = status_code

    def generate_explanation(self, _question):
        raise HTTPError(response=DummyResponse(self.status_code))


class InMemoryQuestionStore:
    def __init__(self):
        self.rows = []

    def create_question(self, question, explanation, created_at):
        row = {
            "id": str(ObjectId()),
            "question": question,
            "explanation": explanation,
            "created_at": created_at,
        }
        self.rows.append(row)
        return row["id"]

    def list_questions(self, limit):
        return sorted(self.rows, key=lambda row: row["created_at"], reverse=True)[:limit]

    def get_question(self, row_id):
        return next((row for row in self.rows if row["id"] == row_id), None)


def seed_questions(store):
    base_time = datetime.now(timezone.utc)
    older_id = store.create_question(
        "Older question",
        "Old explanation",
        (base_time - timedelta(minutes=10)).isoformat(),
    )
    newer_id = store.create_question(
        "Newer question",
        "New explanation",
        (base_time - timedelta(minutes=1)).isoformat(),
    )
    return {"older": older_id, "newer": newer_id}


class FailingStore:
    def create_question(self, *_a, **_kw):
        raise DatabaseError("insert failed")


def create_test_client(
    *,
    gemini_service=None,
    question_store=None,
    config_overrides=None,
    seed_history=True,
):
    app = create_app(
        {
            "TESTING": True,
            "INIT_EXTERNAL_SERVICES": False,
            **(config_overrides or {}),
        }
    )
    app.gemini_service = gemini_service or FakeGeminiService()
    app.question_store = question_store if question_store is not None else InMemoryQuestionStore()

    if seed_history and not isinstance(app.question_store, FailingStore):
        seed_questions(app.question_store)

    return app.test_client()


def test_index_serves_frontend():
    client = create_test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"AI Homework Explainer" in response.data


def test_health_endpoint():
    client = create_test_client()
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_create_question_success():
    client = create_test_client()
    response = client.post("/api/questions", json={"question": "Explain kinetic energy."})
    assert response.status_code == 201
    payload = response.get_json()
    assert ObjectId.is_valid(payload["id"])
    assert payload["question"] == "Explain kinetic energy."
    assert "guided explanation" in payload["explanation"]


def test_create_question_missing_question_returns_400():
    client = create_test_client()
    response = client.post("/api/questions", json={})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Question is required."


def test_create_question_whitespace_only_returns_400():
    client = create_test_client()
    response = client.post("/api/questions", json={"question": "   "})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Question is required."


def test_create_question_over_max_length_returns_400():
    client = create_test_client(config_overrides={"MAX_QUESTION_LENGTH": 10})
    response = client.post("/api/questions", json={"question": "x" * 11})
    assert response.status_code == 400
    assert "at most 10 characters" in response.get_json()["error"]


def test_create_question_handles_gemini_401():
    client = create_test_client(gemini_service=FailingGeminiService(401))
    response = client.post("/api/questions", json={"question": "Explain AI"})
    assert response.status_code == 502
    assert "Gemini authentication failed" in response.get_json()["error"]


def test_create_question_handles_gemini_403():
    client = create_test_client(gemini_service=FailingGeminiService(403))
    response = client.post("/api/questions", json={"question": "Explain AI"})
    assert response.status_code == 502
    assert response.get_json()["error"] == "Gemini API access denied for this key or model."


def test_create_question_handles_gemini_429():
    client = create_test_client(gemini_service=FailingGeminiService(429))
    response = client.post("/api/questions", json={"question": "Explain AI"})
    assert response.status_code == 502
    assert response.get_json()["error"] == "Gemini API quota exceeded. Try again later."


def test_create_question_handles_database_write_failure():
    client = create_test_client(question_store=FailingStore(), seed_history=False)
    response = client.post("/api/questions", json={"question": "Explain AI"})
    assert response.status_code == 500
    assert "Database write failed" in response.get_json()["error"]


def test_get_questions_rejects_invalid_limit():
    client = create_test_client()
    response = client.get("/api/questions?limit=abc")
    assert response.status_code == 400
    assert response.get_json()["error"] == "limit must be an integer."


def test_get_questions_returns_items_sorted_newest_first():
    client = create_test_client()
    response = client.get("/api/questions?limit=5")
    assert response.status_code == 200
    items = response.get_json()
    assert len(items) == 2
    assert items[0]["question"] == "Newer question"
    assert items[1]["question"] == "Older question"


def test_get_question_rejects_invalid_id():
    client = create_test_client()
    response = client.get("/api/questions/not-a-valid-id")
    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid question ID."


def test_get_question_returns_404_when_missing():
    client = create_test_client()
    response = client.get(f"/api/questions/{ObjectId()}")
    assert response.status_code == 404
    assert response.get_json()["error"] == "Question not found."


def test_get_question_returns_existing_item():
    store = InMemoryQuestionStore()
    ids = seed_questions(store)
    client = create_test_client(question_store=store, seed_history=False)

    response = client.get(f"/api/questions/{ids['older']}")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["id"] == ids["older"]
    assert payload["question"] == "Older question"
