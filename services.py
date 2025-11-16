"""Business logic services for BLV Dashboard"""
import json
import re
from models import Settings, Conversation, Message, HTTPRequest

class ChatService:
    """Chat with Claude AI service"""

    @staticmethod
    def get_system_prompt():
        """Get current system prompt from settings"""
        return Settings.get('system_prompt')

    @staticmethod
    def set_system_prompt(prompt):
        """Update system prompt"""
        Settings.set('system_prompt', prompt)

    @staticmethod
    def get_api_key():
        """Get Claude API key"""
        return Settings.get('claude_api_key')

    @staticmethod
    def set_api_key(api_key):
        """Set Claude API key"""
        Settings.set('claude_api_key', api_key)

    @staticmethod
    def get_rules():
        """Get current rules from settings"""
        return Settings.get('rules') or ''

    @staticmethod
    def set_rules(rules):
        """Update rules"""
        Settings.set('rules', rules)

    @staticmethod
    def create_conversation(title='New Conversation'):
        """Create new conversation"""
        return Conversation.create(title)

    @staticmethod
    def get_conversations():
        """Get all conversations"""
        return Conversation.get_all()

    @staticmethod
    def rename_conversation(conversation_id, new_title):
        """Rename a conversation"""
        return Conversation.rename(conversation_id, new_title)

    @staticmethod
    def delete_conversation(conversation_id):
        """Delete a conversation and all its messages"""
        return Conversation.delete(conversation_id)

    @staticmethod
    def get_conversation_messages(conversation_id):
        """Get messages for a conversation"""
        return Message.get_by_conversation(conversation_id)

    @staticmethod
    def save_message(conversation_id, role, content):
        """Save a message"""
        return Message.create(conversation_id, role, content)


class BurpParserService:
    """Parse Burp Suite HTTP requests"""

    @staticmethod
    def parse_http_request(raw_request):
        """Parse raw HTTP request into structured data"""
        lines = raw_request.strip().split('\n')

        if not lines:
            return None

        # Parse request line
        request_line = lines[0].strip()
        match = re.match(r'(\w+)\s+(.+?)\s+HTTP/[\d.]+', request_line)

        if not match:
            return None

        method = match.group(1)
        path = match.group(2)

        # Parse headers
        headers = {}
        body_start = 0

        for i, line in enumerate(lines[1:], 1):
            line = line.strip()

            if not line:
                # Empty line = end of headers
                body_start = i + 1
                break

            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip()] = value.strip()

        # Extract host
        host = headers.get('Host', '')

        # Build full URL
        protocol = 'https' if 'https://' in raw_request.lower() or ':443' in host else 'http'
        url = f"{protocol}://{host}{path}"

        # Extract body
        body = '\n'.join(lines[body_start:]).strip() if body_start > 0 else ''

        # Try to detect GraphQL
        graphql_operation = None
        graphql_query = None

        if body and ('query' in body or 'mutation' in body):
            try:
                body_json = json.loads(body)
                graphql_operation = body_json.get('operationName')
                graphql_query = body_json.get('query')
            except:
                pass

        return {
            'method': method,
            'url': url,
            'host': host,
            'path': path,
            'headers': headers,
            'body': body,
            'graphql_operation': graphql_operation,
            'graphql_query': graphql_query
        }

    @staticmethod
    def save_request(raw_request):
        """Parse and save HTTP request to database"""
        parsed = BurpParserService.parse_http_request(raw_request)

        if not parsed:
            return None

        # Convert headers to JSON
        headers_json = json.dumps(parsed['headers'])

        req_id = HTTPRequest.create(
            raw_request=raw_request,
            method=parsed['method'],
            url=parsed['url'],
            host=parsed['host'],
            path=parsed['path'],
            headers_json=headers_json,
            body=parsed['body'],
            graphql_operation=parsed['graphql_operation'],
            graphql_query=parsed['graphql_query']
        )

        return req_id

    @staticmethod
    def get_all_requests(limit=50):
        """Get all parsed requests"""
        return HTTPRequest.get_all(limit)

    @staticmethod
    def get_request(req_id):
        """Get request by ID"""
        return HTTPRequest.get(req_id)
