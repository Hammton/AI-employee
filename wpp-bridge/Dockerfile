# Node.js WPP Bridge - WhatsApp Connection Layer
FROM node:20-slim

# Install Chromium dependencies for WPPConnect
RUN apt-get update && apt-get install -y \
    chromium \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    xdg-utils \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Set Chromium path for WPPConnect
ENV CHROME_BIN=/usr/bin/chromium
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

WORKDIR /app

# Install Node.js dependencies
COPY package*.json ./
RUN npm install --production

# Copy application code
COPY *.js ./

# Expose ports
EXPOSE 3001

# Create session directory (will be mounted as volume)
RUN mkdir -p /app/tokens
VOLUME /app/tokens

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:3001/api/status || exit 1

# Run the bridge
CMD ["node", "index.js"]
