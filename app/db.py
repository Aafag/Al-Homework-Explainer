import sqlite3


class DatabaseError(RuntimeError):
    pass


def get_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


class SQLiteQuestionStore:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def init_schema(self) -> None:
        try:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS questions (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    question    TEXT    NOT NULL,
                    explanation TEXT    NOT NULL,
                    created_at  TEXT    NOT NULL
                )
            """)
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON questions (created_at)")
            self.conn.commit()
        except sqlite3.Error as exc:
            raise DatabaseError(exc) from exc

    def create_question(self, question: str, explanation: str, created_at: str) -> int:
        try:
            cursor = self.conn.execute(
                "INSERT INTO questions (question, explanation, created_at) VALUES (?, ?, ?)",
                (question, explanation, created_at),
            )
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as exc:
            raise DatabaseError(exc) from exc

    def list_questions(self, limit: int) -> list:
        try:
            return self.conn.execute(
                "SELECT * FROM questions ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        except sqlite3.Error as exc:
            raise DatabaseError(exc) from exc

    def get_question(self, row_id: int):
        try:
            return self.conn.execute(
                "SELECT * FROM questions WHERE id = ?", (row_id,)
            ).fetchone()
        except sqlite3.Error as exc:
            raise DatabaseError(exc) from exc


class PostgresQuestionStore:
    def __init__(self, database_url: str):
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
        except ImportError as exc:
            raise RuntimeError(
                "Postgres support requires psycopg2-binary. Run `pip install -r requirements.txt`."
            ) from exc

        self.psycopg2 = psycopg2
        self.cursor_factory = RealDictCursor
        self.conn = psycopg2.connect(database_url)

    def init_schema(self) -> None:
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS questions (
                        id          SERIAL PRIMARY KEY,
                        question    TEXT NOT NULL,
                        explanation TEXT NOT NULL,
                        created_at  TEXT NOT NULL
                    )
                """)
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON questions (created_at)")
            self.conn.commit()
        except self.psycopg2.Error as exc:
            self.conn.rollback()
            raise DatabaseError(exc) from exc

    def create_question(self, question: str, explanation: str, created_at: str) -> int:
        try:
            with self.conn.cursor(cursor_factory=self.cursor_factory) as cursor:
                cursor.execute(
                    """
                    INSERT INTO questions (question, explanation, created_at)
                    VALUES (%s, %s, %s)
                    RETURNING id
                    """,
                    (question, explanation, created_at),
                )
                row = cursor.fetchone()
            self.conn.commit()
            return row["id"]
        except self.psycopg2.Error as exc:
            self.conn.rollback()
            raise DatabaseError(exc) from exc

    def list_questions(self, limit: int) -> list:
        try:
            with self.conn.cursor(cursor_factory=self.cursor_factory) as cursor:
                cursor.execute(
                    "SELECT * FROM questions ORDER BY created_at DESC LIMIT %s",
                    (limit,),
                )
                return cursor.fetchall()
        except self.psycopg2.Error as exc:
            self.conn.rollback()
            raise DatabaseError(exc) from exc

    def get_question(self, row_id: int):
        try:
            with self.conn.cursor(cursor_factory=self.cursor_factory) as cursor:
                cursor.execute("SELECT * FROM questions WHERE id = %s", (row_id,))
                return cursor.fetchone()
        except self.psycopg2.Error as exc:
            self.conn.rollback()
            raise DatabaseError(exc) from exc


def init_db(app) -> None:
    database_url = app.config["DATABASE_URL"]

    if database_url:
        store = PostgresQuestionStore(database_url)
        app.db_path = None
        app.db_conn = store.conn
    else:
        db_path = app.config["SQLITE_PATH"]
        conn = get_connection(db_path)
        store = SQLiteQuestionStore(conn)
        app.db_path = db_path
        app.db_conn = conn

    try:
        store.init_schema()
    except DatabaseError as exc:
        raise RuntimeError(f"Database initialization failed: {exc}") from exc

    app.question_store = store
