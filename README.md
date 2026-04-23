# 🎵 NavoHub - Telegram Music Bot

Professional Telegram bot for music search and download.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure bot
cp config/.env.example config/.env
# Edit config/.env and add your BOT_TOKEN

# Setup YouTube cookies (IMPORTANT!)
python scripts/setup_cookies.py
# Or manually: docs/COOKIES.md

# Run bot (Production)
python bot.py

# Run bot (Development - Auto-reload)
python dev.py
```

## 🍪 YouTube Cookie Setup (REQUIRED)

YouTube bot detection'dan qochish uchun cookie kerak:

```bash
# Lokal kompyuter (avtomatik)
python scripts/setup_cookies.py

# Server (manual)
# 1. Chrome extension: "Get cookies.txt LOCALLY"
# 2. YouTube'ga login qiling
# 3. Cookie export qiling
# 4. scripts/cookies.txt ga joylang
```

To'liq qo'llanma: [docs/COOKIES.md](docs/COOKIES.md)

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

- **Heroku**: `git push heroku main`
- **Railway**: `railway up`
- **Render**: `render.yaml` ishlatadi
- **VPS**: Systemd service

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
