/**
 * WPPConnect Bridge for PocketAgent
 * 
 * This Node.js service handles all WhatsApp communication using WPPConnect,
 * which properly manages browser automation, session persistence, and CSP bypassing.
 * 
 * The Python FastAPI app communicates with this bridge via HTTP.
 */

import wppconnect from '@wppconnect-team/wppconnect';
import express from 'express';
import cors from 'cors';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
app.use(cors());
app.use(express.json({ limit: '50mb' }));

// Configuration
const PORT = process.env.WPP_BRIDGE_PORT || 3001;
const PYTHON_CALLBACK_URL = process.env.PYTHON_CALLBACK_URL || 'http://localhost:8000';
const SESSION_NAME = process.env.WPP_SESSION_NAME || 'pocket-agent';
const HEADLESS = process.env.WPP_HEADLESS === 'true';
const TOKEN_FOLDER = path.join(__dirname, 'tokens');

// State
let client = null;
let isReady = false;
let qrCode = null;
let connectionStatus = 'disconnected';
const processedMessages = new Set();

// Ensure tokens folder exists
if (!fs.existsSync(TOKEN_FOLDER)) {
    fs.mkdirSync(TOKEN_FOLDER, { recursive: true });
}

console.log('🚀 Starting WPP Bridge...');
console.log(`   Session: ${SESSION_NAME}`);
console.log(`   Headless: ${HEADLESS}`);
console.log(`   Token Folder: ${TOKEN_FOLDER}`);

// Initialize WPPConnect
async function initializeWPP() {
    try {
        client = await wppconnect.create({
            session: SESSION_NAME,
            headless: HEADLESS,
            useChrome: true,
            logQR: true,
            folderNameToken: TOKEN_FOLDER,
            autoClose: 0, // Don't auto-close
            disableWelcome: true,
            updatesLog: true,

            // QR Code handling
            catchQR: (base64Qrimg, asciiQR, attempts, urlCode) => {
                console.log('\n📱 Scan QR Code to login:');
                console.log(asciiQR);
                qrCode = base64Qrimg;
                connectionStatus = 'waiting_qr';
            },

            // Session status
            statusFind: (status, session) => {
                console.log(`📊 Status: ${status}`);
                connectionStatus = status;

                if (status === 'isLogged' || status === 'qrReadSuccess') {
                    isReady = true;
                    qrCode = null;
                }
            },

            // Browser options
            browserArgs: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--disable-gpu'
            ],
        });

        console.log('✅ WPPConnect client created');
        setupEventListeners();
        isReady = true;
        connectionStatus = 'connected';

    } catch (error) {
        console.error('❌ WPPConnect initialization failed:', error);
        connectionStatus = 'error';
    }
}

