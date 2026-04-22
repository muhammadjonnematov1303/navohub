# 🔥 NavoHub Bot - Development Guide

## Auto-Reload (Nodemon o'rniga)

Bot development uchun auto-reload funksiyasi mavjud. Fayl o'zgarganda bot avtomatik qayta ishga tushadi.

### 🚀 Ishga Tushirish

```bash
python dev.py
```

### ✨ Xususiyatlar

- ✅ **Auto-reload**: `.py` fayllar o'zgarganda avtomatik restart
- ✅ **Real-time**: O'zgarishlar darhol qo'llaniladi
- ✅ **Nodemon'ga o'xshash**: Node.js development tajribasi
- ✅ **Oson to'xtatish**: `Ctrl+C` bilan to'xtatish

### 📝 Qanday Ishlaydi?

1. `dev.py` ishga tushadi
2. `bot.py` avtomatik ishga tushadi
3. Siz `bot.py` ni o'zgartirasiz
4. Bot avtomatik qayta ishga tushadi
5. O'zgarishlar darhol test qilinadi

### 🎯 Misol

```bash
# Terminal 1: Development mode
python dev.py

# Terminal 2: Kod yozish
# bot.py ni o'zgartiring va saqlang
# Bot avtomatik qayta ishga tushadi!
```

### 📊 Chiqish Namunasi

```
==================================================
  🔥 NavoHub Bot - Development Mode
  📝 Auto-reload yoqilgan
==================================================

💡 Maslahat:
  • bot.py faylini o'zgartiring
  • Bot avtomatik qayta ishga tushadi
  • To'xtatish: Ctrl+C

==================================================

[Bot ishga tushadi...]

🔄 Fayl o'zgardi: bot.py
⏳ Bot qayta ishga tushmoqda...

[Bot qayta ishga tushadi...]
```

### ⚙️ Sozlamalar

`dev.py` faylida quyidagilarni sozlash mumkin:

- **Restart delay**: `1 soniya` (ko'p marta restart oldini olish)
- **Kuzatiladigan fayllar**: `.py` fayllar
- **Kuzatiladigan papka**: Joriy papka

### 🔧 Production vs Development

**Production (server uchun):**
```bash
python bot.py
```

**Development (kod yozish uchun):**
```bash
python dev.py
```

### 💡 Maslahatlar

1. **Tez development**: Har safar o'zgarishdan keyin botni qo'lda to'xtatish/ishga tushirish shart emas
2. **Xatolarni tezda topish**: O'zgarishlar darhol test qilinadi
3. **Vaqt tejash**: Auto-reload 50% vaqt tejaydi

### 🐛 Muammolar

**Bot qayta ishga tushmayapti?**
- `Ctrl+C` bosib to'xtating
- `python dev.py` qayta ishga tushiring

**Juda ko'p marta restart bo'lyapti?**
- 1 soniya ichida faqat 1 marta restart bo'ladi
- Faylni saqlashdan oldin to'liq yozing

**Watchdog o'rnatilmagan?**
```bash
pip install watchdog
```

---

**Dasturchi:** @MuhammadjonXP  
**Sana:** 2024-12-23
