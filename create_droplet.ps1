# DigitalOcean Droplet Creation Script (PowerShell)
# This creates a $6/month Ubuntu 22.04 droplet for AI Employee

Write-Host "🚀 Creating DigitalOcean Droplet for AI Employee..." -ForegroundColor Green
Write-Host ""

# Check if TOKEN is set
if (-not $env:TOKEN) {
    Write-Host "❌ Error: TOKEN environment variable not set" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please set your DigitalOcean API token:" -ForegroundColor Yellow
    Write-Host '$env:TOKEN = "your_digitalocean_api_token_here"' -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Get your token at: https://cloud.digitalocean.com/account/api/tokens" -ForegroundColor Yellow
    exit 1
}

# Create droplet
Write-Host "Creating droplet..." -ForegroundColor Yellow

$headers = @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer $env:TOKEN"
}

$body = @{
    name = "ai-employee-prod"
    size = "s-1vcpu-1gb"
    region = "sfo3"
    image = "ubuntu-22-04-x64"
    monitoring = $true
    tags = @("ai-employee", "production")
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "https://api.digitalocean.com/v2/droplets" -Method Post -Headers $headers -Body $body
    
    Write-Host "✅ Droplet created successfully!" -ForegroundColor Green
    Write-Host ""
    
    $dropletId = $response.droplet.id
    Write-Host "📋 Droplet ID: $dropletId" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "⏳ Waiting for droplet to be ready (this takes about 60 seconds)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 60
    
    # Get droplet details
    Write-Host "🔍 Getting droplet IP address..." -ForegroundColor Yellow
    $details = Invoke-RestMethod -Uri "https://api.digitalocean.com/v2/droplets/$dropletId" -Method Get -Headers $headers
    
    $ipAddress = $details.droplet.networks.v4 | Where-Object { $_.type -eq "public" } | Select-Object -First 1 -ExpandProperty ip_address
    
    if ($ipAddress) {
        Write-Host ""
        Write-Host "✅ Droplet is ready!" -ForegroundColor Green
        Write-Host ""
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
        Write-Host "📊 DROPLET DETAILS" -ForegroundColor Cyan
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
        Write-Host "Name:       ai-employee-prod"
        Write-Host "IP Address: $ipAddress" -ForegroundColor Green
        Write-Host "Droplet ID: $dropletId"
        Write-Host "Region:     San Francisco (sfo3)"
        Write-Host "Size:       1GB RAM / 1 vCPU / 25GB SSD"
        Write-Host "Cost:       `$6/month"
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "🔐 NEXT STEPS:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "1. Get your root password from DigitalOcean dashboard:"
        Write-Host "   https://cloud.digitalocean.com/droplets/$dropletId" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "2. SSH into your droplet:"
        Write-Host "   ssh root@$ipAddress" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "3. Run the deployment script:"
        Write-Host "   curl -fsSL https://raw.githubusercontent.com/Hammton/AI-employee/main/deploy_vps.sh -o deploy.sh" -ForegroundColor Cyan
        Write-Host "   chmod +x deploy.sh" -ForegroundColor Cyan
        Write-Host "   ./deploy.sh" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
        
        # Save details to file
        $info = @"
DigitalOcean Droplet Information
================================

Name:       ai-employee-prod
IP Address: $ipAddress
Droplet ID: $dropletId
Region:     San Francisco (sfo3)
Size:       1GB RAM / 1 vCPU / 25GB SSD
Cost:       `$6/month
Created:    $(Get-Date)

SSH Command:
ssh root@$ipAddress

Dashboard:
https://cloud.digitalocean.com/droplets/$dropletId

Next Steps:
1. Get root password from dashboard
2. SSH into droplet
3. Run deployment script
"@
        
        $info | Out-File -FilePath "droplet_info.txt" -Encoding UTF8
        
        Write-Host "💾 Droplet info saved to: droplet_info.txt" -ForegroundColor Green
        Write-Host ""
    } else {
        Write-Host "⏳ Droplet is still initializing. Check dashboard:" -ForegroundColor Yellow
        Write-Host "   https://cloud.digitalocean.com/droplets/$dropletId" -ForegroundColor Cyan
    }
} catch {
    Write-Host "❌ Error creating droplet!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Error details:" -ForegroundColor Yellow
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "- Invalid API token"
    Write-Host "- Insufficient permissions"
    Write-Host "- Region not available"
    Write-Host "- Billing issue"
}
