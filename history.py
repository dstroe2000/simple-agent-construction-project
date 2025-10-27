"""
history.py
-------------------
Persistent chat and workspace history management for the AI agent.

This module provides a SQLite-backed database interface for managing multiple chat workspaces, their message histories, and a digital twin context summary for each workspace.

Features:
- Create, list, rename, and delete chat workspaces.
- Store and retrieve per-chat message history (user/assistant pairs).
- Store, retrieve, and update a context summary (digital twin) for each workspace, with timestamp.
- Database schema auto-migration for context summary support.

Usage:
    db = ChatHistoryDB()
    chat_id = db.create_chat("My Project")
    db.add_to_history(chat_id, "User message", "Assistant reply")
    db.set_context_summary(chat_id, "Summary of the chat so far...")
    summary = db.get_context_summary(chat_id)
    db.close()

Schema:
- chats(chat_id, chat_name, created_at, context_summary, context_updated_at)
- history(id, chat_id, user, assistant)
"""

import sqlite3
from typing import List, Tuple, Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Path to the SQLite database file. Can be set via the CHAT_HISTORY_DB_PATH environment variable in .env.
DB_PATH = os.getenv("CHAT_HISTORY_DB_PATH", "chat_history.sqlite")


class ChatHistoryDB:
    """
    SQLite-backed persistent chat/workspace and history manager.

    Each chat (workspace) has:
        - A unique ID and name
        - Creation timestamp
        - A context summary (digital twin memory) and its last update timestamp
        - A message history (user/assistant pairs)
    """
    def __init__(self, db_path: str = DB_PATH):
        """
        Initialize the database connection and ensure schema is up to date.
        Args:
            db_path (str): Path to the SQLite database file.
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self._init_db()

    def _init_db(self):
        """
        Internal method to initialize or migrate the database schema.
        Ensures all required tables and columns exist for chat, history, and context summary.
        """
        """
        Create tables if they do not exist and migrate schema for context summary support.
        Adds context_summary and context_updated_at columns to chats if missing.
        """
        c = self.conn.cursor()
        # Add context_summary column if it doesn't exist
        c.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                context_summary TEXT DEFAULT NULL,
                context_updated_at TIMESTAMP DEFAULT NULL
            )
        """)
        # Try to add context_summary and context_updated_at columns if missing (for migration)
        try:
            c.execute("ALTER TABLE chats ADD COLUMN context_summary TEXT DEFAULT NULL")
        except sqlite3.OperationalError:
            pass
        try:
            c.execute("ALTER TABLE chats ADD COLUMN context_updated_at TIMESTAMP DEFAULT NULL")
        except sqlite3.OperationalError:
            pass
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

    def set_context_summary(self, chat_id: int, summary: str):
        """
        Set or update the context summary (digital twin) for a chat/workspace.
        Also updates the context_updated_at timestamp.
        Args:
            chat_id (int): The chat to update.
            summary (str): The new context summary.
        """
        c = self.conn.cursor()
        c.execute(
            "UPDATE chats SET context_summary = ?, context_updated_at = CURRENT_TIMESTAMP WHERE chat_id = ?",
            (summary, chat_id)
        )
        self.conn.commit()


    def get_context_summary(self, chat_id: int) -> Optional[str]:
        """
        Retrieve the context summary for a chat/workspace.
        Args:
            chat_id (int): The chat to query.
        Returns:
            Optional[str]: The context summary, or None if not set.
        """
        c = self.conn.cursor()
        c.execute("SELECT context_summary FROM chats WHERE chat_id = ?", (chat_id,))
        row = c.fetchone()
        return row[0] if row and row[0] is not None else None


    def get_context_updated_at(self, chat_id: int) -> Optional[str]:
        """
        Retrieve the last update timestamp for a chat's context summary.
        Args:
        Configuration:
        - The path to the SQLite database file is controlled by the `CHAT_HISTORY_DB_PATH` environment variable.
        - To change the database location, set `CHAT_HISTORY_DB_PATH` in your `.env` file. Defaults to `chat_history.sqlite` in the current directory if not set.
            chat_id (int): The chat to query.
        Returns:
            Optional[str]: The timestamp, or None if not set.
        """
        c = self.conn.cursor()
        c.execute("SELECT context_updated_at FROM chats WHERE chat_id = ?", (chat_id,))
        row = c.fetchone()
        return row[0] if row and row[0] is not None else None

    def create_chat(self, chat_name: str) -> int:
        """
        Create a new chat workspace and return its ID.
        Args:
            chat_name (str): Name for the new chat/workspace.
        Returns:
            int: The chat_id of the newly created chat.
        """
        c = self.conn.cursor()
        c.execute("INSERT INTO chats (chat_name) VALUES (?)", (chat_name,))
        self.conn.commit()
        return c.lastrowid

    def list_chats(self) -> List[Tuple[int, str, str]]:
        """
        List all chats/workspaces in the database, most recent first.
        Returns:
            List[Tuple[int, str, str]]: (chat_id, chat_name, created_at) for each chat.
        """
        c = self.conn.cursor()
        c.execute("SELECT chat_id, chat_name, created_at FROM chats ORDER BY created_at DESC")
        return c.fetchall()

    def rename_chat(self, chat_id: int, new_name: str):
        """
        Rename a chat/workspace by its ID.
        Args:
            chat_id (int): The chat to rename.
            new_name (str): The new name for the chat.
        """

        c = self.conn.cursor()
        c.execute("UPDATE chats SET chat_name = ? WHERE chat_id = ?", (new_name, chat_id))
        self.conn.commit()

    def delete_chat(self, chat_id: int):
        """
        Delete a chat/workspace and all its associated history.
        Args:
            chat_id (int): The chat to delete.
        """
        c = self.conn.cursor()
        c.execute("DELETE FROM chats WHERE chat_id = ?", (chat_id,))
        self.conn.commit()

    def load_history(self, chat_id: int) -> List[Tuple[str, str]]:
        """
        Load the full message history for a chat/workspace.
        Args:
            chat_id (int): The chat to load history for.
        Returns:
            List[Tuple[str, str]]: List of (user, assistant) message pairs, oldest first.
        """
        c = self.conn.cursor()
        c.execute("SELECT user, assistant FROM history WHERE chat_id = ? ORDER BY id ASC", (chat_id,))
        return c.fetchall()

    def add_to_history(self, chat_id: int, user: str, assistant: str):
        """
        Add a user/assistant message pair to a chat's history.
        Args:
            chat_id (int): The chat to add to.
            user (str): The user's message.
            assistant (str): The assistant's reply.
        """
        c = self.conn.cursor()
        c.execute("INSERT INTO history (chat_id, user, assistant) VALUES (?, ?, ?)", (chat_id, user, assistant))
        self.conn.commit()

    def clear_history(self, chat_id: int):
        """
        Delete all message history for a chat/workspace.
        Args:
            chat_id (int): The chat to clear.
        """
        c = self.conn.cursor()
        c.execute("DELETE FROM history WHERE chat_id = ?", (chat_id,))
        self.conn.commit()

    def close(self):
        """
        Close the database connection.
        Call this when done with the database to free resources.
        """
        self.conn.close()

