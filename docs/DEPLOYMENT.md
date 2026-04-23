# 🚀 NavoHub Bot - Deployment Guide

Bot'ni turli platformalarga deploy qilish qo'llanmasi.

---

## 📋 Talab Qilinadigan Narsalar

- Python 3.11+
- FFmpeg
- 2GB RAM (minimal)
- BOT_TOKEN (BotFather'dan)

---

## 🐳 Docker (Tavsiya Etiladi)

### 1. Docker Build

```bash
docker build -t navohub-bot .
```

### 2. Docker Run

```bash
docker run -d \
  --name navohub-bot \
  --restart unless-stopped \
  -e BOT_TOKEN="your_bot_token_here" \
  -v $(pwd)/data:/app/data \
  navohub-bot
```

### 3. Docker Compose

```bash
# .env faylini sozlang
cp config/.env.example config/.env
nano config/.env

# Ishga tushiring
docker-compose up -d

# Loglarni ko'rish
docker-compose logs -f

# To'xtatish
docker-compose down
```

---

## ☁️ Heroku

### 1. Heroku CLI O'rnatish

```bash
# Windows
winget install Heroku.HerokuCLI

# Mac
brew tap heroku/brew && brew install heroku

# Linux
curl https://cli-assets.heroku.com/install.sh | sh
```

### 2. Deploy

```bash
# Login
heroku login

# App yaratish
heroku create navohub-bot

# Config o'rnatish
heroku config:set BOT_TOKEN="your_bot_token_here"

# Deploy
git push heroku main

# Loglarni ko'rish
heroku logs --tail
```

---

## 🚂 Railway

### 1. Railway CLI

```bash
npm i -g @railway/cli
railway login
```

### 2. Deploy

```bash
# Yangi project
railway init

# Config
railway variables set BOT_TOKEN="your_bot_token_here"

# Deploy
railway up

# Loglar
railway logs
```

### 3. Web Dashboard

1. https://railway.app ga kiring
2. "New Project" → "Deploy from GitHub"
3. Repository tanlang
4. Environment Variables qo'shing:
   - `BOT_TOKEN`: your_bot_token_here
5. Deploy!

---

## 🎨 Render (Tavsiya Etiladi - Bepul)

### 1. GitHub'ga Push

```bash
# Barcha o'zgarishlarni commit qiling
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### 2. Render Dashboard

1. [Render.com](https://render.com) ga kiring (GitHub bilan)
2. "New +" → "Blueprint" tanlang
3. GitHub repository'ni ulang
4. `render.yaml` avtomatik topiladi va quyidagi sozlamalar qo'llaniladi:
   - **Service Type**: Web Service
   - **Name**: navohub-bot
   - **Environment**: Python 3
   - **Region**: Oregon (yoki yaqin region)
   - **Plan**: Free
   - **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt && mkdir -p data scripts`
   - **Start Command**: `python bot.py`
   - **Health Check**: `/health` endpoint

### 3. Environment Variables

Render dashboard'da Environment Variables qo'shing:

```
BOT_TOKEN=your_bot_token_here
PORT=8080
```

### 4. Deploy

"Apply" tugmasini bosing. Render avtomatik:
- Repository'ni clone qiladi
- Dependencies o'rnatadi
- Bot'ni ishga tushiradi
- Health check orqali monitoring qiladi

### 5. Monitoring

```bash
# Render dashboard'da:
- Logs: Real-time loglarni ko'rish
- Metrics: CPU, Memory, Network
- Events: Deploy history
- Shell: SSH access (paid plans)
```

### 6. Auto-Deploy

Har safar `git push` qilganingizda, Render avtomatik yangi versiyani deploy qiladi.

### Render Xususiyatlari

**Bepul Plan:**
- ✅ 750 soat/oy (1 service uchun)
- ✅ 512 MB RAM
- ✅ 1 GB disk space
- ✅ Avtomatik SSL
- ✅ Health check monitoring
- ✅ GitHub auto-deploy
- ⚠️ 15 daqiqa inactivity'dan keyin sleep mode

**Paid Plans ($7/mo):**
- ✅ 24/7 uptime (sleep yo'q)
- ✅ 2 GB RAM
- ✅ SSH access
- ✅ Custom domains

### Render vs Boshqalar

| Feature | Render | Heroku | Railway |
|---------|--------|--------|---------|
| Bepul plan | ✅ 750h | ❌ Yo'q | ✅ $5 credit |
| Auto-deploy | ✅ | ✅ | ✅ |
| Sleep mode | ⚠️ 15min | ⚠️ 30min | ❌ Yo'q |
| Disk space | 1 GB | 512 MB | 1 GB |
| Setup | Oson | O'rtacha | Oson |

### Troubleshooting

**Bot sleep mode'ga tushadi?**
- Bepul plan'da 15 daqiqa inactivity'dan keyin sleep
- Birinchi request'da 30-60 soniya wake up vaqti
- Yechim: Paid plan ($7/mo) yoki cron job bilan ping

**Health check fail?**
- `/health` endpoint ishlayotganini tekshiring
- Logs'da xatolarni qidiring
- PORT environment variable to'g'ri o'rnatilganini tekshiring

**Deploy fails?**
- `requirements.txt` to'g'ri formatda ekanligini tekshiring
- Python version'ni tekshiring (3.11)
- Build logs'ni o'qing

---

## 🐧 VPS (Ubuntu/Debian)

### 1. Server Tayyorlash

```bash
# Update
sudo apt update && sudo apt upgrade -y

# Python va FFmpeg
sudo apt install -y python3.11 python3-pip ffmpeg git

# Project clone
git clone https://github.com/yourusername/NavoHub.git
cd NavoHub
```

### 2. Virtual Environment

```bash
# Venv yaratish
python3 -m venv .venv

# Aktivlashtirish
source .venv/bin/activate

# Dependencies
pip install -r requirements.txt
```

### 3. Config

```bash
# .env sozlash
cp config/.env.example config/.env
nano config/.env
# BOT_TOKEN ni kiriting
```

### 4. Systemd Service

```bash
# Service fayl yaratish
sudo nano /etc/systemd/system/navohub.service
```

Quyidagini kiriting:

```ini
[Unit]
Description=NavoHub Telegram Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/NavoHub
Environment="PATH=/home/your_username/NavoHub/.venv/bin"
ExecStart=/home/your_username/NavoHub/.venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Service yoqish
sudo systemctl daemon-reload
sudo systemctl enable navohub
sudo systemctl start navohub

# Status
sudo systemctl status navohub

# Loglar
sudo journalctl -u navohub -f
```

---

## 🔄 PM2 (Node.js Process Manager)

```bash
# PM2 o'rnatish
npm install -g pm2

# Bot ishga tushirish
pm2 start bot.py --name navohub-bot --interpreter python3

# Auto-restart
pm2 startup
pm2 save

# Monitoring
pm2 monit

# Loglar
pm2 logs navohub-bot

# Restart
pm2 restart navohub-bot

# Stop
pm2 stop navohub-bot
```

---

## 📊 Monitoring

### Loglar

```bash
# Real-time
tail -f data/activity.log

# Oxirgi 100 qator
tail -n 100 data/activity.log

# Qidiruv
grep "ERROR" data/activity.log
```

### Health Check

Bot ishlayotganini tekshirish:

```bash
# Process
ps aux | grep bot.py

# Port (agar webhook ishlatilsa)
netstat -tulpn | grep python
```

---

## 🔐 Xavfsizlik

### 1. Environment Variables

```bash
# .env faylini himoyalash
chmod 600 config/.env

# Git'ga qo'shmaslik
echo "config/.env" >> .gitignore
```

### 2. Firewall

```bash
# UFW (Ubuntu)
sudo ufw allow ssh
sudo ufw enable
```

### 3. Updates

```bash
# Muntazam yangilash
git pull
pip install -r requirements.txt --upgrade
sudo systemctl restart navohub
```

---

## 🐛 Troubleshooting

### Bot ishlamayapti?

```bash
# Loglarni tekshirish
tail -f data/activity.log

# Python xatolari
python bot.py

# Dependencies
pip install -r requirements.txt --force-reinstall
```

### FFmpeg topilmayapti?

```bash
# O'rnatish
sudo apt install ffmpeg  # Linux
brew install ffmpeg      # Mac
# Windows: https://ffmpeg.org/download.html
```

### Memory muammolari?

```bash
# RAM tekshirish
free -h

# Swap qo'shish (Linux)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 📈 Scaling

### Multiple Instances

Bir nechta bot nusxasini ishga tushirish uchun:

```bash
# Instance 1
BOT_TOKEN="token1" python bot.py &

# Instance 2
BOT_TOKEN="token2" python bot.py &
```

### Load Balancing

Nginx yoki HAProxy ishlatish mumkin.

---

## 🎯 Best Practices

1. ✅ **Docker ishlatish** (izolyatsiya va portability)
2. ✅ **Systemd/PM2** (auto-restart)
3. ✅ **Monitoring** (loglar va alertlar)
4. ✅ **Backup** (data/ papkasi)
5. ✅ **Updates** (muntazam yangilash)
6. ✅ **Security** (firewall, env vars)

---

## 📞 Yordam

Muammo bo'lsa:
- GitHub Issues: https://github.com/yourusername/NavoHub/issues
- Telegram: @MuhammadjonXP_Admin

---

**Muvaffaqiyatli deploy qiling!** 🚀
