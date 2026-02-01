#!/bin/bash

# DigitalOcean Droplet Creation Script
# This creates a $6/month Ubuntu 22.04 droplet for AI Employee

echo "🚀 Creating DigitalOcean Droplet for AI Employee..."
echo ""

# Check if TOKEN is set
if [ -z "$TOKEN" ]; then
    echo "❌ Error: TOKEN environment variable not set"
    echo ""
    echo "Please set your DigitalOcean API token:"
    echo "export TOKEN='your_digitalocean_api_token_here'"
    echo ""
    echo "Get your token at: https://cloud.digitalocean.com/account/api/tokens"
    exit 1
fi

# Create droplet
echo "Creating droplet..."
RESPONSE=$(curl -X POST -H 'Content-Type: application/json' \
-H "Authorization: Bearer $TOKEN" \
-d '{
  "name":"ai-employee-prod",
  "size":"s-1vcpu-1gb",
  "region":"sfo3",
  "image":"ubuntu-22-04-x64",
  "monitoring":true,
  "tags":["ai-employee","production"]
}' \
"https://api.digitalocean.com/v2/droplets")

# Check if creation was successful
if echo "$RESPONSE" | grep -q '"droplet"'; then
    echo "✅ Droplet created successfully!"
    echo ""
    
    # Extract droplet ID
    DROPLET_ID=$(echo "$RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    echo "📋 Droplet ID: $DROPLET_ID"
    echo ""
    
    echo "⏳ Waiting for droplet to be ready (this takes about 60 seconds)..."
    sleep 60
    
    # Get droplet details
    echo "🔍 Getting droplet IP address..."
    DETAILS=$(curl -X GET -H 'Content-Type: application/json' \
    -H "Authorization: Bearer $TOKEN" \
    "https://api.digitalocean.com/v2/droplets/$DROPLET_ID")
    
    # Extract IP address
    IP_ADDRESS=$(echo "$DETAILS" | grep -o '"ip_address":"[^"]*' | head -1 | cut -d'"' -f4)
    
    if [ -n "$IP_ADDRESS" ]; then
        echo ""
        echo "✅ Droplet is ready!"
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📊 DROPLET DETAILS"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "Name:       ai-employee-prod"
        echo "IP Address: $IP_ADDRESS"
        echo "Droplet ID: $DROPLET_ID"
        echo "Region:     San Francisco (sfo3)"
        echo "Size:       1GB RAM / 1 vCPU / 25GB SSD"
        echo "Cost:       $6/month"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "🔐 NEXT STEPS:"
        echo ""
        echo "1. Get your root password from DigitalOcean dashboard:"
        echo "   https://cloud.digitalocean.com/droplets/$DROPLET_ID"
        echo ""
        echo "2. SSH into your droplet:"
        echo "   ssh root@$IP_ADDRESS"
        echo ""
        echo "3. Run the deployment script:"
        echo "   curl -fsSL https://raw.githubusercontent.com/Hammton/AI-employee/main/deploy_vps.sh -o deploy.sh"
        echo "   chmod +x deploy.sh"
        echo "   ./deploy.sh"
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        # Save details to file
        cat > droplet_info.txt << EOF
DigitalOcean Droplet Information
================================

Name:       ai-employee-prod
IP Address: $IP_ADDRESS
Droplet ID: $DROPLET_ID
Region:     San Francisco (sfo3)
Size:       1GB RAM / 1 vCPU / 25GB SSD
Cost:       \$6/month
Created:    $(date)

SSH Command:
ssh root@$IP_ADDRESS

Dashboard:
https://cloud.digitalocean.com/droplets/$DROPLET_ID

Next Steps:
1. Get root password from dashboard
2. SSH into droplet
3. Run deployment script
EOF
        
        echo "💾 Droplet info saved to: droplet_info.txt"
        echo ""
    else
        echo "⏳ Droplet is still initializing. Check dashboard:"
        echo "   https://cloud.digitalocean.com/droplets/$DROPLET_ID"
    fi
else
    echo "❌ Error creating droplet!"
    echo ""
    echo "Response:"
    echo "$RESPONSE"
    echo ""
    echo "Common issues:"
    echo "- Invalid API token"
    echo "- Insufficient permissions"
    echo "- Region not available"
    echo "- Billing issue"
fi
