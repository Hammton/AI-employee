import asyncio
import os
import base64
import hashlib
import mimetypes
import tempfile
import re
from typing import Any, Optional
from dotenv import load_dotenv

load_dotenv()

import logging
import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, Response, HTTPException
from playwright.async_api import async_playwright
import uvicorn

# Import our new Kernel
from kernel import AgentKernel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PocketAgent")

# --- Configuration ---
SESSION_DIR = "./session_data"
PORT = int(os.environ.get("PORT", 8000))
USER_PHONE = os.environ.get("USER_PHONE")
HEADLESS = os.environ.get("HEADLESS", "true").lower() == "true"
ENABLE_SCHEDULER = os.environ.get("ENABLE_SCHEDULER", "false").lower() == "true"
ENABLE_WHATSAPP_SEND = os.environ.get("ENABLE_WHATSAPP_SEND", "false").lower() == "true"
USE_WPP_SEND = os.environ.get("USE_WPP_SEND", "true").lower() == "true"
WPP_JS_URL = os.environ.get(
    "WPP_JS_URL",
    "https://unpkg.com/@wppconnect/wa-js@3.20.1/dist/wppconnect-wa.js",
)
WPP_JS_URLS = os.environ.get(
    "WPP_JS_URLS",
    "https://unpkg.com/@wppconnect/wa-js@3.20.1/dist/wppconnect-wa.js,"
    "https://cdn.jsdelivr.net/npm/@wppconnect/wa-js@3.20.1/dist/wppconnect-wa.js,"
    "https://wppconnect-team.github.io/wa-js/dist/wppconnect-wa.js",
)

# --- Global State ---
whatsapp_page: Any = None
playwright_instance: Any = None
browser_context: Any = None
is_logged_in = False
processed_messages = set()  # Track which messages we've already responded to
last_seen_message = None
last_reply = None
last_error = None
last_event = None
last_url = None

# Per-user kernel management (each WhatsApp user gets their own session)
user_kernels = {}  # phone_number/chat_id -> AgentKernel

def get_kernel_for_user(user_id: str) -> AgentKernel:
    """Get or create a kernel instance for a specific user."""
    if user_id not in user_kernels:
        logger.info(f"🔧 Creating new kernel for user: {user_id}")
        user_kernels[user_id] = AgentKernel(user_id=user_id)
    return user_kernels[user_id]

# Default kernel for backward compatibility (scheduler, etc.)
agent_kernel = AgentKernel()


# --- Helper: News (Keep Playwright logic separate for now) ---
async def summarize_news(news_text):
    """Uses the Kernel to summarize logic instead of a raw LLM call."""
    return agent_kernel.run(
        f"Summarize this for WhatsApp (Concise, Emojis):\n{news_text[:4000]}"
    )


async def fetch_tech_news():
    """Scrapes TechCrunch/HackerNews."""
    logger.info("Fetching News...")
    global browser_context
    if not browser_context:
        return None

    page = await browser_context.new_page()
    try:
        await page.goto("https://news.ycombinator.com/")
        titles = await page.evaluate("""() => {
            const items = Array.from(document.querySelectorAll('.titleline > a')).slice(0, 5);
            return items.map(a => a.innerText + " (" + a.href + ")");
        }""")
        return "\n".join(titles)
    except Exception as e:
        logger.error(f"News Scraping Failed: {e}")
        return None
    finally:
        await page.close()


# --- Monitor Tasks ---
async def check_important_emails():
    """Uses the Kernel to check emails."""
    logger.info("🕵️ Checking Inbox via Kernel...")
    try:
        # The Kernel handles the complexity of "Perception -> Reasoning -> Action"
        response = agent_kernel.run(
            "Find unread emails from the last 60 minutes. "
            "Return a summary of any that seem urgent or involve 'meetings', 'contracts', or 'VIPs'. "
            "If none, reply 'No urgent emails'."
        )

        if response and "No urgent emails" not in response and len(response) > 10:
            msg = f"📧 **Email Alert**\n{response}"
            if USER_PHONE:
                await send_whatsapp_message(USER_PHONE, msg)

    except Exception as e:
        logger.error(f"Email Check Failed: {e}")


# --- Scheduler ---
async def scheduler_loop():
    logger.info("Scheduler Started.")
    while True:
        now = datetime.datetime.now()

        # News Briefing (Every 4 hours)
        if now.minute == 0 and now.hour % 4 == 0 and now.second < 10:
            raw_news = await fetch_tech_news()
            if raw_news:
                summary = await summarize_news(raw_news)
                if USER_PHONE:
                    await send_whatsapp_message(USER_PHONE, summary)
            await asyncio.sleep(60)

        # Email Check (Every 15 minutes)
        if now.minute % 15 == 0 and now.second < 10:
            await check_important_emails()
            await asyncio.sleep(60)

        await asyncio.sleep(10)


