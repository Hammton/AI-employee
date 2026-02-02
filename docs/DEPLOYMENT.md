# Deployment Guide - Digital Ocean

This guide covers deploying Pocket Agent to Digital Ocean using Docker and App Platform.

## Prerequisites

- Digital Ocean account
- Docker installed locally
- Git repository connected to Digital Ocean

## Option 1: Digital Ocean App Platform (Recommended)

### Step 1: Prepare Your Repository

Ensure your repository has:
- `Dockerfile` (already included)
- `docker-compose.yml` (already included)
- `.env.example` (already included)

### Step 2: Create App on Digital Ocean

1. Go to [Digital Ocean App Platform](https://cloud.digitalocean.com/apps)
2. Click "Create App"
3. Connect your GitHub repository
4. Select the repository: `Hammton/AI-employee`
5. Select branch: `main`

### Step 3: Configure Components

**Component 1: Python Backend**
- Name: `pocket-agent-backend`
- Type: Web Service
- Dockerfile Path: `./Dockerfile`
- HTTP Port: `8000`
- Instance Size: Basic ($12/month)

**Component 2: WPP Bridge**
- Name: `wpp-bridge`
- Type: Web Service
- Dockerfile Path: `./wpp-bridge/Dockerfile`
- HTTP Port: `3001`
- Instance Size: Basic ($12/month)

### Step 4: Set Environment Variables

Add these environment variables in the App Platform dashboard:

```bash
# Required
OPENROUTER_API_KEY=your_openrouter_key
COMPOSIO_API_KEY=your_composio_key
MEM0_API_KEY=your_mem0_key
ANCHOR_BROWSER_API_KEY=your_anchor_browser_key

# Model Configuration
LLM_MODEL=google/gemini-3-flash-preview
VISION_MODEL=google/gemini-3-flash-preview
IMAGE_MODEL=google/gemini-2.5-flash-image

# Server Configuration
PORT=8000
WPP_BRIDGE_PORT=3001
WPP_BRIDGE_URL=http://wpp-bridge:3001

# WhatsApp Configuration
USER_PHONE=+1234567890
WPP_SESSION_NAME=pocket-agent
WPP_HEADLESS=true

# Features
AUTONOMOUS_EXECUTION_APPROVAL=true
PROACTIVE_MODE_ENABLED=true
```

### Step 5: Deploy

1. Click "Create Resources"
2. Wait for deployment (5-10 minutes)
3. Note the URLs:
   - Backend: `https://pocket-agent-backend-xxxxx.ondigitalocean.app`
   - WPP Bridge: `https://wpp-bridge-xxxxx.ondigitalocean.app`

### Step 6: Update Environment Variables

Update these variables with the deployed URLs:
```bash
WPP_BRIDGE_URL=https://wpp-bridge-xxxxx.ondigitalocean.app
PYTHON_CALLBACK_URL=https://pocket-agent-backend-xxxxx.ondigitalocean.app
```

Redeploy the app after updating.

## Option 2: Digital Ocean Droplet (Manual)

### Step 1: Create Droplet

1. Go to [Digital Ocean Droplets](https://cloud.digitalocean.com/droplets)
2. Click "Create Droplet"
3. Choose:
   - Image: Ubuntu 22.04 LTS
   - Plan: Basic ($12/month - 2GB RAM)
   - Region: Closest to your users
   - Authentication: SSH Key

### Step 2: Connect to Droplet

```bash
ssh root@your_droplet_ip
```

### Step 3: Install Dependencies

```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Install Node.js (for WPP Bridge)
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# Install Python
apt install -y python3 python3-pip python3-venv
```

### Step 4: Clone Repository

```bash
cd /opt
git clone https://github.com/Hammton/AI-employee.git pocket-agent
cd pocket-agent
```

### Step 5: Configure Environment

```bash
cp .env.example .env
nano .env
```

Add your API keys and configuration.

### Step 6: Start Services

```bash
# Start with Docker Compose
docker-compose up -d

# Or start manually
# Terminal 1: Python Backend
python3 main.py

# Terminal 2: WPP Bridge
cd wpp-bridge
npm install
node index.js
```

### Step 7: Setup Firewall

```bash
# Allow SSH
ufw allow 22

# Allow HTTP/HTTPS
ufw allow 80
ufw allow 443

# Allow application ports
ufw allow 8000
ufw allow 3001

# Enable firewall
ufw enable
```

### Step 8: Setup Nginx (Optional)

```bash
# Install Nginx
apt install -y nginx

# Configure reverse proxy
nano /etc/nginx/sites-available/pocket-agent
```

Add this configuration:
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /wpp {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable the site:
```bash
ln -s /etc/nginx/sites-available/pocket-agent /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### Step 9: Setup SSL (Optional)

```bash
# Install Certbot
apt install -y certbot python3-certbot-nginx

# Get SSL certificate
certbot --nginx -d your_domain.com
```

### Step 10: Setup Process Manager

```bash
# Install PM2
npm install -g pm2

# Start Python backend
pm2 start main.py --name pocket-agent --interpreter python3

# Start WPP Bridge
cd wpp-bridge
pm2 start index.js --name wpp-bridge

# Save PM2 configuration
pm2 save
pm2 startup
```

## Monitoring

### Check Logs

**App Platform:**
- Go to your app in Digital Ocean dashboard
- Click "Runtime Logs"

**Droplet:**
```bash
# Docker logs
docker-compose logs -f

# PM2 logs
pm2 logs

# System logs
journalctl -u pocket-agent -f
```

### Health Checks

```bash
# Check Python backend
curl http://localhost:8000/health

# Check WPP Bridge
curl http://localhost:3001/health
```

## Troubleshooting

### Issue: WhatsApp not connecting
**Solution**: Make sure `WPP_HEADLESS=false` for first setup to scan QR code, then change to `true` for production.

### Issue: Out of memory
**Solution**: Upgrade to a larger droplet (4GB RAM recommended for production).

### Issue: Services not starting
**Solution**: Check logs and ensure all environment variables are set correctly.

## Cost Estimate

**App Platform:**
- 2 Basic services: $24/month
- Total: ~$24/month

**Droplet:**
- Basic Droplet (2GB): $12/month
- Total: ~$12/month

## Security Best Practices

1. Use environment variables for all secrets
2. Enable firewall (UFW)
3. Setup SSL certificates
4. Regular security updates: `apt update && apt upgrade`
5. Use SSH keys instead of passwords
6. Setup fail2ban for SSH protection
7. Regular backups of data

## Backup Strategy

```bash
# Backup skills and memory
tar -czf backup-$(date +%Y%m%d).tar.gz skills/ memory/ session_data/

# Upload to Digital Ocean Spaces
# Install s3cmd first
apt install -y s3cmd
s3cmd put backup-*.tar.gz s3://your-bucket/backups/
```

## Auto-Deploy on Push

Create `.github/workflows/deploy-digitalocean.yml`:

```yaml
name: Deploy to Digital Ocean

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to Droplet
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.DROPLET_IP }}
          username: root
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/pocket-agent
            git pull origin main
            docker-compose down
            docker-compose up -d --build
```

Add these secrets to your GitHub repository:
- `DROPLET_IP`: Your droplet IP address
- `SSH_PRIVATE_KEY`: Your SSH private key

## Support

For issues or questions:
- GitHub Issues: https://github.com/Hammton/AI-employee/issues
- Documentation: See `/docs` folder
