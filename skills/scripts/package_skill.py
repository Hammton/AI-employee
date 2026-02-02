#!/usr/bin/env python3
"""
Package a Skill for Distribution

Validates and packages a skill into a distributable .skill file.

Usage:
    python package_skill.py <path/to/skill-folder>
    python package_skill.py <path/to/skill-folder> ./dist

The script:
1. Validates the skill (frontmatter, structure, description)
2. Packages into a .skill file (zip with .skill extension)
"""

import argparse
import os
import re
import yaml
import zipfile
from pathlib import Path
from typing import List, Tuple


class SkillValidator:
    """Validates skill structure and content."""
    
    def __init__(self, skill_path: Path):
        self.skill_path = skill_path
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate(self) -> bool:
        """Run all validations. Returns True if valid."""
        self._validate_structure()
        self._validate_frontmatter()
        self._validate_description()
        self._validate_resources()
        
        return len(self.errors) == 0
    
    def _validate_structure(self):
        """Validate basic skill structure."""
        # Check skill directory exists
        if not self.skill_path.exists():
            self.errors.append(f"Skill directory not found: {self.skill_path}")
            return
        
        if not self.skill_path.is_dir():
            self.errors.append(f"Path is not a directory: {self.skill_path}")
            return
        
        # Check SKILL.md exists
        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            self.errors.append("SKILL.md not found (required)")
        
        # Check for disallowed files
        disallowed = ["README.md", "CHANGELOG.md", "INSTALLATION_GUIDE.md", "QUICK_REFERENCE.md"]
        for filename in disallowed:
            if (self.skill_path / filename).exists():
                self.warnings.append(f"Extraneous file found: {filename} (consider removing)")
    
    def _validate_frontmatter(self):
        """Validate YAML frontmatter."""
        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            return
        
        content = skill_md.read_text(encoding='utf-8')
        
        # Check frontmatter exists
        if not content.startswith("---"):
            self.errors.append("SKILL.md must start with YAML frontmatter (---)")
            return
        
        # Extract frontmatter
        match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not match:
            self.errors.append("Invalid YAML frontmatter format")
            return
        
        try:
            frontmatter = yaml.safe_load(match.group(1))
        except yaml.YAMLError as e:
            self.errors.append(f"Invalid YAML in frontmatter: {e}")
            return
        
        # Check required fields
        if not frontmatter.get("name"):
            self.errors.append("Frontmatter missing required field: name")
        
        if not frontmatter.get("description"):
            self.errors.append("Frontmatter missing required field: description")
        
        # Check for extra fields (only name and description allowed)
        allowed_fields = {"name", "description"}
        extra_fields = set(frontmatter.keys()) - allowed_fields
        if extra_fields:
            self.warnings.append(f"Extra frontmatter fields: {extra_fields}")
    
    def _validate_description(self):
        """Validate description quality."""
        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            return
        
        content = skill_md.read_text(encoding='utf-8')
        match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return
        
        try:
            frontmatter = yaml.safe_load(match.group(1))
            description = frontmatter.get("description", "")
        except:
            return
        
        # Check description length
        if len(description) < 50:
            self.warnings.append("Description is very short - include when to use this skill")
        
        # Check for placeholder text
        if "[REPLACE" in description or "TODO" in description:
            self.errors.append("Description contains placeholder text - please complete it")
    
    def _validate_resources(self):
        """Validate bundled resources."""
        # Check scripts are executable
        scripts_dir = self.skill_path / "scripts"
        if scripts_dir.exists():
            for script in scripts_dir.glob("*.py"):
                # Just check it's valid Python syntax
                try:
                    with open(script, 'r') as f:
                        compile(f.read(), script, 'exec')
                except SyntaxError as e:
                    self.errors.append(f"Script syntax error in {script.name}: {e}")
        
        # Check body isn't too long
        skill_md = self.skill_path / "SKILL.md"
        if skill_md.exists():
            content = skill_md.read_text(encoding='utf-8')
            lines = content.split('\n')
            if len(lines) > 500:
                self.warnings.append(f"SKILL.md is {len(lines)} lines - consider splitting into references")


def package_skill(skill_path: Path, output_dir: Path = None) -> Path:
    """Package a skill into a .skill file."""
    
    skill_name = skill_path.name
    
    if output_dir is None:
        output_dir = skill_path.parent
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create .skill file (zip with .skill extension)
    skill_file = output_dir / f"{skill_name}.skill"
    
    with zipfile.ZipFile(skill_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_path.rglob('*'):
            if file_path.is_file():
                # Skip __pycache__ and other unwanted files
                if '__pycache__' in str(file_path):
                    continue
                if file_path.suffix in ['.pyc', '.pyo']:
                    continue
                
                arcname = file_path.relative_to(skill_path.parent)
                zf.write(file_path, arcname)
    
    return skill_file


def main():
    parser = argparse.ArgumentParser(
        description="Validate and package a skill"
    )
    parser.add_argument(
        "skill_path",
        help="Path to the skill directory"
    )
    parser.add_argument(
        "output_dir",
        nargs="?",
        help="Output directory for .skill file (default: skill's parent directory)"
    )
    parser.add_argument(
        "--validate-only", "-v",
        action="store_true",
        help="Only validate, don't package"
    )
    
    args = parser.parse_args()
    
    skill_path = Path(args.skill_path).resolve()
    output_dir = Path(args.output_dir).resolve() if args.output_dir else None
    
    # Validate
    print(f"🔍 Validating skill: {skill_path.name}")
    validator = SkillValidator(skill_path)
    is_valid = validator.validate()
    
    # Report warnings
    for warning in validator.warnings:
        print(f"   ⚠️  {warning}")
    
    # Report errors
    for error in validator.errors:
        print(f"   ❌ {error}")
    
    if not is_valid:
        print(f"\n❌ Validation failed ({len(validator.errors)} errors)")
        return 1
    
    print(f"   ✅ Validation passed")
    
    if args.validate_only:
        return 0
    
    # Package
    print(f"\n📦 Packaging skill...")
    skill_file = package_skill(skill_path, output_dir)
    
    # Get file size
    size_kb = skill_file.stat().st_size / 1024
    
    print(f"""
✅ Skill packaged successfully!

📁 Output: {skill_file}
📊 Size: {size_kb:.1f} KB

To install this skill:
  1. Copy {skill_file.name} to your skills directory
  2. Extract: unzip {skill_file.name}
  3. The skill will be auto-discovered on next agent startup
""")
    
    return 0


if __name__ == "__main__":
    exit(main())
