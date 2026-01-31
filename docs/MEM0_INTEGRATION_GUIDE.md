# Mem0 Integration Guide - Intelligent Memory for PocketAgent

## Why Mem0 > Simple Conversation Storage

### Simple Memory (What We Had)
```json
{
  "role": "user",
  "content": "I'm a vegetarian and allergic to nuts",
  "timestamp": "2026-01-31T10:00:00"
}
```
**Problem:** Just stores raw text. AI has to re-read everything every time.

### Mem0 Intelligence (What We Get)
```json
{
  "memory": "Allergic to nuts",
  "categories": ["health", "dietary_restrictions"],
  "user_id": "user123",
  "score": 0.95
}
```
**Benefit:** Extracts facts, categorizes, enables semantic search!

## Key Features

### 1. **Automatic Fact Extraction**
Mem0 automatically extracts key information:
- User preferences
- Personal details
- Work context
- Relationships
- Goals and tasks

### 2. **Semantic Search**
Instead of keyword matching, Mem0 understands meaning:
```python
# Query: "What are my food restrictions?"
# Finds: "Allergic to nuts", "Vegetarian diet"
# Even though exact words don't match!
```

### 3. **Categorization**
Automatically organizes memories:
- Health
- Work
- Personal
- Preferences
- Relationships

### 4. **Context Building**
Builds a rich user profile over time:
- Dietary preferences
- Work projects
- Location
- Communication style
- Interests

## Setup Instructions

### Step 1: Get Mem0 API Key
1. Sign up at https://app.mem0.ai/
2. Go to https://app.mem0.ai/dashboard/settings?tab=api-keys
3. Create a new API key
4. Copy it

### Step 2: Add to .env
```bash
MEM0_API_KEY=your_actual_key_here
```

### Step 3: Test Integration
```bash
python integrate_mem0.py
```

You should see:
```
✓ Added 3 conversations
→ Allergic to nuts (score: 0.95)
→ Working on Python AI agent project (score: 0.92)
→ Lives in Nairobi (score: 0.88)
```

## Integration into Kernel

### Current Flow (Without Mem0)
```
User Message → Kernel → AI Model → Response
```

### New Flow (With Mem0)
```
User Message → Kernel → Load Context from Mem0 → AI Model (with context) → Response → Save to Mem0
```

### Code Changes Needed

#### 1. Add Mem0 to Kernel Init
```python
# In kernel.py
from integrate_mem0 import Mem0Memory

class AgentKernel:
    def __init__(self, user_id: str = "default_user"):
        # ... existing code ...
        
        # Add Mem0 memory
        try:
            self.memory = Mem0Memory()
            logger.info("Mem0 memory initialized")
        except Exception as e:
            logger.warning(f"Mem0 not available: {e}")
            self.memory = None
```

#### 2. Load Context Before Processing
```python
# In kernel.py run() method
def run(self, goal: str):
    if not self.agent_executor:
        self.setup()
        if not self.agent_executor:
            return "Agent Kernel not initialized."
    
    # Load relevant context from Mem0
    context = ""
    if self.memory:
        try:
            context = self.memory.get_context(self.user_id, goal, limit=5)
            logger.info(f"Loaded context from Mem0: {len(context)} chars")
        except Exception as e:
            logger.warning(f"Failed to load context: {e}")
    
    # Inject context into the goal
    if context:
        enhanced_goal = f"{context}\n\nCurrent Query: {goal}"
    else:
        enhanced_goal = goal
    
    try:
        logger.info(f"Reasoning on goal: {goal}")
        result = self.agent_executor.invoke(
            {"messages": [{"role": "user", "content": enhanced_goal}]}
        )
        
        # Extract response
        messages = result.get("messages", [])
        if messages:
            last_message = messages[-1]
            content = self._extract_content(last_message)
            
            # Save to Mem0
            if self.memory and content:
                try:
                    self.memory.add_conversation(self.user_id, [
                        {"role": "user", "content": goal},
                        {"role": "assistant", "content": content}
                    ])
                    logger.info("Saved conversation to Mem0")
                except Exception as e:
                    logger.warning(f"Failed to save to Mem0: {e}")
            
            return content
        
        return ""
        
    except Exception as e:
        logger.error(f"Kernel Error: {e}")
        return f"Error executing goal: {e}"
```

#### 3. Helper Method for Content Extraction
```python
def _extract_content(self, message):
    """Extract content from various message formats"""
    if hasattr(message, 'content'):
        content = message.content
    elif isinstance(message, dict):
        content = message.get('content')
    else:
        content = str(message)
    
    # Handle list content
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, str):
                text_parts.append(item)
            elif hasattr(item, 'text'):
                text_parts.append(item.text)
        content = ' '.join(text_parts)
    
    return str(content) if content else ""
```

