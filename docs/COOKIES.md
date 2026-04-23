# 🍪 YouTube Cookie Sozlash

YouTube bot detection'dan qochish uchun cookie kerak.

---

## ❓ Nega Cookie Kerak?

YouTube serverlar:
- ✅ Oddiy brauzerlarni qabul qiladi
- ❌ Botlarni bloklaydi (CAPTCHA chiqaradi)
- ❌ Server IP'larni shubhali deb biladi

Cookie = YouTube sizni "haqiqiy foydalanuvchi" deb biladi.

---

## 🚀 Variant 1: Avtomatik (Lokal Kompyuter)

Agar botni o'z kompyuteringizda ishlatayotgan bo'lsangiz:

```bash
# Chrome'ni to'liq yoping
python scripts/setup_cookies.py
```

Bu script:
1. Chrome'dan cookie'larni oladi
2. `scripts/cookies.txt` ga saqlaydi
3. Bot avtomatik ishlatadi

---

## 🌐 Variant 2: Manual (Render/Railway/VPS)

Server'da browser yo'q, shuning uchun qo'lda export qilish kerak.

### 1️⃣ Chrome Extension O'rnatish

Chrome Web Store'dan o'rnating:
👉 **[Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)**

### 2️⃣ YouTube'ga Login Qiling

1. YouTube.com ga kiring
2. Akkauntingizga login qiling
3. Biror video oching (masalan: https://youtube.com/watch?v=dQw4w9WgXcQ)

### 3️⃣ Cookie Export Qiling

1. Extension ikonasini bosing (Chrome toolbar'da)
2. "Export" tugmasini bosing
3. `cookies.txt` fayli yuklab olinadi

### 4️⃣ Projectga Joylang

**Lokal kompyuter:**
```bash
# Yuklab olingan faylni ko'chiring
cp ~/Downloads/cookies.txt scripts/cookies.txt
```

**Render.com/Railway:**
1. Repository'ga commit qiling:
```bash
cp ~/Downloads/cookies.txt scripts/cookies.txt
git add scripts/cookies.txt
git commit -m "Add YouTube cookies"
git push
```

2. Yoki Environment Variable sifatida (katta bo'lsa):
```bash
# cookies.txt ni base64 ga o'giring
base64 scripts/cookies.txt > cookies_base64.txt

# Render.com'da Environment Variable qo'shing:
# Key: YOUTUBE_COOKIES_BASE64
# Value: (cookies_base64.txt ichidagi matn)
```

---

## 🔧 Bot Konfiguratsiyasi

Bot avtomatik `scripts/cookies.txt` ni tekshiradi:

```python
# bot.py (allaqachon qo'shilgan)
COOKIES_FILE = BASE_DIR / "scripts" / "cookies.txt"

def _ydl_base_opts() -> dict:
    opts = {
        "quiet": True,
        "geo_bypass": True,
        # ...
    }
    if COOKIES_FILE.exists() and COOKIES_FILE.stat().st_size > 100:
        opts["cookiefile"] = str(COOKIES_FILE)
        log.info("[COOKIE]  cookies.txt ishlatilmoqda")
    return opts
```

---

## ⚠️ MUHIM Eslatmalar

### 1. Cookie Muddati
- Cookie'lar 7-30 kun ishlaydi
- Eskirsa → yana export qiling
- Bot logida "Sign in to confirm you're not a bot" ko'rinsa = cookie eskigan

### 2. Xavfsizlik
- Cookie'larni hech kimga bermang!
- `.gitignore` da `scripts/cookies.txt` bor (commit bo'lmaydi)
- Public repository'da cookie'ni commit qilmang!

### 3. Render.com Deploy
```bash
# .gitignore'da qo'shing (allaqachon bor):
scripts/cookies.txt

# Agar cookie kerak bo'lsa:
# 1. Lokal export qiling
# 2. Render.com'da manual upload qiling
# 3. Yoki environment variable ishlatng
```

---

## 🐛 Troubleshooting

### "Sign in to confirm you're not a bot"
```bash
# Cookie eskigan yoki yo'q
# Yechim: Yana export qiling
python scripts/setup_cookies.py
```

### "ERROR: unable to download video data"
```bash
# Cookie formati noto'g'ri
# Yechim: "Get cookies.txt LOCALLY" extension ishlatng
```

### Bot cookie'ni topolmayapti
```bash
# Fayl yo'lini tekshiring
ls -la scripts/cookies.txt

# Fayl hajmi 100 baytdan katta bo'lishi kerak
du -h scripts/cookies.txt
```

---

## 📊 Cookie Bilan vs Cookie'siz

| Holat | Cookie'siz | Cookie Bilan |
|-------|-----------|--------------|
| Musiqa yuklanishi | ❌ Bloklangan | ✅ Ishlaydi |
| Video yuklanishi | ❌ CAPTCHA | ✅ Ishlaydi |
| Tezlik | - | ✅ Tez |
| Xavfsizlik | ✅ Xavfsiz | ⚠️ Cookie himoyalang |

---

## 🎯 Qisqacha

1. Chrome'ga extension o'rnating
2. YouTube'ga login qiling
3. Cookie export qiling
4. `scripts/cookies.txt` ga joylang
5. Bot'ni ishga tushiring

**Natija:** Musiqa va video yana yuklanadi! 🎵

---

## 📞 Yordam

Muammo bo'lsa:
- Telegram: @MuhammadjonXP_Admin
- GitHub Issues: https://github.com/muhammadjonnematov1303/navohub/issues

---

**Muvaffaqiyatli sozlang!** 🚀
