"""
PocketAgent - AI-Powered WhatsApp Assistant

This is a refactored version that uses WPPConnect (Node.js) for WhatsApp communication
instead of raw Playwright + wa-js injection. The architecture is:

    WhatsApp Web <--> WPP Bridge (Node.js) <--> PocketAgent (Python/FastAPI)

Benefits:
- No CSP blocking issues
- Proper session persistence
- Stable API that doesn't break with WhatsApp updates
- Rich event system for messages, read receipts, etc.
"""

import asyncio
import os
import base64
import httpx
import tempfile
import re
from typing import Any, Optional
from dotenv import load_dotenv

load_dotenv()

import logging
import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, Response, HTTPException, Request
from pydantic import BaseModel
import uvicorn

# Import our Kernel
from kernel import AgentKernel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PocketAgent")

# --- Configuration ---
PORT = int(os.environ.get("PORT", 8000))
USER_PHONE = os.environ.get("USER_PHONE")
WPP_BRIDGE_URL = os.environ.get("WPP_BRIDGE_URL", "http://localhost:3001")
ENABLE_SCHEDULER = os.environ.get("ENABLE_SCHEDULER", "false").lower() == "true"

# Per-user kernel management (each WhatsApp user gets their own session)
user_kernels = {}  # phone_number/chat_id -> AgentKernel

def get_kernel_for_user(user_id: str) -> AgentKernel:
    """Get or create a kernel instance for a specific user."""
    if user_id not in user_kernels:
        logger.info(f"🔧 Creating new kernel for user: {user_id}")
        user_kernels[user_id] = AgentKernel(user_id=user_id)
        # Initialize with common apps pre-loaded
        user_kernels[user_id].setup(apps=["gmail", "googlecalendar", "googlesheets", "notion", "anchor_browser"])
    return user_kernels[user_id]

# Default kernel for backward compatibility (scheduler, etc.)
agent_kernel = AgentKernel()
# Initialize with common apps pre-loaded
agent_kernel.setup(apps=["gmail", "googlecalendar", "googlesheets", "notion", "anchor_browser"])

# HTTP client for WPP Bridge
http_client: Optional[httpx.AsyncClient] = None

# Message tracking
processed_messages = set()


# --- Pydantic Models ---
class IncomingMessage(BaseModel):
    id: str
    from_: str = ""  # 'from' is reserved keyword, will be aliased
    to: Optional[str] = None
    body: Optional[str] = ""
    type: Optional[str] = "chat"
    isGroupMsg: Optional[bool] = False
    sender: Optional[dict] = None
    timestamp: Optional[int] = None
    hasMedia: Optional[bool] = False
    mediaType: Optional[str] = None
    mediaBase64: Optional[str] = None
    mediaMimetype: Optional[str] = None
    mediaFilename: Optional[str] = None

    class Config:
        populate_by_name = True
        extra = "allow"


class SendTextRequest(BaseModel):
    to: str
    message: str


class SendImageRequest(BaseModel):
    to: str
    base64: str
    caption: Optional[str] = None
    filename: Optional[str] = None


# --- WPP Bridge Client ---
async def wpp_send_text(to: str, message: str) -> bool:
    """Send text message via WPP Bridge."""
    if not http_client:
        return False
    try:
        response = await http_client.post(
            f"{WPP_BRIDGE_URL}/send/text",
            json={"to": to, "message": message},
            timeout=30.0,
        )
        return response.status_code == 200
    except Exception as e:
        logger.error(f"WPP send_text failed: {e}")
        return False


async def wpp_send_image(
    to: str, image_base64: str, caption: str = "", filename: str = "image.png"
) -> bool:
    """Send image via WPP Bridge."""
    if not http_client:
        return False
    try:
        response = await http_client.post(
            f"{WPP_BRIDGE_URL}/send/image",
            json={
                "to": to,
                "base64": image_base64,
                "caption": caption,
                "filename": filename,
            },
            timeout=60.0,
        )
        return response.status_code == 200
    except Exception as e:
        logger.error(f"WPP send_image failed: {e}")
        return False


