#!/usr/bin/env python3
"""
Port Finder Utility

Utility script to find free ports and check port availability.
"""

import socket
import sys
from typing import List, Optional

def find_free_port(start_port: int = 5000, max_attempts: int = 100) -> Optional[int]:
    """
    Find a free port starting from start_port.
    
    Args:
        start_port: Starting port number to check
        max_attempts: Maximum number of ports to check
        
    Returns:
        Free port number or None if no free port found
    """
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

def check_port_availability(port: int) -> bool:
    """
    Check if a specific port is available.
    
    Args:
        port: Port number to check
        
    Returns:
        True if port is available, False otherwise
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def find_multiple_free_ports(count: int = 5, start_port: int = 5000) -> List[int]:
    """
    Find multiple free ports.
    
    Args:
        count: Number of free ports to find
        start_port: Starting port number
        
    Returns:
        List of free port numbers
    """
    free_ports = []
    current_port = start_port
    
    while len(free_ports) < count:
        port = find_free_port(current_port, 1)
        if port:
            free_ports.append(port)
            current_port = port + 1
        else:
            current_port += 1
            
        if current_port > 65535:
            break
    
    return free_ports

def main():
    """Main function for command line usage."""
    if len(sys.argv) < 2:
        print("Port Finder Utility")
        print("=" * 20)
        print("Usage:")
        print("  python port_finder.py find [start_port] [max_attempts]")
        print("  python port_finder.py check <port>")
        print("  python port_finder.py multiple [count] [start_port]")
        print()
        print("Examples:")
        print("  python port_finder.py find")
        print("  python port_finder.py find 8000 50")
        print("  python port_finder.py check 5000")
        print("  python port_finder.py multiple 5 5000")
        return
    
    command = sys.argv[1].lower()
    
    if command == "find":
        start_port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
        max_attempts = int(sys.argv[3]) if len(sys.argv) > 3 else 100
        
        print(f"🔍 Looking for free port starting from {start_port}...")
        port = find_free_port(start_port, max_attempts)
        
        if port:
            print(f"✅ Found free port: {port}")
        else:
            print(f"❌ No free port found in range {start_port}-{start_port + max_attempts}")
    
    elif command == "check":
        if len(sys.argv) < 3:
            print("❌ Error: Please specify a port number")
            return
        
        port = int(sys.argv[2])
        available = check_port_availability(port)
        
        if available:
            print(f"✅ Port {port} is available")
        else:
            print(f"❌ Port {port} is not available")
    
    elif command == "multiple":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        start_port = int(sys.argv[3]) if len(sys.argv) > 3 else 5000
        
        print(f"🔍 Looking for {count} free ports starting from {start_port}...")
        ports = find_multiple_free_ports(count, start_port)
        
        if ports:
            print(f"✅ Found {len(ports)} free ports:")
            for port in ports:
                print(f"  • {port}")
        else:
            print(f"❌ Could not find {count} free ports")
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'find', 'check', or 'multiple'")

if __name__ == "__main__":
    main() 