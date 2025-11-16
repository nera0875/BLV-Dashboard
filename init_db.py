"""Initialize SQLite database for BLV Dashboard"""
import sqlite3
import os

DB_FILE = 'blv_dashboard.db'

def init_database():
    """Create SQLite database with all required tables"""

    # Remove existing database if it exists
    if os.path.exists(DB_FILE):
        print(f"[!] Removing existing database: {DB_FILE}")
        os.remove(DB_FILE)

    # Create new database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    print(f"[+] Creating new database: {DB_FILE}")

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")

    # Table: settings
    cursor.execute("""
        CREATE TABLE settings (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("[+] Created table: settings")

    # Table: conversations
    cursor.execute("""
        CREATE TABLE conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL DEFAULT 'New Conversation',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("[+] Created table: conversations")

    # Table: messages
    cursor.execute("""
        CREATE TABLE messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
        )
    """)
    print("[+] Created table: messages")

    # Table: http_requests (Burp parser)
    cursor.execute("""
        CREATE TABLE http_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_request TEXT NOT NULL,
            method TEXT,
            url TEXT,
            host TEXT,
            path TEXT,
            headers_json TEXT,
            body TEXT,
            graphql_operation TEXT,
            graphql_query TEXT,
            parsed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("[+] Created table: http_requests")

    # Create indexes for better query performance
    cursor.execute("CREATE INDEX idx_messages_conversation ON messages(conversation_id)")
    cursor.execute("CREATE INDEX idx_conversations_created ON conversations(created_at DESC)")
    cursor.execute("CREATE INDEX idx_http_requests_parsed ON http_requests(parsed_at DESC)")
    print("[+] Created indexes")

    # Insert default settings
    default_settings = [
        ('system_prompt', 'You are a helpful security research assistant specialized in analyzing business logic vulnerabilities. Focus on economic exploits, workflow bypasses, temporal attacks, and privilege escalation.'),
        ('claude_api_key', ''),
        ('rules', '')
    ]

    cursor.executemany(
        "INSERT INTO settings (key, value) VALUES (?, ?)",
        default_settings
    )
    print("[+] Inserted default settings")

    conn.commit()
    conn.close()

    print(f"\n[SUCCESS] Database initialized successfully: {DB_FILE}")
    print(f"[INFO] Tables created: settings, conversations, messages, http_requests")

if __name__ == '__main__':
    init_database()
