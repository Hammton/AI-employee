---
name: skill-creator
description: Guide for creating effective skills. Use when the user wants to create, update, or package a skill that extends the agent's capabilities. Triggers include phrases like "create a skill", "make a new skill", "build a workflow skill", "package my skill", "help me define a skill", or when discussing reusable workflows that should be saved.
---

# Skill Creator

Create modular, self-contained packages that extend agent capabilities.

## Core Principles

### 1. Concise is Key
Context is shared with everything else. Only add what the agent doesn't already know.
- Challenge each line: "Does this justify its token cost?"
- Prefer concise examples over verbose explanations

### 2. Progressive Disclosure
Three levels of loading:
1. **Metadata** (name + description) - Always in context
2. **SKILL.md body** - When skill triggers
3. **Bundled resources** - As needed

### 3. Description is Primary Trigger
The `description` field determines when the skill activates. Include:
- What the skill does
- Specific triggers and contexts
- Example phrases that should trigger it

## Skill Structure

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description - required)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/     - Executable code (deterministic operations)
    ├── references/  - Documentation loaded as needed
    └── assets/      - Output files (templates, images)
```

## Creation Workflow

### Step 1: Understand with Examples

Ask:
- "What functionality should this skill support?"
- "Give examples of how you'd use it"
- "What would you say to trigger this skill?"

### Step 2: Plan Resources

For each example, identify:
- Scripts for repeated/deterministic code
- References for documentation to load as needed
- Assets for templates/files used in output

### Step 3: Initialize

```bash
python skills/scripts/init_skill.py <skill-name> --path skills/
```

Creates proper structure with examples to customize.

### Step 4: Implement

1. Edit SKILL.md with workflow and description
2. Add/replace scripts for deterministic operations
3. Add references for documentation
4. Add assets for output templates
5. Delete example files you don't need

### Step 5: Package

```bash
python skills/scripts/package_skill.py skills/<skill-name>
```

Validates and creates distributable .skill file.

## SKILL.md Template

```yaml
---
name: skill-name
description: What this skill does. When to use it. Include trigger phrases.
---
```

```markdown
# Skill Title

## Purpose
[One paragraph on what problem this solves]

## Workflow
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Key Considerations
- [Important point 1]
- [Important point 2]
```

## What NOT to Include

❌ README.md, CHANGELOG.md, INSTALLATION_GUIDE.md
❌ Setup/testing procedures  
❌ User-facing documentation
❌ Verbose explanations of obvious things
❌ "When to Use" sections in body (use description instead)

## Degrees of Freedom

Match specificity to task fragility:

| Freedom Level | When to Use | Example |
|--------------|-------------|---------|
| High (text) | Multiple valid approaches | "Summarize the key points" |
| Medium (pseudocode) | Preferred pattern exists | "Follow this structure, adapt as needed" |
| Low (scripts) | Fragile/error-prone operations | `scripts/rotate_pdf.py` |

## See Also

- `references/workflows.md` - Multi-step process patterns
- `references/output-patterns.md` - Template and format patterns
