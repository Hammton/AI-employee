# Skills System Design for PocketAgent

## What Are Skills and Why They're Valuable

### The Problem Skills Solve

Right now, your agent can do many things, but:
1. **No Memory of Workflows**: If a user teaches you a process, you forget it next session
2. **Repetitive Instructions**: Users must explain the same multi-step tasks repeatedly
3. **No Personalization**: Every user starts from scratch
4. **Context Overload**: Loading all capabilities at once wastes tokens

### What Skills Are

Skills are **reusable, modular capabilities** that:
- Package instructions, workflows, and context into folders
- Load on-demand (only when needed)
- Persist across sessions
- Can be user-created or pre-built
- Are version-controlled and shareable

Think of them as **"muscle memory" for your AI agent**.

---

## Real User Cases

### Case 1: Morning Email Routine
**User Request**: "Every morning at 8am, read my emails, draft a LinkedIn post about interesting topics, and save it to Notion"

**Without Skills**: User must explain this every single day
**With Skills**: 
```
skills/morning-routine/
├── SKILL.md          # Instructions for the workflow
├── schedule.json     # When to run (8am daily)
└── templates/
    └── linkedin.md   # LinkedIn post template
```

The agent:
1. Loads the skill at 8am automatically
2. Follows the workflow instructions
3. Uses the template for consistency
4. Saves results to Notion

### Case 2: Product Photography Workflow
**User Request**: "When I send a product image, analyze it, generate a professional product shot, and create a marketing description"

**Without Skills**: User must explain the full workflow each time
**With Skills**:
```
skills/product-photography/
├── SKILL.md              # Workflow instructions
├── prompts/
│   ├── analysis.txt      # How to analyze products
│   └── generation.txt    # Image generation prompt template
└── examples/
    └── good_shots.md     # Reference examples
```

### Case 3: Code Review Assistant
**User Request**: "Review my code for security issues, performance problems, and suggest improvements"

**Without Skills**: Generic code review
**With Skills**:
```
skills/code-review/
├── SKILL.md
├── checklists/
│   ├── security.md       # Security checklist
│   ├── performance.md    # Performance patterns
│   └── best-practices.md # Language-specific best practices
└── scripts/
    └── analyze.py        # Optional: automated checks
```

---

## How Skills Work

### 1. Skill Structure
```
skills/
├── email-management/
│   ├── SKILL.md              # Main instructions (REQUIRED)
│   ├── schedule.json         # When to run (OPTIONAL)
│   ├── templates/            # Reusable templates (OPTIONAL)
│   │   └── email_draft.md
│   └── scripts/              # Executable scripts (OPTIONAL)
│       └── filter_emails.py
│
├── linkedin-posting/
│   ├── SKILL.md
│   ├── templates/
│   │   └── post_template.md
│   └── examples/
│       └── good_posts.md
│
└── notion-integration/
    ├── SKILL.md
    └── config.json           # Notion database IDs, etc.
```

### 2. SKILL.md Format
```markdown
---
name: Morning Email Routine
version: 1.0.0
triggers:
  - schedule: "0 8 * * *"  # Cron format: 8am daily
  - keywords: ["morning routine", "daily email"]
dependencies:
  - gmail
  - notion
  - linkedin
---

# Morning Email Routine

## Purpose
Automate the morning email review and LinkedIn content creation workflow.

## Workflow
1. **Read Emails** (8:00 AM)
   - Fetch unread emails from Gmail
   - Filter for important topics (AI, tech, business)
   - Summarize key points

2. **Draft LinkedIn Post**
   - Extract interesting insights from emails
   - Use template from `templates/linkedin.md`
   - Keep it professional and engaging
   - Include relevant hashtags

3. **Save to Notion**
   - Create new page in "Content Ideas" database
   - Add draft post
   - Tag with "LinkedIn" and "Draft"
   - Set status to "Review"

## Templates
- LinkedIn post template: `templates/linkedin.md`

## Configuration
- Notion database ID: stored in user memory
- Email filters: AI, technology, business, startups
```

### 3. How Skills Load

**Dynamic Loading** (saves context):
```python
# User says: "Run my morning routine"
# Agent:
1. Searches skills/ folder for matching skill
2. Loads SKILL.md into context
3. Executes workflow
4. Unloads skill after completion
```

