from urllib.parse import urlparse


class DatabaseError(RuntimeError):
    pass


class MongoQuestionStore:
    def __init__(self, mongodb_uri: str, database_name: str):
        try:
            from bson import ObjectId
            from pymongo import DESCENDING, MongoClient
            from pymongo.errors import PyMongoError
        except ImportError as exc:
            raise RuntimeError(
                "MongoDB support requires pymongo. Run `pip install -r requirements.txt`."
            ) from exc

        self.ObjectId = ObjectId
        self.DESCENDING = DESCENDING
        self.PyMongoError = PyMongoError
        self.client = MongoClient(mongodb_uri)
        self.database = self.client[self._resolve_database_name(mongodb_uri, database_name)]
        self.collection = self.database["questions"]

    def _resolve_database_name(self, mongodb_uri: str, database_name: str) -> str:
        if database_name:
            return database_name

        parsed = urlparse(mongodb_uri)
        name = parsed.path.lstrip("/").split("?", 1)[0]
        return name or "ai_homework_explainer"

    def _serialize(self, document: dict | None):
        if not document:
            return None

        return {
            "id": str(document["_id"]),
            "question": document["question"],
            "explanation": document["explanation"],
            "created_at": document["created_at"],
        }

    def init_schema(self) -> None:
        try:
            self.client.admin.command("ping")
            self.collection.create_index(
                [("created_at", self.DESCENDING)],
                name="idx_created_at",
            )
        except self.PyMongoError as exc:
            raise DatabaseError(exc) from exc

    def create_question(self, question: str, explanation: str, created_at: str) -> str:
        try:
            result = self.collection.insert_one(
                {
                    "question": question,
                    "explanation": explanation,
                    "created_at": created_at,
                }
            )
            return str(result.inserted_id)
        except self.PyMongoError as exc:
            raise DatabaseError(exc) from exc

    def list_questions(self, limit: int) -> list:
        try:
            cursor = self.collection.find().sort("created_at", self.DESCENDING).limit(limit)
            return [self._serialize(document) for document in cursor]
        except self.PyMongoError as exc:
            raise DatabaseError(exc) from exc

    def get_question(self, question_id: str):
        if not self.ObjectId.is_valid(question_id):
            return None

        try:
            document = self.collection.find_one({"_id": self.ObjectId(question_id)})
            return self._serialize(document)
        except self.PyMongoError as exc:
            raise DatabaseError(exc) from exc


def init_db(app) -> None:
    mongodb_uri = app.config["MONGODB_URI"]
    if not mongodb_uri:
        raise RuntimeError("Database initialization failed: MONGODB_URI is required.")

    store = MongoQuestionStore(
        mongodb_uri=mongodb_uri,
        database_name=app.config["MONGODB_DB_NAME"],
    )

    try:
        store.init_schema()
    except DatabaseError as exc:
        raise RuntimeError(f"Database initialization failed: {exc}") from exc

    app.db_path = None
    app.db_conn = None
    app.db_client = store.client
    app.question_store = store