async def wpp_send_file(
    to: str, file_base64: str, filename: str, caption: str = "", mimetype: str = ""
) -> bool:
    """Send file via WPP Bridge."""
    if not http_client:
        return False
    try:
        response = await http_client.post(
            f"{WPP_BRIDGE_URL}/send/file",
            json={
                "to": to,
                "base64": file_base64,
                "filename": filename,
                "caption": caption,
                "mimetype": mimetype,
            },
            timeout=60.0,
        )
        return response.status_code == 200
    except Exception as e:
        logger.error(f"WPP send_file failed: {e}")
        return False


async def wpp_start_typing(chat_id: str) -> bool:
    """Start typing indicator."""
    if not http_client:
        return False
    try:
        response = await http_client.post(
            f"{WPP_BRIDGE_URL}/typing/start",
            json={"chatId": chat_id},
            timeout=10.0,
        )
        return response.status_code == 200
    except:
        return False


async def wpp_stop_typing(chat_id: str) -> bool:
    """Stop typing indicator."""
    if not http_client:
        return False
    try:
        response = await http_client.post(
            f"{WPP_BRIDGE_URL}/typing/stop",
            json={"chatId": chat_id},
            timeout=10.0,
        )
        return response.status_code == 200
    except:
        return False


async def wpp_get_status() -> dict:
    """Get WPP Bridge connection status."""
    if not http_client:
        return {"ready": False, "connected": False}
    try:
        response = await http_client.get(f"{WPP_BRIDGE_URL}/status", timeout=10.0)
        return response.json()
    except:
        return {"ready": False, "connected": False}


# --- Message Processing ---
def _extract_image_prompt(text: str) -> Optional[str]:
    """Extract image generation prompt from message."""
    if not text:
        return None
    trimmed = text.strip()
    if not trimmed:
        return None

    lowered = trimmed.lower()

    # 1. Check for /image command first (highest priority)
    if lowered.startswith("/image") or lowered.startswith("/img"):
        return trimmed.replace("/image", "").replace("/img", "").strip()

    # 2. EXPLICIT image keywords - must have these to be considered image generation
    visual_nouns = ["image", "picture", "photo", "illustration", "art", "drawing", "artwork", "painting", "sketch"]
    has_visual_noun = any(noun in lowered for noun in visual_nouns)
    
    # 3. Check for explicit "image of..." patterns (highest confidence)
    explicit_patterns = [
        "image of", "picture of", "photo of", "illustration of", "art of",
        "drawing of", "painting of", "sketch of"
    ]
    for pattern in explicit_patterns:
        if pattern in lowered:
            logger.info(f"🎨 Detected image request (explicit pattern): {trimmed[:50]}...")
            return trimmed
    
    # 4. Check for "generate/create/make/draw" + explicit visual noun
    # This prevents "create a spreadsheet" from being treated as image generation
    generation_verbs = ["generate", "create", "make", "draw", "render", "design", "produce"]
    
    if has_visual_noun:
        # Only consider it an image request if there's BOTH a verb AND a visual noun
        has_verb = any(verb in lowered for verb in generation_verbs)
        if has_verb:
            logger.info(f"🎨 Detected image request (verb + visual noun): {trimmed[:50]}...")
            return trimmed
    
    # 5. Special case: "draw" at the start is usually for images
    if lowered.startswith("draw "):
        logger.info(f"🎨 Detected image request (starts with 'draw'): {trimmed[:50]}...")
        return trimmed
    
    # 6. Special case: "show me a picture/image" patterns
    show_patterns = ["show me a picture", "show me an image", "show me a photo"]
    if any(pattern in lowered for pattern in show_patterns):
        logger.info(f"🎨 Detected image request (show me pattern): {trimmed[:50]}...")
        return trimmed

    return None


