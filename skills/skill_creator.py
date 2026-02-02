"""
Skill Creator - Generate skills from natural language and conversations

Phase 2 of the Skills Architecture: Enables the agent to learn and create
skills from user interactions, turning repeated workflows into reusable patterns.

Key Features:
- Natural language → Structured skill conversion
- Conversation history → Skill extraction
- Pattern detection → Skill suggestions
- Memory integration for learning

Philosophy: "Every repeated workflow is a skill waiting to be born"
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime

logger = logging.getLogger("PocketKernel.SkillCreator")


@dataclass
class SkillBlueprint:
    """Blueprint for a skill being created."""
    name: str
    description: str
    triggers: List[str] = field(default_factory=list)
    steps: List[str] = field(default_factory=list)
    tools_used: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    user_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    source: str = "natural_language"  # natural_language, conversation, suggestion
    
    def to_skill_md(self) -> str:
        """Convert blueprint to SKILL.md content following canonical pattern.
        
        Key principles:
        - ONLY name and description in frontmatter (description is primary trigger)
        - Description must be comprehensive: what it does + when to use + trigger phrases
        - Body is concise - only add context the agent doesn't already have
        """
        # Build comprehensive description (this is the PRIMARY trigger mechanism)
        trigger_phrases = ", ".join(f'"{t}"' for t in self.triggers[:5]) if self.triggers else ""
        tools_list = ", ".join(self.tools_used) if self.tools_used else ""
        
        description_parts = [self.description]
        if self.triggers:
            description_parts.append(f"Triggers: {trigger_phrases}.")
        if self.tools_used:
            description_parts.append(f"Tools: {tools_list}.")
        
        full_description = " ".join(description_parts)
        
        # YAML frontmatter - ONLY name and description per canonical pattern
        # Use folded style (>) to handle special characters/colons in description
        frontmatter = f"""---
name: {self.name}
description: >
  {full_description}
---"""
        
        # Build concise workflow section
        steps_md = "\n".join(f"{i+1}. {step}" for i, step in enumerate(self.steps)) if self.steps else "1. Execute the requested action"
        
        # Body is loaded AFTER triggering, so keep it concise
        body = f"""

# {self.name.replace('-', ' ').title()}

## Purpose

{self.description}

## Workflow

{steps_md}
"""
        
        # Only add tools section if there are tools
        if self.tools_used:
            tools_section = "\n".join(f"- `{tool}`" for tool in self.tools_used)
            body += f"""
## Tools

