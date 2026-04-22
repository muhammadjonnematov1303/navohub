#!/usr/bin/env python3
"""
NavoHub Bot - Development Mode (Auto-Reload)
Fayl o'zgarganda bot avtomatik qayta ishga tushadi
"""

import sys
import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class BotReloader(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.last_restart = 0
        self.restart_bot()
    
    def on_modified(self, event):
        # Faqat .py fayllar o'zgarganda
        if event.src_path.endswith('.py'):
            # 1 soniyadan kam vaqt o'tgan bo'lsa, restart qilmaslik (ko'p marta restart oldini olish)
            if time.time() - self.last_restart < 1:
                return
            
            print(f"\n🔄 Fayl o'zgardi: {Path(event.src_path).name}")
            print("⏳ Bot qayta ishga tushmoqda...\n")
            self.restart_bot()
    
    def restart_bot(self):
        # Eski jarayonni to'xtatish
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        
        # Yangi jarayonni boshlash
        self.process = subprocess.Popen(
            [sys.executable, "bot.py"],
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        self.last_restart = time.time()

def main():
    print("=" * 50)
    print("  🔥 NavoHub Bot - Development Mode")
    print("  📝 Auto-reload yoqilgan")
    print("=" * 50)
    print("\n💡 Maslahat:")
    print("  • bot.py faylini o'zgartiring")
    print("  • Bot avtomatik qayta ishga tushadi")
    print("  • To'xtatish: Ctrl+C\n")
    print("=" * 50 + "\n")
    
    # Watchdog sozlash
    event_handler = BotReloader()
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n⛔ Development mode to'xtatildi")
        observer.stop()
        if event_handler.process:
            event_handler.process.terminate()
    
    observer.join()

if __name__ == "__main__":
    main()
