-- BLV Dashboard - PostgreSQL Schema Initialization
-- Database: gestion
-- Schema: api

-- Create schema
CREATE SCHEMA IF NOT EXISTS api;

-- Table: settings (API keys, system prompt)
CREATE TABLE IF NOT EXISTS api.settings (
    key VARCHAR(255) PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: conversations
CREATE TABLE IF NOT EXISTS api.conversations (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) DEFAULT 'New Conversation',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: messages
CREATE TABLE IF NOT EXISTS api.messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES api.conversations(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: http_requests (Burp parsed requests)
CREATE TABLE IF NOT EXISTS api.http_requests (
    id SERIAL PRIMARY KEY,
    raw_request TEXT NOT NULL,
    method VARCHAR(10),
    url TEXT,
    host VARCHAR(500),
    path TEXT,
    headers_json JSONB,
    body TEXT,
    graphql_operation VARCHAR(255),
    graphql_query TEXT,
    parsed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default settings
INSERT INTO api.settings (key, value)
VALUES
    ('claude_api_key', ''),
    ('system_prompt', 'You are a helpful security research assistant specialized in analyzing business logic vulnerabilities. Focus on economic exploits, workflow bypasses, temporal attacks, and privilege escalation.')
ON CONFLICT (key) DO NOTHING;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON api.messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created ON api.messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_conversations_created ON api.conversations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_http_requests_parsed ON api.http_requests(parsed_at DESC);