// Event listeners
function setupEventListeners() {
    if (!client) return;

    // New message handler
    client.onMessage(async (message) => {
        try {
            // Skip messages we've already processed
            const msgId = message.id || `${message.from}_${message.timestamp}`;
            if (processedMessages.has(msgId)) return;
            processedMessages.add(msgId);

            // Keep set size manageable
            if (processedMessages.size > 1000) {
                const arr = Array.from(processedMessages);
                processedMessages.clear();
                arr.slice(-500).forEach(id => processedMessages.add(id));
            }

            // Skip own messages
            if (message.fromMe) return;

            // Skip group messages (optional - can be configured)
            // if (message.isGroupMsg) return;

            console.log(`📩 New message from ${message.sender?.pushname || message.from}: ${message.body?.substring(0, 50) || '[media]'}`);

            // Prepare message payload
            const payload = {
                id: msgId,
                from: message.from,
                to: message.to,
                body: message.body || '',
                type: message.type,
                isGroupMsg: message.isGroupMsg,
                sender: {
                    id: message.sender?.id,
                    name: message.sender?.pushname || message.sender?.name,
                    phone: message.sender?.id?.split('@')[0],
                },
                timestamp: message.timestamp,
                hasMedia: message.hasMedia,
                mediaType: message.mimetype,
            };

            // Handle media if present
            // Check both hasMedia AND message.type since hasMedia can be undefined for media messages
            const mediaTypes = ['image', 'video', 'audio', 'ptt', 'document', 'sticker'];
            const isMediaMessage = message.hasMedia || mediaTypes.includes(message.type);

            if (isMediaMessage) {
                console.log(`📎 Media message detected! Type: ${message.type}, hasMedia: ${message.hasMedia}, mimetype: ${message.mimetype}`);
                let mediaDownloaded = false;

                // Method 1: Try decryptFile first (more reliable for WPPConnect)
                try {
                    console.log('📎 Trying decryptFile method...');
                    const buffer = await client.decryptFile(message);
                    if (buffer && buffer.length > 0) {
                        const base64Data = buffer.toString('base64');
                        console.log(`📎 decryptFile succeeded! Length: ${base64Data.length} chars`);

                        // Detect mimetype from buffer
                        let detectedMime = message.mimetype || 'application/octet-stream';
                        const firstBytes = buffer.slice(0, 8).toString('hex');
                        if (firstBytes.startsWith('89504e47')) detectedMime = 'image/png';
                        else if (firstBytes.startsWith('ffd8ff')) detectedMime = 'image/jpeg';
                        else if (firstBytes.startsWith('474946')) detectedMime = 'image/gif';
                        else if (firstBytes.startsWith('52494646')) detectedMime = 'image/webp';
                        else if (firstBytes.startsWith('25504446')) detectedMime = 'application/pdf';

                        console.log(`📎 Detected mimetype: ${detectedMime}`);

                        payload.mediaBase64 = base64Data;
                        payload.mediaMimetype = detectedMime;
                        payload.mediaFilename = message.filename || `file_${Date.now()}`;
                        payload.hasMedia = true;
                        mediaDownloaded = true;
                    }
                } catch (e) {
                    console.log(`📎 decryptFile failed: ${e.message}`);
                }

                // Method 2: Try downloadMedia as fallback
                if (!mediaDownloaded) {
                    try {
                        console.log('📎 Trying downloadMedia method...');
                        const media = await client.downloadMedia(message);
                        if (media && media.data && media.data.length > 0) {
                            console.log(`📎 downloadMedia succeeded! Length: ${media.data.length} chars`);
                            payload.mediaBase64 = media.data;
                            payload.mediaMimetype = media.mimetype || message.mimetype;
                            payload.mediaFilename = media.filename || `file_${Date.now()}`;
                            payload.hasMedia = true;
                            mediaDownloaded = true;
                        } else {
                            console.log('📎 downloadMedia returned empty data');
                        }
                    } catch (e) {
                        console.log(`📎 downloadMedia failed: ${e.message}`);
                    }
                }

                // Method 3: Use thumbnail from message body as last resort
                if (!mediaDownloaded && message.body && message.type === 'image') {
                    // Check if body looks like base64 image data
                    const body = message.body;
                    if (body.startsWith('/9j/') || body.startsWith('iVBOR')) {
                        console.log('📎 Using thumbnail from message body (low quality fallback)');
                        payload.mediaBase64 = body;
                        payload.mediaMimetype = body.startsWith('/9j/') ? 'image/jpeg' : 'image/png';
                        payload.mediaFilename = `thumbnail_${Date.now()}.jpg`;
                        payload.hasMedia = true;
                        payload.body = '/extract';  // Keep the command
                        mediaDownloaded = true;
                        console.log('⚠️ Warning: Using low-quality thumbnail. Full image download failed.');
                    }
                }

                if (!mediaDownloaded) {
                    console.error('📎 All media download methods failed!');
                }
            } else {
                console.log(`📎 Not a media message (type=${message.type}, hasMedia=${message.hasMedia})`);
            }

            // Forward to Python backend
            try {
                const response = await fetch(`${PYTHON_CALLBACK_URL}/whatsapp/incoming`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload),
                });

                if (response.ok) {
                    const result = await response.json();

                    // If Python returns a response, send it back
                    if (result.reply) {
                        await client.sendText(message.from, result.reply);
                        console.log(`✅ Replied to ${message.from}`);
                    }
                }
            } catch (e) {
                console.error('Failed to forward to Python:', e.message);
            }

        } catch (error) {
            console.error('Message handler error:', error);
        }
    });

    // Presence updates
    client.onPresenceChanged((presence) => {
        console.log(`👁 Presence: ${presence.id} is ${presence.state}`);
    });

    // Ack (read receipts)
    client.onAck((ack) => {
        // ack.ack: 0=sent, 1=delivered, 2=read
        const states = ['sent', 'delivered', 'read'];
        console.log(`✓ Message ${ack.id?.id?.substring(0, 10)} ${states[ack.ack] || 'unknown'}`);
    });

    console.log('📡 Event listeners attached');
}

