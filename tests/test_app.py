from datetime import datetime, timedelta, timezone

from bson import ObjectId

from app import create_app


class FakeInsertResult:
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id


class FakeCursor(list):
    def sort(self, field, direction):
        return sorted(self, key=lambda doc: doc[field], reverse=direction == -1)


class FakeQuestionsCollection:
    def __init__(self):
        self.docs = []

    def insert_one(self, doc):
        stored = doc.copy()
        stored["_id"] = ObjectId()
        self.docs.append(stored)
        return FakeInsertResult(stored["_id"])

    def find(self, _query, limit=20):
        return FakeCursor(self.docs[:limit])

    def find_one(self, query):
        for doc in self.docs:
            if doc["_id"] == query["_id"]:
                return doc
        return None


class FakeGeminiService:
    def generate_explanation(self, question):
        return f"## Explanation\n\nThis is a guided explanation for: {question}"


def create_test_client():
    app = create_app(
        {
            "TESTING": True,
            "INIT_EXTERNAL_SERVICES": False,
        }
    )
    app.gemini_service = FakeGeminiService()
    app.questions_collection = FakeQuestionsCollection()

    seeded_doc = {
        "_id": ObjectId(),
        "question": "Earlier question",
        "explanation": "Seeded explanation",
        "created_at": datetime.now(timezone.utc) - timedelta(minutes=5),
    }
    app.questions_collection.docs.append(seeded_doc)

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


def test_create_question_and_fetch_history():
    client = create_test_client()

    create_response = client.post(
        "/api/questions",
        json={"question": "Explain kinetic energy."},
    )

    assert create_response.status_code == 201
    created_item = create_response.get_json()
    assert created_item["question"] == "Explain kinetic energy."
    assert "guided explanation" in created_item["explanation"]

    list_response = client.get("/api/questions?limit=5")

    assert list_response.status_code == 200
    items = list_response.get_json()
    assert len(items) == 2
    assert items[0]["question"] == "Explain kinetic energy."

    detail_response = client.get(f"/api/questions/{created_item['id']}")

    assert detail_response.status_code == 200
    assert detail_response.get_json()["id"] == created_item["id"]