def strip_markdown(text: str) -> str:
    """Strip markdown formatting for cleaner WhatsApp display."""
    if not text:
        return text
    # Remove bold/italic markers
    text = text.replace("**", "").replace("__", "")
    # Remove code blocks but keep content
    text = text.replace("```", "")
    # Remove single backticks
    text = re.sub(r"`([^`]+)`", r"\1", text)
    # Remove headers (# ## ###)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    return text


async def process_message(msg: dict) -> str:
    """
    Process an incoming WhatsApp message and generate a response.
    This is where the magic happens - AI reasoning on the message.
    """
    msg_text = msg.get("body", "") or ""
    msg_type = msg.get("type", "chat")
    has_media = msg.get("hasMedia", False)
    media_base64 = msg.get("mediaBase64")
    media_mimetype = msg.get("mediaMimetype", "")
    sender_name = (
        msg.get("sender", {}).get("name", "User") if msg.get("sender") else "User"
    )
    # Handle both 'from' and 'from_' (aliased in incoming endpoint)
    chat_id = msg.get("from") or msg.get("from_") or ""
    
    # Get user-specific kernel (per-user session isolation)
    user_kernel = get_kernel_for_user(chat_id)

    # Detect if body is actually base64 image data (thumbnail) instead of text
    # JPEG base64 starts with /9j/, PNG base64 starts with iVBOR
    if msg_text and (msg_text.startswith("/9j/") or msg_text.startswith("iVBOR")):
        logger.info(
            f"📎 Detected base64 thumbnail in body, treating as image-only message"
        )
        msg_text = ""  # Clear the fake "text"

    # Detailed logging for debugging
    logger.info(
        f"📩 Processing message from {sender_name}: {msg_text[:50] if msg_text else '[media]'}"
    )
    logger.info(
        f"   Type: {msg_type}, hasMedia: {has_media}, mimetype: {media_mimetype}"
    )
    logger.info(
        f"   Media base64 present: {bool(media_base64)}, length: {len(media_base64) if media_base64 else 0}"
    )

    # Start typing indicator
    await wpp_start_typing(chat_id)

    try:
        # --- Command Handling ---
        text_lower = msg_text.strip().lower() if msg_text else ""

        # /image command
        # /help command
        if text_lower.startswith("/help") or text_lower.startswith("/commands"):
            return """🤖 *PocketAgent Commands*

*🔌 Tool Management (Composio)*
/connect <tool> - Connect a SaaS tool (github, calendar, slack, etc.)
/status <tool> - Check if a tool is connected
/tools - List active tools

*📸 Image Generation*
/image <prompt> - Generate an image from text

*🎙️ Voice*
/voice <text> - Convert text to speech

*📄 Document Analysis*
Send any image, PDF, or document with:
- /extract or /ocr - Extract all text
- Or just describe what you want

*💬 Chat*
Just type naturally and I'll use connected tools!

*Supported file types:*
Images (JPG, PNG, WebP), PDF, DOCX, TXT"""

        # /connect command - Dynamically enable ANY Composio tool (250+ apps)
        if text_lower.startswith("/connect") or text_lower.startswith("/enable"):
            # Popular toolkits for quick reference
            POPULAR_APPS = [
                "github",
                "gmail",
                "googlecalendar",
                "slack",
                "notion",
                "googledrive",
                "googlesheets",
                "googledocs",
                "twitter",
                "linkedin",
                "hubspot",
                "salesforce",
                "jira",
                "asana",
                "linear",
                "trello",
                "airtable",
                "discord",
                "teams",
                "outlook",
                "dropbox",
                "figma",
                "stripe",
                "shopify",
            ]

            app_name = (
                msg_text.split(" ", 1)[1].strip().lower() if " " in msg_text else ""
            )

            # Handle /connect list - show all available toolkits
            if app_name == "list" or app_name == "all":
                all_apps_list = user_kernel.list_toolkits(limit=100)
                if not all_apps_list:
                    return "❌ Could not fetch toolkits. Check COMPOSIO_API_KEY and try again."
                display_list = ", ".join(all_apps_list[:50])
                return f"""📋 *All Available Toolkits ({len(all_apps_list)}+)*

{display_list}...

💡 Type /connect <name> to add any toolkit.
Example: /connect shopify"""

            if not app_name:
                popular = ", ".join(POPULAR_APPS[:15])
                return f"""🔌 *Connect Any Composio Tool (250+ available)*

Usage: /connect <tool_name>

*Popular Tools:*
{popular}

/connect list - See all available tools

Example: /connect github
Example: /connect shopify

💡 First authenticate: `composio add <tool>`"""

            try:
                # Check if already connected
                if user_kernel.check_connection(app_name):
                    # Add the app to active toolkits if not already there
                    user_kernel.add_apps([app_name])
                    current_apps = user_kernel.active_toolkits
                    app_display = app_name.upper()
                    
                    return f"""✅ *{app_display} Already Connected!*

You're all set! Your {app_name} account is already connected and ready to use.

*Active Toolkits:* {", ".join(current_apps)}

Try asking me:
• "What are my {app_name} tasks?"
• "Create a new {app_name} item..."
• "Show my {app_name} status"

💡 Use /tools to see all connected tools"""
                
                # Generate auth Link (only if not connected)
                auth_url = user_kernel.get_auth_url(app_name)
                
                # If auth_url is None, it means already connected (shouldn't happen due to check above, but just in case)
                if auth_url is None:
                    user_kernel.add_apps([app_name])
                    return f"✅ {app_name.upper()} is already connected! Try asking me about your {app_name} data."
                
                # Add the app to the kernel
                user_kernel.add_apps([app_name])
                
                current_apps = user_kernel.active_toolkits
                app_display = app_name.upper()
                
                return f"""✅ *Setup for {app_display} initialized*

🔗 *Action Required:* 
Please authorize the connection using this link:
{auth_url}

*Active Toolkits:* {", ".join(current_apps)}

Once authorized, you can use natural language like:
• "Create a {app_name} item..."
• "Check {app_name} status..." """
            except Exception as e:
                logger.error(f"Failed to connect {app_name}: {e}")
                # Try to provide auth link even on failure
                try:
                    auth_url = user_kernel.get_auth_url(app_name, force=True)
                    if auth_url is None:
                        return f"✅ {app_name.upper()} is already connected!"
                    return f"""⚠️ *Authorization Needed*

Please connect {app_name} using this link:
{auth_url}

After authorizing, try `/connect {app_name}` again."""
                except:
                    return f"❌ Failed to connect {app_name}: {e}"

        # /tools command - List active tools
        if text_lower.startswith("/tools") or text_lower.startswith("/apps"):
            if not user_kernel.active_toolkits:
                return "No tools connected yet.\n\nUse /connect <tool> to add tools."

            current_apps = user_kernel.active_toolkits
            return f"🔧 *Active Toolkits:* {', '.join(current_apps)}\n\nUse /connect <tool> to add more."
        
        # /status command - Check connection status for a specific app
        if text_lower.startswith("/status"):
            app_name = (
                msg_text.split(" ", 1)[1].strip().lower() if " " in msg_text else ""
            )
            
            if not app_name:
                return """📊 *Connection Status*

Usage: /status <app_name>

Example: /status asana
Example: /status gmail

This will check if you have an active connection to the specified app."""
            
            try:
                is_connected = user_kernel.check_connection(app_name)
                app_display = app_name.upper()
                
                if is_connected:
                    return f"""✅ *{app_display} Status: Connected*

Your {app_name} account is connected and ready to use!

Try asking me:
• "What are my {app_name} tasks?"
• "Show my {app_name} data"

💡 Use /tools to see all connected tools"""
                else:
                    return f"""❌ *{app_display} Status: Not Connected*

You haven't connected your {app_name} account yet.

To connect, use: /connect {app_name}

This will generate an authorization link for you."""
            except Exception as e:
                logger.error(f"Status check failed for {app_name}: {e}")
                return f"⚠️ Could not check status for {app_name}. Error: {str(e)[:100]}"

        # /image command
        if text_lower.startswith("/image") or text_lower.startswith("/img"):
            prompt = msg_text.split(" ", 1)[1].strip() if " " in msg_text else ""
            if not prompt:
                return "Usage: /image <prompt>\nExample: /image a futuristic city at sunset"

            logger.info(f"🎨 Image command detected. Prompt: {prompt}")
            image_bytes = user_kernel.generate_image(prompt)

            if image_bytes:
                logger.info(f"✅ Image generated! Size: {len(image_bytes)} bytes")
                b64 = base64.b64encode(image_bytes).decode("ascii")
                success = await wpp_send_image(
                    chat_id, b64, caption="Here you go! 🎨", filename="generated.png"
                )
                logger.info(f"Image send result: {success}")
                return ""  # Empty response since we sent image directly
            else:
                logger.warning("❌ Image generation returned None")
                return "Image generation failed. Please try again."

        # Natural language image request
        image_prompt = _extract_image_prompt(msg_text)
        if image_prompt is not None:
            prompt = image_prompt or msg_text
            logger.info(f"🎨 Natural image request detected. Prompt: {prompt}")
            image_bytes = user_kernel.generate_image(prompt)

            if image_bytes:
                logger.info(f"✅ Image generated! Size: {len(image_bytes)} bytes")
                b64 = base64.b64encode(image_bytes).decode("ascii")
                success = await wpp_send_image(
                    chat_id, b64, caption="Here you go! 🎨", filename="generated.png"
                )
                logger.info(f"Image send result: {success}")
                return ""
            else:
                logger.warning("❌ Image generation returned None")
                return "I couldn't generate that image. Please try a different prompt."

        # /voice command
        if text_lower.startswith("/voice") or text_lower.startswith("/audio"):
            speech_text = msg_text.split(" ", 1)[1].strip() if " " in msg_text else ""
            if not speech_text:
                return "Usage: /voice <text>\nExample: /voice Hello, how are you today?"

            audio_bytes = user_kernel.generate_speech(speech_text)
            if audio_bytes:
                b64 = base64.b64encode(audio_bytes).decode("ascii")
                await wpp_send_file(chat_id, b64, "voice.mp3", mimetype="audio/mpeg")
                return ""
            return "Voice generation failed."

        # /extract command - for explicit text extraction from attached media
        if text_lower.startswith("/extract") or text_lower.startswith("/ocr"):
            if not has_media or not media_base64:
                return "📄 Usage: Send an image or PDF with the caption /extract\n\nI'll extract all text from it using AI vision/OCR."
            # Will be handled in the media section below with OCR-focused prompt

        # --- Media Handling ---
        if has_media and media_base64:
            logger.info(
                f"📎 Media received: type={media_mimetype}, size={len(media_base64)} chars"
            )
            media_bytes = base64.b64decode(media_base64)
            logger.info(f"📎 Decoded media: {len(media_bytes)} bytes")

            # Voice note / audio
            if media_mimetype and media_mimetype.startswith("audio/"):
                logger.info("🎙️ Processing audio/voice note...")
                transcript = user_kernel.transcribe_audio(media_bytes)
                if not transcript:
                    return "I received your voice note but couldn't transcribe it. Please try again."

                prompt = f"User {sender_name} sent a voice note. Transcript:\n{transcript}\n\nReply helpfully and concisely."
                return user_kernel.run(prompt)

            # Image - use vision model
            if media_mimetype and media_mimetype.startswith("image/"):
                logger.info(f"🖼️ Processing image with vision model...")
                caption = f"Caption: {msg_text}\n" if msg_text else ""

                # If user asks to extract text, focus on OCR
                text_lower = (msg_text or "").lower()

                # Check if user wants to GENERATE a new image based on this one
                is_generate_request = any(
                    keyword in text_lower
                    for keyword in [
                        "generate",
                        "create",
                        "make",
                        "product shot",
                        "enhance",
                        "redesign",
                        "new image",
                        "better image",
                        "professional",
                        "marketing",
                    ]
                )

                if is_generate_request:
                    logger.info("🎨 Image generation from reference detected!")
                    try:
                        # First, analyze the image to understand what's in it
                        analysis_prompt = "Describe this product in detail: its type, color, style, material, and key features. Be specific and brief."
                        product_description = user_kernel.run_with_vision(
                            media_bytes, analysis_prompt
                        )
                        logger.info(
                            f"🎨 Product analysis: {product_description[:100]}..."
                        )

                        # Build a generation prompt
                        user_request = msg_text or "product shot"
                        gen_prompt = f"""Professional {user_request} of: {product_description}

Style: Premium e-commerce product photography, clean white or gradient background, perfect studio lighting, high-end commercial quality, sharp focus, elegant presentation."""

                        logger.info(
                            f"🎨 Generating image with prompt: {gen_prompt[:100]}..."
                        )
                        image_bytes = user_kernel.generate_image(gen_prompt)

                        if image_bytes:
                            logger.info(
                                f"✅ Product image generated! Size: {len(image_bytes)} bytes"
                            )
                            b64 = base64.b64encode(image_bytes).decode("ascii")
                            await wpp_send_image(
                                chat_id,
                                b64,
                                caption="Here's your product shot! 🎨",
                                filename="product_shot.png",
                            )
                            return ""
                        else:
                            logger.warning("❌ Image generation returned None")
                            return "I analyzed the product but couldn't generate the new image. Please try again or use /image <description> for text-to-image."
                    except Exception as e:
                        logger.error(f"❌ Image generation flow error: {e}")
                        import traceback

                        logger.error(traceback.format_exc())
                        return f"Sorry, I couldn't generate the product shot. Error: {str(e)[:100]}"

                is_ocr_request = any(
                    keyword in text_lower
                    for keyword in [
                        "/extract",
                        "/ocr",
                        "extract",
                        "text",
                        "read",
                        "ocr",
                        "what does it say",
                        "transcribe",
                    ]
                )

                # Check if user wants paraphrasing instead of verbatim
                is_paraphrase_request = any(
                    keyword in text_lower
                    for keyword in [
                        "/paraphrase",
                        "/summarize",
                        "/summary",
                        "paraphrase",
                        "summarize",
                        "summary",
                        "simplify",
                        "explain",
                        "in your own words",
                    ]
                )

                # Check for invoice/quote/financial document
                is_financial_doc = any(
                    keyword in text_lower
                    for keyword in [
                        "invoice",
                        "quote",
                        "receipt",
                        "bill",
                        "price",
                        "total",
                        "payment",
                        "cost",
                        "amount",
                        "quotation",
                    ]
                )

                if is_financial_doc:
                    prompt = """Extract all financial information from this document:
- List all items/services with their prices
- Show subtotals, taxes, discounts if present
- Show the TOTAL amount clearly
- Include invoice/quote number, date, and company details if visible
- Format prices with currency symbols

Present the information in a clear, structured format."""
                elif is_paraphrase_request:
                    prompt = """Analyze this image and extract the key information. Don't just copy the text verbatim - instead:
1. Summarize the main points in clear, concise language
2. Paraphrase the content in your own words
3. Highlight the key takeaways or actionable insights
4. If it's a document, social post, or article, provide the essence of the message

Be thorough but present it in a digestible format."""
                elif is_ocr_request:
                    prompt = "Extract and transcribe ALL text from this image. Be thorough, accurate, and include every piece of text you can see, maintaining the structure where possible."
                else:
                    prompt = f"User {sender_name} sent an image. {caption}Describe what you see and respond helpfully."

                logger.info(f"🖼️ Vision prompt: {prompt[:100]}...")
                result = user_kernel.run_with_vision(media_bytes, prompt)
                result = strip_markdown(result)
                logger.info(f"🖼️ Vision result: {result[:200] if result else 'None'}...")
                return result

            # Document - use AI-powered processing
            if media_mimetype:
                filename = msg.get("mediaFilename", "document")
                logger.info(f"📄 Processing document: {filename} ({media_mimetype})")
                user_request = (
                    msg_text or "Summarize this document and extract key information."
                )

                # For image documents (screenshots, photos of documents), use vision
                if media_mimetype in [
                    "image/jpeg",
                    "image/png",
                    "image/webp",
                    "image/gif",
                ]:
                    logger.info("📄 Document is an image, using vision...")
                    prompt = f"Extract and analyze ALL text from this image. The user sent this as a document named '{filename}'."
                    if msg_text:
                        prompt += f"\n\nUser request: {msg_text}"
                    return user_kernel.run_with_vision(media_bytes, prompt)

                # For PDFs - use OpenRouter's file-parser plugin (AI-powered)
                if media_mimetype == "application/pdf" or filename.lower().endswith(
                    ".pdf"
                ):
                    logger.info("📄 Using OpenRouter AI for PDF processing...")
                    prompt = (
                        f"Analyze this PDF document named '{filename}'. {user_request}"
                    )
                    result = user_kernel.run_with_pdf(media_bytes, prompt, filename)
                    if result and not result.startswith("PDF analysis error"):
                        return result
                    # Fall back to local extraction if AI fails
                    logger.warning(
                        "📄 AI PDF processing failed, trying local extraction..."
                    )

                # For DOCX, TXT, etc. - use local extraction + AI analysis
                extracted = user_kernel.extract_document_text(
                    media_bytes, filename=filename, mime_type=media_mimetype
                )
                logger.info(
                    f"📄 Extracted {len(extracted) if extracted else 0} chars from document"
                )

                if extracted:
                    prompt = f"User {sender_name} sent a document named '{filename}'.\n\nDocument content:\n{extracted[:6000]}\n\nRequest: {user_request}\n\nProvide a helpful response."
                    return user_kernel.run(prompt)

                return "I received the document but couldn't read its contents. Supported formats: PDF, DOCX, TXT, images."

        # --- Regular Text Message ---
        if not msg_text:
            return ""

        # 🎯 PROACTIVE MODE: Detect friction and act autonomously
        from proactive_agent import FrictionDetector
        
        friction = FrictionDetector.detect(msg_text)
        
        if friction['has_friction']:
            logger.info(f"🎯 Friction detected: {[fp['keyword'] for fp in friction['friction_points']]}")
            logger.info(f"   Categories: {list(set([fp['category'] for fp in friction['friction_points']]))}")
            
            # Execute proactive workflow - agent will build solution autonomously
            result = user_kernel.run_proactive(friction)
            return strip_markdown(result)
        
        # Run through the AI agent (normal mode)
        result = user_kernel.run(msg_text)
        return strip_markdown(result)

    finally:
        # Stop typing indicator
        await wpp_stop_typing(chat_id)


