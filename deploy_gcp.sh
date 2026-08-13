#!/bin/bash
set -e

echo "========================================================"
echo "🚀 DEPLOYING TABFM TRADING PREDICTOR ON GCP VM"
echo "========================================================"

# 1. System Updates & Essential Tools
echo "📦 1/6: Installing System Dependencies (Python, Node, Build tools)..."
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git curl build-essential

# 2. Install Node.js (v20 LTS) & PM2 if not present
if ! command -v node &> /dev/null; then
    echo "📦 Installing Node.js LTS..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

if ! command -v pm2 &> /dev/null; then
    echo "🔧 Installing PM2 Process Manager..."
    sudo npm install -g pm2
fi

# 3. Setup Python Virtual Environment & Dependencies
echo "🐍 2/6: Setting up Python Virtual Environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. Build React Production Bundle
echo "🎨 3/6: Building React Frontend..."
cd web
npm install
npm run build
cd ..

# 5. Stop previous PM2 instance if running
pm2 delete trading-app 2>/dev/null || true

# 6. Launch FastAPI Backend via PM2
echo "⚙️ 4/6: Starting FastAPI Backend on Port 8000..."
pm2 start "venv/bin/python web/server.py" --name "trading-app"
pm2 save

# 7. Install Cloudflared (Quick Tunnel as in RentalBox)
echo "☁️ 5/6: Configuring Cloudflare Tunnel..."
if ! command -v cloudflared &> /dev/null; then
    echo "📥 Downloading Cloudflared..."
    curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
    sudo dpkg -i cloudflared.deb
    rm cloudflared.deb
fi

# Kill old cloudflared tunnels
pkill -f "cloudflared tunnel" 2>/dev/null || true

# 8. Start Cloudflared Tunnel
echo "🌐 6/6: Starting Cloudflare Quick Tunnel..."
nohup cloudflared tunnel --url http://127.0.0.1:8000 > cf.log 2>&1 &

echo "========================================================"
echo "✅ DEPLOYMENT COMPLETED SUCCESSFULLY!"
echo "========================================================"
echo "⏳ Waiting for Cloudflare Tunnel URL..."
sleep 4

echo "📄 Public URL:"
grep -o "https://[a-zA-Z0-9-]*\.trycloudflare\.com" cf.log | tail -n 1 || echo "Please check cf.log for tunnel URL"
echo "========================================================"
