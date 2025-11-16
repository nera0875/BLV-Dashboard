"""BLV Dashboard - Main Flask Application"""
import json
from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from anthropic import Anthropic
from config import Config
from services import ChatService, BurpParserService

app = Flask(__name__)
app.config.from_object(Config)

# Routes - Pages
@app.route('/')
def index():
    """Dashboard homepage - Chat interface"""
    return render_template('pages/chat.html')

@app.route('/mindset')
def mindset():
    """Mindset settings page"""
    return render_template('pages/mindset.html')

@app.route('/burp-parser')
def burp_parser():
    """Burp request parser page"""
    return render_template('pages/burp_parser.html')

@app.route('/rules')
def rules():
    """Rules configuration page"""
    return render_template('pages/rules.html')


# API Routes - Settings
@app.route('/api/settings/api-key', methods=['GET', 'POST'])
def api_key_settings():
    """Get or update API key"""
    if request.method == 'GET':
        api_key = ChatService.get_api_key()
        # Mask API key for security
        masked = api_key[:10] + '...' + api_key[-4:] if api_key and len(api_key) > 14 else ''
        return jsonify({'api_key': masked, 'is_set': bool(api_key)})

    # POST
    data = request.get_json()
    api_key = data.get('api_key', '').strip()

    if not api_key:
        return jsonify({'error': 'API key required'}), 400

    ChatService.set_api_key(api_key)
    return jsonify({'success': True})


@app.route('/api/settings/system-prompt', methods=['GET', 'POST'])
def system_prompt_settings():
    """Get or update system prompt"""
    if request.method == 'GET':
        prompt = ChatService.get_system_prompt()
        return jsonify({'system_prompt': prompt})

    # POST
    data = request.get_json()
    prompt = data.get('system_prompt', '').strip()

    if not prompt:
        return jsonify({'error': 'System prompt required'}), 400

    ChatService.set_system_prompt(prompt)
    return jsonify({'success': True})


@app.route('/api/settings/rules', methods=['GET', 'POST'])
def rules_settings():
    """Get or update rules"""
    if request.method == 'GET':
        rules = ChatService.get_rules()
        return jsonify({'rules': rules})

    # POST
    data = request.get_json()
    rules = data.get('rules', '').strip()

    ChatService.set_rules(rules)
    return jsonify({'success': True})


# API Routes - Conversations
@app.route('/api/conversations', methods=['GET', 'POST'])
def conversations():
    """Get all conversations or create new one"""
    if request.method == 'GET':
        convs = ChatService.get_conversations()
        return jsonify([dict(c) for c in convs])

    # POST - create new conversation
    data = request.get_json()
    title = data.get('title', 'New Conversation')
    conv_id = ChatService.create_conversation(title)
    return jsonify({'id': conv_id, 'title': title})


@app.route('/api/conversations/<int:conv_id>/messages')
def conversation_messages(conv_id):
    """Get messages for a conversation"""
    messages = ChatService.get_conversation_messages(conv_id)
    return jsonify([dict(m) for m in messages])


@app.route('/api/conversations/<int:conv_id>', methods=['PUT', 'DELETE'])
def conversation_actions(conv_id):
    """Update or delete a conversation"""
    if request.method == 'PUT':
        # Rename conversation
        data = request.get_json()
        new_title = data.get('title', '').strip()

        if not new_title:
            return jsonify({'error': 'Title required'}), 400

        ChatService.rename_conversation(conv_id, new_title)
        return jsonify({'success': True})

    elif request.method == 'DELETE':
        # Delete conversation
        ChatService.delete_conversation(conv_id)
        return jsonify({'success': True})


@app.route('/api/chat', methods=['POST'])
def chat():
    """Send message to Claude AI - streaming response"""
    data = request.get_json()
    conversation_id = data.get('conversation_id')
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({'error': 'Message required'}), 400

    # Get API key
    api_key = ChatService.get_api_key()
    if not api_key:
        return jsonify({'error': 'API key not configured'}), 400

    # Save user message
    ChatService.save_message(conversation_id, 'user', user_message)

    # Get conversation history
    messages = ChatService.get_conversation_messages(conversation_id)
    history = [{'role': m['role'], 'content': m['content']} for m in messages]

    # Get system prompt (Mindset)
    system_prompt = ChatService.get_system_prompt()

    # Get rules and combine with system prompt
    rules = ChatService.get_rules()
    if rules:
        system_prompt = f"{system_prompt}\n\n# RULES\n{rules}"

    def generate():
        """Stream Claude response"""
        try:
            client = Anthropic(api_key=api_key)

            assistant_message = ''

            with client.messages.stream(
                model='claude-sonnet-4-5-20250929',
                max_tokens=4096,
                system=system_prompt,
                messages=history
            ) as stream:
                try:
                    for text in stream.text_stream:
                        assistant_message += text
                        yield f"data: {json.dumps({'chunk': text})}\n\n"
                except GeneratorExit:
                    # Client disconnected (abort from frontend) - save partial message
                    if assistant_message.strip():
                        ChatService.save_message(conversation_id, 'assistant',
                            assistant_message + '\n\n*[Response stopped by user]*')
                    raise

            # Save assistant message (only if completed normally)
            ChatService.save_message(conversation_id, 'assistant', assistant_message)

            yield f"data: {json.dumps({'done': True})}\n\n"

        except GeneratorExit:
            # Re-raise to properly close the generator
            raise
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')


# API Routes - Burp Parser
@app.route('/api/burp/parse', methods=['POST'])
def parse_burp_request():
    """Parse Burp HTTP request"""
    data = request.get_json()
    raw_request = data.get('raw_request', '').strip()

    if not raw_request:
        return jsonify({'error': 'Raw request required'}), 400

    # Parse and save
    req_id = BurpParserService.save_request(raw_request)

    if not req_id:
        return jsonify({'error': 'Failed to parse request'}), 400

    # Get saved request
    saved = BurpParserService.get_request(req_id)

    return jsonify({
        'success': True,
        'id': req_id,
        'request': dict(saved)
    })


@app.route('/api/burp/requests')
def get_burp_requests():
    """Get all parsed Burp requests"""
    limit = request.args.get('limit', 50, type=int)
    requests = BurpParserService.get_all_requests(limit)
    return jsonify([dict(r) for r in requests])


if __name__ == '__main__':
    app.run(debug=True, port=5000, threaded=True)
