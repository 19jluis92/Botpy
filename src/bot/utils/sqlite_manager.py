import sqlite3
from contextlib import closing
import logging

DB_PATH = "lala_memory.db"
logger = logging.getLogger(__name__)

def init_db():
    logger.warning(f"[WARNING] {DB_PATH}. Creando nueva base de datos.")
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()

def save_message(user_id, role, content):
    logger.info(f"[INFO] Guardando mensaje para user_id: {user_id}")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO conversations (user_id, role, content) VALUES (?, ?, ?)",
            (user_id, role, content)
        )
        conn.commit()

def clear_memory(user_id):
    logger.warning(f"[WARNING] Limpiando memoria para user_id: {user_id}")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "DELETE FROM conversations WHERE user_id = ?",
            (user_id,)
        )
        conn.commit()

def load_history(user_id, limit=20):
    logger.info(f"[INFO] Cargando historial para user_id: {user_id}")
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            """
            SELECT role, content
            FROM conversations
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, limit)
        ).fetchall()

    # regresar en orden correcto
    rows.reverse()
    logger.info(f"[INFO] historial cargado para user_id: {user_id} historial length: {len(rows)}")
    return [{"role": r[0], "content": r[1]} for r in rows]