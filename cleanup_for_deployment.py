"""Clean up project for deployment"""
import os
import shutil
from pathlib import Path

def cleanup_project():
    """Organize and clean up project files"""
    print("\n" + "=" * 70)
    print("CLEANING UP PROJECT FOR DEPLOYMENT")
    print("=" * 70)
    
    # Create directories
    dirs_to_create = [
        "docs",
        "tests",
        "scripts",
        "archive"
    ]
    
    for dir_name in dirs_to_create:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✓ Created {dir_name}/ directory")
    
    # Files to keep in root
    keep_in_root = {
        # Core application files
        "main_v2.py",
        "kernel.py",
        "integrate_mem0.py",
        
        # Configuration
        ".env",
        "requirements.txt",
        "package.json",
        "package-lock.json",
        
        # Docker/Deployment
        "Dockerfile",
        "Dockerfile.python",
        "docker-compose.yml",
        "railway.json",
        "railway.toml",
        "render.yaml",
        
        # Documentation (keep main ones)
        "README.md",
        "DEPLOYMENT.md",
        "USE_CASES.md",
        
        # Utility scripts
        "connect_anchor_browser.py",
        "start.bat",
    }
    
    # Move documentation files
    doc_files = [
        "FINAL_ACHIEVEMENT_REPORT.md",
        "MEM0_INTEGRATION_GUIDE.md",
        "MOLTBOT_COMPARISON_AND_ROADMAP.md",
        "QUICK_START_GUIDE.md",
        "ACHIEVEMENT_SUMMARY.md",
        "ANCHOR_BROWSER_SETUP.md",
        "GET_TOOLS_SOLUTION_SUMMARY.md",
        "GOOGLEDOCS_SHEETS_FIX.md",
        "ANTIGRAVITY_CONNECTION_FIX.md",
        "CONNECTION_CHECK_FIX.md",
        "QUICK_START.md",
        "SESSION_SUMMARY.md",
        "RUN_MAIN_V2.md",
        "MAIN_V2_PER_USER_FIX.md",
        "BEFORE_AFTER_COMPARISON.md",
        "PER_USER_FIX_SUMMARY.md",
        "MULTI_TOOL_SUCCESS_SUMMARY.md",
        "ASANA_SOLUTION.md",
        "ASANA_LIMITATION.md",
        "ASANA_TEST_RESULTS.md",
        "ANALYSIS_REPORT.md",
        "FIX_SUMMARY.md",
        "FINAL_STATUS_REPORT.md",
        "TOOL_EXECUTION_FIX_SUMMARY.md",
        "connect_gmail_instructions.md",
    ]
    
    # Move test files
    test_files = [
        f for f in os.listdir(".")
        if f.startswith("test_") and f.endswith(".py")
    ]
    
    # Move check/debug files
    check_files = [
        f for f in os.listdir(".")
        if (f.startswith("check_") or f.startswith("debug_") or 
            f.startswith("diagnose_") or f.startswith("verify_") or
            f.startswith("inspect_") or f.startswith("find_") or
            f.startswith("discover_") or f.startswith("explore_") or
            f.startswith("list_") or f.startswith("get_")) 
        and f.endswith(".py")
        and f not in keep_in_root
    ]
    
    # Move utility scripts
    script_files = [
        "add_memory_system.py",
        "downgrade_composio.py",
        "generate_gmail_url.py",
        "agent_with_auth.py",
        "modal_agent.py",
        "modal_agent_v2.py",
        "modal_test.py",
        "final_test.py",
    ]
    
    moved_count = 0
    
    # Move documentation
    print("\n📚 Moving documentation files...")
    for file in doc_files:
        if os.path.exists(file):
            try:
                shutil.move(file, f"docs/{file}")
                print(f"  → docs/{file}")
                moved_count += 1
            except Exception as e:
                print(f"  ✗ Failed to move {file}: {e}")
    
    # Move test files
    print("\n🧪 Moving test files...")
    for file in test_files:
        if os.path.exists(file):
            try:
                shutil.move(file, f"tests/{file}")
                print(f"  → tests/{file}")
                moved_count += 1
            except Exception as e:
                print(f"  ✗ Failed to move {file}: {e}")
    
    # Move check/debug files
    print("\n🔍 Moving check/debug files...")
    for file in check_files:
        if os.path.exists(file):
            try:
                shutil.move(file, f"scripts/{file}")
                print(f"  → scripts/{file}")
                moved_count += 1
            except Exception as e:
                print(f"  ✗ Failed to move {file}: {e}")
    
    # Move utility scripts
    print("\n🛠️  Moving utility scripts...")
    for file in script_files:
        if os.path.exists(file):
            try:
                shutil.move(file, f"scripts/{file}")
                print(f"  → scripts/{file}")
                moved_count += 1
            except Exception as e:
                print(f"  ✗ Failed to move {file}: {e}")
    
    # Files to delete (temporary/generated)
    files_to_delete = [
        "nul",
        "python",
        "output.txt",
        "auth_configs_output.txt",
        "test_auth_output.txt",
        "server.log",
        "qr_test.png",
        "error.jpg",
        "rece.jpg",
        "Screenshot 2026-01-29 135701.jpg",
    ]
    
    print("\n🗑️  Deleting temporary files...")
    for file in files_to_delete:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"  ✗ Deleted {file}")
                moved_count += 1
            except Exception as e:
                print(f"  ✗ Failed to delete {file}: {e}")
    
    # Create .gitignore if it doesn't exist
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/
server.log

# Memory
memory/*.json

# Session data
session_data/

# Node modules
node_modules/
wpp-bridge/node_modules/
wpp-bridge/tokens/

# Cache
.ruff_cache/
.pytest_cache/
.mypy_cache/

# Temporary files
*.tmp
*.temp
nul
python
output.txt
qr_test.png

# Images (except docs)
*.jpg
*.png
*.gif
!docs/*.png
!docs/*.jpg
"""
    
    if not os.path.exists(".gitignore"):
        with open(".gitignore", "w") as f:
            f.write(gitignore_content)
        print("\n✓ Created .gitignore")
    
    print("\n" + "=" * 70)
    print(f"CLEANUP COMPLETE! Moved/deleted {moved_count} files")
    print("=" * 70)
    
    print("\n📁 Project structure:")
    print("  ├── main_v2.py          (FastAPI server)")
    print("  ├── kernel.py           (AI agent core)")
    print("  ├── integrate_mem0.py   (Memory system)")
    print("  ├── requirements.txt    (Python deps)")
    print("  ├── .env                (Configuration)")
    print("  ├── wpp-bridge/         (WhatsApp bridge)")
    print("  ├── docs/               (Documentation)")
    print("  ├── tests/              (Test files)")
    print("  ├── scripts/            (Utility scripts)")
    print("  └── memory/             (User memories)")
    
    print("\n✅ Ready for deployment!")
    print("\nNext steps:")
    print("1. Review .env for production secrets")
    print("2. Test: python main_v2.py")
    print("3. Deploy to Railway/Render/Cloudflare")

if __name__ == "__main__":
    cleanup_project()
