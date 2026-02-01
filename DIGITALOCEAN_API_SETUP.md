# 🚀 DigitalOcean API Deployment Guide

## Quick Setup (3 Steps)

### Step 1: Get Your API Token

1. Go to **https://cloud.digitalocean.com/account/api/tokens**
2. Click **"Generate New Token"**
3. Name: `ai-employee-deployment`
4. Check **"Write"** scope
5. Click **"Generate Token"**
6. **Copy the token** (you won't see it again!)

---

### Step 2: Create Droplet via API

**On Windows (PowerShell):**

```powershell
# Set your API token
$env:TOKEN = "your_digitalocean_api_token_here"

# Run the script
.\create_droplet.ps1
```

**On Linux/Mac (Bash):**

```bash
# Set your API token
export TOKEN='your_digitalocean_api_token_here'

# Run the script
bash create_droplet.sh
```

**Or use curl directly:**

```bash
curl -X POST -H 'Content-Type: application/json' \
-H "Authorization: Bearer $TOKEN" \
-d '{
  "name":"ai-employee-prod",
  "size":"s-1vcpu-1gb",
  "region":"sfo3",
  "image":"ubuntu-22-04-x64",
  "monitoring":true,
  "tags":["ai-employee","production"]
}' \
"https://api.digitalocean.com/v2/droplets"
```

---

### Step 3: Deploy Your AI Employee

After the droplet is created (takes ~60 seconds):

1. **Get the IP address** from the script output or dashboard
2. **Get root password** from DigitalOcean email or dashboard
3. **SSH into droplet:**
   ```bash
   ssh root@YOUR_DROPLET_IP
   ```
4. **Run deployment script:**
   ```bash
   curl -fsSL https://raw.githubusercontent.com/Hammton/AI-employee/main/deploy_vps.sh -o deploy.sh
   chmod +x deploy.sh
   ./deploy.sh
   ```

---

## 📊 Droplet Specifications

| Setting | Value |
|---------|-------|
| **Name** | ai-employee-prod |
| **OS** | Ubuntu 22.04 LTS |
| **Size** | s-1vcpu-1gb |
| **RAM** | 1 GB |
| **CPU** | 1 vCPU |
| **Storage** | 25 GB SSD |
| **Transfer** | 1000 GB |
| **Region** | San Francisco (sfo3) |
| **Cost** | $6/month |
| **Monitoring** | Enabled |

---

## 🌍 Available Regions

You can change the region in the script. Popular options:

| Region Code | Location |
|-------------|----------|
| `nyc1`, `nyc3` | New York |
| `sfo3` | San Francisco |
| `tor1` | Toronto |
| `lon1` | London |
| `fra1` | Frankfurt |
| `ams3` | Amsterdam |
| `sgp1` | Singapore |
| `blr1` | Bangalore |

---

## 💰 Pricing

- **Droplet:** $6/month
- **Backups:** +$1.20/month (optional)
- **Monitoring:** Free
- **Bandwidth:** 1TB included (free)

**Total:** $6-7/month

---

## 🔧 Advanced Options

### Create with SSH Key (More Secure)

1. **Add SSH key to DigitalOcean:**
   - Go to https://cloud.digitalocean.com/account/security
   - Click "Add SSH Key"
   - Paste your public key

2. **Get SSH key ID:**
   ```bash
   curl -X GET -H "Authorization: Bearer $TOKEN" \
   "https://api.digitalocean.com/v2/account/keys"
   ```

3. **Create droplet with SSH key:**
   ```bash
   curl -X POST -H 'Content-Type: application/json' \
   -H "Authorization: Bearer $TOKEN" \
   -d '{
     "name":"ai-employee-prod",
     "size":"s-1vcpu-1gb",
     "region":"sfo3",
     "image":"ubuntu-22-04-x64",
     "ssh_keys":["YOUR_SSH_KEY_ID"],
     "monitoring":true
   }' \
   "https://api.digitalocean.com/v2/droplets"
   ```

---

## 📋 Useful API Commands

### List All Droplets
```bash
curl -X GET -H "Authorization: Bearer $TOKEN" \
"https://api.digitalocean.com/v2/droplets"
```

### Get Droplet Details
```bash
curl -X GET -H "Authorization: Bearer $TOKEN" \
"https://api.digitalocean.com/v2/droplets/DROPLET_ID"
```

### Delete Droplet
```bash
curl -X DELETE -H "Authorization: Bearer $TOKEN" \
"https://api.digitalocean.com/v2/droplets/DROPLET_ID"
```

### List Available Sizes
```bash
curl -X GET -H "Authorization: Bearer $TOKEN" \
"https://api.digitalocean.com/v2/sizes"
```

### List Available Regions
```bash
curl -X GET -H "Authorization: Bearer $TOKEN" \
"https://api.digitalocean.com/v2/regions"
```

---

## 🚨 Troubleshooting

### Error: "Unable to authenticate"
**Solution:** Check your API token is correct and has "Write" scope

### Error: "Region not available"
**Solution:** Try a different region (e.g., `nyc3` instead of `sfo3`)

### Error: "Size not available"
**Solution:** The $6/month plan might not be available in that region. Try another region.

### Error: "Billing issue"
**Solution:** Add a payment method to your DigitalOcean account

### Can't SSH into droplet
**Solution:** 
- Wait 2-3 minutes for droplet to fully boot
- Check your firewall isn't blocking port 22
- Get root password from DigitalOcean dashboard

---

## ✅ Quick Checklist

- [ ] Got DigitalOcean API token
- [ ] Set TOKEN environment variable
- [ ] Ran create_droplet script
- [ ] Got droplet IP address
- [ ] Got root password from dashboard
- [ ] SSH'd into droplet
- [ ] Ran deployment script
- [ ] Connected WhatsApp
- [ ] Tested AI employee

---

## 🎯 Next Steps After Creation

1. **SSH into droplet:**
   ```bash
   ssh root@YOUR_IP
   ```

2. **Run deployment:**
   ```bash
   curl -fsSL https://raw.githubusercontent.com/Hammton/AI-employee/main/deploy_vps.sh -o deploy.sh
   chmod +x deploy.sh
   ./deploy.sh
   ```

3. **Connect WhatsApp** (follow prompts)

4. **Test it!**

---

## 📚 Documentation

- **DigitalOcean API Docs:** https://docs.digitalocean.com/reference/api/
- **Droplet Creation:** https://docs.digitalocean.com/reference/api/api-reference/#operation/droplets_create
- **Full Deployment Guide:** See `DEPLOYMENT_GUIDE.md`

---

**Your droplet will be ready in ~60 seconds!** 🚀

After creation, follow the deployment steps to install your AI employee.
