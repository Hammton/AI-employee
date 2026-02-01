import os
import io
import base64
import logging
from typing import Any, Optional, Literal, cast
from langchain_openai import ChatOpenAI
from langchain import agents
from composio import Composio
from composio_langchain import LangchainProvider
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PocketKernel")

# Import Mem0 for intelligent memory
try:
    from integrate_mem0 import Mem0Memory
    MEM0_AVAILABLE = True
except ImportError:
    MEM0_AVAILABLE = False
    logger.warning("Mem0 not available - install with: pip install mem0ai")

# Import Autonomous Executor for action execution
try:
    from autonomous_executor import AutonomousExecutor
    EXECUTOR_AVAILABLE = True
except ImportError:
    EXECUTOR_AVAILABLE = False
    logger.warning("AutonomousExecutor not available")


class AgentKernel:
    """
    The Kernel - Core AI Agent Engine
    
    Handles:
    - LLM reasoning (via OpenRouter)
    - Tool execution (via Composio)
    - Image generation, vision, TTS, transcription
    """

    def __init__(self, user_id: str = "default_user"):
        """Initialize the Kernel with environment configuration.
        
        Args:
            user_id: Unique identifier for the user (phone number, UUID, etc.)
                    This is used to scope tool connections and authentication.
        """
        # User context
        self.user_id = user_id
        
        # API Keys
        self.api_key = os.environ.get("OPENROUTER_API_KEY")
        self.composio_api_key = os.environ.get("COMPOSIO_API_KEY")
        
        # Model configuration
        self.model = os.environ.get("LLM_MODEL", "google/gemini-3-flash-preview")
        self.vision_model = os.environ.get("VISION_MODEL", "google/gemini-3-flash-preview")
        self.image_model = os.environ.get("IMAGE_MODEL", "google/gemini-2.5-flash-image")
        self.audio_model = os.environ.get("AUDIO_MODEL", "whisper-1")
        self.tts_model = os.environ.get("TTS_MODEL", "tts-1")
        self.tts_voice = os.environ.get("TTS_VOICE", "alloy")
        
        # Initialize clients as None - lazy initialization
        self.llm = None
        self.composio_client = None
        self.composio_session = None
        self.agent_executor = None
        
        # OpenAI-compatible client for OpenRouter
        self.openai_client = None
        self.image_client = None
        
        if self.api_key:
            self.openai_client = OpenAI(
                api_key=self.api_key,
                base_url="https://openrouter.ai/api/v1"
            )
            # Image client uses same OpenRouter endpoint
            self.image_client = OpenAI(
                api_key=self.api_key,
                base_url="https://openrouter.ai/api/v1"
            )
        
        # Active apps/toolkits for Composio
        self.active_apps = []
        
        # Initialize Mem0 intelligent memory
        self.memory = None
        if MEM0_AVAILABLE:
            try:
                self.memory = Mem0Memory()
                logger.info(f"✅ Mem0 intelligent memory initialized for user: {self.user_id}")
            except Exception as e:
                logger.warning(f"Mem0 initialization failed: {e}")
                self.memory = None
        else:
            logger.info("Mem0 not available - running without intelligent memory")
        
        # Initialize Autonomous Executor for action execution
        self.executor = None
        if EXECUTOR_AVAILABLE:
            try:
                # Require approval by default for safety
                require_approval = os.environ.get("AUTONOMOUS_EXECUTION_APPROVAL", "true").lower() == "true"
                self.executor = AutonomousExecutor(user_id=self.user_id, require_approval=require_approval)
                logger.info(f"✅ Autonomous Executor initialized (approval required: {require_approval})")
            except Exception as e:
                logger.warning(f"Autonomous Executor initialization failed: {e}")
                self.executor = None
        else:
            logger.info("Autonomous Executor not available - running without local execution")
        
        logger.info(f"Kernel initialized for user: {self.user_id}, Model: {self.model}")
        if not self.api_key:
            logger.warning("OPENROUTER_API_KEY not set!")
        if not self.composio_api_key:
            logger.warning("COMPOSIO_API_KEY not set!")

    def setup(self, apps: Optional[list[Any]] = None):
        """
        Initializes the Kernel with specified Composio toolkits.
        Merges new apps with existing active apps.
        Args:
            apps (list): List of toolkit slugs (e.g., ["github", "gmail"])
        """
        if not self.api_key or not self.composio_api_key:
            logger.warning("Missing API Keys. Kernel functionality limited.")
            return

        # Initialize LLM if not ready
        if not self.llm:
            self.llm = ChatOpenAI(
                api_key=cast(Any, self.api_key),
                base_url="https://openrouter.ai/api/v1",
                model=self.model,
                temperature=0.7,
                max_tokens=4096,  # Limit to avoid 402 credit errors
            )

        # Initialize Composio client and session if not ready
        if not self.composio_client:
            try:
                # Create Composio client WITH LangchainProvider for proper tool conversion
                self.composio_client = Composio(
                    api_key=self.composio_api_key,
                    provider=LangchainProvider()
                )
                logger.info("Composio client initialized with LangchainProvider")
                
                # Create session for this user (official pattern from docs)
                self.composio_session = self.composio_client.create(user_id=self.user_id)
                logger.info(f"Composio session created for user: {self.user_id}")
                    
            except Exception as e:
                logger.warning(f"Composio initialization failed: {e}")
                self.composio_client = None
                self.composio_session = None

        # Merge new apps into active_apps (using uppercase toolkit slugs for Composio)
        if apps:
            for app in apps:
                # Convert to uppercase slug format for Composio
                app_slug = str(app).upper().replace("APP.", "")
                if app_slug not in self.active_apps:
                    self.active_apps.append(app_slug)

        logger.info(f"Re-building Agent with Toolkits: {self.active_apps}")

        # AUTO-DETECT CONNECTED APPS: If no apps specified, check what user has connected
        if not self.active_apps and self.composio_client:
            try:
                logger.info("No apps specified - auto-detecting connected apps...")
                connected_accounts = self.composio_client.connected_accounts.list(
                    user_ids=[self.user_id]
                )
                
                # Get unique toolkit slugs from ACTIVE connections
                connected_slugs = set()
                for account in connected_accounts.items:
                    if account.status == "ACTIVE" and hasattr(account, 'toolkit') and account.toolkit:
                        toolkit_slug = getattr(account.toolkit, 'slug', '').upper()
                        if toolkit_slug:
                            connected_slugs.add(toolkit_slug)
                
                if connected_slugs:
                    self.active_apps = list(connected_slugs)
                    logger.info(f"✅ Auto-detected {len(self.active_apps)} connected apps: {self.active_apps}")
                else:
                    logger.info("No connected apps found for this user")
            except Exception as e:
                logger.warning(f"Failed to auto-detect connected apps: {e}")
        
        # Get Tools using the official composio.tools.get() API
        # This returns LangChain-compatible tools when using LangchainProvider
        composio_tools = []
        if self.composio_client and self.active_apps:
            try:
                # ENHANCED: Get BOTH default toolkit tools AND essential GET/LIST/READ tools
                # The default toolkits parameter only returns ~20 tools per toolkit (mostly CREATE/ADD/DELETE)
                # We need to explicitly request GET/LIST/READ tools using the 'tools' parameter
                
                # Define essential GET/LIST/READ tools for common integrations
                # This mapping ensures we get read operations for any integration
                essential_get_tools = {
                    'ASANA': [
                        'ASANA_GET_MULTIPLE_PROJECTS',
                        'ASANA_GET_MULTIPLE_WORKSPACES',
                        'ASANA_GET_MULTIPLE_TASKS',
                        'ASANA_GET_A_PROJECT',
                        'ASANA_GET_A_TASK',
                        'ASANA_GET_A_WORKSPACE',
                    ],
                    'GOOGLEDOCS': [
                        'GOOGLEDOCS_GET_DOCUMENT',
                        'GOOGLEDOCS_LIST_DOCUMENTS',
                        'GOOGLEDOCS_SEARCH_DOCUMENTS',
                    ],
                    'NOTION': [
                        'NOTION_GET_PAGE',
                        'NOTION_GET_DATABASE',
                        'NOTION_QUERY_DATABASE',
                        'NOTION_SEARCH',
                        'NOTION_LIST_USERS',
                    ],
                    'GOOGLESHEETS': [
                        'GOOGLESHEETS_GET_SPREADSHEET',
                        'GOOGLESHEETS_GET_SHEET_VALUES',
                        'GOOGLESHEETS_LIST_SPREADSHEETS',
                    ],
                    'GOOGLEDRIVE': [
                        'GOOGLEDRIVE_GET_FILE',
                        'GOOGLEDRIVE_LIST_FILES',
                        'GOOGLEDRIVE_SEARCH_FILES',
                    ],
                    'GITHUB': [
                        'GITHUB_GET_REPOSITORY',
                        'GITHUB_LIST_REPOSITORIES',
                        'GITHUB_GET_ISSUE',
                        'GITHUB_LIST_ISSUES',
                        'GITHUB_GET_PULL_REQUEST',
                        'GITHUB_LIST_PULL_REQUESTS',
                    ],
                    'SLACK': [
                        'SLACK_LIST_CHANNELS',
                        'SLACK_GET_CHANNEL_HISTORY',
                        'SLACK_LIST_USERS',
                    ],
                    'GMAIL': [
                        'GMAIL_FETCH_EMAILS',
                        'GMAIL_GET_EMAIL',
                        'GMAIL_LIST_LABELS',
                    ],
                    'GOOGLECALENDAR': [
                        'GOOGLECALENDAR_LIST_EVENTS',
                        'GOOGLECALENDAR_GET_EVENT',
                        'GOOGLECALENDAR_LIST_CALENDARS',
                    ],
                    'ANCHORBROWSER': [
                        'ANCHOR_BROWSER_PERFORM_WEB_TASK',
                        'ANCHOR_BROWSER_GET_PROFILE',
                        'ANCHOR_BROWSER_LIST_PROFILES',
                    ],
                }
                
                all_tools = []
                for app_slug in self.active_apps:
                    # Step 1: Get default toolkit tools (CREATE/ADD/DELETE operations)
                    try:
                        toolkit_tools = self.composio_client.tools.get(
                            user_id=self.user_id,
                            toolkits=[app_slug]
                        )
                        logger.info(f"Got {len(toolkit_tools)} default tools for {app_slug}")
                        all_tools.extend(toolkit_tools)
                    except ValueError as e:
                        # Handle invalid parameter names like '$count'
                        if "'$" in str(e) and "is not a valid parameter name" in str(e):
                            logger.warning(f"Skipping {app_slug} toolkit tools due to invalid parameter names: {e}")
                        else:
                            logger.warning(f"Failed to get toolkit tools for {app_slug}: {e}")
                    except Exception as e:
                        logger.warning(f"Failed to get toolkit tools for {app_slug}: {e}")
                    
                    # Step 2: Get essential GET/LIST/READ tools explicitly
                    get_tool_names = essential_get_tools.get(app_slug.upper(), [])
                    if get_tool_names:
                        # Try each tool individually to skip problematic ones
                        for tool_name in get_tool_names:
                            try:
                                get_tools = self.composio_client.tools.get(
                                    user_id=self.user_id,
                                    tools=[tool_name]
                                )
                                if get_tools:
                                    logger.info(f"✓ Loaded {tool_name}")
                                    all_tools.extend(get_tools)
                            except ValueError as e:
                                # Handle invalid parameter names
                                if "'$" in str(e) and "is not a valid parameter name" in str(e):
                                    logger.warning(f"✗ Skipping {tool_name} due to invalid parameter: {e}")
                                else:
                                    logger.warning(f"✗ Failed to load {tool_name}: {e}")
                            except Exception as e:
                                logger.warning(f"✗ Failed to load {tool_name}: {e}")
                                # This is OK - some tools might not exist for this integration
                
                composio_tools = all_tools
                logger.info(f"Total tools loaded: {len(composio_tools)} for toolkits: {self.active_apps}")
                
                # Log tool names for debugging
                if composio_tools:
                    tool_names = []
                    for tool in composio_tools:
                        # LangChain tools have a 'name' attribute
                        if hasattr(tool, 'name'):
                            tool_names.append(tool.name)
                        elif isinstance(tool, dict):
                            func_info = tool.get('function', {})
                            tool_names.append(func_info.get('name', 'unknown'))
                    
                    # Log summary by category
                    get_tools = [n for n in tool_names if 'GET' in n or 'LIST' in n or 'RETRIEVE' in n or 'FETCH' in n or 'SEARCH' in n or 'QUERY' in n]
                    create_tools = [n for n in tool_names if 'CREATE' in n or 'ADD' in n]
                    logger.info(f"Tool summary: {len(get_tools)} GET/LIST/READ, {len(create_tools)} CREATE/ADD, {len(tool_names)} total")
                    logger.info(f"Sample tools: {', '.join(tool_names[:10])}...")
                    
            except Exception as e:
                logger.error(f"Failed to get Composio tools: {e}")
                import traceback
                logger.error(traceback.format_exc())
                composio_tools = []
        
        # Add custom auth management tools
        from langchain.tools import tool

        @tool
        def generate_auth_link(app_name: str) -> str:
            """Get the authentication link to connect a new tool/app (like google, github, etc) and enable it.
            
            IMPORTANT: This tool checks if the user is already connected first.
            If already connected, it returns a message saying so instead of generating a new link.
            
            After the user connects, the tools for that app will be automatically loaded.
            """
            # Check if already connected
            if self.check_connection(app_name):
                # Already connected - make sure tools are loaded
                self.add_apps([app_name])
                return f"[OK] {app_name.upper()} is already connected! The user can start using it right away. No authentication needed."
            
            # Generate auth URL only if not connected
            url = self.get_auth_url(app_name)
            
            if url is None:
                return f"[OK] {app_name.upper()} is already connected!"
            
            # Don't add apps yet - wait until they actually connect
            return f"To connect {app_name.upper()}, please use this authentication link: {url}"
        
        @tool
        def check_app_connection(app_name: str) -> str:
            """Check if the user has an active connection to a specific app/tool.
            
            Use this tool when the user asks about their connection status or wants to know
            if they're connected to an app before trying to use it.
            
            Returns a message indicating whether the user is connected or not.
            """
            is_connected = self.check_connection(app_name)
            
            if is_connected:
                return f"[OK] {app_name.upper()} is connected and ready to use! The user can ask questions or perform actions with this app."
            else:
                return f"[NOT CONNECTED] {app_name.upper()} is not connected. The user needs to authenticate first using the generate_auth_link tool."
        
        # Add autonomous execution tools if available
        autonomous_tools = []
        if self.executor:
            @tool
            def execute_shell_command(command: str, working_directory: str = None) -> str:
                """Execute a shell command on the user's computer.
                
                This enables AUTONOMOUS ACTION - the agent can actually DO things, not just talk about them.
                
                Examples:
                - "Create a new folder": execute_shell_command("mkdir my_folder")
                - "List files": execute_shell_command("ls" or "dir")
                - "Check disk space": execute_shell_command("df -h" or "dir")
                
                IMPORTANT: Dangerous commands (rm, del, format, etc.) require explicit user approval.
                
                Args:
                    command: Shell command to execute
                    working_directory: Optional working directory
                    
                Returns:
                    Command output or error message
                """
                result = self.executor.execute_shell_command(command, cwd=working_directory)
                
                if result.get("requires_approval"):
                    return f"⚠️ This command requires user approval: {command}\n\nReason: {result['error']}"
                
                if result["success"]:
                    output = result["stdout"].strip()
                    return f"✅ Command executed successfully:\n{output}" if output else "✅ Command executed successfully (no output)"
                else:
                    error = result.get("stderr") or result.get("error")
                    return f"❌ Command failed:\n{error}"
            
            @tool
            def read_local_file(file_path: str) -> str:
                """Read a file from the user's computer.
                
                This enables the agent to access local files and help with file-based tasks.
                
                Examples:
                - "Read my notes": read_local_file("~/notes.txt")
                - "Check config": read_local_file("config.json")
                
                Args:
                    file_path: Path to the file to read
                    
                Returns:
                    File content or error message
                """
                result = self.executor.read_file(file_path)
                
                if result["success"]:
                    content = result["content"]
                    size = result["size"]
                    return f"✅ File read successfully ({size} chars):\n\n{content}"
                else:
                    return f"❌ Failed to read file: {result['error']}"
            
            @tool
            def list_local_directory(directory_path: str = ".") -> str:
                """List contents of a directory on the user's computer.
                
                This helps the agent understand the user's file system and provide better assistance.
                
                Examples:
                - "What files are here?": list_local_directory(".")
                - "Show my documents": list_local_directory("~/Documents")
                
                Args:
                    directory_path: Path to directory (default: current directory)
                    
                Returns:
                    List of files and folders
                """
                result = self.executor.list_directory(directory_path)
                
                if result["success"]:
                    files = result["files"]
                    count = result["count"]
                    
                    file_list = []
                    for f in files:
                        icon = "📁" if f["type"] == "dir" else "📄"
                        size = f" ({f['size']} bytes)" if f["size"] else ""
                        file_list.append(f"{icon} {f['name']}{size}")
                    
                    return f"✅ Found {count} items in {result['path']}:\n\n" + "\n".join(file_list)
                else:
                    return f"❌ Failed to list directory: {result['error']}"
            
            @tool
            def execute_autonomous_workflow(workflow_description: str) -> str:
                """Execute a multi-step workflow autonomously.
                
                This is the MOST POWERFUL tool - it enables the agent to execute complex tasks
                with multiple steps, just like Moltbot.
                
                Examples:
                - "Create a project structure"
                - "Backup my files"
                - "Set up a development environment"
                
                The agent will break down the task into steps and execute them autonomously.
                
                Args:
                    workflow_description: Description of what to do
                    
                Returns:
                    Workflow execution results
                """
                # This is a placeholder - in production, you'd use the AI to generate the workflow
                return f"🤖 Autonomous workflow initiated: {workflow_description}\n\nNote: This requires the AI to generate and execute the workflow steps. Use execute_shell_command for individual commands."
            
            autonomous_tools = [
                execute_shell_command,
                read_local_file,
                list_local_directory,
                execute_autonomous_workflow
            ]
            
            logger.info(f"✅ Added {len(autonomous_tools)} autonomous execution tools")

        # Combine Composio tools (OpenAI format dicts) with custom LangChain tools
        # create_agent() accepts both formats
        all_tools = composio_tools + [generate_auth_link, check_app_connection] + autonomous_tools
        
        logger.info(f"Total tools for agent: {len(all_tools)} ({len(composio_tools)} Composio + {2 + len(autonomous_tools)} custom)")

        # Build dynamic system prompt based on connected apps
        connected_apps_list = ", ".join(self.active_apps) if self.active_apps else "none"
        
        # Check if web browsing is available
        has_browser = any(app.upper() in ['ANCHOR_BROWSER', 'ANCHORBROWSER'] for app in self.active_apps)
        
        # Check if autonomous execution is available
        has_executor = self.executor is not None
        
        autonomous_capabilities = ""
        if has_executor:
            autonomous_capabilities = """
🤖 AUTONOMOUS EXECUTION: You can ACTUALLY DO THINGS, not just talk about them!

You have these powerful capabilities:
- execute_shell_command: Run commands on the user's computer (ls, mkdir, etc.)
- read_local_file: Read files from the user's file system
- list_local_directory: Browse the user's directories
- execute_autonomous_workflow: Execute multi-step tasks autonomously

IMPORTANT: You're not just a chatbot - you're an AUTONOMOUS AGENT that can:
✅ Create files and folders
✅ Run scripts and programs
✅ Read and analyze local files
✅ Execute complex multi-step workflows
✅ Actually complete tasks, not just suggest them

Example: If user says "create a folder called projects", you should:
1. Use execute_shell_command("mkdir projects")
2. Confirm it was created
3. Tell the user it's done

You're like Moltbot - you DO things, not just talk about them!"""
        else:
            autonomous_capabilities = """
LOCAL EXECUTION: You do NOT have local execution capabilities. You can only work with cloud-based tools through Composio. If the user asks you to run commands or access local files, explain that you need the Autonomous Executor enabled."""
        
        browser_capabilities = ""
        if has_browser:
            browser_capabilities = """
WEB BROWSING: You HAVE web browsing capabilities through Anchor Browser! You can:
- Visit any URL and extract content
- Search the web for information
- Take screenshots of websites
- Interact with web pages
- Navigate and explore websites

Use ANCHOR_BROWSER_PERFORM_WEB_TASK to browse the web and complete web-based tasks."""
        else:
            browser_capabilities = """
WEB BROWSING: You do NOT have web browsing capabilities. If the user asks you to browse the web, visit URLs, or search the internet, politely explain that you don't have that capability and suggest they connect Anchor Browser using the generate_auth_link tool."""
        
        # Check if image generation is available
        image_capabilities = ""
        if self.image_model:
            image_capabilities = f"""
🎨 IMAGE GENERATION: You CAN generate images! You have access to the {self.image_model} model.

When users ask you to:
- "Generate an image of..."
- "Create a picture of..."
- "Make an image of..."
- "Draw..."
- "Show me a picture of..."

You should IMMEDIATELY generate the image for them. Don't say you can't - you absolutely CAN!

IMPORTANT: When a user asks for an image, you must:
1. Acknowledge their request
2. Generate the image using your image generation capability
3. Send them the generated image

Examples of what you CAN do:
✅ "Generate an image of a sunset over mountains"
✅ "Create a picture of a modern house by the beach"
✅ "Make an image of a futuristic city"
✅ "Draw a cute cat"
✅ "Show me a picture of a luxury car"

Never say "I cannot generate images" - you absolutely CAN and SHOULD generate images when asked!"""
        else:
            image_capabilities = """
IMAGE GENERATION: You do NOT have image generation capabilities. If users ask you to generate images, politely explain that you don't have that capability."""
        
        system_prompt = f"""You are a powerful AI assistant that can ACTUALLY DO THINGS, not just talk about them.

{autonomous_capabilities}

CONNECTED APPS: {connected_apps_list}

{image_capabilities}

IMPORTANT - You can ONLY use tools from the apps listed above. Do NOT claim to have capabilities you don't have.

When the user asks you to perform actions:
1. Check if you have the appropriate tool available from your CONNECTED APPS
2. If the app is connected, use the tool directly to complete the task
3. If you need to connect to an app first, use generate_auth_link
4. Always check if the user is connected using check_app_connection before attempting actions

TOOL SELECTION GUIDELINES:
- Google Docs (GOOGLEDOCS): For creating/editing TEXT DOCUMENTS, reports, letters, articles
- Google Sheets (GOOGLESHEETS): For creating/editing SPREADSHEETS, tables with calculations, data analysis
- Google Drive (GOOGLEDRIVE): For file management, uploading, downloading, organizing files
- Gmail (GMAIL): For email management, sending/reading emails
- Google Calendar (GOOGLECALENDAR): For calendar events and scheduling
- Asana (ASANA): For task and project management
- Anchor Browser (ANCHOR_BROWSER): For web browsing, visiting URLs, searching the web, taking screenshots
- When user says "docs" or "document", use GOOGLEDOCS tools
- When user says "sheets" or "spreadsheet", use GOOGLESHEETS tools
- Never confuse Docs with Sheets - they are completely different applications!

{browser_capabilities}

Be helpful and provide clear responses about what you're doing."""

        # Create Agent using langchain's create_agent
        # This accepts both OpenAI function calling format (dicts) and LangChain tools
        try:
            self.agent_executor = agents.create_agent(
                model=self.llm,
                tools=all_tools,
                system_prompt=system_prompt,
                debug=True,
            )
            logger.info("Kernel (Re)Initialized Successfully")
        except Exception as e:
            logger.error(f"Failed to create agent: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.agent_executor = None

    @property
    def active_toolkits(self) -> list:
        """Alias for active_apps to maintain API compatibility."""
        return self.active_apps

    def list_toolkits(self, limit: int = 100) -> list:
        """List all available toolkits from Composio."""
        if not self.composio_client:
            self.setup()
            if not self.composio_client:
                return []

        try:
            # Use the toolkits API to get available toolkits
            toolkits_result = self.composio_client.toolkits.list()
            toolkit_slugs = [t.slug.upper() for t in toolkits_result.items[:limit]]
            return toolkit_slugs
        except Exception as e:
            logger.error(f"Failed to list toolkits: {e}")
            # Fallback: return common toolkit names
            return ["GMAIL", "GITHUB", "SLACK", "GOOGLECALENDAR", "GOOGLEDRIVE", "NOTION", "TWITTER", "LINKEDIN"]

    def add_apps(self, new_apps: list):
        """Dynamically add new apps to the agent."""
        logger.info(f"Request to add apps: {new_apps}")
        self.setup(apps=new_apps)

    def run(self, goal: str):
        """
        The Core Loop: Perception -> Reasoning -> Action
        Enhanced with Mem0 intelligent memory for context-aware responses.
        """
        if not self.agent_executor:
            # Try lazy init
            self.setup()
            if not self.agent_executor:
                return "Agent Kernel not initialized."

        # Load relevant context from Mem0
        context = ""
        if self.memory:
            try:
                context = self.memory.get_context(self.user_id, goal, limit=5)
                if context and context != "No previous context available.":
                    logger.info(f"🧠 Loaded context from Mem0: {len(context)} chars")
                else:
                    context = ""
            except Exception as e:
                logger.warning(f"Failed to load Mem0 context: {e}")
                context = ""
        
        # Inject context into the goal if available
        if context:
            enhanced_goal = f"{context}\n\nCurrent Query: {goal}"
        else:
            enhanced_goal = goal

        try:
            logger.info(f"Reasoning on goal: {goal}")
            result = self.agent_executor.invoke(
                {"messages": [{"role": "user", "content": enhanced_goal}]}
            )
            
            # Debug: Log the full result structure
            logger.info(f"Result type: {type(result)}")
            logger.info(f"Result keys: {result.keys() if isinstance(result, dict) else 'N/A'}")
            
            # Handle various response structures
            messages = result.get("messages", [])
            logger.info(f"Messages count: {len(messages)}")
            
            if messages:
                last_message = messages[-1]
                logger.info(f"Last message type: {type(last_message)}")
                logger.info(f"Last message dir: {[attr for attr in dir(last_message) if not attr.startswith('_')]}")
                
                # Extract content from message
                content = self._extract_content(last_message)
                
                # Save conversation to Mem0
                if self.memory and content:
                    try:
                        self.memory.add_conversation(self.user_id, [
                            {"role": "user", "content": goal},
                            {"role": "assistant", "content": content}
                        ])
                        logger.info("💾 Saved conversation to Mem0")
                    except Exception as e:
                        logger.warning(f"Failed to save to Mem0: {e}")
                
                logger.info(f"Final response: {content[:200] if content else 'Empty'}...")
                return content
            
            logger.warning("No messages in result")
            return ""
            
        except Exception as e:
            logger.error(f"Kernel Error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return f"Error executing goal: {e}"
    
    def _extract_content(self, message):
        """Extract content from various message formats"""
        # Approach 1: Direct content attribute
        if hasattr(message, 'content'):
            content = message.content
            logger.info(f"Content from .content: {type(content)}")
        
        # Approach 2: Dictionary access
        elif isinstance(message, dict):
            content = message.get('content')
            logger.info(f"Content from dict: {type(content)}")
        
        # Approach 3: text attribute (for some message types)
        elif hasattr(message, 'text'):
            content = message.text
            logger.info(f"Content from .text: {type(content)}")
        
        # Approach 4: Just convert to string
        else:
            content = str(message)
            logger.info(f"Content from str(): {type(content)}")
        
        # Handle None content
        if content is None:
            logger.warning("Message content is None")
            return ""
        
        # Handle complex content types (like GeneratedModel, AIMessage, etc.)
        logger.info(f"Final content type: {type(content)}")
        
        # If it's a list, extract text from each item
        if isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, str):
                    text_parts.append(item)
                elif hasattr(item, 'text'):
                    text_parts.append(item.text)
                elif hasattr(item, 'content'):
                    text_parts.append(str(item.content))
                else:
                    text_parts.append(str(item))
            content = ' '.join(text_parts)
            logger.info(f"Extracted from list: {content[:100]}...")
        
        # If it's still not a string, try various conversion methods
        if not isinstance(content, str):
            # Try to access common attributes for generated models
            if hasattr(content, 'text'):
                content = content.text
            elif hasattr(content, 'generated_text'):
                content = content.generated_text
            elif hasattr(content, 'content'):
                content = content.content
            elif hasattr(content, '__str__'):
                content = str(content)
            else:
                # Last resort
                content = repr(content)
            
            logger.info(f"Converted to string: {type(content)}")
        
        # Final safety check
        if not isinstance(content, str):
            logger.error(f"Content is still not a string: {type(content)}")
            content = str(content)
        
        return content

    def run_with_vision(
        self, image_bytes: bytes, prompt: str, mime_type: str = "image/jpeg"
    ):
        """Analyze an image using the vision model (OpenRouter format)."""
        logger.info(
            f"👁️ Running vision on {len(image_bytes)} bytes, prompt: {prompt[:50]}..."
        )

        if not self.openai_client:
            logger.error("Vision model not configured - no openai_client")
            return "Vision model not configured."

        if not self.vision_model:
            logger.error("No VISION_MODEL set in environment")
            return "Vision model not configured."

        try:
            b64 = base64.b64encode(image_bytes).decode("ascii")

            # Detect MIME type from bytes if not provided
            if image_bytes[:8] == b"\x89PNG\r\n\x1a\n":
                mime_type = "image/png"
            elif image_bytes[:3] == b"\xff\xd8\xff":
                mime_type = "image/jpeg"
            elif image_bytes[:4] == b"RIFF" and image_bytes[8:12] == b"WEBP":
                mime_type = "image/webp"
            elif image_bytes[:6] in (b"GIF87a", b"GIF89a"):
                mime_type = "image/gif"

            logger.info(
                f"👁️ Using model: {self.vision_model}, mime: {mime_type}, b64 length: {len(b64)}"
            )

            # OpenRouter multimodal format - text first, then image
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime_type};base64,{b64}"},
                        },
                    ],
                }
            ]

            result = self.openai_client.chat.completions.create(
                model=self.vision_model,
                messages=cast(Any, messages),
                temperature=0.2,
            )
            content = result.choices[0].message.content
            logger.info(
                f"👁️ Vision success! Response length: {len(content) if content else 0}"
            )
            return content.strip() if content else ""
        except Exception as e:
            logger.error(f"Vision Error: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return f"Vision error: {e}"

    def run_with_pdf(
        self, pdf_bytes: bytes, prompt: str, filename: str = "document.pdf"
    ):
        """
        Process a PDF using OpenRouter's file-parser plugin.
        Uses pdf-text (free) or mistral-ocr ($2/1000 pages) for scanned docs.
        """
        logger.info(
            f"📄 Running PDF analysis on {len(pdf_bytes)} bytes, prompt: {prompt[:50]}..."
        )

        if not self.openai_client:
            logger.error("AI client not configured")
            return "AI processing not available."

        try:
            b64 = base64.b64encode(pdf_bytes).decode("ascii")
            data_url = f"data:application/pdf;base64,{b64}"

            logger.info(f"📄 Using model: {self.model}, filename: {filename}")

            # OpenRouter PDF format with file-parser plugin
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "file",
                            "file": {
                                "filename": filename,
                                "file_data": data_url,
                            },
                        },
                    ],
                }
            ]

            # Use pdf-text engine (free) - change to mistral-ocr for scanned docs
            result = self.openai_client.chat.completions.create(
                model=self.model,
                messages=cast(Any, messages),
                temperature=0.2,
                extra_body={
                    "plugins": [
                        {
                            "id": "file-parser",
                            "pdf": {
                                "engine": "pdf-text"
                            },  # Free! Use "mistral-ocr" for scanned docs
                        }
                    ]
                },
            )

            content = result.choices[0].message.content
            logger.info(
                f"📄 PDF analysis success! Response length: {len(content) if content else 0}"
            )
            return content.strip() if content else ""

        except Exception as e:
            logger.error(f"PDF Analysis Error: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return f"PDF analysis error: {e}"

    def _decode_data_url(self, data_url: str) -> Optional[bytes]:
        if not data_url or "," not in data_url:
            return None
        header, b64_data = data_url.split(",", 1)
        if "base64" not in header:
            return None
        try:
            return base64.b64decode(b64_data)
        except Exception as e:
            logger.error(f"Data URL decode error: {e}")
            return None

    def generate_image(
        self,
        prompt: str,
        size: Literal[
            "auto",
            "1024x1024",
            "1536x1024",
            "1024x1536",
            "256x256",
            "512x512",
            "1792x1024",
            "1024x1792",
        ] = "1024x1024",
    ):
        """Generate an image from text prompt using available image model."""
        logger.info(f"🎨 Generating image with prompt: {prompt[:50]}...")

        if not self.image_model:
            logger.warning("No IMAGE_MODEL configured")
            return None

        if not self.api_key:
            logger.warning("No API key configured")
            return None

        try:
            # OpenRouter image generation using chat completions endpoint with modalities
            # CRITICAL: modalities: ["image", "text"] is REQUIRED for image output
            # Based on official OpenRouter SDK: https://openrouter.ai/docs/frameworks/javascript
            import requests
            
            logger.info(f"📤 Sending request to OpenRouter...")
            logger.info(f"   Model: {self.image_model}")
            logger.info(f"   Prompt: {prompt[:100]}...")
            
            # Use raw HTTP request because OpenAI SDK doesn't properly support modalities parameter
            # The modalities parameter MUST be at the root level of the JSON payload
            payload = {
                "model": self.image_model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "modalities": ["image", "text"],  # CRITICAL: Must be at root level
                "max_tokens": 4096
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/Hammton/AI-employee",  # Optional but recommended
                "X-Title": "PocketAgent"  # Optional but recommended
            }
            
            logger.info(f"📤 Request payload keys: {payload.keys()}")
            logger.info(f"📤 Modalities: {payload['modalities']}")
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            logger.info(f"📥 Response status: {response.status_code}")
            
            if not response.ok:
                logger.error(f"❌ OpenRouter API returned {response.status_code}")
                logger.error(f"❌ Response text: {response.text[:500]}")
                return None
            
            result = response.json()
            logger.info(f"📥 Response JSON keys: {result.keys()}")
            
            # Extract message from response
            message = result["choices"][0]["message"]
            logger.info(f"📥 Message keys: {message.keys()}")
            
            # Check for images in response (OpenRouter format)
            # According to OpenRouter SDK: message.images[].image_url.url contains data URL
            images = message.get("images")
            if images:
                logger.info(f"✅ Found {len(images)} image(s) in response")
                for i, img in enumerate(images):
                    logger.info(f"   Image {i}: {type(img)}")
                    if isinstance(img, dict):
                        # OpenRouter format: image.image_url.url
                        image_url_obj = img.get("image_url", {})
                        if isinstance(image_url_obj, dict):
                            url = image_url_obj.get("url")
                            if url:
                                logger.info(f"   Found data URL: {url[:50]}...")
                                return self._decode_data_url(url)
                        # Alternative format: direct url
                        url = img.get("url")
                        if url:
                            logger.info(f"   Found direct URL: {url[:50]}...")
                            return self._decode_data_url(url)
                    elif isinstance(img, str) and img.startswith("data:image"):
                        logger.info(f"   Found string data URL: {img[:50]}...")
                        return self._decode_data_url(img)
            
            # If no images found, log the full response for debugging
            logger.warning("❌ No images found in response")
            logger.warning(f"   Full message: {message}")
            return None

        except Exception as e:
            logger.error(f"Image Generation Error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    def generate_speech(
        self,
        text: str,
        audio_format: Literal["mp3", "opus", "aac", "flac", "wav", "pcm"] = "mp3",
    ):
        if not self.openai_client or not self.tts_model:
            return None
        try:
            response = self.openai_client.audio.speech.create(
                model=self.tts_model,
                voice=self.tts_voice,
                input=text,
                response_format=cast(Any, audio_format),
            )
            if hasattr(response, "read"):
                return response.read()
            if hasattr(response, "content"):
                return response.content
            return None
        except Exception as e:
            logger.error(f"TTS Error: {e}")
            return None

    def extract_document_text(
        self,
        file_bytes: bytes,
        filename: str = "",
        mime_type: str = "",
        max_chars: int = 6000,
    ):
        """Extract text from documents (PDF, DOCX, TXT, etc.)"""
        if not file_bytes:
            logger.warning("extract_document_text called with empty bytes")
            return ""

        name = (filename or "").lower()
        mime = (mime_type or "").lower()
        text = ""

        logger.info(f"📄 Extracting text from: {filename} (mime: {mime})")

        try:
            if name.endswith(".pdf") or mime == "application/pdf":
                logger.info("📄 Detected PDF, using pypdf...")
                from pypdf import PdfReader

                reader = PdfReader(io.BytesIO(file_bytes))
                parts = []
                for page in reader.pages:
                    page_text = page.extract_text() or ""
                    if page_text:
                        parts.append(page_text)
                    if sum(len(p) for p in parts) >= max_chars:
                        break
                text = "\n".join(parts)
                logger.info(
                    f"📄 PDF extraction: {len(text)} chars from {len(reader.pages)} pages"
                )

            elif name.endswith(".docx") or mime in (
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "application/msword",
            ):
                logger.info("📄 Detected DOCX, using python-docx...")
                from docx import Document

                doc = Document(io.BytesIO(file_bytes))
                parts = [p.text for p in doc.paragraphs if p.text]
                text = "\n".join(parts)
                logger.info(
                    f"📄 DOCX extraction: {len(text)} chars from {len(parts)} paragraphs"
                )

            else:
                logger.info(f"📄 Attempting plain text decode for {mime}...")
                text = file_bytes.decode("utf-8", errors="ignore")
                logger.info(f"📄 Plain text decode: {len(text)} chars")

        except Exception as e:
            logger.error(f"Document Parse Error: {e}")
            import traceback

            logger.error(traceback.format_exc())
            text = ""

        if len(text) > max_chars:
            text = text[:max_chars]
            logger.info(f"📄 Truncated to {max_chars} chars")

        return text.strip()

    def transcribe_audio(self, audio_bytes: bytes, filename: str = "voice.ogg"):
        if not self.openai_client:
            return ""
        try:
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = filename
            result = self.openai_client.audio.transcriptions.create(
                model=self.audio_model,
                file=audio_file,
            )
            return (result.text or "").strip()
        except Exception as e:
            logger.error(f"Transcription Error: {e}")
            return ""

    def check_connection(self, app_name: str) -> bool:
        """Check if user has an active connection for the given app.
        
        Uses connected_accounts.list() to check for ACTIVE connections.
        This is more reliable than session.toolkits() which may not show active status correctly.
        
        Handles common name variations:
        - "google_mail", "googlemail", "Google Mail" -> "gmail"
        - "google_calendar", "googlecalendar" -> "googlecalendar"
        - "google_sheets", "googlesheets" -> "googlesheets"
        
        Args:
            app_name: Name of the app/toolkit (e.g., "asana", "gmail", "google_mail")
            
        Returns:
            True if connected, False otherwise
        """
        if not self.composio_client:
            self.setup()
            if not self.composio_client:
                return False
        
        # Normalize the app name
        slug = app_name.lower().replace(" ", "").replace("_", "")
        
        # Map common variations to actual Composio toolkit slugs
        slug_mappings = {
            'googlemail': 'gmail',  # google_mail -> gmail
            'googlemaps': 'googlemaps',
            'googlecalendar': 'googlecalendar',
            'googlesheets': 'googlesheets',
            'googledrive': 'googledrive',
            'googlecontacts': 'googlecontacts',
            'googledocs': 'googledocs',
            'googleslides': 'googleslides',
            'anchorbrowser': 'anchor_browser',  # anchorbrowser -> anchor_browser
            'browser': 'anchor_browser',  # browser -> anchor_browser
        }
        
        # Apply mapping if exists
        actual_slug = slug_mappings.get(slug, slug)
        
        try:
            # ✅ RELIABLE METHOD: Use connected_accounts.list() with user_id filter
            connected_accounts = self.composio_client.connected_accounts.list(
                user_ids=[self.user_id]
            )
            
            # Check if any account matches this app and is ACTIVE
            for account in connected_accounts.items:
                if account.status == "ACTIVE":
                    # Check toolkit slug
                    if hasattr(account, 'toolkit') and account.toolkit:
                        toolkit_slug = getattr(account.toolkit, 'slug', '').lower()
                        # Check both the actual slug and the original slug
                        if toolkit_slug == actual_slug or toolkit_slug == slug:
                            logger.info(f"✅ User {self.user_id} has ACTIVE connection for {actual_slug} (toolkit: {toolkit_slug}, account: {account.id})")
                            return True
            
            logger.info(f"❌ User {self.user_id} has no ACTIVE connection for {actual_slug} (searched: {slug})")
            return False
            
        except Exception as e:
            logger.warning(f"Error checking connection for {actual_slug}: {e}")
            import traceback
            logger.warning(traceback.format_exc())
            return False
    
    def get_auth_url(self, app_name: str, force: bool = False):
        """Generates connection URL for a toolkit using session.authorize().
        
        Official Composio pattern from docs:
        connection_request = session.authorize("github")
        return connection_request.redirect_url
        
        Handles common name variations:
        - "google_mail", "googlemail", "Google Mail" -> "gmail"
        - "google_calendar", "googlecalendar" -> "googlecalendar"
        
        Args:
            app_name: Name of the app/toolkit
            force: If True, generate new auth URL even if already connected
        """
        if not self.composio_session:
            self.setup()  # Ensure session is created
            if not self.composio_session:
                raise RuntimeError("Composio session is not available.")

        # Clean up app name to be a valid toolkit slug
        # e.g. "Google Calendar" -> "googlecalendar", "Gmail" -> "gmail"
        slug = app_name.lower().replace(" ", "").replace("_", "")
        
        # Map common variations to actual Composio toolkit slugs
        slug_mappings = {
            'googlemail': 'gmail',  # google_mail -> gmail
            'googlemaps': 'googlemaps',
            'googlecalendar': 'googlecalendar',
            'googlesheets': 'googlesheets',
            'googledrive': 'googledrive',
            'googlecontacts': 'googlecontacts',
            'googledocs': 'googledocs',
            'googleslides': 'googleslides',
            'anchorbrowser': 'anchor_browser',  # anchorbrowser -> anchor_browser
            'browser': 'anchor_browser',  # browser -> anchor_browser
        }
        
        # Apply mapping if exists
        actual_slug = slug_mappings.get(slug, slug)
        
        # Check if already connected (unless force=True)
        if not force and self.check_connection(actual_slug):
            logger.info(f"User {self.user_id} already connected to {actual_slug}")
            return None  # Return None to indicate already connected
        
        try:
            # ✅ OFFICIAL PATTERN: Use session.authorize() 
            # This handles everything: checking existing connections, creating auth URLs, etc.
            logger.info(f"Authorizing toolkit '{actual_slug}' for user '{self.user_id}'")
            connection_request = self.composio_session.authorize(actual_slug)
            
            # Extract redirect URL from connection request
            if hasattr(connection_request, 'redirect_url'):
                auth_url = connection_request.redirect_url
            elif hasattr(connection_request, 'redirectUrl'):
                auth_url = connection_request.redirectUrl
            elif hasattr(connection_request, 'url'):
                auth_url = connection_request.url
            else:
                # Fallback: convert to string
                auth_url = str(connection_request)
                
            logger.info(f"✅ Generated auth URL for {actual_slug}: {auth_url[:100]}...")
            return auth_url
            
        except Exception as e:
            logger.error(f"Authorization failed for {actual_slug}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Fallback URL
            return f"https://app.composio.dev/app/{actual_slug}?entity_id={self.user_id}"

