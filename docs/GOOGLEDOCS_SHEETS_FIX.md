# Google Docs vs Google Sheets Confusion Fix

## Problem
User asked to "Add a detailed brief... on my google docs" but the agent tried to use Google Sheets tools instead, resulting in error:
```
No connected account found for entity ID ... for toolkit googlesheets
```

The user had Google Docs connected but NOT Google Sheets.

## Root Cause
The LLM was confusing Google Docs with Google Sheets and selecting the wrong toolkit. This is an LLM decision problem, not a tool availability issue.

## Solution
Updated the system prompt in `kernel.py` (lines 309-327) to include clear guidelines for tool selection:

```python
IMPORTANT - Tool Selection Guidelines:
- Google Docs (GOOGLEDOCS): For creating/editing TEXT DOCUMENTS, reports, letters, articles
- Google Sheets (GOOGLESHEETS): For creating/editing SPREADSHEETS, tables with calculations, data analysis
- Google Drive (GOOGLEDRIVE): For file management, uploading, downloading, organizing files
- When user says "docs" or "document", use GOOGLEDOCS tools
- When user says "sheets" or "spreadsheet", use GOOGLESHEETS tools
- Never confuse Docs with Sheets - they are completely different applications!
```

## Verification
- ✅ Google Docs CREATE tools are available in default toolkit
- ✅ `GOOGLEDOCS_CREATE_DOCUMENT` exists
- ✅ `GOOGLEDOCS_CREATE_DOCUMENT_MARKDOWN` exists
- ✅ System prompt now clearly distinguishes between Docs and Sheets

## Files Modified
- `kernel.py` (system prompt, lines 309-327)

## Files Created
- `check_googledocs_tools.py` - Script to verify available Google Docs tools
- `GOOGLEDOCS_SHEETS_FIX.md` - This document

## Status
✅ **FIXED** - System prompt updated to prevent LLM from confusing Google Docs with Google Sheets

The agent should now correctly use GOOGLEDOCS tools when the user mentions "docs" or "documents", and GOOGLESHEETS tools when they mention "sheets" or "spreadsheets".