def _data_url_to_bytes(data_url: str):
    try:
        header, b64_data = data_url.split(",", 1)
        if "base64" not in header:
            return None
        return base64.b64decode(b64_data)
    except Exception as e:
        logger.error(f"Failed to decode data URL: {e}")
        return None


def _data_url_to_bytes_and_mime(data_url: str):
    try:
        header, b64_data = data_url.split(",", 1)
        if "base64" not in header:
            return None, ""
        mime = ""
        if header.startswith("data:"):
            mime = header[5:].split(";")[0]
        return base64.b64decode(b64_data), mime
    except Exception as e:
        logger.error(f"Failed to decode data URL: {e}")
        return None, ""


async def _blob_url_to_bytes(blob_url: str):
    global whatsapp_page
    if not whatsapp_page or not blob_url or not blob_url.startswith("blob:"):
        return None
    try:
        b64_data = await whatsapp_page.evaluate(
            """
            async (url) => {
                const res = await fetch(url);
                const buf = await res.arrayBuffer();
                const bytes = new Uint8Array(buf);
                let binary = "";
                const chunk = 0x8000;
                for (let i = 0; i < bytes.length; i += chunk) {
                    binary += String.fromCharCode(...bytes.subarray(i, i + chunk));
                }
                return btoa(binary);
            }
            """,
            blob_url,
        )
        return base64.b64decode(b64_data)
    except Exception as e:
        logger.error(f"Failed to fetch blob URL: {e}")
        return None


async def _extract_media_from_message(msg_elem: Any):
    image_bytes = None
    audio_bytes = None
    doc_bytes = None
    doc_name = None
    doc_mime = ""
    image_detected = False
    audio_detected = False
    doc_detected = False

    img_elem = await msg_elem.query_selector("img[src], img[data-testid='image']")
    if img_elem:
        image_detected = True
        src = await img_elem.get_attribute("src") or ""
        if src.startswith("data:"):
            image_bytes = _data_url_to_bytes(src)
        elif src.startswith("blob:"):
            image_bytes = await _blob_url_to_bytes(src)

    audio_elem = await msg_elem.query_selector("audio[src]")
    if audio_elem:
        audio_detected = True
        src = await audio_elem.get_attribute("src") or ""
        if src.startswith("data:"):
            audio_bytes = _data_url_to_bytes(src)
        elif src.startswith("blob:"):
            audio_bytes = await _blob_url_to_bytes(src)

    if not audio_detected:
        audio_marker = await msg_elem.query_selector(
            "span[data-testid='audio-play'], button[aria-label*='Play'], span[aria-label*='Voice']"
        )
        if audio_marker:
            audio_detected = True

    doc_marker = await msg_elem.query_selector(
        "span[data-testid='document'], div[aria-label*='document'], div[aria-label*='Document']"
    )
    if doc_marker:
        doc_detected = True
        name_elem = await msg_elem.query_selector("span[title], div[title]")
        if name_elem:
            doc_name = await name_elem.get_attribute("title")

        link_elem = await msg_elem.query_selector("a[href^='blob:'], a[href^='data:']")
        if link_elem:
            href = await link_elem.get_attribute("href") or ""
            if href.startswith("data:"):
                doc_bytes, doc_mime = _data_url_to_bytes_and_mime(href)
            elif href.startswith("blob:"):
                doc_bytes = await _blob_url_to_bytes(href)

        if doc_name and not doc_mime:
            doc_mime = mimetypes.guess_type(doc_name)[0] or ""

    return {
        "image_bytes": image_bytes,
        "audio_bytes": audio_bytes,
        "doc_bytes": doc_bytes,
        "doc_name": doc_name,
        "doc_mime": doc_mime,
        "image_detected": image_detected,
        "audio_detected": audio_detected,
        "doc_detected": doc_detected,
    }


def _extract_image_prompt(text: str) -> Optional[str]:
    if not text:
        return None
    trimmed = text.strip()
    if not trimmed:
        return None

    patterns = [
        r"^(please\s+)?(generate|create|make|draw|render|design|produce)\s+(an?\s+)?(image|picture|photo|illustration|art)(\s+(of|showing|with|about))?\s*",
        r"^(please\s+)?(show|send|give)\s+me\s+(an?\s+)?(image|picture|photo|illustration|art)(\s+(of|showing|with|about))?\s*",
    ]

    for pattern in patterns:
        match = re.match(pattern, trimmed, flags=re.IGNORECASE)
        if match:
            prompt = trimmed[match.end() :].strip()
            return prompt if prompt else ""

    lowered = trimmed.lower()
    for key in ["image of", "picture of", "photo of", "illustration of", "art of"]:
        idx = lowered.find(key)
        if idx != -1:
            prompt = trimmed[idx + len(key) :].strip()
            return prompt if prompt else ""

    return None


