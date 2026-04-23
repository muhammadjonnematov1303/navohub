# ✅ Render Deploy Checklist

## O'zgartirilgan Fayllar

### 1. bot.py
- ✅ Health check server qo'shildi (`/health` endpoint)
- ✅ `aiohttp.web` server ishga tushadi
- ✅ PORT environment variable'dan o'qiydi

### 2. render.yaml
- ✅ Web service konfiguratsiyasi
- ✅ Build va start commands
- ✅ Health check path: `/health`
- ✅ Disk mount (1GB)
- ✅ Auto-deploy yoqilgan

### 3. .renderignore
- ✅ Keraksiz fayllarni ignore qiladi
- ✅ Docker va Railway fayllarini o'tkazib yuboradi

### 4. config/.env.example
- ✅ PORT=8080 qo'shildi

### 5. README.md
- ✅ Render deploy qo'llanmasi qo'shildi

### 6. docs/DEPLOYMENT.md
- ✅ To'liq Render deploy qo'llanmasi
- ✅ Troubleshooting bo'limi

### 7. RENDER_DEPLOY.md (YANGI)
- ✅ Qisqa 5 daqiqalik qo'llanma
- ✅ Step-by-step instructions

### 8. render-build.sh (YANGI)
- ✅ Build script (optional)

---

## Deploy Qadamlari

### 1. GitHub'ga Push
```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### 2. Render Dashboard
1. https://dashboard.render.com ga kiring
2. "New +" → "Blueprint"
3. GitHub repository ulang
4. "Apply" bosing

### 3. Environment Variables
```
BOT_TOKEN=your_bot_token_here
PORT=8080
```

### 4. Deploy!
Render avtomatik deploy qiladi (2-3 daqiqa)

---

## Tekshirish

- [ ] Logs'da "✅ Bot tayyor" ko'rinadi
- [ ] Health check "Healthy"
- [ ] Bot Telegram'da javob beradi
- [ ] `/start` buyrug'i ishlaydi
- [ ] Musiqa qidiruv ishlaydi

---

## Muammolar?

**Bot sleep mode'ga tushadi?**
- Bepul plan'da 15 daqiqa inactivity'dan keyin sleep
- Polling ishlaydi, lekin birinchi request sekin bo'lishi mumkin

**Deploy fails?**
- Build logs'ni tekshiring
- `requirements.txt` to'g'ri ekanligini tekshiring

**Health check fails?**
- `/health` endpoint ishlayotganini tekshiring
- PORT environment variable to'g'ri o'rnatilganini tekshiring

---

## Yordam

- 📖 [Qisqa qo'llanma](RENDER_DEPLOY.md)
- 📖 [To'liq qo'llanma](docs/DEPLOYMENT.md)
- 💬 Telegram: @MuhammadjonXP_Admin