**Scheduled Loading** (for automation):
```python
# At 8:00 AM:
1. Scheduler checks skills with schedule.json
2. Loads matching skills
3. Executes workflows
4. Sends results to user
```

---

## Implementation Plan (Safe, No Breaking Changes)

### Phase 1: Core Skills Infrastructure (Week 1)

#### Step 1.1: Create Skills Directory Structure
```python
# skills/skill_manager.py
class SkillManager:
    def __init__(self, skills_dir="skills"):
        self.skills_dir = skills_dir
        self.loaded_skills = {}
    
    def discover_skills(self):
        """Scan skills/ folder and return available skills"""
        pass
    
    def load_skill(self, skill_name):
        """Load a skill's SKILL.md into memory"""
        pass
    
    def unload_skill(self, skill_name):
        """Remove skill from active context"""
        pass
    
    def get_skill_prompt(self, skill_name):
        """Get the skill's instructions as a prompt"""
        pass
```

#### Step 1.2: Integrate with Kernel (NO BREAKING CHANGES)
```python
# kernel.py - ADD these methods (don't modify existing ones)
class AgentKernel:
    def __init__(self, user_id: str = "default_user"):
        # ... existing code ...
        
        # NEW: Skills system
        self.skill_manager = SkillManager(f"skills/{user_id}")
        self.active_skills = []
    
    def load_skill(self, skill_name: str):
        """Load a skill for this session"""
        skill_prompt = self.skill_manager.get_skill_prompt(skill_name)
        self.active_skills.append(skill_name)
        return skill_prompt
    
    def run_with_skill(self, prompt: str, skill_name: str):
        """Run agent with a specific skill loaded"""
        skill_prompt = self.load_skill(skill_name)
        enhanced_prompt = f"{skill_prompt}\n\nUser Request: {prompt}"
        return self.run(enhanced_prompt)
```

#### Step 1.3: Add Skill Commands to main_v2.py (NO BREAKING CHANGES)
```python
# main_v2.py - ADD these commands (don't modify existing ones)

# /skills command - List available skills
if text_lower.startswith("/skills") or text_lower.startswith("/list-skills"):
    skills = user_kernel.skill_manager.discover_skills()
    if not skills:
        return "No skills available yet. Create your first skill with /create-skill"
    
    skill_list = "\n".join([f"• {s['name']} - {s['description']}" for s in skills])
    return f"📚 Available Skills:\n\n{skill_list}\n\nUse /use-skill <name> to activate"

# /use-skill command - Load and use a skill
if text_lower.startswith("/use-skill"):
    skill_name = msg_text.split(" ", 1)[1].strip() if " " in msg_text else ""
    if not skill_name:
        return "Usage: /use-skill <skill_name>\nExample: /use-skill morning-routine"
    
    try:
        result = user_kernel.run_with_skill(
            "Execute this skill's workflow",
            skill_name
        )
        return result
    except Exception as e:
        return f"Failed to run skill: {e}"

# /create-skill command - Interactive skill creation
if text_lower.startswith("/create-skill"):
    return """📝 Create a New Skill

Send me the details in this format:

**Name**: morning-routine
**Description**: Read emails and draft LinkedIn posts
**Workflow**:
1. Read unread emails
2. Extract interesting topics
3. Draft LinkedIn post
4. Save to Notion

I'll create the skill for you!"""
```

### Phase 2: User-Created Skills (Week 2)

#### Step 2.1: Skill Creation Interface
```python
# skills/skill_creator.py
class SkillCreator:
    def create_from_conversation(self, user_input: str, user_id: str):
        """Create a skill from natural language description"""
        # Parse user input
        # Generate SKILL.md
        # Save to skills/{user_id}/{skill_name}/
        pass
    
    def create_from_example(self, example_messages: list, skill_name: str):
        """Learn a skill from example interactions"""
        # Analyze conversation history
        # Extract workflow pattern
        # Generate SKILL.md
        pass
```

#### Step 2.2: Memory Integration
```python
# When user teaches a workflow:
# "Remember this: Every morning, read my emails and draft a LinkedIn post"

# Agent:
1. Detects "remember this" trigger
2. Extracts workflow from conversation
3. Creates skill automatically
4. Saves to skills/{user_id}/
5. Confirms: "✅ Created skill 'morning-routine'. Use /use-skill morning-routine to run it"
```

