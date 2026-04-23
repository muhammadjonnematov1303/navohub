# 🚀 Render'ga Deploy Qilish (5 daqiqa)

NavoHub bot'ni Render platformasiga deploy qilish uchun qisqa qo'llanma.

---

## 📋 Kerakli Narsalar

- ✅ GitHub account
- ✅ Render account ([render.com](https://render.com) - bepul)
- ✅ Telegram Bot Token ([@BotFather](https://t.me/BotFather) dan)

---

## 🎯 Deploy Qadamlari

### 1️⃣ GitHub'ga Push

```bash
# Repository'ni GitHub'ga yuklang
git add .
git commit -m "Ready for Render"
git push origin main
```

### 2️⃣ Render'da Blueprint Deploy

1. [Render Dashboard](https://dashboard.render.com) ga kiring
2. **"New +"** → **"Blueprint"** tanlang
3. **"Connect a repository"** → GitHub'ni ulang
4. Repository'ni tanlang (NavoHub)
5. `render.yaml` avtomatik topiladi
6. **"Apply"** bosing

### 3️⃣ Environment Variables

Deploy jarayonida yoki keyin qo'shing:

```
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
PORT=8080
```

**Bot Token olish:**
1. Telegram'da [@BotFather](https://t.me/BotFather) ga boring
2. `/newbot` buyrug'ini yuboring
3. Bot nomini kiriting
4. Username kiriting (masalan: `NavoHubBot`)
5. Token'ni nusxalang

### 4️⃣ Deploy Tugadi! 🎉

Render avtomatik:
- ✅ Dependencies o'rnatadi
- ✅ Bot'ni ishga tushiradi
- ✅ Health check qiladi
- ✅ Loglarni ko'rsatadi

---

## 📊 Monitoring

### Logs Ko'rish

Render dashboard → Service → **"Logs"** tab

```
⚙️  Bot sozlanmoqda...
🌐 Health check server ishga tushdi: port 8080
✅ Bot tayyor: @NavoHubBot
👂 Xabarlar kutilmoqda...
```

### Health Check

Render avtomatik `/health` endpoint'ni tekshiradi:
- ✅ **Healthy**: Bot ishlayapti
- ❌ **Unhealthy**: Bot xato berdi

---

## 🔄 Auto-Deploy

Har safar `git push` qilganingizda Render avtomatik yangi versiyani deploy qiladi:

```bash
# Kod o'zgartirish
git add .
git commit -m "Update bot"
git push origin main

# Render avtomatik deploy qiladi (1-2 daqiqa)
```

---

## ⚙️ Sozlamalar

### render.yaml

Loyihada `render.yaml` fayli bor, u quyidagi sozlamalarni o'z ichiga oladi:

```yaml
services:
  - type: web
    name: navohub-bot
    env: python
    region: oregon
    plan: free
    buildCommand: |
      pip install --upgrade pip
      pip install -r requirements.txt
      mkdir -p data scripts
    startCommand: python bot.py
    envVars:
      - key: BOT_TOKEN
        sync: false
      - key: PORT
        value: 8080
    healthCheckPath: /health
    autoDeploy: true
    disk:
      name: navohub-data
      mountPath: /opt/render/project/src/data
      sizeGB: 1
```

### Disk Space

Render bepul plan'da 1 GB disk space beradi. Bu quyidagilar uchun ishlatiladi:
- `data/users.json` - Foydalanuvchilar bazasi
- `data/stats.json` - Statistika
- `data/activity.log` - Loglar

---

## 💰 Narxlar

### Bepul Plan

- ✅ 750 soat/oy (1 service uchun)
- ✅ 512 MB RAM
- ✅ 1 GB disk
- ✅ Avtomatik SSL
- ⚠️ 15 daqiqa inactivity'dan keyin sleep mode

**Sleep Mode:**
- Bot 15 daqiqa ishlatilmasa sleep mode'ga tushadi
- Birinchi request'da 30-60 soniya wake up vaqti
- Telegram bot'lar uchun muammo emas (polling ishlaydi)

### Paid Plan ($7/mo)

- ✅ 24/7 uptime (sleep yo'q)
- ✅ 2 GB RAM
- ✅ 10 GB disk
- ✅ SSH access
- ✅ Custom domains

---

## 🐛 Troubleshooting

### Bot ishlamayapti?

1. **Logs tekshiring:**
   - Render dashboard → Logs
   - Xatolarni qidiring

2. **Environment variables:**
   - `BOT_TOKEN` to'g'ri o'rnatilganini tekshiring
   - `PORT=8080` mavjudligini tekshiring

3. **Health check:**
   - `/health` endpoint ishlayotganini tekshiring
   - Render dashboard'da "Healthy" yozuvini ko'ring

### Deploy fails?

1. **Build logs:**
   - Render dashboard → Events → Build logs
   - Xatolarni o'qing

2. **Dependencies:**
   - `requirements.txt` to'g'ri formatda ekanligini tekshiring
   - Python version 3.11 ishlatilayotganini tekshiring

3. **GitHub connection:**
   - Repository to'g'ri ulanganini tekshiring
   - `render.yaml` fayli mavjudligini tekshiring

### Sleep mode muammosi?

Bepul plan'da bot 15 daqiqa inactivity'dan keyin sleep mode'ga tushadi.

**Yechimlar:**
1. Paid plan ($7/mo) - 24/7 uptime
2. Cron job bilan ping (masalan, [cron-job.org](https://cron-job.org))
3. Boshqa platform (Railway, VPS)

---

## 📞 Yordam

Muammo bo'lsa:
- 📖 [To'liq qo'llanma](docs/DEPLOYMENT.md)
- 💬 Telegram: @MuhammadjonXP_Admin
- 🐛 GitHub Issues

---

## ✅ Checklist

Deploy qilishdan oldin:

- [ ] GitHub'ga push qildingizmi?
- [ ] Bot Token oldingizmi?
- [ ] Render account yaratdingizmi?
- [ ] `render.yaml` fayli mavjudmi?
- [ ] `.renderignore` fayli mavjudmi?

Deploy qilgandan keyin:

- [ ] Logs'da xato yo'qmi?
- [ ] Health check "Healthy"mi?
- [ ] Bot Telegram'da javob beradimi?
- [ ] Environment variables to'g'rimi?

---

**Muvaffaqiyatli deploy qiling!** 🚀

Bot: [@NavoHubBot](https://t.me/NavoHubBot)
