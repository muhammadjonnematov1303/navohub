# 🎵 NavoHub — Telegram Musiqa va Video Bot

Telegram bot - musiqa qidirish va video yuklash tizimi bilan.

## ✨ Imkoniyatlar

### 🎵 Musiqa qidiruv
- Foydalanuvchi yozgan nom bo'yicha aniq musiqa topiladi
- YouTube API orqali ultra tez qidiruv (0.3-2 soniya)
- Eng mos 10 ta natija ko'rsatiladi
- Har bir natija:
  - 🎵 Nomi
  - 👤 Ijrochisi
  - ⏱ Davomiyligi
  - 👁 Ko'rishlar soni
  - 🖼 Cover rasmi
- MP3 formatda yuklab beriladi

### 🎬 Video yuklash
- YouTube, TikTok, Instagram qo'llab-quvvatlanadi
- Format tanlash (inline tugmalar):
  - 144p, 240p, 360p, 480p, 720p, 1080p, 4K
  - Original sifat
  - 🎵 MP3 (faqat audio)
  - 🖼 Picture preview
- Tanlangan format bo'yicha yuklab beriladi

### ⚡ Tezlik va optimizatsiya
- Cache tizimi (24 soat)
- Qidiruv 2-4 soniyadan oshmasin
- Parallel yuklab olish
- Xatoliklar chiroyli ko'rsatiladi

### 🎨 UX/UI
- Chiroyli va tartibli tugmalar
- Tushunarli xabarlar
- Agar musiqa topilmasa → "Kechirasiz, topilmadi 😔"
- Agar link noto'g'ri → "Link noto'g'ri yoki qo'llab-quvvatlanmaydi ❌"

## 🚀 O'rnatish

### 1. Talablar
```bash
pip install -r requirements.txt
```

### 2. Sozlash
`.env` faylini yarating:
```env
BOT_TOKEN=sizning_bot_tokeningiz
```

### 3. Ishga tushirish
```bash
python music_bot.py
```

## 📋 Buyruqlar

- `/start` — Botni boshlash
- `/help` yoki `/yordam` — Qo'llanma

## 🎯 Foydalanish

### Musiqa qidirish
1. Qo'shiq nomini yozing: `Mirjalol Nematov Nozka`
2. Bot 10 ta natija ko'rsatadi
3. Raqam bosib yuklab oling

### Video yuklash
1. Havola yuboring: `https://youtube.com/watch?v=...`
2. Format tanlang (144p - 1080p, MP3, rasm)
3. Yuklab oling

## 🛠 Texnologiyalar

- **aiogram 3.7** — Telegram Bot API
- **yt-dlp** — Video/audio yuklash
- **aiohttp** — Async HTTP
- **FFmpeg** — Media konvertatsiya

## 📦 Fayl tuzilishi

```
NavoHub/
├── music_bot.py          # Asosiy bot
├── requirements.txt      # Python kutubxonalari
├── .env                  # Sozlamalar
├── downloads/            # Vaqtinchalik fayllar
├── users.json           # Foydalanuvchilar
└── ffmpeg/              # FFmpeg (avtomatik yuklanadi)
```

## ⚙️ Sozlamalar

`music_bot.py` faylida:
- `SEARCH_LIMIT = 10` — Qidiruv natijalari soni
- `MAX_DURATION = 1200` — Maksimal davomiylik (20 daqiqa)
- `MAX_FILE_MB = 50` — Maksimal fayl hajmi
- `CACHE_TTL = 86400` — Cache muddati (24 soat)

## 🔒 Xavfsizlik

- Bot tokeni `.env` faylida saqlanadi
- Fayllar avtomatik tozalanadi
- Session tizimi (1 soat)

## 📝 Litsenziya

MIT License

## 👨‍💻 Muallif

- **Dasturchi:** @MuhammadjonXP
- **Admin:** @MuhammadjonXP_Admin

---

🤖 Bot: https://t.me/NavoHubBot
