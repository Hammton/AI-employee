#!/usr/bin/env python3
"""
Initialize a New Skill

Creates a properly structured skill directory with:
- SKILL.md template with YAML frontmatter
- Example resource directories (scripts/, references/, assets/)

Usage:
    python init_skill.py <skill-name> --path <output-directory>
    
Example:
    python init_skill.py morning-digest --path ../skills
"""

import argparse
import os
from pathlib import Path
from datetime import datetime


SKILL_MD_TEMPLATE = '''---
name: {skill_name}
description: {description}
---

# {skill_title}

## Purpose

[Describe what this skill does and the problem it solves]

## Workflow

1. [First step]
2. [Second step]
3. [Third step]

## Key Considerations

- [Important consideration 1]
- [Important consideration 2]

## Examples

### Example 1: [Scenario]

```
[Example input/output]
```
'''

EXAMPLE_SCRIPT = '''#!/usr/bin/env python3
"""
Example script for {skill_name} skill.

This script demonstrates the structure of skill scripts.
Replace or delete this file based on your skill's needs.

Usage:
    python example_script.py <args>
"""

import sys


def main():
    """Main entry point."""
    print("Example script for {skill_name}")
    print(f"Arguments: {sys.argv[1:]}")
    

if __name__ == "__main__":
    main()
'''

EXAMPLE_REFERENCE = '''# Reference: {skill_title}

This is an example reference file. References contain documentation
that Claude loads into context as needed.

## When to Use This Reference

- [Scenario 1]
- [Scenario 2]

## Contents

[Detailed reference content here]
'''

EXAMPLE_ASSET_README = '''# Assets for {skill_title}

This directory contains files used in the skill's output:
- Templates
- Images  
- Boilerplate code
- Sample documents

Files here are NOT loaded into context but are used/copied by Claude.

Delete this file when adding real assets.
'''


def init_skill(skill_name: str, output_path: str, description: str = None):
    """Initialize a new skill directory."""
    
    # Create skill directory
    skill_dir = Path(output_path) / skill_name
    
    if skill_dir.exists():
        print(f"❌ Error: Skill directory already exists: {skill_dir}")
        return False
    
    # Create directories
    skill_dir.mkdir(parents=True)
    (skill_dir / "scripts").mkdir()
    (skill_dir / "references").mkdir()
    (skill_dir / "assets").mkdir()
    
    # Format skill title
    skill_title = skill_name.replace("-", " ").replace("_", " ").title()
    
    # Generate description if not provided
    if not description:
        description = f"[REPLACE: Describe what {skill_title} does and when it should be used. Include specific triggers and contexts.]"
    
    # Write SKILL.md
    skill_md = SKILL_MD_TEMPLATE.format(
        skill_name=skill_name,
        skill_title=skill_title,
        description=description
    )
    (skill_dir / "SKILL.md").write_text(skill_md)
    
    # Write example files
    (skill_dir / "scripts" / "example_script.py").write_text(
        EXAMPLE_SCRIPT.format(skill_name=skill_name)
    )
    (skill_dir / "references" / "example_reference.md").write_text(
        EXAMPLE_REFERENCE.format(skill_title=skill_title)
    )
    (skill_dir / "assets" / "README.md").write_text(
        EXAMPLE_ASSET_README.format(skill_title=skill_title)
    )
    
    print(f"✅ Skill initialized: {skill_dir}")
    print(f"""
📁 {skill_name}/
├── SKILL.md              ← Edit this! Add your skill description and workflow
├── scripts/
│   └── example_script.py ← Replace with your scripts or delete
├── references/
│   └── example_reference.md ← Replace with your docs or delete
└── assets/
    └── README.md         ← Replace with templates/images or delete

Next steps:
1. Edit SKILL.md with your skill's description and workflow
2. Add scripts for deterministic/repeated operations
3. Add references for documentation to load as needed
4. Add assets for templates/files to use in output
5. Delete example files you don't need
6. Run 'python package_skill.py {skill_dir}' to package
""")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a new skill directory"
    )
    parser.add_argument(
        "skill_name",
        help="Name of the skill (kebab-case, e.g., 'morning-digest')"
    )
    parser.add_argument(
        "--path", "-p",
        default=".",
        help="Output directory for the skill (default: current directory)"
    )
    parser.add_argument(
        "--description", "-d",
        help="Short description of the skill"
    )
    
    args = parser.parse_args()
    
    # Validate skill name
    skill_name = args.skill_name.lower().replace(" ", "-").replace("_", "-")
    
    success = init_skill(skill_name, args.path, args.description)
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
