#!/usr/bin/env python3
"""
AI Command Generator - Web UI

Flask web application providing a modern web interface for the AI Command Generator.
"""

import os
import sys
import json
import datetime
import socket
from pathlib import Path
from typing import Dict, List, Optional

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from command_mapper import CommandMapper
from executor import CommandExecutor

try:
    from flask import Flask, render_template, request, jsonify, session
    from flask_socketio import SocketIO, emit
except ImportError:
    print("Flask not installed. Installing required packages...")
    os.system("pip install flask flask-socketio")
    from flask import Flask, render_template, request, jsonify, session
    from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ai-command-generator-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize components
command_mapper = CommandMapper()
executor = CommandExecutor()

# Chat history storage (in memory for web session)
chat_history = []

@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages via REST API."""
    data = request.get_json()
    user_input = data.get('message', '').strip()
    
    if not user_input:
        return jsonify({'error': 'No message provided'})
    
    # Process the command
    result = process_command(user_input)
    
    return jsonify(result)

@socketio.on('send_message')
def handle_message(data):
    """Handle WebSocket messages."""
    user_input = data.get('message', '').strip()
    
    if not user_input:
        emit('error', {'error': 'No message provided'})
        return
    
    # Process the command
    result = process_command(user_input)
    
    # Emit response back to client
    emit('bot_response', result)

def process_command(user_input: str) -> Dict:
    """Process a user command and return result."""
    try:
        # Map to command
        # Use spell correction and mapping
        mapped_command, original_input, suggested_correction = command_mapper.map_to_command_with_correction(user_input)
        
        if not mapped_command:
            return {
                'type': 'error',
                'message': "I couldn't understand that command. Please try rephrasing.",
                'timestamp': datetime.datetime.now().isoformat(),
                'user_input': user_input,
                'mapped_command': None,
                'execution_result': None,
                'success': False
            }
        
        # Check if this is an intelligent command (Python script)
        is_intelligent_command = mapped_command.startswith('python -c')
        
        # Check if this is a command listing request
        is_command_listing = any(keyword in user_input.lower() for keyword in ['list all commands', 'show all commands', 'help commands'])
        is_redis_listing = any(keyword in user_input.lower() for keyword in ['list redis commands', 'show redis commands'])
        
        # Check if there was a spelling correction
        if suggested_correction:
            if is_redis_listing:
                message = f"I think you meant: '{suggested_correction}'\n\nI'll show you all Redis commands."
            elif is_command_listing:
                message = f"I think you meant: '{suggested_correction}'\n\nI'll show you all available commands organized by category."
            elif is_intelligent_command:
                message = f"I think you meant: '{suggested_correction}'\n\nI'll check Redis sentinel status and start it if needed."
            else:
                message = f"I think you meant: '{suggested_correction}'\n\nI'll execute: {mapped_command}"
        else:
            if is_redis_listing:
                message = f"I'll show you all Redis commands."
            elif is_command_listing:
                message = f"I'll show you all available commands organized by category."
            elif is_intelligent_command:
                message = f"I'll check Redis sentinel status and start it if needed."
            else:
                message = f"I'll execute: {mapped_command}"
        
        # For web UI, we'll show the command but not execute it automatically
        # User can choose to execute via a separate action
        return {
            'type': 'command_mapped',
            'message': message,
            'timestamp': datetime.datetime.now().isoformat(),
            'user_input': user_input,
            'mapped_command': mapped_command,
            'execution_result': None,
            'success': True,
            'needs_confirmation': True,
            'suggested_correction': suggested_correction,
            'is_intelligent_command': is_intelligent_command,
            'is_command_listing': is_command_listing,
            'is_redis_listing': is_redis_listing
        }
        
    except Exception as e:
        return {
            'type': 'error',
            'message': f"Error processing command: {str(e)}",
            'timestamp': datetime.datetime.now().isoformat(),
            'user_input': user_input,
            'mapped_command': None,
            'execution_result': None,
            'success': False
        }

@app.route('/api/execute', methods=['POST'])
def execute_command():
    """Execute a mapped command."""
    data = request.get_json()
    mapped_command = data.get('command', '').strip()
    user_input = data.get('user_input', '').strip()
    
    if not mapped_command:
        return jsonify({'error': 'No command provided'})
    
    try:
        # Execute the command
        result = executor.execute(mapped_command, user_input)
        
        return jsonify({
            'type': 'execution_result',
            'success': result.success,
            'output': result.output,
            'error': result.error,
            'execution_time': result.execution_time,
            'timestamp': datetime.datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'type': 'error',
            'error': f"Execution error: {str(e)}",
            'timestamp': datetime.datetime.now().isoformat()
        })

@app.route('/api/history')
def get_history():
    """Get chat history."""
    return jsonify(chat_history)

@app.route('/api/clear_history', methods=['POST'])
def clear_history():
    """Clear chat history."""
    global chat_history
    chat_history = []
    return jsonify({'message': 'History cleared'})

@app.route('/api/help')
def get_help():
    """Get help information."""
    help_data = {
        'examples': [
            "open chrome",
            "list all ports with 8085",
            "check wifi status",
            "search for weather in London",
            "list files in current directory",
            "what is the current time",
            "display current date",
            "start redis sentinel",
            "start redis server",
            "check redis status",
            "check redis sentinel status",
            "check RAM status",
            "check cpu usage",
            "list all commands",
            "list redis commands",
            "start zookeeper",
            "start kafka",
            "list kafka topics",
            "delete kafka topic my_topic"
        ],
        'features': [
            "Natural language to command conversion",
            "Cross-platform support",
            "AI-powered mapping (with OpenAI API)",
            "Fallback pattern matching",
            "Safe command execution",
            "Command history tracking"
        ]
    }
    return jsonify(help_data)

@app.route('/api/commands')
def get_commands():
    """Get all available commands organized by category."""
    try:
        from command_mapper import CommandMapper
        mapper = CommandMapper()
        categories = mapper.get_commands_by_category()
        
        # Format the data for the frontend
        formatted_categories = {}
        for category, commands in categories.items():
            formatted_categories[category] = []
            for cmd in commands:
                formatted_categories[category].append({
                    'example': cmd['example'],
                    'description': cmd['description'],
                    'command': cmd['command']
                })
        
        return jsonify({
            'categories': formatted_categories,
            'total_commands': sum(len(cmds) for cmds in categories.values())
        })
    except Exception as e:
        return jsonify({
            'error': f'Error loading commands: {str(e)}',
            'categories': {},
            'total_commands': 0
        })

def find_free_port(start_port=5000, max_attempts=100):
    """Find a free port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"Could not find a free port in range {start_port}-{start_port + max_attempts}")

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    templates_dir = Path(__file__).parent / 'templates'
    templates_dir.mkdir(exist_ok=True)
    
    # Find a free port
    try:
        port = find_free_port()
        print("🤖 AI Command Generator - Web UI")
        print("=" * 40)
        print(f"Platform: {command_mapper.system}")
        print(f"AI Available: {command_mapper.use_ai}")
        print(f"Server starting on http://localhost:{port}")
        print("Press Ctrl+C to stop")
        
        socketio.run(app, debug=True, host='0.0.0.0', port=port)
    except RuntimeError as e:
        print(f"❌ Error: {e}")
        sys.exit(1) 