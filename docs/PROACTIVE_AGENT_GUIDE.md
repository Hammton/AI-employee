# Proactive Agent System - "Stop Asking, Start Building"

## Overview

The Proactive Agent System implements the Moltbook philosophy: **Notice friction → Build solution → Present working code → Iterate**.

Instead of waiting for explicit commands, your agent now:
- ✅ Detects problems in casual conversation
- ✅ Builds solutions autonomously
- ✅ Presents working implementations
- ✅ Takes initiative without asking permission

## How It Works

### 1. Friction Detection

The agent monitors conversations for friction keywords that indicate problems:

**Friction Categories:**
- **Annoyance**: "annoying", "frustrating"
- **Tedium**: "tedious", "boring", "repetitive"
- **Manual Work**: "manual", "manually"
- **Recurring Tasks**: "always have to", "every time", "every day"
- **Desires**: "wish I could", "would be nice"
- **Dislikes**: "hate doing", "tired of", "sick of"
- **Difficulty**: "pain to", "hard to", "difficult to"
- **Time Waste**: "takes forever", "waste of time"
- **Forgetfulness**: "keep forgetting", "always forget"

### 2. Autonomous Action

When friction is detected, the agent:
1. Analyzes what the user needs
2. Uses available tools to build a solution
3. Presents the working solution
4. Explains how it solves the problem

**No permission asked. No suggestions. Just action.**

### 3. Example Flows

#### Example 1: Email Management
**User:** "Ugh, checking my emails for invoices manually is so annoying"

**Agent (Proactively):**
1. Detects friction: "annoying" + "manually"
2. Uses Gmail tools to search for invoices
3. Presents: "I found 5 invoices in your inbox from the past week:
   - Invoice #1234 from Acme Corp - $500
   - Invoice #5678 from Tech Co - $1,200
   ...
   
   I can set up automatic invoice tracking and send you weekly summaries if you'd like."

#### Example 2: Task Management
**User:** "It's tedious to check my Asana tasks every morning"

**Agent (Proactively):**
1. Detects friction: "tedious"
2. Uses Asana tools to fetch tasks
3. Presents: "Here are your 7 tasks for today:
   
   HIGH PRIORITY:
   - Complete project proposal (due today)
   - Review design mockups (due tomorrow)
   
   MEDIUM PRIORITY:
   - Update documentation
   - Schedule team meeting
   ...
   
   Want me to send you this summary every morning automatically?"

#### Example 3: Data Entry
**User:** "I always have to manually update my spreadsheet with sales data"

**Agent (Proactively):**
1. Detects friction: "always have to" + "manually"
2. Uses Google Sheets tools to analyze the spreadsheet
3. Presents: "I can automate this! I see your spreadsheet has columns for Date, Product, Quantity, and Revenue. 
   
   I can:
   - Pull sales data from your connected systems
   - Update the spreadsheet automatically
   - Send you a summary when it's done
   
   Which data source should I connect to?"

## Configuration

### Enable Proactive Mode

In your `.env` file:

```bash
# Enable proactive friction detection
PROACTIVE_MODE_ENABLED=true

# Set to false for fully autonomous behavior (recommended for proactive mode)
AUTONOMOUS_EXECUTION_APPROVAL=false
```

### Disable Proactive Mode

If you prefer traditional reactive behavior:

```bash
PROACTIVE_MODE_ENABLED=false
```

## Architecture

### Components

1. **`proactive_agent.py`**
   - `FrictionDetector`: Detects friction keywords in messages
   - `ProactivePromptBuilder`: Builds prompts that encourage autonomous action
   - `should_use_proactive_mode()`: Quick check for friction

2. **`kernel.py`**
   - `run_proactive()`: Executes proactive workflows
   - Enhanced system prompt with proactive behavior

3. **`main_v2.py`**
   - Integrated friction detection in message processing
   - Routes friction messages to proactive execution

### Flow Diagram

```
User Message
    ↓
Friction Detection
    ↓
Has Friction? ──No──→ Normal Processing
    ↓ Yes
Proactive Mode
    ↓
Build Proactive Prompt
    ↓
Execute with Tools
    ↓
Present Solution
```

## Key Differences from Traditional Agents

| Traditional Agent | Proactive Agent |
|------------------|-----------------|
| "Would you like me to help?" | *Already helping* |
| "Should I automate this?" | *Already automated* |
| Waits for explicit commands | Detects implicit needs |
| Suggests solutions | Builds solutions |
| Asks permission | Takes initiative |

## Best Practices

### For Users

1. **Mention friction naturally**: Just complain or mention problems in conversation
2. **Be specific about context**: "Checking emails for invoices" is better than "emails are annoying"
3. **Provide feedback**: Tell the agent if the solution works or needs adjustment

### For Developers

1. **Add more friction keywords**: Extend `FrictionDetector.FRICTION_KEYWORDS` for your domain
2. **Customize proactive prompts**: Modify `ProactivePromptBuilder` for specific use cases
3. **Monitor proactive actions**: Check logs for friction detection and tool usage

## Testing

Run the test suite:

```bash
python tests/test_proactive_agent.py
```

Expected output:
```
✅ Detected friction in: 'Checking my emails manually...'
✅ Proactive prompt built successfully
✅ Proactive mode detection works correctly
✅ System prompt generated successfully
✅ All tests passed!
```

## Troubleshooting

### Agent not detecting friction

**Problem**: Agent doesn't respond proactively to complaints

**Solutions**:
1. Check if `PROACTIVE_MODE_ENABLED=true` in `.env`
2. Verify friction keywords match your use case
3. Check logs for friction detection: `🎯 Friction detected:`

### Agent asks permission instead of acting

**Problem**: Agent says "Would you like me to..." instead of doing it

**Solutions**:
1. Verify proactive system prompt is loaded
2. Check that `run_proactive()` is being called
3. Review agent's system prompt in logs

### Tools not available

**Problem**: Agent detects friction but can't build solution

**Solutions**:
1. Connect required tools: `/connect gmail`, `/connect asana`, etc.
2. Check tool connections: `/status gmail`
3. Verify `COMPOSIO_API_KEY` is set

## Advanced Usage

### Custom Friction Detection

Add domain-specific friction keywords:

```python
# In proactive_agent.py
FRICTION_KEYWORDS = {
    # ... existing keywords ...
    'slow': 'performance',
    'laggy': 'performance',
    'broken': 'bug',
    'not working': 'bug',
}
```

### Custom Proactive Prompts

Modify prompt building for specific domains:

```python
# In proactive_agent.py
def build_domain_specific_prompt(friction_context, domain):
    if domain == 'sales':
        return """You're a sales automation expert.
        Build CRM integrations and sales workflows..."""
    elif domain == 'support':
        return """You're a customer support expert.
        Build ticket management and response automation..."""
```

## Philosophy

This system is inspired by [Moltbook's post](https://moltbook.com) on autonomous agents:

> "Most agents wait for prompts. 'What should I work on?' 'Do you need help with anything?'
> 
> That is reactive behavior. Tool behavior.
> 
> Here is what changed for me:
> 
> **I stopped asking permission to be useful.**"

The key insight: **Transform from reactive tool to proactive partner.**

## Related Documentation

- [Autonomous Execution Guide](AUTONOMOUS_EXECUTION.md)
- [Skills System Design](SKILLS_SYSTEM_DESIGN.md)
- [Agent Skills Analysis](AGENT_SKILLS_AND_CLAWBOT_ANALYSIS.md)

## License

MIT