## Benefits You Get

### 1. **Persistent User Context**
```
User: "What did I tell you about my diet?"
AI: "You mentioned you're vegetarian and allergic to nuts."
```

### 2. **Proactive Assistance**
```
User: "Recommend a restaurant"
AI: "Since you're vegetarian and allergic to nuts, I'll find places with those options."
```

### 3. **Long-term Memory**
```
User (Week 1): "I'm working on a Python project"
User (Week 2): "How's my project going?"
AI: "Your Python AI agent project? Let me check the latest updates..."
```

### 4. **Smart Context Loading**
Only loads relevant memories for each query:
- Query about food → Loads dietary preferences
- Query about work → Loads project context
- Query about location → Loads location info

## Example Usage

### Conversation 1 (Building Context)
```
User: "I'm a software developer in Nairobi"
AI: "Great! What kind of development do you do?"
User: "I build AI agents with Python"
AI: "Interesting! Are you working on any projects?"
```

**Mem0 Extracts:**
- Occupation: Software developer
- Location: Nairobi
- Skills: AI agents, Python
- Current activity: Building projects

### Conversation 2 (Using Context)
```
User: "Find me a coworking space"
AI: "I'll find coworking spaces in Nairobi for you. Since you work on AI projects, would you prefer spaces with good tech communities?"
```

**Mem0 Retrieved:**
- Location: Nairobi
- Work: AI projects
- Context: Needs workspace

### Conversation 3 (Long-term Memory)
```
User: "What have I been working on?"
AI: "You've been building AI agents with Python. You're based in Nairobi and work as a software developer."
```

**Mem0 Retrieved:**
- All relevant work context
- Location context
- Professional background

## Cost & Performance

### Mem0 Pricing
- **Free Tier**: 1,000 memories/month
- **Pro**: $20/month for 10,000 memories
- **Enterprise**: Custom pricing

### Performance
- **Add Memory**: ~100ms
- **Search**: ~50ms
- **Get Context**: ~100ms

**Impact:** Minimal latency, huge context improvement!

## Comparison: Simple vs Mem0

| Feature | Simple JSON | Mem0 |
|---------|-------------|------|
| **Storage** | Raw conversations | Extracted facts |
| **Search** | Keyword matching | Semantic search |
| **Context** | Manual filtering | Automatic relevance |
| **Categories** | None | Automatic |
| **Scalability** | Poor (large files) | Excellent (indexed) |
| **Intelligence** | None | High |

## Testing Checklist

- [ ] Mem0 API key added to .env
- [ ] `pip install mem0ai` completed
- [ ] `python integrate_mem0.py` runs successfully
- [ ] Kernel updated with Mem0 integration
- [ ] Test conversation with memory
- [ ] Verify context retrieval
- [ ] Check semantic search

## Next Steps

1. **Get API Key** (5 min)
   - Sign up at https://app.mem0.ai/
   - Get API key
   - Add to .env

2. **Test Integration** (5 min)
   ```bash
   python integrate_mem0.py
   ```

3. **Update Kernel** (15 min)
   - Add Mem0 to __init__
   - Update run() method
   - Add _extract_content() helper

4. **Test End-to-End** (10 min)
   - Restart server
   - Send test messages
   - Verify memory works

5. **Deploy** (5 min)
   - Add MEM0_API_KEY to production env
   - Deploy updated code

## Troubleshooting

### "MEM0_API_KEY not found"
**Solution:** Add to .env file:
```bash
MEM0_API_KEY=your_key_here
```

### "Failed to save to Mem0"
**Solution:** Check API key is valid and has quota remaining

### "Context not loading"
**Solution:** Verify memories exist:
```python
memory = Mem0Memory()
all_memories = memory.get_all_memories(user_id)
print(all_memories)
```

## Advanced Features

### 1. **Memory Categories**
Mem0 automatically categorizes:
- health
- work
- personal
- preferences
- relationships

### 2. **Memory Scores**
Each memory has a relevance score (0-1):
- 0.9-1.0: Highly relevant
- 0.7-0.9: Relevant
- 0.5-0.7: Somewhat relevant
- <0.5: Not very relevant

### 3. **Memory Updates**
Mem0 can update existing memories:
```python
# Old: "Lives in Nairobi"
# New: "Lives in Nairobi, Kenya, East Africa"
# Mem0 merges and updates automatically
```

### 4. **Memory Deletion**
Clean up old or irrelevant memories:
```python
memory.delete_memory(memory_id)
memory.delete_all_memories(user_id)
```

## Conclusion

Mem0 transforms your agent from a **stateless chatbot** into an **intelligent assistant** that:
- Remembers user preferences
- Builds context over time
- Provides proactive assistance
- Scales to thousands of users

**This is the missing piece that makes your agent truly personal!** 🧠✨