// === REST API Endpoints ===

// Health check
app.get('/health', (req, res) => {
    res.json({
        status: 'ok',
        ready: isReady,
        connectionStatus,
        hasClient: !!client,
    });
});

// Get QR code (for web UI)
app.get('/qr', (req, res) => {
    if (qrCode) {
        res.json({ qr: qrCode });
    } else if (isReady) {
        res.json({ message: 'Already logged in' });
    } else {
        res.json({ message: 'QR not available yet' });
    }
});

// Get connection status
app.get('/status', async (req, res) => {
    let connected = false;
    let phone = null;

    if (client) {
        try {
            connected = await client.isConnected();
            const hostDevice = await client.getHostDevice();
            phone = hostDevice?.id?.user;
        } catch (e) {
            // Ignore
        }
    }

    res.json({
        ready: isReady,
        connected,
        phone,
        status: connectionStatus,
    });
});

// Send text message
app.post('/send/text', async (req, res) => {
    const { to, message } = req.body;

    if (!client || !isReady) {
        return res.status(503).json({ error: 'WhatsApp not connected' });
    }

    if (!to || !message) {
        return res.status(400).json({ error: 'Missing "to" or "message"' });
    }

    try {
        // Normalize phone number
        let chatId = to;
        if (!chatId.includes('@')) {
            chatId = chatId.replace(/[^0-9]/g, '') + '@c.us';
        }

        const result = await client.sendText(chatId, message);
        console.log(`📤 Sent to ${chatId}: ${message.substring(0, 50)}`);
        res.json({ success: true, messageId: result.id });
    } catch (error) {
        console.error('Send failed:', error);
        res.status(500).json({ error: error.message });
    }
});

// Send image
app.post('/send/image', async (req, res) => {
    const { to, base64, caption, filename } = req.body;

    if (!client || !isReady) {
        return res.status(503).json({ error: 'WhatsApp not connected' });
    }

    try {
        let chatId = to;
        if (!chatId.includes('@')) {
            chatId = chatId.replace(/[^0-9]/g, '') + '@c.us';
        }

        // WPPConnect needs a file path, not a data URL
        // Save base64 to temp file, send, then delete
        const tempDir = path.join(__dirname, 'temp');
        if (!fs.existsSync(tempDir)) {
            fs.mkdirSync(tempDir, { recursive: true });
        }

        const tempFilename = `img_${Date.now()}_${Math.random().toString(36).substring(7)}.png`;
        const tempPath = path.join(tempDir, tempFilename);

        // Extract base64 data (remove data URL prefix if present)
        let imageData = base64;
        if (imageData.startsWith('data:')) {
            imageData = imageData.split(',')[1];
        }

        // Write to temp file
        fs.writeFileSync(tempPath, Buffer.from(imageData, 'base64'));
        console.log(`💾 Saved temp image: ${tempPath}`);

        try {
            // Send the image file
            const result = await client.sendImage(
                chatId,
                tempPath,
                filename || 'image.png',
                caption || ''
            );

            console.log(`📤 Image sent to ${chatId}`);
            res.json({ success: true, messageId: result?.id });
        } finally {
            // Clean up temp file
            try {
                fs.unlinkSync(tempPath);
                console.log(`🧹 Cleaned up temp file`);
            } catch (e) {
                // Ignore cleanup errors
            }
        }
    } catch (error) {
        console.error('Send image failed:', error);
        res.status(500).json({ error: error.message });
    }
});

