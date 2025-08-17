#!/usr/bin/env python3
"""
AI Command Generator - Web UI Launcher

This script sets up the environment and launches the web-based chatbot interface.
"""

import os
import sys
import subprocess
import webbrowser
import time
import socket
import re
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import flask
        import flask_socketio
        return True
    except ImportError:
        return False

def install_dependencies():
    """Install required dependencies."""
    print("Installing required dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies. Please install manually:")
        print("pip install flask flask-socketio")
        return False

def create_templates_directory():
    """Ensure templates directory exists."""
    templates_dir = Path(__file__).parent / 'templates'
    templates_dir.mkdir(exist_ok=True)
    return templates_dir.exists()

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

def extract_port_from_output(output):
    """Extract port number from server output."""
    # Look for patterns like "Server starting on http://localhost:PORT"
    match = re.search(r'http://localhost:(\d+)', output)
    if match:
        return int(match.group(1))
    return None

def launch_web_ui():
    """Launch the web UI."""
    print("🤖 AI Command Generator - Web UI")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("web_ui.py").exists():
        print("❌ Error: web_ui.py not found. Please run this script from the ai_command_generator directory.")
        return False
    
    # Check dependencies
    if not check_dependencies():
        print("⚠️  Flask dependencies not found.")
        if not install_dependencies():
            return False
    
    # Ensure templates directory exists
    if not create_templates_directory():
        print("❌ Error: Could not create templates directory.")
        return False
    
    # Check if templates/index.html exists
    if not Path("templates/index.html").exists():
        print("❌ Error: templates/index.html not found.")
        return False
    
    print("✅ Environment ready!")
    print("🚀 Starting web server...")
    print("📱 The web interface will open in your browser automatically.")
    print("⏹️  Press Ctrl+C to stop the server")
    print()
    
    # Find a free port first
    try:
        free_port = find_free_port()
        print(f"🔍 Found free port: {free_port}")
    except RuntimeError as e:
        print(f"❌ Error finding free port: {e}")
        return False
    
    # Launch the web UI with port detection
    try:
        # Start the web UI process
        process = subprocess.Popen(
            [sys.executable, "web_ui.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Wait for server to start and extract port
        port = None
        max_wait = 10  # seconds
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            if process.poll() is not None:
                print("❌ Web UI process exited unexpectedly")
                return False
            
            # Read output line by line
            line = process.stdout.readline()
            if line:
                print(line.strip())
                if not port:
                    port = extract_port_from_output(line)
                    if port:
                        print(f"🌐 Server detected on port: {port}")
                        break
            
            time.sleep(0.1)
        
        if not port:
            print(f"⚠️  Could not detect port, using fallback: {free_port}")
            port = free_port
        
        # Open browser after server is ready
        def open_browser():
            time.sleep(1)  # Give server a moment to fully start
            try:
                webbrowser.open(f'http://localhost:{port}')
                print(f"📱 Browser opened: http://localhost:{port}")
            except Exception as e:
                print(f"⚠️  Could not open browser automatically. Please visit http://localhost:{port}")
        
        # Start browser in background
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Wait for process to complete
        process.wait()
        
    except KeyboardInterrupt:
        print("\n👋 Web UI stopped. Goodbye!")
        if 'process' in locals():
            process.terminate()
    except Exception as e:
        print(f"❌ Error launching web UI: {e}")
        return False
    
    return True

def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("AI Command Generator - Web UI Launcher")
        print()
        print("Usage:")
        print("  python launch_web_ui.py          # Launch web UI")
        print("  python launch_web_ui.py --help   # Show this help")
        print()
        print("Features:")
        print("  • Modern web-based chatbot interface")
        print("  • Real-time communication via WebSocket")
        print("  • Interactive command execution")
        print("  • Beautiful responsive design")
        print("  • Works on desktop and mobile browsers")
        return
    
    success = launch_web_ui()
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main() 