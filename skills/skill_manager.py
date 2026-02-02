"""
Skills Manager - Core skills infrastructure for PocketAgent

This module implements the skills loading and management system inspired by
OpenClaw/Moltbot's architecture. Skills are modular, self-contained packages
that extend agent capabilities with specialized knowledge, workflows, and tools.

Based on the "Progressive Disclosure" principle:
1. Metadata (name + description) - Always in context (~100 words)
2. SKILL.md body - When skill triggers (<5k words)  
3. Bundled resources - As needed (scripts, references)
"""

import os
import re
import logging
import yaml
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field

logger = logging.getLogger("PocketKernel.Skills")


@dataclass
class SkillMetadata:
    """Skill metadata extracted from SKILL.md frontmatter."""
    name: str
    description: str
    path: Path
    triggers: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    schedule: Optional[str] = None
    
    def matches_query(self, query: str) -> bool:
        """Check if this skill matches a user query."""
        query_lower = query.lower()
        
        # Check name match
        if self.name.lower() in query_lower:
            return True
        
        # Check trigger keywords
        for trigger in self.triggers:
            if trigger.lower() in query_lower:
                return True
        
        # Check description keywords
        desc_words = self.description.lower().split()
        matches = sum(1 for word in desc_words if word in query_lower)
        if matches >= 2:  # At least 2 keyword matches
            return True
        
        return False