// Send file
app.post('/send/file', async (req, res) => {
    const { to, base64, filename, caption, mimetype } = req.body;

    if (!client || !isReady) {
        return res.status(503).json({ error: 'WhatsApp not connected' });
    }

    try {
        let chatId = to;
        if (!chatId.includes('@')) {
            chatId = chatId.replace(/[^0-9]/g, '') + '@c.us';
        }

        const dataUrl = base64.startsWith('data:')
            ? base64
            : `data:${mimetype || 'application/octet-stream'};base64,${base64}`;

        const result = await client.sendFile(chatId, dataUrl, filename, caption || '');
        res.json({ success: true, messageId: result.id });
    } catch (error) {
        console.error('Send file failed:', error);
        res.status(500).json({ error: error.message });
    }
});

// Send location
app.post('/send/location', async (req, res) => {
    const { to, latitude, longitude, title } = req.body;

    if (!client || !isReady) {
        return res.status(503).json({ error: 'WhatsApp not connected' });
    }

    try {
        let chatId = to;
        if (!chatId.includes('@')) {
            chatId = chatId.replace(/[^0-9]/g, '') + '@c.us';
        }

        const result = await client.sendLocation(chatId, latitude, longitude, title || '');
        res.json({ success: true, messageId: result.id });
    } catch (error) {
        console.error('Send location failed:', error);
        res.status(500).json({ error: error.message });
    }
});

// Send seen/read receipt
app.post('/send/seen', async (req, res) => {
    const { chatId } = req.body;

    if (!client || !isReady) {
        return res.status(503).json({ error: 'WhatsApp not connected' });
    }

    try {
        await client.sendSeen(chatId);
        res.json({ success: true });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Start typing indicator
app.post('/typing/start', async (req, res) => {
    const { chatId } = req.body;

    if (!client || !isReady) {
        return res.status(503).json({ error: 'WhatsApp not connected' });
    }

    try {
        await client.startTyping(chatId);
        res.json({ success: true });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Stop typing indicator
app.post('/typing/stop', async (req, res) => {
    const { chatId } = req.body;

    if (!client || !isReady) {
        return res.status(503).json({ error: 'WhatsApp not connected' });
    }

    try {
        await client.stopTyping(chatId);
        res.json({ success: true });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get all chats
app.get('/chats', async (req, res) => {
    if (!client || !isReady) {
        return res.status(503).json({ error: 'WhatsApp not connected' });
    }

    try {
        const chats = await client.getAllChats();
        res.json(chats.map(c => ({
            id: c.id._serialized,
            name: c.name,
            isGroup: c.isGroup,
            unreadCount: c.unreadCount,
            lastMessage: c.lastMessage?.body?.substring(0, 100),
        })));
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get messages from a chat
app.get('/messages/:chatId', async (req, res) => {
    if (!client || !isReady) {
        return res.status(503).json({ error: 'WhatsApp not connected' });
    }

    try {
        const messages = await client.loadAndGetAllMessagesInChat(
            req.params.chatId,
            true, // include me
            false // include notifications
        );

        res.json(messages.slice(-50).map(m => ({
            id: m.id,
            from: m.from,
            body: m.body,
            type: m.type,
            timestamp: m.timestamp,
            fromMe: m.fromMe,
        })));
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Logout
app.post('/logout', async (req, res) => {
    if (!client) {
        return res.status(400).json({ error: 'No client' });
    }

    try {
        await client.logout();
        isReady = false;
        connectionStatus = 'disconnected';
        res.json({ success: true });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Start server
app.listen(PORT, () => {
    console.log(`\n🌐 WPP Bridge running on http://localhost:${PORT}`);
    console.log(`   Health: http://localhost:${PORT}/health`);
    console.log(`   Status: http://localhost:${PORT}/status\n`);

    // Initialize WPPConnect after server starts
    initializeWPP();
});

// Graceful shutdown
process.on('SIGINT', async () => {
    console.log('\n🛑 Shutting down...');
    if (client) {
        try {
            await client.close();
        } catch (e) {
            // Ignore
        }
    }
    process.exit(0);
});
