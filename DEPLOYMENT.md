# ☁️ Deployment Guide (DigitalOcean)

Deploy your Trace Kernel to the cloud in minutes using the DigitalOcean Console. No complex SSH setup required.

---

## Step 1: Create a Droplet

1. Log in to [DigitalOcean](https://cloud.digitalocean.com).
2. Click **Create** -> **Droplets**.
3. **Choose Region**: Pick the one closest to you (e.g., New York, London).
4. **Choose Image**: **Ubuntu 22.04 (LTS)** or higher.
5. **Choose Size**: **Basic ($6/mo)** is sufficient (1GB RAM / 1 CPU).
6. **Authentication Method**: Select **Password** (easiest for beginners). Create a strong root password.
7. Click **Create Droplet**.

---

## Step 2: Access the Console

1. Wait for the green dot ● indicating the droplet is active.
2. Click on the droplet name.
3. Click the **Access** tab (left menu) or the **Console** button (top right).
4. Click **Launch Droplet Console**.
   - A browser window will open looking like a black terminal screen.
   - If asked for login, type `root` and press Enter.

---

## Step 3: Deployment

Copy and paste these commands into the console window one by one:

**1. Clone the Refinery:**
```bash
git clone https://github.com/yourusername/pocket-agent.git
cd pocket-agent
```

**2. Run the Deployment Script:**
```bash
chmod +x deploy_vps.sh
./deploy_vps.sh
```

**3. Follow the Prompts:**
The script will ask for:
- Your API Keys (OpenRouter, Composio)
- Your Phone Number

It will automatically:
- Install Python, Node.js, Chrome
- Set up the environment
- Start the services

---

## Step 4: Connect WhatsApp

The console will show the logs. You need to verify the WhatsApp connection.

1. View the Bridge logs:
```bash
journalctl -u wpp-bridge -f
```

2. You will see a **QR Code** (text format) or a link.
   - **Scan the QR Code** with your phone (WhatsApp > Linked Devices).

3. Once connected, press `Ctrl+C` to exit the log view.

---

## Step 5: Verification

Check if your agent is running:
```bash
systemctl status pocketagent
```
(Look for "Active: active (running)")

**Your Agent is now LIVE in the cloud! 24/7.**
You can close the console window. The agent keeps running.

---

## 🛠️ Management

- **Restart Agent**: `systemctl restart pocketagent`
- **View Logs**: `journalctl -u pocketagent -f`
- **Update Code**: 
  ```bash
  cd /root/pocket-agent
  git pull
  systemctl restart pocketagent
  ```
