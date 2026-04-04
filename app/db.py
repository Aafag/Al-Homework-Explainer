import sqlite3


def get_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db(app) -> None:
    db_path = app.config["SQLITE_PATH"]

    try:
        conn = get_connection(db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                question    TEXT    NOT NULL,
                explanation TEXT    NOT NULL,
                created_at  TEXT    NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON questions (created_at)")
        conn.commit()
    except sqlite3.Error as exc:
        raise RuntimeError(f"SQLite initialization failed: {exc}") from exc

    app.db_path = db_path
    app.db_conn = conn

