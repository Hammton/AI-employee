# Asana GET Tools Solution

## Problem
When using `composio_client.tools.get(user_id=user_id, toolkits=["asana"])`, Composio only returns 20 tools, and they're all CREATE/ADD/DELETE operations. The GET/LIST/READ tools are NOT included.

## Root Cause
Composio's `toolkits=["asana"]` parameter returns a limited subset of tools (20 tools), which doesn't include the GET operations needed to read data from Asana.

## Solution
Use the `tools` parameter to explicitly request the GET tools we need:

```python
# Get specific Asana GET tools
get_tools = composio_client.tools.get(
    user_id=user_id,
    tools=[
        "ASANA_GET_MULTIPLE_PROJECTS",
        "ASANA_GET_MULTIPLE_WORKSPACES",
        "ASANA_GET_MULTIPLE_TASKS",
        "ASANA_GET_A_PROJECT",
        "ASANA_GET_A_TASK",
        # Add more as needed
    ]
)

# Get the default toolkit tools
toolkit_tools = composio_client.tools.get(
    user_id=user_id,
    toolkits=["asana"]
)

# Combine them
all_asana_tools = toolkit_tools + get_tools
```

## Verified GET Tools Available
✓ `ASANA_GET_MULTIPLE_PROJECTS` - List projects by workspace or team
✓ `ASANA_GET_MULTIPLE_WORKSPACES` - List all accessible workspaces
✓ `ASANA_GET_MULTIPLE_TASKS` - List tasks with filters
✓ `ASANA_GET_A_PROJECT` - Get a specific project by GID
✓ `ASANA_GET_A_TASK` - Get a specific task by GID

## Implementation
Update `kernel.py` in the `setup()` method to fetch both toolkit tools AND specific GET tools for Asana.

## Status
- ✅ Connection check works (slug mapping is correct)
- ✅ GET tools exist in Composio
- ⚠️ Need to update kernel to fetch GET tools explicitly
