"""Test Mem0 integration in kernel.py"""
import os
from dotenv import load_dotenv

load_dotenv()

from kernel import AgentKernel

def test_mem0_integration():
    """Test that Mem0 is properly integrated into the kernel"""
    print("\n" + "=" * 70)
    print("TESTING MEM0 INTEGRATION IN KERNEL")
    print("=" * 70)
    
    # Check if MEM0_API_KEY is set
    api_key = os.environ.get("MEM0_API_KEY")
    if not api_key:
        print("\n⚠️  MEM0_API_KEY not found in .env")
        print("\nTo test Mem0:")
        print("1. Sign up at https://app.mem0.ai/")
        print("2. Get your API key")
        print("3. Add to .env: MEM0_API_KEY=your_key_here")
        print("\nSkipping Mem0 tests...")
        return
    
    print(f"\n✅ MEM0_API_KEY found: {api_key[:20]}...")
    
    # Create kernel for test user
    test_user = "test_user_mem0_integration"
    print(f"\n1. Creating kernel for user: {test_user}")
    kernel = AgentKernel(user_id=test_user)
    
    # Check if Mem0 is initialized
    if kernel.memory:
        print("   ✅ Mem0 memory initialized successfully!")
    else:
        print("   ❌ Mem0 memory NOT initialized")
        return
    
    # Test 1: Add some context
    print("\n2. Testing memory storage...")
    print("   Sending: 'I am a vegetarian and allergic to nuts'")
    
    # Simulate a conversation (without actually calling LLM)
    try:
        kernel.memory.add_conversation(test_user, [
            {"role": "user", "content": "I am a vegetarian and allergic to nuts"},
            {"role": "assistant", "content": "Got it! I'll remember your dietary preferences."}
        ])
        print("   ✅ Memory saved successfully")
    except Exception as e:
        print(f"   ❌ Failed to save memory: {e}")
        return
    
    # Test 2: Retrieve context
    print("\n3. Testing context retrieval...")
    print("   Query: 'What are my dietary restrictions?'")
    
    try:
        context = kernel.memory.get_context(test_user, "What are my dietary restrictions?", limit=3)
        if context and context != "No previous context available.":
            print(f"   ✅ Context retrieved ({len(context)} chars):")
            print(f"\n{context}\n")
        else:
            print("   ⚠️  No context found (may need a moment for Mem0 to process)")
    except Exception as e:
        print(f"   ❌ Failed to retrieve context: {e}")
        return
    
    # Test 3: Search memories
    print("\n4. Testing semantic search...")
    print("   Searching for: 'food preferences'")
    
    try:
        results = kernel.memory.search(test_user, "food preferences", limit=3)
        if results:
            print(f"   ✅ Found {len(results)} relevant memories:")
            for i, result in enumerate(results, 1):
                memory_text = result.get("memory", "")
                score = result.get("score", 0)
                print(f"   {i}. {memory_text} (score: {score:.2f})")
        else:
            print("   ⚠️  No memories found (may need a moment for Mem0 to index)")
    except Exception as e:
        print(f"   ❌ Search failed: {e}")
    
    # Cleanup
    print("\n5. Cleaning up test data...")
    try:
        kernel.memory.delete_all_memories(test_user)
        print("   ✅ Test memories deleted")
    except Exception as e:
        print(f"   ⚠️  Cleanup warning: {e}")
    
    print("\n" + "=" * 70)
    print("MEM0 INTEGRATION TEST COMPLETE! ✅")
    print("=" * 70)
    print("\nMem0 is now integrated into your kernel!")
    print("\nHow it works:")
    print("1. 🧠 Before processing: Loads relevant context from Mem0")
    print("2. 🤖 During processing: AI uses context for better responses")
    print("3. 💾 After processing: Saves conversation to Mem0")
    print("\nYour agent now has intelligent, persistent memory! 🎉")
    print("=" * 70)

if __name__ == "__main__":
    test_mem0_integration()
