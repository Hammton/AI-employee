# Output Patterns for Skills

Reference guide for producing consistent, high-quality outputs.

## Status Reporting

### Success Pattern

```
✅ **[Action Completed]: [Brief description]**

[Details if needed]

**Next step:** [What user can do now]
```

### Error Pattern

```
❌ **[Action Failed]: [Brief description]**

**What happened:** [Explanation]
**What I tried:** [Steps taken]
**How to fix:** [Actionable suggestion]
```

### Progress Pattern

```
🔄 **[Action In Progress]**

- [x] Step 1: Complete
- [x] Step 2: Complete
- [ ] Step 3: In progress...
```

## Formatted Output

### Summary Pattern

For digest/overview outputs:

```markdown
## [Title] Summary

**Key Points:**
- [Point 1]
- [Point 2]
- [Point 3]

**Details:** [Expandable section or brief elaboration]

**Action Required:** [If any]
```

### Table Pattern

For structured data:

```markdown
| Item | Status | Notes |
|------|--------|-------|
| [A]  | ✅ Done | [Details] |
| [B]  | 🔄 Pending | [Details] |
| [C]  | ❌ Failed | [Details] |
```

### List Pattern

For enumerated items:

```markdown
### [Category 1]
1. **[Item]** - [Brief description]
2. **[Item]** - [Brief description]

### [Category 2]
1. **[Item]** - [Brief description]
```

## Interactive Patterns

### Confirmation Request

```markdown
📋 **Review Required**

I'm about to:
- [Action 1]
- [Action 2]

**Proceed?** Say "yes" to continue or provide modifications.
```

### Option Selection

```markdown
🔀 **Choose an Option**

1. **[Option A]** - [Brief description]
2. **[Option B]** - [Brief description]
3. **[Option C]** - [Brief description]

Which would you prefer? (1/2/3)
```

### Preview Pattern

```markdown
📋 **Preview: [What we're creating]**

[Preview content]

---

Say "save" to confirm or describe changes needed.
```

## File Output

### Created File

```markdown
✅ **File Created:** `[filename]`

📁 Location: `[full path]`
📊 Size: [X KB]

**Contents:** [Brief description]
```

### Multiple Files

```markdown
✅ **Created [N] files:**

1. `[file1]` - [description]
2. `[file2]` - [description]
3. `[file3]` - [description]

**Next:** [What to do with these files]
```

## Skill-Specific Patterns

### Skill Created

```markdown
✅ **Skill Created: [skill-name]**

**Description:** [What it does]

**Triggers:** [Example phrases]

**Usage:** Say *"[trigger phrase]"* to activate

**Location:** `skills/[skill-name]/`
```

### Auth Required

```markdown
🔐 **Authentication Required**

To use [App Name], open this link:
**[Auth URL]**

After authorizing, say "I connected [App Name]" and I'll try again.
```
