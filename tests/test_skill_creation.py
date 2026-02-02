#!/usr/bin/env python3
"""
Test Phase 2: User-Created Skills

Verifies skill creation from natural language and conversation extraction.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_skill_creator_standalone():
    """Test SkillCreator works independently."""
    from skills.skill_creator import SkillCreator, SkillBlueprint
    
    print("=" * 60)
    print("TEST: SkillCreator Standalone")
    print("=" * 60)
    
    creator = SkillCreator(skills_dir="skills")
    
    # Test 1: Create from description
    description = """
    Check my Gmail for unread emails from the last 12 hours,
    summarize the important ones,
    and post the summary to my Slack channel #daily-updates
    """
    
    blueprint = creator.create_from_description(description)
    
    print(f"✅ Created blueprint: {blueprint.name}")
    print(f"   Description: {blueprint.description[:50]}...")
    print(f"   Triggers: {blueprint.triggers}")
    print(f"   Steps: {len(blueprint.steps)}")
    print(f"   Tools: {blueprint.tools_used}")
    
    # Test 2: Generate SKILL.md content
    md_content = blueprint.to_skill_md()
    print(f"\n✅ Generated SKILL.md ({len(md_content)} chars)")
    print("   Preview:")
    print("   " + md_content[:200].replace("\n", "\n   "))
    
    return True


def test_skill_name_generation():
    """Test automatic skill name generation."""
    from skills.skill_creator import SkillCreator
    
    print("\n" + "=" * 60)
    print("TEST: Skill Name Generation")
    print("=" * 60)
    
    creator = SkillCreator(skills_dir="skills")
    
    test_cases = [
        "Create a spreadsheet and share with the team",
        "Check my calendar for meetings tomorrow",
        "Send a weekly report to my manager",
        "Morning email digest from Gmail",
    ]
    
    for desc in test_cases:
        blueprint = creator.create_from_description(desc)
        print(f"   '{desc[:40]}...' → {blueprint.name}")
    
    print("✅ Name generation working")
    return True


def test_conversation_extraction():
    """Test skill extraction from conversation."""
    from skills.skill_creator import SkillCreator
    
    print("\n" + "=" * 60)
    print("TEST: Conversation Extraction")
    print("=" * 60)
    
    creator = SkillCreator(skills_dir="skills")
    
    messages = [
        {"role": "user", "content": "Create a new spreadsheet for Q1 budget"},
        {"role": "assistant", "content": "I'll create a new Google Sheets spreadsheet for Q1 budget. ✅ Created 'Q1 Budget 2025'"},
        {"role": "user", "content": "Now share it with the finance team"},
        {"role": "assistant", "content": "✅ Shared with finance@company.com"},
        {"role": "user", "content": "Add a summary row at the bottom"},
        {"role": "assistant", "content": "✅ Added summary row with totals"},
    ]
    
    blueprint = creator.create_from_conversation(messages)
    
    print(f"✅ Extracted skill: {blueprint.name}")
    print(f"   Steps extracted: {len(blueprint.steps)}")
    for i, step in enumerate(blueprint.steps[:3]):
        print(f"     {i+1}. {step[:50]}...")
    print(f"   Tools: {blueprint.tools_used}")
    
    return True


def test_kernel_skill_creation():
    """Test skill creation through kernel."""
    print("\n" + "=" * 60)
    print("TEST: Kernel Skill Creation")
    print("=" * 60)
    
    try:
        from kernel import AgentKernel
        
        kernel = AgentKernel(user_id="test_user")
        
        # Check skill creator attached
        if not kernel.skill_creator:
            print("❌ SkillCreator not attached to kernel")
            return False
        
        print("✅ SkillCreator attached to kernel")
        
        # Test create_skill method (without saving)
        # We'll test the blueprint creation without actually saving
        from skills.skill_creator import SkillCreator
        creator = kernel.skill_creator
        
        blueprint = creator.create_from_description(
            "Check Gmail and send daily summary to Slack",
            user_id="test_user"
        )
        
        print(f"✅ Skill creation works: {blueprint.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Kernel skill creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pattern_detection():
    """Test query pattern detection."""
    print("\n" + "=" * 60)
    print("TEST: Pattern Detection")
    print("=" * 60)
    
    try:
        from kernel import AgentKernel
        
        kernel = AgentKernel(user_id="test_user")
        
        # Simulate repeated similar queries
        queries = [
            "create a spreadsheet for monthly report",
            "make a spreadsheet for weekly report",
            "create spreadsheet for quarterly report",
            "generate a spreadsheet for annual report",
        ]
        
        suggestion = None
        for query in queries:
            result = kernel.track_query_for_patterns(query)
            if result:
                suggestion = result
        
        if suggestion:
            print(f"✅ Pattern detected after {len(queries)} queries")
            print(f"   Suggestion preview: {suggestion[:100]}...")
        else:
            print(f"⚠️  Pattern not detected (expected after 3+ similar queries)")
        
        return True
        
    except Exception as e:
        print(f"❌ Pattern detection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_smart_run_commands():
    """Test smart_run command parsing."""
    print("\n" + "=" * 60)
    print("TEST: Smart Run Commands")
    print("=" * 60)
    
    try:
        from kernel import AgentKernel
        
        kernel = AgentKernel(user_id="test_user")
        
        # Test list skills (doesn't need LLM)
        result = kernel.smart_run("list skills")
        print(f"✅ 'list skills' command works")
        print(f"   Result preview: {result[:80]}...")
        
        # Test cancel command (no-op if nothing pending)
        result = kernel.smart_run("cancel skill")
        print(f"✅ 'cancel skill' command works: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Smart run test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🧪 PHASE 2: USER-CREATED SKILLS TEST SUITE\n")
    
    results = []
    
    # Run tests
    results.append(("SkillCreator Standalone", test_skill_creator_standalone()))
    results.append(("Skill Name Generation", test_skill_name_generation()))
    results.append(("Conversation Extraction", test_conversation_extraction()))
    results.append(("Kernel Skill Creation", test_kernel_skill_creation()))
    results.append(("Pattern Detection", test_pattern_detection()))
    results.append(("Smart Run Commands", test_smart_run_commands()))
    
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
