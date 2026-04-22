#!/usr/bin/env python3
"""
Chrome'dan YouTube cookie'larini eksport qilish.
Ishlatish: Chrome'ni to'liq yopib, bu faylni ishga tushiring.
"""
import subprocess, sys, time
from pathlib import Path

print("=" * 50)
print("  NavoHub — Cookie eksport vositasi")
print("=" * 50)
print()
print("DIQQAT: Chrome'ni to'liq yoping (tizim tepsisidagini ham)!")
input("Chrome yopilgandan keyin ENTER bosing...")
print()
print("Cookie'lar yuklanmoqda...")

out = Path(__file__).parent / "cookies.txt"
try:
    r = subprocess.run(
        [sys.executable, "-m", "yt_dlp",
         "--cookies-from-browser", "chrome",
         "--cookies", str(out),
         "--skip-download",
         "https://www.youtube.com/watch?v=drFuVNBBU0c"],
        capture_output=True, text=True, timeout=30
    )
    if out.exists() and out.stat().st_size > 100:
        print(f"[OK]  cookies.txt saqlandi: {out}")
        print("Endi botni ishga tushiring — musiqa yuklanadi!")
    else:
        print("[XATO]  Cookie'lar saqlanmadi.")
        print("Sabab:", r.stderr[:300] if r.stderr else "noma'lum")
except Exception as e:
    print("[XATO] ", e)

print()
input("Tugadi. ENTER bosib dasturni yoping...")
