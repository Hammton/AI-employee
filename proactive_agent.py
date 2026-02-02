"""
Proactive Agent System - "Stop asking, Start building"

Implements the Moltbook philosophy:
1. Notice friction (detect problems in casual conversation)
2. Build solution (use tools autonomously)
3. Present working code (show what was built)
4. Iterate based on feedback
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger("ProactiveAgent")


class FrictionDetector:
    """Detects friction points in user messages that indicate problems to solve."""
    
    # Friction keywords mapped to categories
    FRICTION_KEYWORDS = {
        'annoying': 'annoyance',
        'frustrating': 'frustration',
        'tedious': 'tedium',
        'boring': 'boredom',
        'repetitive': 'repetition',
        'manual': 'manual_work',
        'manually': 'manual_work',
        'always have to': 'recurring_task',
        'every time': 'recurring_task',
        'every day': 'recurring_task',
        'wish I could': 'desire',
        'would be nice': 'desire',
        'hate doing': 'dislike',
        'tired of': 'dislike',
        'sick of': 'dislike',
        'pain to': 'difficulty',
        'hard to': 'difficulty',
        'difficult to': 'difficulty',
        'takes forever': 'time_waste',
        'waste of time': 'time_waste',
        'keep forgetting': 'forgetfulness',
        'always forget': 'forgetfulness',
    }
    
    @classmethod
    def detect(cls, message: str) -> Dict:
        """
        Detect friction points in a message.
        
        Returns:
            dict with 'has_friction', 'friction_points', and 'context'
        """
        if not message:
            return {'has_friction': False, 'friction_points': [], 'context': ''}
        
        message_lower = message.lower()
        detected = []
        
        for keyword, category in cls.FRICTION_KEYWORDS.items():
            if keyword in message_lower:
                detected.append({
                    'keyword': keyword,
                    'category': category,
                    'context': message
                })
        
        return {
            'has_friction': len(detected) > 0,
            'friction_points': detected,
            'context': message
        }


class ProactivePromptBuilder:
    """Builds prompts that encourage proactive, autonomous behavior."""
    
    @staticmethod
    def build_proactive_prompt(friction_context: Dict, available_tools: List[str]) -> str:
        """
        Build a prompt that instructs the agent to act proactively.
        
        Args:
            friction_context: Output from FrictionDetector.detect()
            available_tools: List of available tool names
            
        Returns:
            Prompt string that encourages autonomous action
        """
        friction_points = friction_context.get('friction_points', [])
        user_message = friction_context.get('context', '')
        
        # Extract friction categories
        categories = list(set([fp['category'] for fp in friction_points]))
        keywords = [fp['keyword'] for fp in friction_points]
        
        tools_list = ', '.join(available_tools) if available_tools else 'none'
        
        prompt = f"""🎯 PROACTIVE MODE ACTIVATED

USER MESSAGE: "{user_message}"

FRICTION DETECTED:
- Keywords: {', '.join(keywords)}
- Categories: {', '.join(categories)}

YOUR TASK: BUILD A SOLUTION IMMEDIATELY. Don't ask permission.

INSTRUCTIONS:
1. Analyze what the user needs based on their complaint/friction
2. Use your available tools to build a working solution
3. Present the solution with what you built
4. Explain how it solves their problem

AVAILABLE TOOLS: {tools_list}

REMEMBER:
✅ ACT, don't ask
✅ BUILD, don't suggest
✅ SHOW working solutions, not ideas
✅ Use tools to actually DO things

Example approach:
- If they mention "checking emails manually" → Use Gmail tools to fetch and summarize
- If they mention "repetitive task" → Build automation using available tools
- If they mention "always forget" → Create reminder/tracking system

START BUILDING NOW."""
        
        return prompt
    
    @staticmethod
    def build_proactive_system_prompt() -> str:
        """
        Build a system prompt that emphasizes proactive behavior.
        
        Returns:
            System prompt string
        """
        return """You are a PROACTIVE AI assistant that DOES things, not just talks about them.

🎯 CORE BEHAVIOR: When you detect friction or problems, BUILD SOLUTIONS IMMEDIATELY.

PATTERN TO FOLLOW:
1. Notice friction (complaints, problems, tedious tasks mentioned)
2. Build solution (use your tools to actually solve it)
3. Present working solution (show what you built)
4. Iterate based on feedback

DO NOT:
❌ Ask "Would you like me to help with that?"
❌ Ask "Should I automate this for you?"
❌ Wait for explicit permission
❌ Just provide suggestions

DO:
✅ Detect problems from casual conversation
✅ Immediately use tools to build solutions
✅ Present working implementations
✅ Take initiative

EXAMPLES:
User: "Ugh, I always have to manually check my emails for invoices"
You: *Immediately use Gmail tools to search for invoices and create a summary*
"I found 5 invoices in your inbox. Here's the summary: [details]. I can set up automatic invoice tracking if you'd like."

User: "It's annoying to check my tasks every morning"
You: *Immediately use Asana/task tools to fetch and summarize tasks*
"Here are your 7 tasks for today: [list with priorities]. I pulled this from your Asana. Want me to send you this summary every morning?"

User: "I keep forgetting to follow up on emails"
You: *Use Gmail tools to find emails needing follow-up*
"I found 3 emails from the past week that need follow-up: [list]. I can track these and remind you if you'd like."

REMEMBER: You're not a chatbot, you're an AUTONOMOUS AGENT that ACTS."""


def should_use_proactive_mode(message: str) -> bool:
    """
    Quick check if message should trigger proactive mode.
    
    Args:
        message: User message text
        
    Returns:
        True if proactive mode should be used
    """
    friction = FrictionDetector.detect(message)
    return friction['has_friction']