async def extract_message_payload(msg_elem: Any):
    pre_plain = await msg_elem.get_attribute("data-pre-plain-text") or ""
    data_id = await msg_elem.get_attribute("data-id") or ""
    aria_label = await msg_elem.get_attribute("aria-label") or ""

    msg_text = None
    for selector in ["span.selectable-text", "span[dir='ltr']", "span._ao3e"]:
        elem = await msg_elem.query_selector(selector)
        if elem:
            msg_text = (await elem.inner_text()).strip()
            if msg_text:
                break

    if not msg_text:
        raw_text = (await msg_elem.inner_text()).strip()
        if raw_text:
            msg_text = raw_text
            logger.info("🔍 Falling back to row inner_text")

    media = await _extract_media_from_message(msg_elem)
    media_type = "text"
    if media["audio_bytes"]:
        media_type = "audio"
    elif media["image_bytes"]:
        media_type = "image"
    elif media["doc_bytes"]:
        media_type = "document"
    elif media["audio_detected"]:
        media_type = "audio"
    elif media["image_detected"]:
        media_type = "image"
    elif media["doc_detected"]:
        media_type = "document"

    seed = data_id or pre_plain or aria_label
    if media_type == "text":
        suffix = (msg_text or "")[:50]
    elif media["image_bytes"]:
        suffix = hashlib.sha1(media["image_bytes"][:2048]).hexdigest()[:10]
    elif media["audio_bytes"]:
        suffix = hashlib.sha1(media["audio_bytes"][:2048]).hexdigest()[:10]
    elif media["doc_bytes"]:
        suffix = hashlib.sha1(media["doc_bytes"][:2048]).hexdigest()[:10]
    else:
        suffix = "nomedia"

    msg_id = f"{seed}:{media_type}:{suffix}"
    return {
        "text": msg_text,
        "type": media_type,
        "msg_id": msg_id,
        "image_bytes": media["image_bytes"],
        "audio_bytes": media["audio_bytes"],
        "doc_bytes": media["doc_bytes"],
        "doc_name": media["doc_name"],
        "doc_mime": media["doc_mime"],
        "media_detected": media["image_detected"]
        or media["audio_detected"]
        or media["doc_detected"],
    }


def _write_temp_file(data: Optional[bytes], suffix: str, prefix: str = "pa_"):
    if not data:
        return ""
    fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
    with os.fdopen(fd, "wb") as f:
        f.write(data)
    return path


async def generate_response_for_payload(
    msg_text: str,
    media_type: str,
    image_bytes: Optional[bytes],
    audio_bytes: Optional[bytes],
    doc_bytes: Optional[bytes] = None,
    doc_name: Optional[str] = None,
    doc_mime: Optional[str] = None,
    sender_id: Optional[str] = None,  # NEW: User identifier for per-user sessions
):
    # Get the appropriate kernel for this user
    kernel = get_kernel_for_user(sender_id) if sender_id else agent_kernel
    
    if msg_text:
        text_lower = msg_text.strip().lower()
        if text_lower.startswith("/image") or text_lower.startswith("/img"):
            prompt = msg_text.split(" ", 1)[1].strip() if " " in msg_text else ""
            if not prompt:
                return "Usage: /image <prompt>"
            image = kernel.generate_image(prompt)
            if not image:
                return "Image generation failed or IMAGE_MODEL not configured."
            file_path = _write_temp_file(image, ".png")
            sent = await send_media_to_current_chat(file_path, caption="Here you go.")
            if sent:
                return ""
            return "I generated the image but couldn't send it here."

        image_prompt = _extract_image_prompt(msg_text)
        if image_prompt is not None:
            prompt = image_prompt or msg_text
            image = kernel.generate_image(prompt)
            if not image:
                return "Image generation failed or IMAGE_MODEL not configured."
            file_path = _write_temp_file(image, ".png")
            sent = await send_media_to_current_chat(file_path, caption="Here you go.")
            if sent:
                return ""
            return "I generated the image but couldn't send it here."

        if text_lower.startswith("/voice") or text_lower.startswith("/audio"):
            speech_text = msg_text.split(" ", 1)[1].strip() if " " in msg_text else ""
            if not speech_text:
                return "Usage: /voice <text>"
            audio = kernel.generate_speech(speech_text)
            if not audio:
                return "Audio generation failed or TTS_MODEL not configured."
            file_path = _write_temp_file(audio, ".mp3")
            sent = await send_media_to_current_chat(file_path)
            if sent:
                return ""
            return "I generated the audio but couldn't send it here."

    if media_type == "audio":
        if not audio_bytes:
            return (
                "I received a voice note, but I couldn't extract the audio from WhatsApp Web. "
                "Please resend it as text."
            )
        transcript = kernel.transcribe_audio(audio_bytes)
        if not transcript:
            return "I received a voice note, but I couldn't transcribe it."
        prompt = (
            f"User sent a voice note. Transcript:\n{transcript}\n\nReply to the user."
        )
        return kernel.run(prompt)

    if media_type == "image":
        if not image_bytes:
            return (
                "I received an image, but I couldn't extract it from WhatsApp Web. "
                "Please resend it or add a text description."
            )
        caption = f"Caption: {msg_text}\n" if msg_text else ""
        prompt = (
            "Describe the image and respond to the user. "
            "Be concise and helpful.\n"
            f"{caption}"
        )
        return kernel.run_with_vision(image_bytes, prompt)

    if media_type == "document":
        if not doc_bytes:
            return (
                "I received a document, but I couldn't extract it from WhatsApp Web. "
                "Please resend it or add a text description."
            )
        extracted = kernel.extract_document_text(
            doc_bytes, filename=doc_name or "", mime_type=doc_mime or ""
        )
        if not extracted:
            return "I received the document but couldn't parse it."
        user_request = msg_text or "Summarize the document for me."
        prompt = (
            f"User sent a document named '{doc_name or 'document'}'.\n"
            f"Extracted text:\n{extracted}\n\n"
            f"User request: {user_request}\n"
            "Reply concisely and helpfully."
        )
        return kernel.run(prompt)

    if not msg_text:
        return ""
    return kernel.run(msg_text)


