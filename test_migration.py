"""Test script to verify SQLite migration is complete and working"""
import sys
import json

print("=" * 60)
print("BLV DASHBOARD - SQLite MIGRATION TEST")
print("=" * 60)

# Test 1: Import all modules
print("\n[TEST 1] Importing modules...")
try:
    from config import Config
    from models import Settings, Conversation, Message, HTTPRequest
    from services import ChatService, BurpParserService
    from app import app
    print("[PASS] All modules imported successfully")
except Exception as e:
    print(f"[FAIL] Import error: {e}")
    sys.exit(1)

# Test 2: Configuration
print("\n[TEST 2] Checking configuration...")
config = Config()
try:
    assert hasattr(config, 'DB_FILE'), "Config missing DB_FILE attribute"
    assert config.DB_FILE == 'blv_dashboard.db', f"Wrong DB_FILE: {config.DB_FILE}"
    print(f"[PASS] Database file: {config.DB_FILE}")
except AssertionError as e:
    print(f"[FAIL] {e}")
    sys.exit(1)

# Test 3: Database connection
print("\n[TEST 3] Testing database connection...")
try:
    from models import get_db
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cur.fetchall()]
    conn.close()

    expected_tables = ['settings', 'conversations', 'messages', 'http_requests']
    for table in expected_tables:
        assert table in tables, f"Missing table: {table}"

    print(f"[PASS] All required tables present: {', '.join(expected_tables)}")
except Exception as e:
    print(f"[FAIL] Database connection error: {e}")
    sys.exit(1)

# Test 4: Settings model
print("\n[TEST 4] Testing Settings model...")
try:
    # Get existing setting
    system_prompt = Settings.get('system_prompt')
    assert system_prompt is not None, "system_prompt not found"

    # Set and get new setting
    Settings.set('test_migration', 'success')
    value = Settings.get('test_migration')
    assert value == 'success', f"Expected 'success', got '{value}'"

    print("[PASS] Settings model working")
except Exception as e:
    print(f"[FAIL] Settings model error: {e}")
    sys.exit(1)

# Test 5: Conversation model
print("\n[TEST 5] Testing Conversation model...")
try:
    # Create conversation
    conv_id = Conversation.create('Migration Test Conversation')
    assert conv_id is not None, "Failed to create conversation"

    # Get conversation
    conv = Conversation.get(conv_id)
    assert conv is not None, "Failed to retrieve conversation"
    assert conv['title'] == 'Migration Test Conversation'

    # Get all conversations
    convs = Conversation.get_all()
    assert len(convs) > 0, "No conversations found"

    # Rename conversation
    Conversation.rename(conv_id, 'Renamed Test')
    conv = Conversation.get(conv_id)
    assert conv['title'] == 'Renamed Test', "Failed to rename"

    print(f"[PASS] Conversation model working (ID: {conv_id})")
except Exception as e:
    print(f"[FAIL] Conversation model error: {e}")
    sys.exit(1)

# Test 6: Message model
print("\n[TEST 6] Testing Message model...")
try:
    # Create messages
    msg_id1 = Message.create(conv_id, 'user', 'Test message from user')
    msg_id2 = Message.create(conv_id, 'assistant', 'Test response from assistant')

    assert msg_id1 is not None, "Failed to create user message"
    assert msg_id2 is not None, "Failed to create assistant message"

    # Get messages
    messages = Message.get_by_conversation(conv_id)
    assert len(messages) == 2, f"Expected 2 messages, got {len(messages)}"
    assert messages[0]['role'] == 'user'
    assert messages[1]['role'] == 'assistant'

    print(f"[PASS] Message model working ({len(messages)} messages)")
except Exception as e:
    print(f"[FAIL] Message model error: {e}")
    sys.exit(1)

# Test 7: HTTPRequest model
print("\n[TEST 7] Testing HTTPRequest model...")
try:
    # Create HTTP request
    headers_json = json.dumps({'Content-Type': 'application/json', 'Host': 'example.com'})
    req_id = HTTPRequest.create(
        raw_request='POST /api/test HTTP/1.1\nHost: example.com\n\n{"test": true}',
        method='POST',
        url='https://example.com/api/test',
        host='example.com',
        path='/api/test',
        headers_json=headers_json,
        body='{"test": true}',
        graphql_operation=None,
        graphql_query=None
    )

    assert req_id is not None, "Failed to create HTTP request"

    # Get request
    req = HTTPRequest.get(req_id)
    assert req is not None, "Failed to retrieve HTTP request"
    assert req['method'] == 'POST'
    assert req['url'] == 'https://example.com/api/test'

    # Get all requests
    requests = HTTPRequest.get_all(10)
    assert len(requests) > 0, "No HTTP requests found"

    print(f"[PASS] HTTPRequest model working (ID: {req_id})")
except Exception as e:
    print(f"[FAIL] HTTPRequest model error: {e}")
    sys.exit(1)

# Test 8: ChatService
print("\n[TEST 8] Testing ChatService...")
try:
    # Test settings access through service
    prompt = ChatService.get_system_prompt()
    assert prompt is not None, "Failed to get system prompt"

    # Test API key
    api_key = ChatService.get_api_key()
    # API key may be empty but method should work

    # Test rules
    rules = ChatService.get_rules()

    # Test conversation methods
    test_conv_id = ChatService.create_conversation('Service Test')
    assert test_conv_id is not None

    convs = ChatService.get_conversations()
    assert len(convs) > 0

    print("[PASS] ChatService working")
except Exception as e:
    print(f"[FAIL] ChatService error: {e}")
    sys.exit(1)

# Test 9: BurpParserService
print("\n[TEST 9] Testing BurpParserService...")
try:
    raw_request = """GET /api/users HTTP/1.1
Host: api.example.com
User-Agent: Mozilla/5.0
Accept: application/json

"""

    # Parse request
    parsed = BurpParserService.parse_http_request(raw_request)
    assert parsed is not None, "Failed to parse request"
    assert parsed['method'] == 'GET'
    assert parsed['host'] == 'api.example.com'

    # Save request
    saved_id = BurpParserService.save_request(raw_request)
    assert saved_id is not None, "Failed to save request"

    # Get saved request
    saved = BurpParserService.get_request(saved_id)
    assert saved is not None, "Failed to retrieve saved request"

    print("[PASS] BurpParserService working")
except Exception as e:
    print(f"[FAIL] BurpParserService error: {e}")
    sys.exit(1)

# Test 10: Cleanup
print("\n[TEST 10] Testing cleanup (delete conversation)...")
try:
    Conversation.delete(conv_id)
    deleted = Conversation.get(conv_id)
    assert deleted is None, "Conversation not deleted"

    # Verify messages were also deleted (cascade)
    messages = Message.get_by_conversation(conv_id)
    assert len(messages) == 0, "Messages not deleted with conversation"

    print("[PASS] Cascade delete working")
except Exception as e:
    print(f"[FAIL] Cleanup error: {e}")
    sys.exit(1)

# Final summary
print("\n" + "=" * 60)
print("MIGRATION TEST RESULTS")
print("=" * 60)
print("[SUCCESS] All 10 tests passed!")
print("\nMigration from PostgreSQL to SQLite is complete.")
print("Database file: blv_dashboard.db")
print("\nTo start the application:")
print("  python app.py")
print("=" * 60)
