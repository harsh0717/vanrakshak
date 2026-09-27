# VanRakshak AI — Production Deployment Guide

This guide covers the simplest and most reliable ways to deploy the **VanRakshak AI** platform to production or live demo environments.

---

## ⚡ Option 1: Free Cloud Hosting on Render.com (Recommended — 3 Minutes)

Render provides free hosting with automatic HTTPS, continuous deployment from GitHub, and zero configuration.

### Steps:
1. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "Prepare VanRakshak for production deployment"
   git push origin main
   ```
2. **Go to [render.com](https://render.com)** and sign in with GitHub.
3. Click **New +** $\rightarrow$ **Web Service**.
4. Connect your GitHub repository (`vanrakshak`).
5. Configure the settings (or let Render detect `render.yaml` automatically):
   - **Name**: `vanrakshak-ai`
   - **Environment**: `Python`
   - **Region**: `Singapore` or `Oregon` (closest to your users)
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Plan**: `Free`
6. Click **Create Web Service**.
7. Once deployed, Render provides a free live HTTPS URL:
   `https://vanrakshak-ai.onrender.com`

---

## 🚂 Option 2: Railway.app (1-Click Deployment)

1. Go to [railway.app](https://railway.app) and log in.
2. Click **New Project** $\rightarrow$ **Deploy from GitHub repo**.
3. Select your `vanrakshak` repository.
4. Railway automatically reads the included `Procfile` and builds the environment.
5. In your project settings, click **Generate Domain** to get a public URL.

---

## 🐳 Option 3: Docker / Docker Compose (Any Cloud VPS / AWS / DigitalOcean)

The project includes a ready-to-run [Dockerfile](file:///d:/vanrakshak/Dockerfile) and [docker-compose.yml](file:///d:/vanrakshak/docker-compose.yml).

### Run with Docker:
```bash
# Build container image
docker build -t vanrakshak:latest .

# Run container on port 5000
docker run -d -p 5000:5000 --name vanrakshak vanrakshak:latest
```

### Run with Docker Compose:
```bash
docker compose up -d
```
Your application will be live at `http://your-server-ip:5000`.

---

## 🖥️ Option 4: Linux Virtual Machine (Ubuntu 22.04 / 24.04 VPS with Nginx + SSL)

If deploying to a DigitalOcean Droplet, AWS EC2, or Azure VM:

### 1. Install System Dependencies:
```bash
sudo apt update && sudo apt install -y python3-pip python3-venv nginx git
```

### 2. Clone and Setup Environment:
```bash
cd /var/www
sudo git clone https://github.com/HARHIL-PATIL/vanrakshak.git
cd vanrakshak
sudo python3 -m venv .venv
sudo .venv/bin/pip install -r requirements.txt
```

### 3. Create Systemd Service (`/etc/systemd/system/vanrakshak.service`):
```ini
[Unit]
Description=VanRakshak AI Production Service
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/vanrakshak
ExecStart=/var/www/vanrakshak/.venv/bin/gunicorn app:app --bind 127.0.0.1:5000 --workers 3
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable vanrakshak
sudo systemctl start vanrakshak
```

### 4. Configure Nginx Reverse Proxy (`/etc/nginx/sites-available/vanrakshak`):
```nginx
server {
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site & get free Let's Encrypt SSL:
```bash
sudo ln -s /etc/nginx/sites-available/vanrakshak /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d your-domain.com
```

---

## 🔐 Credentials for Demo Evaluators
- **Public Citizen Portal**: No credentials required (open access).
- **Officer Command Console**:
  - **Officer ID**: `admin@1234`
  - **Password**: `harshil`
  - **Officer Name**: Harshil Patil (Chief Range Forest Officer & Administrator)
