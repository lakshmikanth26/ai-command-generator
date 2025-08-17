"""
Command Executor - Safe Command Execution and History Management

Handles the execution of system commands with safety checks and maintains
command history for the user.
"""

import os
import subprocess
import json
import datetime
from typing import Optional, Dict, List
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ExecutionResult:
    """Result of command execution."""
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    exit_code: int = 0
    execution_time: float = 0.0

class CommandExecutor:
    """Executes system commands safely and maintains history."""
    
    def __init__(self, history_file: str = "command_history.json"):
        self.history_file = Path(history_file)
        self.history = self._load_history()
        
        # Dangerous commands that require confirmation
        self.dangerous_commands = [
            "rm -rf",
            "sudo rm",
            "sudo shutdown",
            "sudo reboot",
            "sudo halt",
            "sudo poweroff",
            "sudo kill",
            "sudo dd",
            "sudo mkfs",
            "sudo fdisk",
            "sudo parted",
            "sudo chmod 777",
            "sudo chown root",
            "sudo passwd",
            "sudo useradd",
            "sudo userdel",
            "sudo groupadd",
            "sudo groupdel"
        ]
    
    def execute(self, command: str, original_input: str = "") -> ExecutionResult:
        """
        Execute a system command safely.
        
        Args:
            command: The system command to execute
            original_input: The original natural language input
            
        Returns:
            ExecutionResult with success status and output
        """
        import time
        start_time = time.time()
        
        # Check if command is dangerous
        if self._is_dangerous_command(command):
            return ExecutionResult(
                success=False,
                error="This command requires additional confirmation due to safety concerns."
            )
        
        try:
            # Execute the command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            execution_time = time.time() - start_time
            
            # Create result
            exec_result = ExecutionResult(
                success=result.returncode == 0,
                output=result.stdout.strip() if result.stdout else None,
                error=result.stderr.strip() if result.stderr else None,
                exit_code=result.returncode,
                execution_time=execution_time
            )
            
            # Save to history
            self._save_to_history(command, original_input, exec_result)
            
            return exec_result
            
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                error="Command execution timed out after 30 seconds."
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=f"Execution error: {str(e)}"
            )
    
    def _is_dangerous_command(self, command: str) -> bool:
        """Check if a command is potentially dangerous."""
        command_lower = command.lower()
        
        for dangerous in self.dangerous_commands:
            if dangerous.lower() in command_lower:
                return True
        
        return False
    
    def _load_history(self) -> List[Dict]:
        """Load command history from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []
    
    def _save_to_history(self, command: str, original_input: str, result: ExecutionResult):
        """Save command execution to history."""
        history_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "original_input": original_input,
            "command": command,
            "success": result.success,
            "exit_code": result.exit_code,
            "execution_time": result.execution_time,
            "output_length": len(result.output) if result.output else 0,
            "error_length": len(result.error) if result.error else 0
        }
        
        self.history.append(history_entry)
        
        # Keep only last 100 entries
        if len(self.history) > 100:
            self.history = self.history[-100:]
        
        # Save to file
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except IOError:
            pass  # Silently fail if can't save history
    
    def show_history(self, limit: int = 10):
        """Display command history."""
        if not self.history:
            print("No command history available.")
            return
        
        print(f"\nCommand History (last {min(limit, len(self.history))} entries):")
        print("-" * 80)
        
        for entry in self.history[-limit:]:
            timestamp = datetime.datetime.fromisoformat(entry["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            status = "✓" if entry["success"] else "✗"
            
            print(f"{timestamp} {status} {entry['original_input']}")
            print(f"  → {entry['command']}")
            if entry["execution_time"] > 0:
                print(f"  ⏱️  {entry['execution_time']:.2f}s")
            print()
    
    def clear_history(self):
        """Clear command history."""
        self.history = []
        if self.history_file.exists():
            self.history_file.unlink()
        print("Command history cleared.")
    
    def get_statistics(self) -> Dict:
        """Get execution statistics."""
        if not self.history:
            return {
                "total_commands": 0,
                "successful_commands": 0,
                "failed_commands": 0,
                "success_rate": 0.0,
                "average_execution_time": 0.0
            }
        
        total = len(self.history)
        successful = sum(1 for entry in self.history if entry["success"])
        failed = total - successful
        avg_time = sum(entry["execution_time"] for entry in self.history) / total
        
        return {
            "total_commands": total,
            "successful_commands": successful,
            "failed_commands": failed,
            "success_rate": (successful / total) * 100,
            "average_execution_time": avg_time
        } 