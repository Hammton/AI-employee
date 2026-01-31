"""Add conversation memory system to PocketAgent"""
import os
import json
from datetime import datetime
from pathlib import Path

class ConversationMemory:
    """Simple conversation memory using JSON files"""
    
    def __init__(self, user_id: str, memory_dir: str = "memory"):
        self.user_id = user_id
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        self.memory_file = self.memory_dir / f"{self._sanitize_user_id(user_id)}.json"
    
    def _sanitize_user_id(self, user_id: str) -> str:
        """Convert user_id to safe filename"""
        return user_id.replace("@", "_at_").replace("+", "plus_").replace("/", "_")
    
    def save_message(self, role: str, content: str, metadata: dict = None):
        """Save a message to conversation history"""
        history = self.load_history()
        
        message = {
            "role": role,  # "user" or "assistant"
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        history.append(message)
        
        # Keep only last 100 messages to avoid huge files
        if len(history) > 100:
            history = history[-100:]
        
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    
    def load_history(self, limit: int = None) -> list:
        """Load conversation history"""
        if not self.memory_file.exists():
            return []
        
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            if limit:
                return history[-limit:]
            return history
        except Exception as e:
            print(f"Error loading memory: {e}")
            return []
    
    def get_context_summary(self, limit: int = 10) -> str:
        """Get a summary of recent conversation for context"""
        history = self.load_history(limit=limit)
        
        if not history:
            return "No previous conversation history."
        
        summary_lines = ["Recent conversation:"]
        for msg in history:
            role = msg['role'].capitalize()
            content = msg['content'][:100]  # Truncate long messages
            summary_lines.append(f"{role}: {content}")
        
        return "\n".join(summary_lines)
    
    def clear_history(self):
        """Clear conversation history"""
        if self.memory_file.exists():
            self.memory_file.unlink()


def demo_memory_system():
    """Demo the memory system"""
    print("\n" + "=" * 70)
    print("CONVERSATION MEMORY SYSTEM DEMO")
    print("=" * 70)
    
    # Create memory for a test user
    user_id = "+254708235245@c.us"
    memory = ConversationMemory(user_id)
    
    print(f"\n1. Creating memory for user: {user_id}")
    print(f"   Memory file: {memory.memory_file}")
    
    # Save some test messages
    print("\n2. Saving test conversation...")
    memory.save_message("user", "Hello, can you help me with my emails?")
    memory.save_message("assistant", "Of course! I can help you manage your emails. What would you like to do?")
    memory.save_message("user", "Show me my unread emails")
    memory.save_message("assistant", "I found 5 unread emails in your inbox...")
    
    # Load history
    print("\n3. Loading conversation history...")
    history = memory.load_history()
    print(f"   Total messages: {len(history)}")
    
    for msg in history:
        print(f"\n   {msg['role'].upper()}: {msg['content']}")
        print(f"   Time: {msg['timestamp']}")
    
    # Get context summary
    print("\n4. Getting context summary...")
    summary = memory.get_context_summary(limit=5)
    print(f"\n{summary}")
    
    print("\n" + "=" * 70)
    print("Memory system is working! ✅")
    print("=" * 70)


if __name__ == "__main__":
    demo_memory_system()