### Phase 3: Scheduled Skills (Week 3)

#### Step 3.1: Scheduler Integration
```python
# scheduler.py - NEW FILE
import schedule
import time
from kernel import AgentKernel

class SkillScheduler:
    def __init__(self):
        self.scheduled_skills = {}
    
    def schedule_skill(self, user_id: str, skill_name: str, cron: str):
        """Schedule a skill to run at specific times"""
        # Parse cron expression
        # Add to schedule
        pass
    
    def run_scheduled_skills(self):
        """Check and run scheduled skills"""
        while True:
            schedule.run_pending()
            time.sleep(60)
```

#### Step 3.2: Add to main_v2.py
```python
# main_v2.py - ADD scheduler startup
if ENABLE_SCHEDULER:
    from scheduler import SkillScheduler
    skill_scheduler = SkillScheduler()
    # Start scheduler in background thread
```

---

## Safety Measures (Preventing Breakage)

### 1. Backward Compatibility
- All new code is ADDITIVE (no modifications to existing functions)
- Skills are OPTIONAL (agent works without them)
- Existing commands unchanged

### 2. Graceful Degradation
```python
# If skills/ folder doesn't exist
if not os.path.exists(self.skills_dir):
    logger.info("Skills directory not found - skills disabled")
    return

# If skill fails to load
try:
    skill_prompt = self.load_skill(skill_name)
except Exception as e:
    logger.warning(f"Skill load failed: {e}")
    return "Skill not available, using default behavior"
```

### 3. Testing Strategy
```python
# tests/test_skills.py
def test_skills_optional():
    """Ensure agent works without skills"""
    kernel = AgentKernel()
    result = kernel.run("Hello")
    assert result  # Should work fine

def test_skill_loading():
    """Test skill loading doesn't break agent"""
    kernel = AgentKernel()
    kernel.load_skill("test-skill")
    result = kernel.run("Hello")
    assert result  # Should still work

def test_invalid_skill():
    """Test graceful handling of invalid skills"""
    kernel = AgentKernel()
    result = kernel.load_skill("nonexistent-skill")
    assert result is None  # Should not crash
```

---

## Example Skills to Start With

### 1. Email Management
```markdown
---
name: Email Management
triggers: ["check emails", "read emails"]
dependencies: ["gmail"]
---

# Email Management Skill

## Workflow
1. Fetch unread emails from Gmail
2. Categorize by importance (urgent, normal, low)
3. Summarize key points
4. Suggest actions (reply, archive, flag)
```

### 2. LinkedIn Content Creator
```markdown
---
name: LinkedIn Content Creator
triggers: ["create linkedin post", "draft post"]
dependencies: ["notion"]
---

# LinkedIn Content Creator

## Workflow
1. Get topic from user or recent emails
2. Research topic (if needed)
3. Draft engaging post (150-300 words)
4. Add relevant hashtags
5. Save to Notion for review
```

### 3. Daily Standup
```markdown
---
name: Daily Standup
schedule: "0 9 * * 1-5"  # 9am weekdays
dependencies: ["asana", "googlecalendar"]
---

# Daily Standup Skill

## Workflow
1. Get today's calendar events
2. Get Asana tasks due today
3. Generate standup summary:
   - What I did yesterday
   - What I'm doing today
   - Any blockers
4. Send to user
```

---

## Why This Won't Break Your Code

### 1. Isolated Module
- Skills system is a separate module (`skills/`)
- Doesn't modify existing kernel.py logic
- Only ADDS new methods

### 2. Optional Feature
- Agent works perfectly without skills
- Skills only load when explicitly requested
- No impact on existing workflows

### 3. Incremental Rollout
- Phase 1: Just skill loading (no automation)
- Phase 2: User creation (still manual)
- Phase 3: Scheduling (fully automated)

### 4. Easy Rollback
```bash
# If something breaks:
git checkout kernel.py  # Restore original
rm -rf skills/          # Remove skills system
# Agent works exactly as before
```

---

## Next Steps

1. **Review this design** - Does it make sense for your use case?
2. **Choose starting point** - Which phase to implement first?
3. **Create first skill** - Start with a simple example
4. **Test thoroughly** - Ensure no breakage
5. **Iterate** - Add more skills based on user feedback

Would you like me to implement Phase 1 now?