{tools_section}
"""
        
        return frontmatter + body
    
    def save(self, skills_dir: Path) -> Path:
        """Save skill to disk following canonical pattern.
        
        Only creates SKILL.md - no extraneous files per skill-creator guidance.
        """
        # Determine save location
        if self.user_id:
            skill_path = skills_dir / self.user_id / self.name
        else:
            skill_path = skills_dir / self.name
        
        # Create directories
        skill_path.mkdir(parents=True, exist_ok=True)
        
        # Write SKILL.md (the ONLY required file)
        skill_file = skill_path / "SKILL.md"
        skill_file.write_text(self.to_skill_md(), encoding='utf-8')
        
        logger.info(f"✅ Saved skill '{self.name}' to {skill_path}")
        return skill_path


class SkillCreator:
    """
    Creates skills from natural language descriptions and conversation history.
    
    Works with or without LLM - uses regex patterns as fallback.
    """
    
    # Common action verbs that indicate workflow steps
    ACTION_VERBS = [
        'create', 'make', 'generate', 'build', 'write',
        'send', 'post', 'share', 'email', 'message',
        'check', 'get', 'fetch', 'retrieve', 'list',
        'update', 'edit', 'modify', 'change',
        'delete', 'remove', 'clear',
        'summarize', 'analyze', 'process',
        'connect', 'link', 'integrate',
        'schedule', 'plan', 'organize'
    ]
    
    # Composio tool patterns
    TOOL_PATTERNS = {
        r'gmail|email|mail': 'gmail',
        r'sheets?|spreadsheet': 'googlesheets',
        r'docs?|document': 'googledocs',
        r'drive|files?': 'googledrive',
        r'calendar|schedule|event': 'googlecalendar',
        r'slack|channel': 'slack',
        r'notion|page|database': 'notion',
        r'github|repo|code': 'github',
        r'asana|task|project': 'asana',
        r'linkedin': 'linkedin',
        r'twitter|tweet': 'twitter',
    }
    
    def __init__(self, skills_dir: str = "skills", llm_client: Any = None):
        """
        Initialize SkillCreator.
        
        Args:
            skills_dir: Base directory for skills
            llm_client: Optional LLM client for advanced extraction
        """
        self.skills_dir = Path(skills_dir)
        self.llm = llm_client
        
        # Ensure directory exists
        self.skills_dir.mkdir(parents=True, exist_ok=True)
    
    def create_from_description(
        self, 
        description: str,
        skill_name: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> SkillBlueprint:
        """
        Create a skill from a natural language description.
        
        Args:
            description: Natural language description of the workflow
            skill_name: Optional name (auto-generated if not provided)
            user_id: Optional user ID for user-specific skill
            
        Returns:
            SkillBlueprint ready to be saved
        """
        # Generate name if not provided
        if not skill_name:
            skill_name = self._generate_skill_name(description)
        
        # Extract components from description
        steps = self._extract_steps(description)
        tools = self._detect_tools(description)
        triggers = self._extract_triggers(description, skill_name)
        
        # Create short description
        short_desc = self._create_short_description(description)
        
        blueprint = SkillBlueprint(
            name=skill_name,
            description=short_desc,
            triggers=triggers,
            steps=steps,
            tools_used=tools,
            user_id=user_id,
            source="natural_language"
        )
        
        logger.info(f"Created blueprint for skill '{skill_name}'")
        return blueprint
    
    def create_from_conversation(
        self,
        messages: List[Dict[str, str]],
        skill_name: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> SkillBlueprint:
        """
        Extract a skill from conversation history.
        
        Args:
            messages: List of {"role": "user"|"assistant", "content": str}
            skill_name: Optional name
            user_id: Optional user ID
            
        Returns:
            SkillBlueprint
        """
        # Combine conversation into context
        conversation_text = self._flatten_conversation(messages)
        
        # Extract the user's intent
        user_messages = [m["content"] for m in messages if m.get("role") == "user"]
        main_request = user_messages[0] if user_messages else conversation_text
        
        # Generate name from request
        if not skill_name:
            skill_name = self._generate_skill_name(main_request)
        
        # Extract steps from assistant's actions
        assistant_messages = [m["content"] for m in messages if m.get("role") == "assistant"]
        steps = self._extract_steps_from_responses(assistant_messages)
        
        # Detect tools mentioned
        tools = self._detect_tools(conversation_text)
        
        # Triggers from user's phrasing
        triggers = self._extract_triggers(main_request, skill_name)
        
        # Description
        short_desc = self._create_short_description(main_request)
        
        blueprint = SkillBlueprint(
            name=skill_name,
            description=short_desc,
            triggers=triggers,
            steps=steps,
            tools_used=tools,
            user_id=user_id,
            source="conversation"
        )
        
        logger.info(f"Created blueprint from conversation: '{skill_name}'")
        return blueprint
    
    def suggest_skill_from_patterns(
        self,
        queries: List[str],
        min_similarity: float = 0.6
    ) -> Optional[SkillBlueprint]:
        """
        Analyze past queries to suggest a skill.
        
        Args:
            queries: List of similar past queries
            min_similarity: Minimum similarity threshold
            
        Returns:
            SkillBlueprint if pattern detected, None otherwise
        """
        if len(queries) < 2:
            return None
        
        # Find common elements
        common_words = self._find_common_words(queries)
        
        if len(common_words) < 2:
            return None
        
        # Generate skill from common pattern
        combined = " ".join(queries)
        skill_name = self._generate_skill_name(" ".join(common_words))
        
        blueprint = self.create_from_description(
            combined,
            skill_name=skill_name
        )
        blueprint.source = "suggestion"
        
        return blueprint
    
    def _generate_skill_name(self, text: str) -> str:
        """Generate a kebab-case skill name from text."""
        # Extract key nouns and verbs
        words = text.lower().split()
        
        # Filter to meaningful words
        stop_words = {'the', 'a', 'an', 'to', 'for', 'and', 'or', 'but', 'in', 'on', 'at', 'with', 'my', 'your', 'their', 'i', 'me', 'you', 'it', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'want', 'please', 'help'}
        
        meaningful = [w for w in words if w.isalnum() and w not in stop_words and len(w) > 2]
        
        # Take first 3-4 meaningful words
        name_parts = meaningful[:4]
        
        if not name_parts:
            name_parts = ["custom-skill"]
        
        return "-".join(name_parts)
    
    def _extract_steps(self, text: str) -> List[str]:
        """Extract workflow steps from description."""
        steps = []
        
        # Look for explicit steps (numbered or bulleted)
        step_patterns = [
            r'(?:^|\n)\s*\d+[.)]\s*(.+?)(?=\n|$)',  # 1. Step or 1) Step
            r'(?:^|\n)\s*[-•*]\s*(.+?)(?=\n|$)',    # - Step or • Step
            r'(?:first|then|next|finally|after that)[,:]?\s*(.+?)(?=[.,]|$)',  # First, ... Then, ...
        ]
        
        for pattern in step_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            steps.extend(matches)
        
        # If no explicit steps, extract action phrases
        if not steps:
            for verb in self.ACTION_VERBS:
                pattern = rf'{verb}\s+(?:the\s+)?(.+?)(?:[.,]|and|then|$)'
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if len(match) > 5:  # Skip very short matches
                        steps.append(f"{verb.capitalize()} {match.strip()}")
        
        # Deduplicate while preserving order
        seen = set()
        unique_steps = []
        for step in steps:
            step_clean = step.strip()
            if step_clean.lower() not in seen and len(step_clean) > 5:
                seen.add(step_clean.lower())
                unique_steps.append(step_clean)
        
        return unique_steps[:10]  # Max 10 steps
    
    def _extract_steps_from_responses(self, responses: List[str]) -> List[str]:
        """Extract steps from assistant responses (what was done)."""
        steps = []
        
        action_indicators = [
            r"(?:I'll|I will|Let me|Going to)\s+(.+?)(?:\.|$)",
            r"(?:Created|Generated|Sent|Posted|Updated|Checked)\s+(.+?)(?:\.|$)",
            r"✅\s*(.+?)(?:\.|$)",
        ]
        
        for response in responses:
            for pattern in action_indicators:
                matches = re.findall(pattern, response, re.IGNORECASE)
                steps.extend(matches)
        
        # Clean and deduplicate
        seen = set()
        unique = []
        for step in steps:
            clean = step.strip()
            if clean.lower() not in seen and len(clean) > 5:
                seen.add(clean.lower())
                unique.append(clean)
        
        return unique[:10]
    
    def _detect_tools(self, text: str) -> List[str]:
        """Detect Composio tools mentioned in text."""
        tools = set()
        text_lower = text.lower()
        
        for pattern, tool in self.TOOL_PATTERNS.items():
            if re.search(pattern, text_lower):
                tools.add(tool)
        
        return list(tools)
    
    def _extract_triggers(self, text: str, skill_name: str) -> List[str]:
        """Extract trigger keywords for the skill."""
        triggers = []
        
        # Add skill name words as triggers
        name_words = skill_name.replace("-", " ").split()
        triggers.extend(name_words)
        
        # Extract key phrases
        key_phrases = [
            r'(?:when|whenever)\s+(?:I|you|user)\s+(.+?)(?:[.,]|$)',
            r'(?:help|need|want)\s+(?:to|with)\s+(.+?)(?:[.,]|$)',
        ]
        
        for pattern in key_phrases:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) < 30:  # Keep triggers short
                    triggers.append(match.strip())
        
        # Add detected tools as triggers
        tools = self._detect_tools(text)
        triggers.extend(tools)
        
        # Deduplicate and limit
        seen = set()
        unique = []
        for t in triggers:
            t_lower = t.lower().strip()
            if t_lower not in seen and len(t_lower) > 2:
                seen.add(t_lower)
                unique.append(t_lower)
        
        return unique[:8]  # Max 8 triggers
    
    def _create_short_description(self, text: str) -> str:
        """Create a short description from longer text."""
        # Take first sentence or first 100 chars
        sentences = re.split(r'[.!?]', text)
        first = sentences[0].strip() if sentences else text[:100]
        
        # Clean and limit length
        first = re.sub(r'\s+', ' ', first)
        if len(first) > 150:
            first = first[:147] + "..."
        
        return first
    
    def _flatten_conversation(self, messages: List[Dict]) -> str:
        """Flatten conversation messages into single text."""
        parts = []
        for msg in messages:
            role = msg.get("role", "unknown").upper()
            content = msg.get("content", "")
            parts.append(f"{role}: {content}")
        return "\n".join(parts)
    
    def _find_common_words(self, texts: List[str]) -> List[str]:
        """Find words common across multiple texts."""
        if not texts:
            return []
        
        # Get word sets
        word_sets = []
        for text in texts:
            words = set(text.lower().split())
            word_sets.append(words)
        
        # Find intersection
        common = word_sets[0]
        for ws in word_sets[1:]:
            common = common.intersection(ws)
        
        # Filter stop words
        stop_words = {'the', 'a', 'an', 'to', 'for', 'and', 'or', 'i', 'me', 'my'}
        return [w for w in common if w not in stop_words and len(w) > 2]
    
    def save_skill(self, blueprint: SkillBlueprint) -> Path:
        """Save a skill blueprint to disk."""
        return blueprint.save(self.skills_dir)
    
    def get_creation_prompt(self, skill_name: str, user_id: Optional[str] = None) -> str:
        """
        Generate a prompt to help user describe their skill.
        
        Returns a formatted message asking for skill details.
        """
        return f"""🛠️ **Creating Skill: {skill_name}**

Please describe your workflow in natural language. Include:

1. **What does this skill do?** (e.g., "Checks my email and summarizes important messages")

2. **What are the steps?** (e.g., "First fetch emails, then filter by sender, finally create a summary")

3. **What tools are involved?** (e.g., Gmail, Slack, Notion)

4. **When should this skill activate?** (e.g., "morning digest", "email summary", "daily update")

---

**Example:**
"Check my Gmail for unread emails from the last 12 hours, 
summarize the important ones using AI, 
and post the summary to my #daily-updates Slack channel"

---

Describe your workflow:"""


# Convenience functions for kernel integration
def create_skill_creator(skills_dir: str = "skills", llm_client: Any = None) -> SkillCreator:
    """Create a SkillCreator instance."""
    return SkillCreator(skills_dir=skills_dir, llm_client=llm_client)
