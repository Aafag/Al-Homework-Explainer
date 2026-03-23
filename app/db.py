from pymongo import MongoClient
from pymongo.errors import PyMongoError


def init_db(app) -> None:
    mongo_uri = app.config["MONGODB_URI"]
    if not mongo_uri:
        raise RuntimeError("MONGODB_URI is required.")

    try:
        client = MongoClient(mongo_uri)
        db = client[app.config["MONGODB_DB"]]
        questions_collection = db["questions"]

        questions_collection.create_index("created_at")
    except PyMongoError as exc:
        raise RuntimeError(f"MongoDB initialization failed: {exc}") from exc

    app.mongo_client = client
    app.db = db
    app.questions_collection = questions_collection

