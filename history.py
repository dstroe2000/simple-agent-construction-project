import sqlite3
from typing import List, Tuple, Optional

DB_PATH = "chat_history.sqlite"

class ChatHistoryDB:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self._init_db()

    def _init_db(self):
        c = self.conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                user TEXT NOT NULL,
                assistant TEXT NOT NULL,
                FOREIGN KEY(chat_id) REFERENCES chats(chat_id) ON DELETE CASCADE
            )
        """)
        self.conn.commit()

    def create_chat(self, chat_name: str) -> int:
        c = self.conn.cursor()
        c.execute("INSERT INTO chats (chat_name) VALUES (?)", (chat_name,))
        self.conn.commit()
        return c.lastrowid

    def list_chats(self) -> List[Tuple[int, str, str]]:
        c = self.conn.cursor()
        c.execute("SELECT chat_id, chat_name, created_at FROM chats ORDER BY created_at DESC")
        return c.fetchall()

    def rename_chat(self, chat_id: int, new_name: str):
        c = self.conn.cursor()
        c.execute("UPDATE chats SET chat_name = ? WHERE chat_id = ?", (new_name, chat_id))
        self.conn.commit()

    def delete_chat(self, chat_id: int):
        c = self.conn.cursor()
        c.execute("DELETE FROM chats WHERE chat_id = ?", (chat_id,))
        self.conn.commit()

    def load_history(self, chat_id: int) -> List[Tuple[str, str]]:
        c = self.conn.cursor()
        c.execute("SELECT user, assistant FROM history WHERE chat_id = ? ORDER BY id ASC", (chat_id,))
        return c.fetchall()

    def add_to_history(self, chat_id: int, user: str, assistant: str):
        c = self.conn.cursor()
        c.execute("INSERT INTO history (chat_id, user, assistant) VALUES (?, ?, ?)", (chat_id, user, assistant))
        self.conn.commit()

    def clear_history(self, chat_id: int):
        c = self.conn.cursor()
        c.execute("DELETE FROM history WHERE chat_id = ?", (chat_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()