# --- Scheduler Tasks ---
async def check_important_emails():
    """Uses the Kernel to check emails."""
    logger.info("🕵️ Checking Inbox via Kernel...")
    try:
        response = agent_kernel.run(
            "Find unread emails from the last 60 minutes. "
            "Return a summary of any that seem urgent or involve 'meetings', 'contracts', or 'VIPs'. "
            "If none, reply 'No urgent emails'."
        )

        if response and "No urgent emails" not in response and len(response) > 10:
            msg = f"📧 **Email Alert**\n{response}"
            if USER_PHONE:
                await wpp_send_text(USER_PHONE, msg)

    except Exception as e:
        logger.error(f"Email Check Failed: {e}")


async def scheduler_loop():
    """Background scheduler for periodic tasks."""
    logger.info("⏰ Scheduler Started.")
    while True:
        try:
            now = datetime.datetime.now()

            # Email Check (Every 15 minutes)
            if now.minute % 15 == 0 and now.second < 10:
                await check_important_emails()
                await asyncio.sleep(60)

            await asyncio.sleep(10)
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            await asyncio.sleep(60)


# --- FastAPI Application ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global http_client

    logger.info("🚀 Starting PocketAgent...")

    # Initialize HTTP client
    http_client = httpx.AsyncClient()

    # Wait for WPP Bridge to be ready
    logger.info(f"🔌 Connecting to WPP Bridge at {WPP_BRIDGE_URL}...")
    for i in range(30):
        try:
            status = await wpp_get_status()
            if status.get("ready"):
                logger.info("✅ WPP Bridge connected!")
                break
            logger.info(f"⏳ Waiting for WPP Bridge... ({i + 1}/30)")
        except:
            pass
        await asyncio.sleep(2)

    # Start scheduler if enabled
    if ENABLE_SCHEDULER:
        asyncio.create_task(scheduler_loop())

    logger.info("✅ PocketAgent Ready!")

    yield

    # Cleanup
    if http_client:
        await http_client.aclose()
    logger.info("👋 PocketAgent shutdown complete.")


