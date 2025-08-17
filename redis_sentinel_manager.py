#!/usr/bin/env python3
"""
Redis Sentinel Manager - Intelligent Redis sentinel operations
"""

import subprocess
import socket
import os
import platform

class RedisSentinelManager:
    """Manages Redis sentinel operations with proper error handling."""
    
    def __init__(self):
        # Cross-platform Redis configuration directory
        system = platform.system().lower()
        if system == "darwin":  # macOS
            self.config_dir = "/Users/lakshmikanthd/Downloads/redis-5.0.7"
        elif system == "windows":  # Windows
            self.config_dir = os.path.join(os.path.expanduser("~"), "Downloads", "redis-5.0.7")
        else:  # Linux
            self.config_dir = os.path.join(os.path.expanduser("~"), "Downloads", "redis-5.0.7")
        
        self.sentinel_conf = os.path.join(self.config_dir, "sentinel.conf")
        self.sentinel_port = 26379  # Default Redis sentinel port
    
    def is_sentinel_running(self):
        """Check if Redis sentinel is currently running on port 26379."""
        try:
            # Try to connect to sentinel port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', self.sentinel_port))
            sock.close()
            return result == 0
        except:
            return False
    
    def start_sentinel(self):
        """Start Redis sentinel if not already running."""
        if self.is_sentinel_running():
            return "Redis sentinel is already running on port 26379"
        
        try:
            # Start sentinel in background
            subprocess.Popen(
                ["redis-sentinel", self.sentinel_conf],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait a moment and check if it started successfully
            import time
            time.sleep(2)
            
            if self.is_sentinel_running():
                return "Redis sentinel started successfully on port 26379"
            else:
                return "Failed to start Redis sentinel"
                
        except Exception as e:
            return f"Failed to start Redis sentinel: {str(e)}"
    
    def stop_sentinel(self):
        """Stop Redis sentinel."""
        if not self.is_sentinel_running():
            return "Redis sentinel is not running"
        
        try:
            # Use redis-cli to connect to sentinel and shutdown
            result = subprocess.run(
                ["redis-cli", "-p", "26379", "shutdown"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return "Redis sentinel stopped successfully"
            else:
                return f"Failed to stop Redis sentinel: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return "Timeout while stopping Redis sentinel"
        except Exception as e:
            return f"Error stopping Redis sentinel: {str(e)}"
    
    def get_sentinel_status(self):
        """Get Redis sentinel status information."""
        if not self.is_sentinel_running():
            return "Redis sentinel is not running"
        
        try:
            result = subprocess.run(
                ["redis-cli", "-p", "26379", "info", "server"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return f"Redis sentinel is running on port 26379\n{result.stdout}"
            else:
                return f"Failed to get sentinel status: {result.stderr}"
                
        except Exception as e:
            return f"Error getting sentinel status: {str(e)}"

def create_sentinel_command():
    """Create a command that intelligently handles Redis sentinel operations."""
    manager = RedisSentinelManager()
    
    if manager.is_sentinel_running():
        return "echo 'Redis sentinel is already running on port 26379'"
    else:
        return f"redis-sentinel {manager.sentinel_conf}"

if __name__ == "__main__":
    # Test the sentinel manager
    manager = RedisSentinelManager()
    print("Sentinel Status:", manager.is_sentinel_running())
    print("Sentinel Info:", manager.get_sentinel_status()) 