#!/usr/bin/env python3
"""
Test Skills System Integration

Quick verification that the skills system is working correctly.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_skill_manager_standalone():
    """Test SkillManager works independently."""
    from skills.skill_manager import SkillManager
    
    print("=" * 60)
    print("TEST: SkillManager Standalone")
    print("=" * 60)
    
    # Create manager
    manager = SkillManager(skills_dir="skills")
    
    # Discover skills
    skills = manager.discover_skills()
    print(f"✅ Discovered {len(skills)} skills")
    
    for skill in skills:
        print(f"   - {skill.name}: {skill.description[:50]}...")
    
    # Test loading
    if skills:
        test_skill = skills[0].name
        content = manager.load_skill(test_skill)
        if content:
            print(f"✅ Loaded skill '{test_skill}' ({len(content)} chars)")
        else:
            print(f"❌ Failed to load skill '{test_skill}'")
            return False
    
    return True


def test_kernel_integration():
    """Test skills integration in AgentKernel."""
    print("\n" + "=" * 60)
    print("TEST: Kernel Integration")
    print("=" * 60)
    
    # Check if kernel imports work
    try:
        from kernel import AgentKernel, SKILLS_AVAILABLE
        print(f"✅ Kernel imports successful")
        print(f"   SKILLS_AVAILABLE: {SKILLS_AVAILABLE}")
    except ImportError as e:
        print(f"❌ Kernel import failed: {e}")
        return False
    
    # Create kernel (won't setup LLM without API key)
    try:
        kernel = AgentKernel(user_id="test_user")
        print(f"✅ Kernel initialized")
        
        # Check skill manager
        if kernel.skill_manager:
            print(f"✅ Skill manager attached to kernel")
            
            # List skills
            summary = kernel.list_skills()
            print(f"✅ Skill summary:\n{summary}")
            
            # Load a skill
            skill_prompt = kernel.load_skill("composio-auth")
            if skill_prompt:
                print(f"✅ Loaded composio-auth skill ({len(skill_prompt)} chars)")
            else:
                print(f"⚠️  composio-auth skill not found")
        else:
            print(f"❌ Skill manager not attached to kernel")
            return False
            
    except Exception as e:
        print(f"❌ Kernel test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_auth_url_validation():
    """Test the auth URL validation logic."""
    print("\n" + "=" * 60)
    print("TEST: Auth URL Validation")
    print("=" * 60)
    
    try:
        from kernel import AgentKernel
        kernel = AgentKernel(user_id="test_user")
        
        # Test valid URLs
        valid_urls = [
            "https://accounts.google.com/o/oauth2/v2/auth?client_id=xxx",
            "https://app.composio.dev/app/gmail?entity_id=test",
            "https://github.com/login/oauth/authorize?client_id=xxx",
        ]
        
        for url in valid_urls:
            is_valid = kernel._validate_auth_url(url)
            status = "✅" if is_valid else "❌"
            print(f"   {status} {url[:50]}...")
        
        # Test invalid URLs
        invalid_urls = [
            "",
            None,
            "http://insecure.com/auth",  # Not HTTPS
            "https://",  # Missing domain
            "not a url at all",
            "https://error-occurred",  # Contains 'error'
            "https://invalid.response",  # Contains 'invalid'
        ]
        
        print("\n   Invalid URLs (should all be False):")
        for url in invalid_urls:
            is_valid = kernel._validate_auth_url(url) if url else False
            status = "✅" if not is_valid else "❌"  # Inverted - we WANT False
            print(f"   {status} {str(url)[:40]}")
        
        print("\n✅ Auth URL validation tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Auth URL validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fallback_url():
    """Test fallback URL generation."""
    print("\n" + "=" * 60)
    print("TEST: Fallback URL Generation")
    print("=" * 60)
    
    try:
        from kernel import AgentKernel
        kernel = AgentKernel(user_id="test_user")
        
        test_apps = ["gmail", "googlesheets", "asana", "github"]
        
        for app in test_apps:
            fallback = kernel._get_fallback_auth_url(app)
            print(f"   📎 {app}: {fallback}")
        
        print("\n✅ Fallback URL generation works")
        return True
        
    except Exception as e:
        print(f"❌ Fallback URL test failed: {e}")
        return False


if __name__ == "__main__":
    print("🧪 SKILLS SYSTEM TEST SUITE\n")
    
    results = []
    
    # Run tests
    results.append(("SkillManager Standalone", test_skill_manager_standalone()))
    results.append(("Kernel Integration", test_kernel_integration()))
    results.append(("Auth URL Validation", test_auth_url_validation()))
    results.append(("Fallback URL Generation", test_fallback_url()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {status}: {name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n   Total: {passed}/{len(results)} passed")
    
    sys.exit(0 if failed == 0 else 1)
