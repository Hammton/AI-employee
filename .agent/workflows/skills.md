---
description: Use or manage the skills system - load skills, list available skills, create new skills, or package skills for distribution
---

# Skills System Workflow

The skills system extends the agent's capabilities with modular, reusable workflows.

## Core Concepts

- **Skills** - Self-contained packages with instructions, scripts, and resources
- **SKILL.md** - Required file with frontmatter (name, description) + instructions
- **Description** - The primary trigger mechanism (must be comprehensive!)
- **Resources** - Optional scripts/, references/, assets/ directories

## Quick Commands

### List Available Skills
```
list skills
```

### Use a Specific Skill
```
use <skill-name>
```
Example: `use composio-auth`

### Create a New Skill
```
create skill <description>
```
Example: `create skill Check Gmail daily and summarize important emails to Slack`

## Skill Creation Workflow

// turbo-all

### Step 1: Initialize a new skill
```bash
python skills/scripts/init_skill.py <skill-name> --path skills/
```

### Step 2: Edit SKILL.md
Update the generated template with:
- Comprehensive description (what + when + triggers)
- Concise workflow steps
- Reference to any scripts/docs

### Step 3: Add Resources (if needed)
- `scripts/` - Python/Bash for deterministic operations
- `references/` - Docs to load as needed
- `assets/` - Templates/images for output

### Step 4: Validate and Package
```bash
python skills/scripts/package_skill.py skills/<skill-name>
```

## Skill Structure

```
skill-name/
├── SKILL.md              ← Required: frontmatter + instructions
├── scripts/              ← Optional: executable code
├── references/           ← Optional: documentation
└── assets/               ← Optional: templates/images
```

## SKILL.md Format

```yaml
---
name: skill-name
description: What it does. When to use it. Include trigger phrases like "X", "Y", "Z".
---
```

```markdown
# Skill Title

## Purpose
[One paragraph]

## Workflow
1. Step one
2. Step two
3. Step three
```

## Key Principles

1. **Description is Primary Trigger** - Must include what it does AND when to use
2. **Concise Body** - Only add context the agent doesn't already have
3. **Progressive Disclosure** - Load resources only when needed
4. **No Extraneous Files** - No README, CHANGELOG, etc.

## Available Skills

Current skills in `skills/` directory:
- `composio-auth` - OAuth authentication for Composio tools
- `skill-creator` - Guide for creating new skills

## Programmatic Access

```python
from kernel import AgentKernel

kernel = AgentKernel(user_id="my_user")
kernel.setup()

# List skills
print(kernel.list_skills())

# Use a skill
result = kernel.run_with_skill("Connect me to Gmail", "composio-auth")

# Create a skill
kernel.create_skill("Check emails daily and summarize to Slack")

# Smart run (auto-detects skills)
result = kernel.smart_run("What skills do I have?")
```
