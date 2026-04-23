# 🎵 NavoHub - Telegram Music Bot

Professional Telegram bot for music search and download.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure bot
cp config/.env.example config/.env
# Edit config/.env and add your BOT_TOKEN

# Run bot (Production)
python bot.py

# Run bot (Development - Auto-reload)
python dev.py
```

## 🔥 Development Mode

Development mode'da bot avtomatik qayta ishga tushadi:

```bash
python dev.py
```

**Xususiyatlar:**
- ✅ Fayl o'zgarganda avtomatik restart
- ✅ Real-time development
- ✅ Nodemon'ga o'xshash
- ✅ Ctrl+C bilan to'xtatish

## 🐳 Docker Deployment

```bash
# Docker Compose (Tavsiya etiladi)
docker-compose up -d

# Yoki Docker
docker build -t navohub-bot .
docker run -d --name navohub-bot -e BOT_TOKEN="your_token" navohub-bot
```

## ☁️ Cloud Deployment

### Render (Tavsiya etiladi - Bepul)

1. **GitHub'ga push qiling:**
   ```bash
   git add .
   git commit -m "Ready for Render deployment"
   git push origin main
   ```

2. **Render.com'da:**
   - [Render Dashboard](https://dashboard.render.com) ga kiring
   - "New +" → "Blueprint" tanlang
   - GitHub repository'ni ulang
   - `render.yaml` avtomatik topiladi
   - Environment Variables'ga `BOT_TOKEN` qo'shing
   - "Apply" bosing

3. **Deploy tugagach:**
   - Bot avtomatik ishga tushadi
   - Health check `/health` endpoint orqali ishlaydi
   - Logs'ni Render dashboard'dan ko'ring

**Render xususiyatlari:**
- ✅ Bepul plan (750 soat/oy)
- ✅ Avtomatik deploy (git push)
- ✅ 1GB disk space
- ✅ SSL sertifikat
- ✅ Health check monitoring

### Railway

```bash
railway login
railway init
railway up
```

### Heroku

```bash
git push heroku main
```

### VPS (Ubuntu/Debian)

```bash
# Systemd service
sudo systemctl enable navohub-bot
sudo systemctl start navohub-bot
```

To'liq qo'llanma: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

## 📁 Project Structure

```
NavoHub/
├── bot.py                  # Main bot
├── config/                 # Configuration
│   ├── .env               # Environment variables
│   └── .env.example       # Example config
├── data/                   # Data files
│   └── users.json         # Users database
├── docs/                   # Documentation
│   ├── README.md          # Full documentation
│   ├── CHANGELOG.md       # Version history
│   └── OPTIMIZATION.md    # Optimization report
├── scripts/                # Utility scripts
│   └── setup_cookies.py   # Cookie setup
├── .gitignore
├── LICENSE
└── requirements.txt
```

## ✨ Features

- 🔍 Fast music search (YouTube InnerTube API)
- 🎵 MP3 download with metadata
- 🎬 Video download (144p - 1080p)
- 📊 Real-time progress bar
- 💾 Smart caching system
- 🖼 Thumbnail support
- ⚡ Optimized performance

## 📚 Documentation

Full documentation: [docs/README.md](docs/README.md)

## 👨‍💻 Author

- **Developer:** @MuhammadjonXP
- **Admin:** @MuhammadjonXP_Admin

## 📝 License

MIT License - see [LICENSE](LICENSE) file

---

🤖 Bot: https://t.me/NavoHubBot