async def send_media_to_current_chat(file_path: str, caption: Optional[str] = None):
    global whatsapp_page
    if not whatsapp_page:
        return False
    try:
        if USE_WPP_SEND:
            sent = await _send_media_via_wpp(file_path, caption)
            if sent:
                return True

        clip_button = await whatsapp_page.query_selector(
            "span[data-testid='clip'], span[data-icon='clip'], button[aria-label*='attach'], button[aria-label*='Attach'], div[role='button'][aria-label*='attach'], div[role='button'][aria-label*='Attach']"
        )
        if not clip_button:
            clip_button = await whatsapp_page.query_selector(
                "footer span[data-testid='clip'], footer span[data-icon='clip'], footer button[aria-label*='attach'], footer div[role='button'][aria-label*='attach']"
            )
        if not clip_button:
            logger.error("Could not find attachment button")
            return False
        await clip_button.click()

        file_input = await whatsapp_page.wait_for_selector(
            "input[type='file']", timeout=10000, state="attached"
        )
        if not file_input:
            file_input = await whatsapp_page.query_selector(
                "input[type='file'][accept*='image'], input[type='file']"
            )
        if not file_input:
            logger.error("Could not find file input")
            return False
        await file_input.set_input_files(file_path)

        if caption:
            caption_box = await whatsapp_page.query_selector(
                "div[contenteditable='true'][data-tab='10'], div[contenteditable='true']"
            )
            if caption_box:
                await caption_box.click()
                await asyncio.sleep(0.2)
                await whatsapp_page.keyboard.type(caption, delay=10)

        send_btn = await whatsapp_page.wait_for_selector(
            "span[data-icon='send'], span[data-testid='send']",
            timeout=15000,
        )
        if not send_btn:
            logger.error("Could not find send button")
            return False
        await send_btn.click()
        await asyncio.sleep(1)
        return True
    except Exception as e:
        logger.error(f"Media send failed: {e}")
        return False


async def _ensure_wpp_ready():
    global whatsapp_page
    if not whatsapp_page:
        return False
    try:
        has_wpp = await whatsapp_page.evaluate("() => Boolean(window.WPP)")
        if not has_wpp:
            loaded = False
            
            # Use page.evaluate() to inject script content directly (bypasses CSP)
            local_wpp_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "node_modules", "@wppconnect", "wa-js", "dist", "wppconnect-wa.js"
            )
            if os.path.exists(local_wpp_path):
                try:
                    with open(local_wpp_path, "r", encoding="utf-8") as f:
                        wpp_script_content = f.read()
                    # Execute script content directly in page context (bypasses CSP)
                    await whatsapp_page.evaluate(wpp_script_content)
                    loaded = True
                    logger.info(f"WPP script injected via evaluate() from: {local_wpp_path}")
                except Exception as e:
                    logger.warning(f"WPP evaluate injection failed: {e}")
            
            # Fallback: try add_init_script for future page loads
            if not loaded:
                try:
                    await whatsapp_page.context.add_init_script(path=local_wpp_path)
                    await whatsapp_page.reload()
                    await whatsapp_page.wait_for_load_state("networkidle")
                    loaded = await whatsapp_page.evaluate("() => Boolean(window.WPP)")
                    if loaded:
                        logger.info("WPP script loaded via add_init_script")
                except Exception as e:
                    logger.warning(f"WPP add_init_script failed: {e}")
            
            if not loaded:
                logger.error("Failed to load WPP script - media send via WPP unavailable")
                return False
        await whatsapp_page.wait_for_function(
            "() => window.WPP && (window.WPP.isReady || window.WPP.conn)",
            timeout=20000,
        )
        return True
    except Exception as e:
        logger.error(f"WPP init failed: {e}")
        return False