app = FastAPI(
    title="PocketAgent",
    description="AI-Powered WhatsApp Assistant",
    lifespan=lifespan,
)


# --- API Endpoints ---
@app.get("/")
async def root():
    """Health check."""
    status = await wpp_get_status()
    return {
        "name": "PocketAgent",
        "status": "running",
        "whatsapp": status,
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/whatsapp/status")
async def whatsapp_status():
    """Get WhatsApp connection status."""
    return await wpp_get_status()


@app.post("/whatsapp/incoming")
async def whatsapp_incoming(request: Request):
    """
    Callback endpoint for incoming WhatsApp messages.
    The WPP Bridge forwards messages here.
    """
    global processed_messages

    try:
        data = await request.json()
        msg_id = data.get("id", "")

        # Deduplicate
        if msg_id in processed_messages:
            return {"reply": None}
        processed_messages.add(msg_id)

        # Keep set manageable
        if len(processed_messages) > 1000:
            processed_messages = set(list(processed_messages)[-500:])

        # Handle 'from' field aliasing
        if "from" in data:
            data["from_"] = data.pop("from")

        # Process and generate response
        reply = await process_message(data)

        if reply and reply.strip():
            return {"reply": reply}
        return {"reply": None}

    except Exception as e:
        logger.error(f"Incoming message error: {e}")
        return {"reply": None}


@app.post("/whatsapp/send")
async def whatsapp_send(request: SendTextRequest):
    """Send a WhatsApp message."""
    success = await wpp_send_text(request.to, request.message)
    if success:
        return {"status": "sent"}
    raise HTTPException(status_code=500, detail="Failed to send message")


@app.post("/whatsapp/send/image")
async def whatsapp_send_image(request: SendImageRequest):
    """Send an image via WhatsApp."""
    success = await wpp_send_image(
        request.to,
        request.base64,
        request.caption or "",
        request.filename or "image.png",
    )
    if success:
        return {"status": "sent"}
    raise HTTPException(status_code=500, detail="Failed to send image")


@app.get("/connect/{app_name}")
async def connect_app(app_name: str):
    """Generate OAuth URL to connect a Composio app."""
    try:
        url = agent_kernel.get_auth_url(app_name)
        return {"url": url, "app": app_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/add-app/{app_name}")
async def add_app(app_name: str):
    """Add a Composio app to the agent."""
    try:
        agent_kernel.add_apps([app_name])
        return {"status": "added", "app": app_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Main Entry Point ---
if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                      POCKET AGENT                         ║
    ║              AI-Powered WhatsApp Assistant                ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  ARCHITECTURE:                                            ║
    ║    WhatsApp Web <-> WPP Bridge (Node.js) <-> PocketAgent  ║
    ║                                                           ║
    ║  SETUP:                                                   ║
    ║    1. Start WPP Bridge: cd wpp-bridge && npm start        ║
    ║    2. Start PocketAgent: python main.py                   ║
    ║    3. Scan QR code in WPP Bridge console                  ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    uvicorn.run(app, host="0.0.0.0", port=PORT)
