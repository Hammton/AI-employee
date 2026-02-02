# Workflow Patterns for Skills

Reference guide for implementing multi-step workflows in skills.

## Sequential Workflows

For processes that must follow a specific order:

```markdown
## Workflow

1. **Gather inputs** - Collect all required information first
2. **Validate** - Check inputs before proceeding
3. **Execute** - Perform the main operation
4. **Verify** - Confirm success before reporting
5. **Report** - Summarize what was done
```

### Example: Email Digest Skill

```markdown
## Workflow

1. **Fetch emails** - Get unread emails from the last 12 hours
2. **Filter** - Keep only emails from known senders or flagged important
3. **Summarize** - Create 1-2 sentence summary for each
4. **Format** - Group by sender/topic, prioritize by importance
5. **Deliver** - Post to Slack or send consolidated email
```

## Conditional Workflows

For processes with branching logic:

```markdown
## Workflow

1. Check X condition
   - If true: Do A, then B
   - If false: Skip to step 3
2. [Next step if condition was true]
3. [Continues regardless]
```

### Example: Connection Check Skill

```markdown
## Workflow

1. **Check if connected** - Query existing connections
   - If connected: Proceed to step 2
   - If not connected: Generate auth link, stop and wait
2. **Execute tool** - Run the requested operation
3. **Handle errors** - If auth fails, generate new link
```

## Loop Workflows

For repeated operations:

```markdown
## Workflow

1. Get list of items to process
2. For each item:
   a. [Operation A]
   b. [Operation B]
   c. Record result
3. Summarize all results
```

## Error Handling Patterns

### Graceful Degradation

```markdown
## Workflow

1. **Try primary method**
   - On success: Continue
   - On failure: Try fallback
2. **Fallback method**
   - On success: Continue with note about fallback
   - On failure: Report what was tried
```

### Retry with Backoff

```markdown
## Error Handling

1. First attempt: Try immediately
2. Second attempt: Wait 2 seconds
3. Third attempt: Wait 5 seconds
4. Final: Report failure with diagnostics
```

## Context-Aware Workflows

For skills that adapt to previous state:

```markdown
## Workflow

1. **Check context**
   - First time: Full initialization
   - Returning: Resume from last state
2. **Execute with awareness** - Use previous context to skip redundant steps
3. **Update context** - Save state for next invocation
```