class SkillManager:
    """
    Manages skill discovery, loading, and lifecycle.
    
    Skills are stored in:
    - Global: skills/ (shared across users)
    - User-specific: skills/{user_id}/ (per-user skills)
    
    Each skill is a folder containing:
    - SKILL.md (required): Instructions and metadata
    - scripts/ (optional): Executable scripts
    - references/ (optional): Documentation
    - assets/ (optional): Templates, images, etc.
    """
    
    def __init__(self, skills_dir: str = "skills", user_id: Optional[str] = None):
        """
        Initialize SkillManager.
        
        Args:
            skills_dir: Base directory for skills
            user_id: User ID for user-specific skills
        """
        self.skills_dir = Path(skills_dir)
        self.user_id = user_id
        self.user_skills_dir = self.skills_dir / user_id if user_id else None
        
        # Cache for loaded skills
        self._skill_cache: Dict[str, SkillMetadata] = {}
        self._loaded_skills: Dict[str, str] = {}  # skill_name -> content
        
        # Ensure directories exist
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        if self.user_skills_dir:
            self.user_skills_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"SkillManager initialized: {self.skills_dir}")
    
    def discover_skills(self) -> List[SkillMetadata]:
        """
        Scan skills directories and return available skills.
        
        Returns metadata only (Progressive Disclosure Level 1).
        """
        skills = []
        
        # Scan global skills
        skills.extend(self._scan_directory(self.skills_dir))
        
        # Scan user-specific skills
        if self.user_skills_dir and self.user_skills_dir.exists():
            skills.extend(self._scan_directory(self.user_skills_dir))
        
        # Cache results
        for skill in skills:
            self._skill_cache[skill.name] = skill
        
        logger.info(f"Discovered {len(skills)} skills")
        return skills
    
    def _scan_directory(self, directory: Path) -> List[SkillMetadata]:
        """Scan a directory for skills."""
        skills = []
        
        if not directory.exists():
            return skills
        
        for item in directory.iterdir():
            if not item.is_dir():
                continue
            
            skill_file = item / "SKILL.md"
            if not skill_file.exists():
                continue
            
            try:
                metadata = self._parse_skill_metadata(skill_file)
                if metadata:
                    skills.append(metadata)
            except Exception as e:
                logger.warning(f"Failed to parse skill {item.name}: {e}")
        
        return skills
    
    def _parse_skill_metadata(self, skill_file: Path) -> Optional[SkillMetadata]:
        """Parse SKILL.md frontmatter for metadata."""
        try:
            content = skill_file.read_text(encoding='utf-8')
            
            # Extract YAML frontmatter
            frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            if not frontmatter_match:
                logger.warning(f"No frontmatter in {skill_file}")
                return None
            
            frontmatter = yaml.safe_load(frontmatter_match.group(1))
            
            # Required fields
            name = frontmatter.get('name')
            description = frontmatter.get('description', '')
            
            if not name:
                logger.warning(f"Missing 'name' in {skill_file}")
                return None
            
            return SkillMetadata(
                name=name,
                description=description,
                path=skill_file.parent,
                triggers=frontmatter.get('triggers', []),
                dependencies=frontmatter.get('dependencies', []),
                schedule=frontmatter.get('schedule')
            )
            
        except Exception as e:
            logger.error(f"Error parsing {skill_file}: {e}")
            return None
    
    def load_skill(self, skill_name: str) -> Optional[str]:
        """
        Load a skill's full content (Progressive Disclosure Level 2).
        
        Args:
            skill_name: Name of the skill to load
            
        Returns:
            Full SKILL.md content or None if not found
        """
        # Check cache first
        if skill_name in self._loaded_skills:
            logger.info(f"Skill '{skill_name}' loaded from cache")
            return self._loaded_skills[skill_name]
        
        # Find skill metadata
        if skill_name not in self._skill_cache:
            self.discover_skills()
        
        metadata = self._skill_cache.get(skill_name)
        if not metadata:
            logger.warning(f"Skill '{skill_name}' not found")
            return None
        
        # Load full content
        skill_file = metadata.path / "SKILL.md"
        try:
            content = skill_file.read_text(encoding='utf-8')
            
            # Remove frontmatter, keep body
            body_match = re.search(r'^---\s*\n.*?\n---\s*\n(.*)$', content, re.DOTALL)
            body = body_match.group(1) if body_match else content
            
            # Cache the loaded content
            self._loaded_skills[skill_name] = body
            
            logger.info(f"Loaded skill '{skill_name}' ({len(body)} chars)")
            return body
            
        except Exception as e:
            logger.error(f"Error loading skill {skill_name}: {e}")
            return None
    
    def unload_skill(self, skill_name: str) -> bool:
        """
        Remove a skill from active context.
        
        Args:
            skill_name: Name of the skill to unload
            
        Returns:
            True if skill was unloaded, False if not loaded
        """
        if skill_name in self._loaded_skills:
            del self._loaded_skills[skill_name]
            logger.info(f"Unloaded skill '{skill_name}'")
            return True
        return False
    
    def get_skill_prompt(self, skill_name: str) -> str:
        """
        Get a skill's instructions formatted as a prompt.
        
        Args:
            skill_name: Name of the skill
            
        Returns:
            Formatted prompt string
        """
        content = self.load_skill(skill_name)
        if not content:
            return ""
        
        metadata = self._skill_cache.get(skill_name)
        
        prompt = f"""# Active Skill: {metadata.name if metadata else skill_name}

{content}

---
You are now operating with the above skill activated. 
Follow the skill's workflow and guidelines.
"""
        return prompt
    
    def find_matching_skill(self, query: str) -> Optional[SkillMetadata]:
        """
        Find the best matching skill for a user query.
        
        Args:
            query: User's natural language query
            
        Returns:
            Best matching skill metadata or None
        """
        if not self._skill_cache:
            self.discover_skills()
        
        for skill in self._skill_cache.values():
            if skill.matches_query(query):
                logger.info(f"Query '{query}' matched skill '{skill.name}'")
                return skill
        
        return None
    
    def get_skill_resource(self, skill_name: str, resource_path: str) -> Optional[str]:
        """
        Load a skill's bundled resource (Progressive Disclosure Level 3).
        
        Args:
            skill_name: Name of the skill
            resource_path: Relative path to resource (e.g., "scripts/run.py")
            
        Returns:
            Resource content or None
        """
        if skill_name not in self._skill_cache:
            self.discover_skills()
        
        metadata = self._skill_cache.get(skill_name)
        if not metadata:
            return None
        
        resource_file = metadata.path / resource_path
        if not resource_file.exists():
            logger.warning(f"Resource not found: {resource_file}")
            return None
        
        try:
            return resource_file.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Error loading resource: {e}")
            return None
    
    def list_skill_resources(self, skill_name: str) -> Dict[str, List[str]]:
        """
        List all resources available in a skill.
        
        Returns:
            Dict mapping resource type to list of file paths
        """
        if skill_name not in self._skill_cache:
            self.discover_skills()
        
        metadata = self._skill_cache.get(skill_name)
        if not metadata:
            return {}
        
        resources = {
            "scripts": [],
            "references": [],
            "assets": []
        }
        
        for resource_type in resources.keys():
            resource_dir = metadata.path / resource_type
            if resource_dir.exists():
                for item in resource_dir.iterdir():
                    if item.is_file():
                        resources[resource_type].append(item.name)
        
        return resources
    
    def get_active_skills_prompt(self) -> str:
        """
        Get a combined prompt from all loaded skills.
        
        Returns:
            Combined prompt string
        """
        if not self._loaded_skills:
            return ""
        
        prompts = []
        for skill_name in self._loaded_skills:
            prompt = self.get_skill_prompt(skill_name)
            if prompt:
                prompts.append(prompt)
        
        return "\n\n---\n\n".join(prompts)
    
    @property
    def active_skills(self) -> List[str]:
        """List of currently loaded skill names."""
        return list(self._loaded_skills.keys())
    
    def get_skills_summary(self) -> str:
        """
        Get a summary of available skills for display.
        
        Returns:
            Formatted summary string
        """
        if not self._skill_cache:
            self.discover_skills()
        
        if not self._skill_cache:
            return "No skills available. Create skills in the skills/ directory."
        
        lines = ["📚 **Available Skills:**\n"]
        
        for skill in self._skill_cache.values():
            status = "✅" if skill.name in self._loaded_skills else "⬜"
            lines.append(f"{status} **{skill.name}** - {skill.description[:100]}...")
        
        lines.append("\n*Use `/skill <name>` to activate a skill*")
        
        return "\n".join(lines)


# Convenience function for kernel integration
def create_skill_manager(user_id: str = None) -> SkillManager:
    """Create a SkillManager instance with default configuration."""
    return SkillManager(skills_dir="skills", user_id=user_id)
