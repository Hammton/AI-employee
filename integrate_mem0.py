"""Integrate Mem0 for intelligent memory and context management"""
import os
from dotenv import load_dotenv
from mem0 import MemoryClient

load_dotenv()

class Mem0Memory:
    """
    Intelligent memory system using Mem0.
    
    Unlike simple conversation storage, Mem0:
    - Extracts key facts and preferences
    - Builds user profiles automatically
    - Enables semantic search
    - Maintains context across sessions
    """
    
    def __init__(self, api_key: str = None):
        """Initialize Mem0 client"""
        self.api_key = api_key or os.environ.get("MEM0_API_KEY")
        if not self.api_key:
            raise ValueError("MEM0_API_KEY not found in environment")
        
        self.client = MemoryClient(api_key=self.api_key)
    
    def add_conversation(self, user_id: str, messages: list):
        """
        Add a conversation to memory.
        Mem0 will automatically extract relevant facts.
        
        Args:
            user_id: Unique user identifier
            messages: List of message dicts with 'role' and 'content'
        
        Example:
            messages = [
                {"role": "user", "content": "I'm working on a Python project"},
                {"role": "assistant", "content": "Great! What kind of project?"}
            ]
        """
        return self.client.add(messages, user_id=user_id)
    
    def add_message(self, user_id: str, role: str, content: str):
        """
        Add a single message to memory.
        
        Args:
            user_id: Unique user identifier
            role: "user" or "assistant"
            content: Message content
        """
        messages = [{"role": role, "content": content}]
        return self.client.add(messages, user_id=user_id)
    
    def search(self, user_id: str, query: str, limit: int = 5):
        """
        Search memories semantically.
        
        Args:
            user_id: Unique user identifier
            query: Search query
            limit: Max results to return
        
        Returns:
            List of relevant memories with scores
        """
        results = self.client.search(
            query, 
            filters={"user_id": user_id},
            limit=limit
        )
        return results.get("results", [])
    
    def get_all_memories(self, user_id: str):
        """Get all memories for a user"""
        # Use search with empty query to get all memories
        # get_all() requires filters in v1.0+
        return self.client.search("", filters={"user_id": user_id}, limit=100)
    
    def get_context(self, user_id: str, current_query: str = None, limit: int = 5) -> str:
        """
        Get relevant context for the current conversation.
        
        This is what you inject into the AI prompt to give it memory.
        
        Args:
            user_id: Unique user identifier
            current_query: Current user query (for semantic search)
            limit: Max memories to include
        
        Returns:
            Formatted context string
        """
        if current_query:
            # Semantic search for relevant memories
            memories = self.search(user_id, current_query, limit=limit)
        else:
            # Get recent memories
            all_memories = self.get_all_memories(user_id)
            memories = all_memories.get("results", [])[:limit]
        
        if not memories:
            return "No previous context available."
        
        # Format memories for context
        context_lines = ["=== RELEVANT CONTEXT FROM MEMORY ==="]
        for mem in memories:
            memory_text = mem.get("memory", "")
            categories = mem.get("categories", [])
            score = mem.get("score", 0)
            
            context_lines.append(f"- {memory_text}")
            if categories:
                context_lines.append(f"  Categories: {', '.join(categories)}")
        
        context_lines.append("=== END CONTEXT ===")
        return "\n".join(context_lines)
    
    def delete_memory(self, memory_id: str):
        """Delete a specific memory"""
        return self.client.delete(memory_id)
    
    def delete_all_memories(self, user_id: str):
        """Delete all memories for a user"""
        return self.client.delete_all(user_id=user_id)


def demo_mem0():
    """Demo Mem0 integration"""
    print("\n" + "=" * 70)
    print("MEM0 INTELLIGENT MEMORY DEMO")
    print("=" * 70)
    
    # Check for API key
    api_key = os.environ.get("MEM0_API_KEY")
    if not api_key:
        print("\n❌ MEM0_API_KEY not found in .env file")
        print("\nTo use Mem0:")
        print("1. Sign up at https://app.mem0.ai/")
        print("2. Get your API key from https://app.mem0.ai/dashboard/settings?tab=api-keys")
        print("3. Add to .env: MEM0_API_KEY=your_key_here")
        return
    
    try:
        memory = Mem0Memory(api_key)
        user_id = "test_user_123"
        
        print(f"\n1. Initializing Mem0 for user: {user_id}")
        
        # Add some conversations
        print("\n2. Adding conversations to memory...")
        
        # Conversation 1: User preferences
        memory.add_conversation(user_id, [
            {"role": "user", "content": "I'm a vegetarian and allergic to nuts"},
            {"role": "assistant", "content": "Got it! I'll remember your dietary preferences."}
        ])
        
        # Conversation 2: Work context
        memory.add_conversation(user_id, [
            {"role": "user", "content": "I'm working on a Python AI agent project"},
            {"role": "assistant", "content": "Interesting! What features are you building?"}
        ])
        
        # Conversation 3: Personal info
        memory.add_conversation(user_id, [
            {"role": "user", "content": "I live in Nairobi and work remotely"},
            {"role": "assistant", "content": "Nice! Remote work from Nairobi sounds great."}
        ])
        
        print("   ✓ Added 3 conversations")
        
        # Search for relevant context
        print("\n3. Searching for relevant context...")
        
        queries = [
            "What are my dietary restrictions?",
            "What project am I working on?",
            "Where do I live?"
        ]
        
        for query in queries:
            print(f"\n   Query: '{query}'")
            results = memory.search(user_id, query, limit=2)
            for result in results:
                print(f"   → {result['memory']} (score: {result.get('score', 0):.2f})")
        
        # Get context for a new query
        print("\n4. Getting context for new conversation...")
        context = memory.get_context(user_id, "Tell me about restaurants", limit=3)
        print(f"\n{context}")
        
        print("\n" + "=" * 70)
        print("Mem0 is working! ✅")
        print("\nMem0 automatically:")
        print("- ✓ Extracted key facts from conversations")
        print("- ✓ Categorized information (health, user_preferences)")
        print("- ✓ Enabled semantic search with relevance scores")
        print("- ✓ Built user context intelligently")
        print("\nYou can now integrate this into kernel.py!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    demo_mem0()
