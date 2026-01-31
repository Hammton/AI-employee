"""Get ALL Asana actions from Composio"""
import os
from dotenv import load_dotenv
from composio import Composio

load_dotenv()

def get_all_asana_actions():
    """Get all Asana actions"""
    print("\n" + "=" * 70)
    print("GETTING ALL ASANA ACTIONS FROM COMPOSIO")
    print("=" * 70)
    
    composio_client = Composio(api_key=os.environ.get("COMPOSIO_API_KEY"))
    user_id = "+254708235245@c.us"
    
    print(f"\nUser: {user_id}")
    
    # Try to get all actions for Asana
    print("\n1. Getting actions from Composio...")
    try:
        # Get all actions for the asana app
        actions = composio_client.actions.list(app="asana")
        
        print(f"\n✓ Found {len(actions.items)} Asana actions\n")
        
        # Categorize
        get_actions = []
        create_actions = []
        delete_actions = []
        update_actions = []
        other_actions = []
        
        for action in actions.items:
            action_name = action.name if hasattr(action, 'name') else str(action)
            
            if 'GET' in action_name or 'RETRIEVE' in action_name or 'LIST' in action_name:
                get_actions.append(action_name)
            elif 'CREATE' in action_name or 'ADD' in action_name:
                create_actions.append(action_name)
            elif 'DELETE' in action_name or 'REMOVE' in action_name:
                delete_actions.append(action_name)
            elif 'UPDATE' in action_name or 'MODIFY' in action_name or 'SET' in action_name:
                update_actions.append(action_name)
            else:
                other_actions.append(action_name)
        
        print(f"📖 GET/READ/LIST Actions ({len(get_actions)}):")
        for action in sorted(get_actions)[:20]:  # Show first 20
            print(f"   - {action}")
        if len(get_actions) > 20:
            print(f"   ... and {len(get_actions) - 20} more")
        
        print(f"\n➕ CREATE/ADD Actions ({len(create_actions)}):")
        for action in sorted(create_actions)[:10]:
            print(f"   - {action}")
        if len(create_actions) > 10:
            print(f"   ... and {len(create_actions) - 10} more")
        
        print(f"\n✏️  UPDATE/MODIFY Actions ({len(update_actions)}):")
        for action in sorted(update_actions)[:10]:
            print(f"   - {action}")
        if len(update_actions) > 10:
            print(f"   ... and {len(update_actions) - 10} more")
        
        print(f"\n🗑️  DELETE/REMOVE Actions ({len(delete_actions)}):")
        for action in sorted(delete_actions):
            print(f"   - {action}")
        
        # Check for specific actions we need
        print("\n" + "=" * 70)
        print("CHECKING FOR SPECIFIC ACTIONS WE NEED:")
        print("=" * 70)
        
        all_action_names = [a.name if hasattr(a, 'name') else str(a) for a in actions.items]
        
        needed_actions = [
            'ASANA_GET_MULTIPLE_PROJECTS',
            'ASANA_GET_MULTIPLE_WORKSPACES',
            'ASANA_GET_MULTIPLE_TASKS',
            'ASANA_GET_A_PROJECT',
            'ASANA_GET_A_TASK',
            'ASANA_GET_PROJECTS_FOR_TEAM',
            'ASANA_GET_TASKS_FROM_A_SECTION'
        ]
        
        for action_name in needed_actions:
            found = action_name in all_action_names
            status = "✓ FOUND" if found else "✗ NOT FOUND"
            print(f"   {action_name:45} {status}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    get_all_asana_actions()