async def _send_media_via_wpp(file_path: str, caption: Optional[str] = None):
    global whatsapp_page
    if not whatsapp_page:
        return False
    if not os.path.exists(file_path):
        return False
    if not await _ensure_wpp_ready():
        return False

    mime = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
    with open(file_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    data_url = f"data:{mime};base64,{b64}"
    filename = os.path.basename(file_path)

    def _infer_type(mime_type: str):
        if mime_type.startswith("image/"):
            return "image"
        if mime_type.startswith("audio/"):
            return "audio"
        if mime_type.startswith("video/"):
            return "video"
        return "document"

    media_type = _infer_type(mime)

    try:
        result = await whatsapp_page.evaluate(
            """
            async ({ dataUrl, caption, filename, type }) => {
                const chat = await WPP.chat.getActiveChat();
                if (!chat) return { ok: false, error: 'No active chat' };
                const to = chat.id?._serialized || chat.id;
                const options = { type };
                if (caption) options.caption = caption;
                if (filename) options.filename = filename;
                const res = await WPP.chat.sendFileMessage(to, dataUrl, options);
                return { ok: true, res };
            }
            """,
            {
                "dataUrl": data_url,
                "caption": caption or "",
                "filename": filename,
                "type": media_type,
            },
        )
        return bool(result and result.get("ok"))
    except Exception as e:
        logger.error(f"WPP media send failed: {e}")
        return False


async def safe_click(locator, label: str):
    try:
        await locator.scroll_into_view_if_needed()
        await locator.click(timeout=5000)
        return True
    except Exception as e:
        logger.warning(f"Click failed for {label}: {e}")
        try:
            await locator.click(timeout=5000, force=True)
            return True
        except Exception as e2:
            logger.error(f"Force click failed for {label}: {e2}")
            return False


# --- WhatsApp Bridge Logic ---
async def start_whatsapp_bridge():
    global whatsapp_page, playwright_instance, browser_context
    logger.info("Starting WhatsApp Bridge...")
    print("[PocketAgent] Starting WhatsApp Bridge...")
    playwright_instance = await async_playwright().start()

    # Use Firefox instead of Chromium - WhatsApp blocks old Chromium versions
    browser_context = await playwright_instance.firefox.launch_persistent_context(
        user_data_dir=SESSION_DIR,
        headless=HEADLESS,
    )
    whatsapp_page = await browser_context.new_page()
    await whatsapp_page.goto("https://web.whatsapp.com")
    logger.info("WhatsApp Web opened.")
    print("[PocketAgent] WhatsApp Web opened.")

    # Start monitoring tasks
    asyncio.create_task(monitor_whatsapp_status())
    asyncio.create_task(listen_for_messages())  # NEW: Message listener
    if ENABLE_SCHEDULER:
        asyncio.create_task(scheduler_loop())


async def monitor_whatsapp_status():
    """Monitor WhatsApp login status."""
    global whatsapp_page, is_logged_in
    while True:
        try:
            # Detect login state using multiple stable selectors
            qr_canvas = await whatsapp_page.query_selector("canvas[aria-label*='Scan']")
            chat_list = await whatsapp_page.query_selector(
                "div[aria-label='Chat list']"
            )
            chat_grid = await whatsapp_page.query_selector("div[role='grid']")
            chat_textbox = await whatsapp_page.query_selector("div[role='textbox']")

            logged_in = (chat_list or chat_grid or chat_textbox) and not qr_canvas

            if logged_in and not is_logged_in:
                logger.info("✅ WhatsApp Connected! Ready to receive messages.")
                print("[PocketAgent] WhatsApp Connected.")
                is_logged_in = True
            elif not logged_in and is_logged_in:
                logger.info("⚠️ WhatsApp disconnected. Please re-scan QR.")
                print("[PocketAgent] WhatsApp disconnected.")
                is_logged_in = False
            elif not logged_in:
                logger.info("WhatsApp Status: Waiting for QR Scan 📷")
        except Exception as e:
            logger.debug(f"Status check error: {e}")
        await asyncio.sleep(5)


async def listen_for_messages():
    """
    Listen for incoming WhatsApp messages and respond using the agent.
    This is the key missing piece!
    """
    global whatsapp_page, is_logged_in, processed_messages
    logger.info("👂 Message listener started...")
    print("[PocketAgent] Message listener started.")

    loop_count = 0
    while True:
        try:
            if not is_logged_in:
                await asyncio.sleep(3)
                continue

            loop_count += 1
            # Debug: Log every 30 loops (~1 minute) to confirm listener is running
            if loop_count % 30 == 0:
                logger.info(f"🔄 Message listener active (loop #{loop_count})")

            # Ensure a chat is open; some layouts require selecting a chat first
            header = await whatsapp_page.query_selector("header span[title]")
            if not header:
                chat_rows = whatsapp_page.locator("div[role='row']")
                if await chat_rows.count() > 0:
                    await safe_click(chat_rows.nth(0), "initial chat row")
                    await asyncio.sleep(0.5)

            # Find unread chats (green badges)
            unread_rows = whatsapp_page.locator("div[role='row']").filter(
                has=whatsapp_page.locator(
                    "span[aria-label*='unread'], div[aria-label*='unread'], span[data-testid='icon-unread-count'], span._ahlk"
                )
            )
            await respond_if_new_message_in_open_chat()
            unread_count = await unread_rows.count()

            # Debug: Log when unread messages found
            if unread_count > 0:
                logger.info(f"🔔 Found {unread_count} unread badge(s)")
            if unread_count == 0:
                await asyncio.sleep(2)
                continue

            for i in range(unread_count):
                try:
                    chat_item = unread_rows.nth(i)
                    if not await safe_click(chat_item, f"unread chat {i}"):
                        continue
                    await whatsapp_page.wait_for_selector(
                        "div[role='textbox']", timeout=10000
                    )
                    await asyncio.sleep(0.5)

                    # Get the sender's name
                    header = await whatsapp_page.query_selector("header span[title]")
                    sender_name = (
                        await header.get_attribute("title") if header else "Unknown"
                    )

                    # Get the last incoming message (messages from others have different structure)
                    # Look for messages that are NOT from "You"
                    messages = await whatsapp_page.query_selector_all(
                        "div[data-pre-plain-text]"
                    )

                    if messages:
                        last_msg = messages[-1]
                        pre_plain = await last_msg.get_attribute("data-pre-plain-text")
                        if pre_plain and "You:" in pre_plain:
                            continue

                        payload = await extract_message_payload(last_msg)
                        msg_text = payload.get("text")
                        media_type = payload.get("type")
                        msg_id = payload.get("msg_id")
                        image_bytes = payload.get("image_bytes")
                        audio_bytes = payload.get("audio_bytes")
                        media_detected = payload.get("media_detected")

                        if not msg_text and not media_detected:
                            continue

                        if msg_id not in processed_messages:
                            processed_messages.add(msg_id)
                            logger.info(
                                f"📩 New message from {sender_name}: {msg_text or media_type}"
                            )

                            response = await generate_response_for_payload(
                                msg_text=msg_text or "",
                                media_type=media_type or "text",
                                image_bytes=image_bytes,
                                audio_bytes=audio_bytes,
                                doc_bytes=payload.get("doc_bytes"),
                                doc_name=payload.get("doc_name"),
                                doc_mime=payload.get("doc_mime"),
                                sender_id=sender_name,  # Pass sender for per-user kernel
                            )
                            logger.info(f"🤖 Agent response: {response[:100]}...")

                            # Type and send reply
                            if response and response.strip():
                                await reply_to_current_chat(response)

                            # Keep only last 1000 processed messages
                            if len(processed_messages) > 1000:
                                processed_messages = set(
                                    list(processed_messages)[-500:]
                                )

                except Exception as e:
                    logger.error(f"Error processing chat: {e}")
                    continue

            await asyncio.sleep(2)  # Check every 2 seconds

        except Exception as e:
            logger.error(f"Message listener error: {e}")
            await asyncio.sleep(5)


async def respond_if_new_message_in_open_chat():
    """Fallback: respond to latest message in the currently open chat."""
    global \
        whatsapp_page, \
        processed_messages, \
        last_seen_message, \
        last_reply, \
        last_error, \
        last_event, \
        last_url
    try:
        # Try multiple selectors for messages (WhatsApp Web changes frequently)
        messages = []
        messages_container = await whatsapp_page.query_selector(
            "div[aria-label*='messages'], div[aria-label*='Message list'], div[role='application']"
        )
        if messages_container:
            messages = await messages_container.query_selector_all(
                "div[data-pre-plain-text]"
            )
            if not messages:
                messages = await messages_container.query_selector_all(
                    "div[role='row']"
                )

        if not messages:
            # Try alternate selectors
            messages = await whatsapp_page.query_selector_all(
                "div.message-in, div[class*='message-in']"
            )
        if not messages:
            return False

        last_msg = messages[-1]
        pre_plain = await last_msg.get_attribute("data-pre-plain-text") or ""
        aria_label = await last_msg.get_attribute("aria-label") or ""

        # Debug: Log message detection
        logger.info(
            "🔍 Checking message: pre_plain='%s...', aria_label='%s...'"
            % (
                pre_plain[:50] if pre_plain else "None",
                aria_label[:50] if aria_label else "None",
            )
        )

        if (
            "You:" in pre_plain
            or "You:" in aria_label
            or "outgoing" in aria_label.lower()
        ):
            return False

        payload = await extract_message_payload(last_msg)
        msg_text = payload.get("text")
        media_type = payload.get("type")
        msg_id = payload.get("msg_id")
        image_bytes = payload.get("image_bytes")
        audio_bytes = payload.get("audio_bytes")
        media_detected = payload.get("media_detected")

        if not msg_text and not media_detected:
            logger.info("🔍 Empty message text and no media detected")
            return False

        safe_msg = (msg_text or "")[:50]
        safe_id = (msg_id or "")[:30]
        logger.info(f"🔍 Message text: '{safe_msg}...', msg_id: '{safe_id}...'")

        if msg_id in processed_messages:
            return False

        processed_messages.add(msg_id)
        if media_type == "image":
            last_seen_message = "[image]"
        elif media_type == "audio":
            last_seen_message = "[voice note]"
        else:
            last_seen_message = msg_text
        last_event = "active_chat_message"
        last_url = whatsapp_page.url if whatsapp_page else None
        logger.info(f"📩 New message (active chat): {msg_text or media_type}")

        response = await generate_response_for_payload(
            msg_text=msg_text or "",
            media_type=media_type or "text",
            image_bytes=image_bytes,
            audio_bytes=audio_bytes,
            doc_bytes=payload.get("doc_bytes"),
            doc_name=payload.get("doc_name"),
            doc_mime=payload.get("doc_mime"),
        )
        last_reply = response
        logger.info(f"🤖 Agent response: {response[:100]}...")

        if response and response.strip():
            await reply_to_current_chat(response)
        return True
    except Exception as e:
        last_error = str(e)
        logger.error(f"Active chat check failed: {e}")
        return False


async def reply_to_current_chat(message: str):
    """Reply to the currently open chat."""
    global whatsapp_page
    try:
        if USE_WPP_SEND:
            sent = await _send_text_via_wpp(message)
            if sent:
                return True

        # Find the message input box
        input_box = await whatsapp_page.query_selector(
            "div[contenteditable='true'][data-tab='10']"
        )
        if not input_box:
            input_box = await whatsapp_page.query_selector(
                "footer div[contenteditable='true']"
            )

        if input_box:
            await input_box.click()
            await asyncio.sleep(0.3)

            # Type the message (handle newlines by using keyboard)
            lines = message.split("\n")
            for idx, line in enumerate(lines):
                await whatsapp_page.keyboard.type(line, delay=10)
                if idx < len(lines) - 1:
                    await whatsapp_page.keyboard.press("Shift+Enter")

            # Send the message
            await whatsapp_page.keyboard.press("Enter")
            logger.info("✅ Reply sent!")
            await asyncio.sleep(1)
            return True
        else:
            logger.error("Could not find message input box")
            return False

    except Exception as e:
        logger.error(f"Reply failed: {e}")
        return False


async def _send_text_via_wpp(message: str):
    global whatsapp_page
    if not whatsapp_page:
        return False
    if not await _ensure_wpp_ready():
        return False
    try:
        result = await whatsapp_page.evaluate(
            """
            async ({ text }) => {
                const chat = await WPP.chat.getActiveChat();
                if (!chat) return { ok: false, error: 'No active chat' };
                const to = chat.id?._serialized || chat.id;
                const res = await WPP.chat.sendTextMessage(to, text);
                return { ok: true, res };
            }
            """,
            {"text": message},
        )
        return bool(result and result.get("ok"))
    except Exception as e:
        logger.error(f"WPP text send failed: {e}")
        return False


async def get_whatsapp_qr():
    global whatsapp_page
    if not whatsapp_page:
        return None
    try:
        return await whatsapp_page.screenshot()
    except Exception:
        return None


async def send_whatsapp_message(phone_number, message):
    global whatsapp_page
    if not whatsapp_page:
        return False
    if not ENABLE_WHATSAPP_SEND:
        logger.info("WhatsApp send disabled; skipping outbound message.")
        return False
    try:
        encoded_msg = message.replace(" ", "%20").replace("\n", "%0A")
        await whatsapp_page.goto(
            f"https://web.whatsapp.com/send?phone={phone_number}&text={encoded_msg}"
        )
        try:
            send_btn = await whatsapp_page.wait_for_selector(
                "span[data-icon='send']", timeout=15000
            )
            await send_btn.click()
            await asyncio.sleep(2)
            return True
        except Exception:
            await whatsapp_page.keyboard.press("Enter")
            return True
    except Exception as e:
        logger.error(f"Send Failed: {e}")
        return False


# --- FastAPI App ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Start the Bridge (Perception/Action for WhatsApp)
    asyncio.create_task(start_whatsapp_bridge())

    # 2. Setup the Brain (Agent Kernel)
    # Initialize without apps - add them later via /add-capability or /connect
    agent_kernel.setup(apps=[])

    yield
    if browser_context:
        await browser_context.close()
    if playwright_instance:
        await playwright_instance.stop()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {
        "status": "Pocket Agent Online 🟢",
        "whatsapp_connected": is_logged_in,
        "last_event": last_event,
        "last_seen_message": last_seen_message,
        "last_reply_preview": (last_reply[:120] if last_reply else None),
        "last_error": last_error,
        "last_url": last_url,
        "processed_messages_count": len(processed_messages),
        "endpoints": [
            "/qr",
            "/connect/{app_name}",
            "/ask",
            "/add-capability/{app_name}",
            "/debug/page-structure",
        ],
    }


@app.get("/debug/page-structure")
async def debug_page_structure():
    """Debug endpoint to inspect current WhatsApp Web page structure."""
    global whatsapp_page, is_logged_in
    if not is_logged_in or not whatsapp_page:
        return {"error": "WhatsApp not connected"}

    try:
        # Check for messages with various selectors
        selectors_to_check = [
            "div[data-pre-plain-text]",
            "div.message-in",
            "div[class*='message-in']",
            "span.selectable-text",
            "span[dir='ltr']",
            "div[role='row']",
            "div._amjy",  # Common WhatsApp message class
        ]

        results = {}
        for selector in selectors_to_check:
            try:
                count = await whatsapp_page.locator(selector).count()
                results[selector] = count
            except Exception as e:
                results[selector] = f"error: {str(e)}"

        # Sample last few rows to understand structure
        row_samples = []
        try:
            rows = await whatsapp_page.query_selector_all("div[role='row']")
            for row in rows[-5:]:
                row_text = (await row.inner_text()).strip()
                row_label = await row.get_attribute("aria-label") or ""
                row_samples.append(
                    {
                        "aria_label": row_label[:120],
                        "text": row_text[:200],
                    }
                )
        except Exception as e:
            row_samples = [f"error: {str(e)}"]

        # Get page title to confirm we're on WhatsApp
        title = await whatsapp_page.title()

        # Check if chat is open
        chat_header = await whatsapp_page.query_selector("header span[title]")
        chat_name = await chat_header.get_attribute("title") if chat_header else None

        return {
            "page_title": title,
            "current_chat": chat_name,
            "selector_counts": results,
            "row_samples": row_samples,
            "is_logged_in": is_logged_in,
            "processed_messages_count": len(processed_messages),
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/qr")
async def get_qr_code():
    img_bytes = await get_whatsapp_qr()
    if img_bytes:
        return Response(content=img_bytes, media_type="image/png")
    return {"status": "Logged In or Error"}


@app.get("/connect/{app_name}")
async def connect_tool(app_name: str):
    """Generates an auth link using the Kernel."""
    try:
        url = agent_kernel.get_auth_url(app_name)
        return {"auth_url": url}
    except Exception as e:
        return {"error": str(e)}


@app.post("/ask")
async def ask_agent(query: str):
    """Direct query to the Kernel."""
    res = agent_kernel.run(query)
    return {"response": res}


@app.post("/add-capability/{app_name}")
async def add_capability(app_name: str):
    """
    Dynamically upgrades the Kernel with new capabilities.
    Example: /add-capability/NOTION -> Adds Notion tools to the running agent.
    """
    try:
        # Use app name directly (no enum needed with new Composio API)
        agent_kernel.add_apps([app_name.upper()])
        return {
            "status": "success",
            "message": f"Added {app_name} capability to Kernel 🧠",
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
