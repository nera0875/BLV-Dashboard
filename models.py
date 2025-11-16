"""Database models for BLV Dashboard"""
import sqlite3
from config import Config

config = Config()

def get_db():
    """Get database connection with Row factory for dict-like access"""
    conn = sqlite3.connect(config.DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

class Settings:
    """Settings model"""

    @staticmethod
    def get(key):
        """Get setting value by key"""
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT value FROM settings WHERE key = ?",
            (key,)
        )
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result[0] if result else None

    @staticmethod
    def set(key, value):
        """Set setting value"""
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO settings (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT (key) DO UPDATE SET value = ?, updated_at = CURRENT_TIMESTAMP""",
            (key, value, value)
        )
        conn.commit()
        cur.close()
        conn.close()

class Conversation:
    """Conversation model"""

    @staticmethod
    def create(title='New Conversation'):
        """Create new conversation"""
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO conversations (title) VALUES (?)",
            (title,)
        )
        conv_id = cur.lastrowid
        conn.commit()
        cur.close()
        conn.close()
        return conv_id

    @staticmethod
    def get_all():
        """Get all conversations"""
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM conversations ORDER BY created_at DESC"
        )
        conversations = cur.fetchall()
        cur.close()
        conn.close()
        return conversations

    @staticmethod
    def get(conv_id):
        """Get conversation by ID"""
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM conversations WHERE id = ?",
            (conv_id,)
        )
        conversation = cur.fetchone()
        cur.close()
        conn.close()
        return conversation

    @staticmethod
    def rename(conv_id, new_title):
        """Rename a conversation"""
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "UPDATE conversations SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (new_title, conv_id)
        )
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def delete(conv_id):
        """Delete a conversation and all its messages"""
        conn = get_db()
        cur = conn.cursor()
        # Delete messages first (cascade should handle this but being explicit)
        cur.execute(
            "DELETE FROM messages WHERE conversation_id = ?",
            (conv_id,)
        )
        # Delete conversation
        cur.execute(
            "DELETE FROM conversations WHERE id = ?",
            (conv_id,)
        )
        conn.commit()
        cur.close()
        conn.close()

class Message:
    """Message model"""

    @staticmethod
    def create(conversation_id, role, content):
        """Create new message"""
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO messages (conversation_id, role, content)
                VALUES (?, ?, ?)""",
            (conversation_id, role, content)
        )
        msg_id = cur.lastrowid
        conn.commit()
        cur.close()
        conn.close()
        return msg_id

    @staticmethod
    def get_by_conversation(conversation_id):
        """Get all messages for a conversation"""
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """SELECT * FROM messages
                WHERE conversation_id = ?
                ORDER BY created_at ASC""",
            (conversation_id,)
        )
        messages = cur.fetchall()
        cur.close()
        conn.close()
        return messages

class HTTPRequest:
    """HTTP Request model (Burp parser)"""

    @staticmethod
    def create(raw_request, method=None, url=None, host=None, path=None,
               headers_json=None, body=None, graphql_operation=None, graphql_query=None):
        """Create new HTTP request record"""
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO http_requests
                (raw_request, method, url, host, path, headers_json, body, graphql_operation, graphql_query)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (raw_request, method, url, host, path, headers_json, body, graphql_operation, graphql_query)
        )
        req_id = cur.lastrowid
        conn.commit()
        cur.close()
        conn.close()
        return req_id

    @staticmethod
    def get_all(limit=50):
        """Get all HTTP requests"""
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM http_requests ORDER BY parsed_at DESC LIMIT ?",
            (limit,)
        )
        requests = cur.fetchall()
        cur.close()
        conn.close()
        return requests

    @staticmethod
    def get(req_id):
        """Get HTTP request by ID"""
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM http_requests WHERE id = ?",
            (req_id,)
        )
        request = cur.fetchone()
        cur.close()
        conn.close()
        return request
