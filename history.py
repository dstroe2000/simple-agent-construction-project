import sqlite3
from typing import List, Tuple

DB_PATH = "chat_history.sqlite"

class ChatHistoryDB:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self._init_db()

    def _init_db(self):
        c = self.conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                assistant TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def load_history(self) -> List[Tuple[str, str]]:
        c = self.conn.cursor()
        c.execute("SELECT user, assistant FROM history ORDER BY id ASC")
        return c.fetchall()

    def add_to_history(self, user: str, assistant: str):
        c = self.conn.cursor()
        c.execute("INSERT INTO history (user, assistant) VALUES (?, ?)", (user, assistant))
        self.conn.commit()

    def clear_history(self):
        c = self.conn.cursor()
        c.execute("DELETE FROM history")
        self.conn.commit()

    def close(self):
        self.conn.close()
