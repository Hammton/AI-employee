"""
Test suite for proactive agent functionality.

Tests friction detection and proactive prompt building.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from proactive_agent import FrictionDetector, ProactivePromptBuilder, should_use_proactive_mode


def test_friction_detection():
    """Test that friction keywords are detected correctly."""
    
    # Test cases with expected friction
    friction_messages = [
        "Checking my emails manually every day is so annoying",
        "I always have to remember to follow up on tasks",
        "It's tedious to update my spreadsheet every morning",
        "I hate doing this repetitive work",
        "Wish I could automate this boring task",
    ]
    
    for msg in friction_messages:
        result = FrictionDetector.detect(msg)
        assert result['has_friction'], f"Should detect friction in: {msg}"
        assert len(result['friction_points']) > 0, f"Should have friction points for: {msg}"
        print(f"✅ Detected friction in: '{msg[:50]}...'")
        print(f"   Keywords: {[fp['keyword'] for fp in result['friction_points']]}")
    
    # Test cases without friction
    normal_messages = [
        "What's the weather today?",
        "Can you help me with this task?",
        "Tell me about Python programming",
    ]
    
    for msg in normal_messages:
        result = FrictionDetector.detect(msg)
        assert not result['has_friction'], f"Should NOT detect friction in: {msg}"
        print(f"✅ No friction in: '{msg}'")


def test_proactive_prompt_building():
    """Test that proactive prompts are built correctly."""
    
    message = "Checking my emails manually is so annoying"
    friction = FrictionDetector.detect(message)
    
    prompt = ProactivePromptBuilder.build_proactive_prompt(
        friction,
        ['GMAIL', 'ASANA', 'GOOGLECALENDAR']
    )
    
    # Verify prompt contains key elements
    assert 'PROACTIVE MODE ACTIVATED' in prompt
    assert 'BUILD A SOLUTION IMMEDIATELY' in prompt
    assert 'GMAIL' in prompt
    assert message in prompt
    
    print("✅ Proactive prompt built successfully")
    print(f"   Prompt length: {len(prompt)} chars")


def test_should_use_proactive_mode():
    """Test the quick check function."""
    
    assert should_use_proactive_mode("This is so annoying") == True
    assert should_use_proactive_mode("I always have to do this manually") == True
    assert should_use_proactive_mode("What's the weather?") == False
    
    print("✅ Proactive mode detection works correctly")


def test_system_prompt():
    """Test that system prompt is generated."""
    
    prompt = ProactivePromptBuilder.build_proactive_system_prompt()
    
    assert 'PROACTIVE' in prompt
    assert 'BUILD SOLUTIONS IMMEDIATELY' in prompt
    assert 'DO NOT' in prompt
    assert 'EXAMPLES' in prompt
    
    print("✅ System prompt generated successfully")
    print(f"   Prompt length: {len(prompt)} chars")


if __name__ == "__main__":
    print("🧪 Testing Proactive Agent System\n")
    
    try:
        test_friction_detection()
        print()
        test_proactive_prompt_building()
        print()
        test_should_use_proactive_mode()
        print()
        test_system_prompt()
        print()
        print("✅ All tests passed!")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
