#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════╗
║            NavoHub — Telegram Musiqa Bot             ║
║        YouTube qidiruv | MP3 | Video formatlar       ║
║                    v2.1 - Optimized                  ║
╚══════════════════════════════════════════════════════╝
"""

# ═══════════════════════════════════════════════════════
# 1. IMPORTLAR
# ═══════════════════════════════════════════════════════
import asyncio
import io as _io
import json
import logging
import os
import re
import shutil
import sys
import tempfile
import time
import unicodedata
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional

import aiohttp
import yt_dlp
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

# .env faylini yuklash
env_path = Path(__file__).parent / "config" / ".env"
load_dotenv(env_path)

# ═══════════════════════════════════════════════════════
# 2. SOZLAMALAR
# ═══════════════════════════════════════════════════════
BOT_TOKEN      = os.getenv("BOT_TOKEN", "8619790841:AAHq4PRVLsltrM4AUwX3RyLGX4MAFqUW7FM")
BOT_LINK       = "https://t.me/NavoHubBot"
DEVELOPER      = "@MuhammadjonXP"
ADMIN_USERNAME = "@MuhammadjonXP_Admin"
CHANNEL_LINK   = "@navohubbot_hisobotlar"  # yoki -100xxxxxxxxxx

# Vaqtinchalik fayllar uchun (RAM'da, disk emas!)
TEMP_DIR = Path(tempfile.gettempdir()) / "navohub_temp"
TEMP_DIR.mkdir(exist_ok=True)

# Data fayllar (yangi struktura)
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

USERS_FILE   = DATA_DIR / "users.json"
STATS_FILE    = DATA_DIR / "stats.json"
COOKIES_FILE = BASE_DIR / "scripts" / "cookies.txt"

SEARCH_LIMIT = 50
PER_PAGE = 10
LOG_FILE = DATA_DIR / "activity.log"  # Path("activity.log") -> DATA_DIR / "activity.log"
MAX_DURATION = 1200    # 20 daqiqa
MAX_FILE_MB  = 2000  # Telegram limit: 2GB (2000 MB)
CACHE_TTL    = 86_400  # 24 soat
SESSION_TTL  = 3_600   # 1 soat

URL_RE = re.compile(
    r"https?://(?:www\.)?(?:"
    r"youtu\.be|youtube\.com|music\.youtube\.com"
    r"|instagram\.com|instagr\.am"
    r"|tiktok\.com|vm\.tiktok\.com|vt\.tiktok\.com"
    r")\S+",
    re.IGNORECASE,
)

# Video sifatlari (pastdan tepaga)
VIDEO_QUALITIES = [
    ("144p",  144),
    ("240p",  240),
    ("360p",  360),
    ("480p",  480),
    ("720p",  720),
    ("1080p", 1080),
    ("4K",    2160),
]

# ═══════════════════════════════════════════════════════
# 3. LOGGING
# ═══════════════════════════════════════════════════════
if hasattr(sys.stdout, "buffer"):
    sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Sodda logging (faqat console va fayl)
class FlushStreamHandler(logging.StreamHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        FlushStreamHandler(sys.stdout),  # Flush bilan
        logging.FileHandler(LOG_FILE, encoding="utf-8")
    ],
    force=True
)
log = logging.getLogger("NavoHub")

# Aiogram va boshqa kutubxonalarning xatolarini butunlay yashirish
logging.getLogger("aiogram").setLevel(logging.CRITICAL)
logging.getLogger("aiogram.event").setLevel(logging.CRITICAL)
logging.getLogger("aiohttp").setLevel(logging.CRITICAL)
logging.getLogger("yt_dlp").setLevel(logging.CRITICAL)

# Darhol test xabari
print("\n" + "=" * 50, flush=True)
print("  🎵 NavoHub Bot", flush=True)
print("=" * 50, flush=True)

# ═══════════════════════════════════════════════════════
# 4. XOTIRA VA KESH
# ═══════════════════════════════════════════════════════
# TEMP_DIR allaqachon yaratilgan (yuqorida)
_pool = ThreadPoolExecutor(max_workers=16)  # 8 -> 16 (tezroq parallel yuklab olish)

user_sessions: dict[int, dict] = {}
_search_cache: dict[str, dict] = {}
_dl_cache:     dict[str, dict] = {}

_http_session: Optional[aiohttp.ClientSession] = None

def _get_http() -> aiohttp.ClientSession:
    global _http_session
    if _http_session is None or _http_session.closed:
        connector = aiohttp.TCPConnector(limit=20, ttl_dns_cache=300)
        _http_session = aiohttp.ClientSession(
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            connector=connector,
        )
    return _http_session

def _cache_get(store: dict, key: str, check_file: bool = False) -> Optional[dict]:
    e = store.get(key)
    if not e:
        return None
    if time.time() - e.get("ts", 0) > CACHE_TTL:
        del store[key]
        return None
    if check_file and not Path(e.get("file_path", "")).exists():
        del store[key]
        return None
    return e

def _cache_set(store: dict, key: str, data: dict, limit: int = 200) -> None:
    data["ts"] = time.time()
    store[key] = data
    if len(store) > limit:
        del store[min(store, key=lambda k: store[k].get("ts", 0))]

# ═══════════════════════════════════════════════════════
# 5. FOYDALANUVCHILAR VA STATISTIKA
# ═══════════════════════════════════════════════════════
def _track_user(uid: int, name: str) -> None:
    try:
        data = json.loads(USERS_FILE.read_text("utf-8")) if USERS_FILE.exists() else {}
        if str(uid) not in data:
            data[str(uid)] = {"name": name, "joined": int(time.time())}
            USERS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), "utf-8")
            log.info("[YANGI]  %s (id=%s)", name, uid)
    except Exception:
        pass

def _load_stats() -> dict:
    if STATS_FILE.exists():
        try:
            return json.loads(STATS_FILE.read_text("utf-8"))
        except Exception:
            pass
    return {}

def _save_stats(data: dict) -> None:
    try:
        STATS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), "utf-8")
    except Exception:
        pass

def _record_download(uid: int, title: str, format_type: str) -> None:
    today = time.strftime("%Y-%m-%d")
    stats = _load_stats()
    if "daily" not in stats:
        stats["daily"] = {}
    if today not in stats["daily"]:
        stats["daily"][today] = {"downloads": 0, "users": set(), "formats": {}}
    stats["daily"][today]["downloads"] += 1
    stats["daily"][today]["users"].add(uid)
    fmt = stats["daily"][today]["formats"]
    fmt[format_type] = fmt.get(format_type, 0) + 1
    _save_stats(stats)

def _get_daily_report() -> str:
    today = time.strftime("%Y-%m-%d")
    stats = _load_stats()
    day_data = stats.get("daily", {}).get(today, {})
    if not day_data:
        return f"📊 Kunlik hisobot - {today}\n\n❌ Bugun hech qanday faoliyat yo'q"
    
    downloads = day_data.get("downloads", 0)
    users = len(day_data.get("users", set()))
    formats = day_data.get("formats", {})
    
    lines = [
        f"📊 Kunlik hisobot - {today}",
        "",
        f"📥 Yuklab olishlar: {downloads}",
        f"👥 Foydalanuvchilar: {users}",
    ]
    if formats:
        lines.append("")
        lines.append("Formatlar:")
        for fmt, cnt in sorted(formats.items()):
            lines.append(f"  • {fmt}: {cnt}")
    
    return "\n".join(lines)

# ═══════════════════════════════════════════════════════
# 6. YORDAMCHI FUNKSIYALAR
# ═══════════════════════════════════════════════════════
def h(text: str) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def fmt_dur(secs) -> str:
    if not secs:
        return "?"
    m, s = divmod(int(secs), 60)
    hrs, m = divmod(m, 60)
    return f"{hrs}:{m:02d}:{s:02d}" if hrs else f"{m}:{s:02d}"

def fmt_views(n) -> str:
    if not n:
        return ""
    if n >= 1_000_000:
        return f"👁 {n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"👁 {int(n/1_000)}K"
    return f"👁 {n}"

def safe_name(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^\w\s\-.]", "", text)
    text = re.sub(r"\s+", "_", text.strip())
    return text[:80] or "track"

def _dur_to_sec(text: str) -> int:
    try:
        parts = [int(x) for x in text.strip().split(":")]
        return sum(v * (60 ** i) for i, v in enumerate(reversed(parts)))
    except Exception:
        return 0

def _views_to_int(text: str) -> int:
    nums = re.sub(r"[^\d]", "", text.split(" ")[0])
    return int(nums) if nums else 0

# ═══════════════════════════════════════════════════════
# 6.1. PROGRESS HELPER (Optimizatsiya)
# ═══════════════════════════════════════════════════════
async def update_progress_bar(
    progress_msg: Message,
    info: dict,
    start_time: float,
    download_complete_flag: list,
    media_type: str = "🎵"
) -> None:
    """
    Umumiy progress bar yangilash funksiyasi.
    
    Args:
        progress_msg: Progress xabari
        info: Media ma'lumotlari (title, uploader, duration)
        start_time: Boshlangan vaqt
        download_complete_flag: [False] - yuklanish tugaganda [True] ga o'zgaradi
        media_type: "🎵" yoki "🎬"
    """
    progress = 0
    while not download_complete_flag[0] and progress < 95:
        await asyncio.sleep(0.5)  # 1s -> 0.5s (tezroq yangilanish)
        progress = min(95, progress + 20)  # 15 -> 20 (tezroq o'sish)
        elapsed = time.time() - start_time
        try:
            title = info.get('title', 'Nomalum')
            uploader = info.get('uploader', '')
            duration = info.get('duration', '?')
            caption_text = (
                f"📥 <b>Yuklanmoqda...</b>\n\n"
                f"{media_type} <b>{h(title)}</b>\n"
                f"👤 {h(uploader)}\n"
                f"⏱ {duration}\n\n"
                f"⏳ Jarayon: <code>{progress}%</code>\n"
                f"⏱ Vaqt: <code>{int(elapsed)}s</code>"
            )
            
            if hasattr(progress_msg, 'photo') and progress_msg.photo:
                await progress_msg.edit_caption(caption_text, parse_mode="HTML")
            else:
                await progress_msg.edit_text(caption_text, parse_mode="HTML")
        except Exception:
            break

async def show_completion(
    progress_msg: Message,
    info: dict,
    elapsed: float,
    media_type: str = "🎵"
) -> None:
    """
    100% tugallangan xabarni ko'rsatish.
    
    Args:
        progress_msg: Progress xabari
        info: Media ma'lumotlari
        elapsed: O'tgan vaqt
        media_type: "🎵" yoki "🎬"
    """
    try:
        title = info.get('title', 'Nomalum')
        uploader = info.get('uploader', '')
        duration = info.get('duration', '?')
        caption_text = (
            f"✅ <b>Tayyor!</b>\n\n"
            f"{media_type} <b>{h(title)}</b>\n"
            f"👤 {h(uploader)}\n"
            f"⏱ {duration}\n\n"
            f"⏳ Jarayon: <code>100%</code>\n"
            f"⏱ Vaqt: <code>{int(elapsed)}s</code>"
        )
        
        if hasattr(progress_msg, 'photo') and progress_msg.photo:
            await progress_msg.edit_caption(caption_text, parse_mode="HTML")
        else:
            await progress_msg.edit_text(caption_text, parse_mode="HTML")
    except Exception:
        pass

# ═══════════════════════════════════════════════════════
# 7. FFMPEG
# ═══════════════════════════════════════════════════════
_FFMPEG_DIR = Path(__file__).parent / "ffmpeg"
_FFMPEG_BIN = _FFMPEG_DIR / "bin" / "ffmpeg.exe"
_FFMPEG_URL = (
    "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/"
    "ffmpeg-master-latest-win64-gpl.zip"
)

def _find_ffmpeg() -> Optional[str]:
    # Avval system FFmpeg ni tekshirish
    if p := shutil.which("ffmpeg"):
        return p
    # Windows uchun local FFmpeg
    return str(_FFMPEG_BIN) if _FFMPEG_BIN.exists() else None

def _install_ffmpeg() -> Optional[str]:
    """FFmpeg'ni yuklab olish va o'rnatish (progress bilan)"""
    log.info("[FFMPEG]  Yuklanmoqda...")
    zip_path = Path(__file__).parent / "ffmpeg_tmp.zip"
    
    try:
        # Progress callback
        def show_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100, (downloaded * 100) // total_size)
                if percent % 10 == 0:  # Har 10% da ko'rsatish
                    print(f"\r[FFMPEG]  Yuklanmoqda... {percent}%", end="", flush=True)
        
        print("[FFMPEG]  Yuklanmoqda... 0%", end="", flush=True)
        urllib.request.urlretrieve(_FFMPEG_URL, zip_path, reporthook=show_progress)
        print("\r[FFMPEG]  Yuklanmoqda... 100%")
        
        log.info("[FFMPEG]  Arxiv ochilmoqda...")
        with zipfile.ZipFile(zip_path, "r") as zf:
            for m in zf.namelist():
                if "/bin/ffmpeg.exe" in m or "/bin/ffprobe.exe" in m:
                    bin_dir = _FFMPEG_DIR / "bin"
                    bin_dir.mkdir(parents=True, exist_ok=True)
                    fname = Path(m).name
                    with zf.open(m) as src, open(bin_dir / fname, "wb") as dst:
                        shutil.copyfileobj(src, dst)
        
        zip_path.unlink()
        log.info("[FFMPEG]  ✅ O'rnatildi: %s", _FFMPEG_BIN)
        return str(_FFMPEG_BIN)
        
    except Exception as ex:
        print(f"\n[FFMPEG]  ❌ Xato: {ex}")
        log.error("[FFMPEG]  O'rnatishda xato: %s", ex, exc_info=True)
        if zip_path.exists():
            try:
                zip_path.unlink()
            except:
                pass
        return None

_FFMPEG = _find_ffmpeg()
if _FFMPEG:
    log.info(f"[FFMPEG]  ✅ Topildi: {_FFMPEG}")
else:
    log.warning("[FFMPEG]  ⚠️  Topilmadi - birinchi video yuklanishida o'rnatiladi")
    log.warning("[FFMPEG]  💡 Yoki qo'lda o'rnating: winget install ffmpeg")

# ═══════════════════════════════════════════════════════
# 8. YOUTUBE INNERTUBE QIDIRUV (ultra tez ~0.3s)
# ═══════════════════════════════════════════════════════
_IT_URL = "https://www.youtube.com/youtubei/v1/search"
_IT_KEY = "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"
_IT_CTX = {"client": {"clientName": "WEB", "clientVersion": "2.20240101.00.00", "hl": "en"}}

async def _search_innertube(query: str) -> list[dict]:
    payload = {"context": _IT_CTX, "query": query, "params": "EgIQAQ=="}
    try:
        sess    = _get_http()
        timeout = aiohttp.ClientTimeout(total=2)
        async with sess.post(
            _IT_URL, params={"key": _IT_KEY}, json=payload, timeout=timeout
        ) as resp:
            data = await resp.json(content_type=None)

        sections = (
            data.get("contents", {})
                .get("twoColumnSearchResultsRenderer", {})
                .get("primaryContents", {})
                .get("sectionListRenderer", {})
                .get("contents", [])
        )
        tracks = []
        for sec in sections:
            for item in sec.get("itemSectionRenderer", {}).get("contents", []):
                vr = item.get("videoRenderer", {})
                vid_id = vr.get("videoId")
                if not vid_id:
                    continue
                title    = vr.get("title",     {}).get("runs", [{}])[0].get("text", 'Nomalum')
                uploader = vr.get("ownerText", {}).get("runs", [{}])[0].get("text", "")
                dur_text = vr.get("lengthText", {}).get("simpleText", "")
                dur_secs = _dur_to_sec(dur_text)
                view_txt = (
                    vr.get("viewCountText", {}).get("simpleText", "")
                    or (vr.get("viewCountText", {}).get("runs") or [{}])[0].get("text", "")
                )
                if vid_id:
                    thumb = f"https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg"

                if dur_secs > MAX_DURATION:
                    continue
                tracks.append({
                    "id":        vid_id,
                    "title":     title,
                    "uploader":  uploader,
                    "duration":  fmt_dur(dur_secs),
                    "dur_secs":  dur_secs,
                    "views":     fmt_views(_views_to_int(view_txt)),
                    "thumbnail": thumb,
                    "url":       f"https://www.youtube.com/watch?v={vid_id}",
                })
                if len(tracks) >= SEARCH_LIMIT:
                    return tracks
        return tracks
    except asyncio.TimeoutError:
        log.warning("[QIDIRUV]  Timeout - InnerTube sekin, yt-dlp ishlatilmoqda")
        return None
    except Exception as ex:
        log.warning("[QIDIRUV XATO]  %s", ex)
        return []

def _search_ytdlp_fallback(query: str) -> list[dict]:
    opts = {
        "quiet": True, "no_warnings": True, "ignoreerrors": True,
        "extract_flat": True, "skip_download": True,
    }
    out = []
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"ytsearch{SEARCH_LIMIT}:{query}", download=False)
        for e in (info or {}).get("entries", []):
            if not e or not e.get("id"):
                continue
            dur = e.get("duration") or 0
            if dur > MAX_DURATION:
                continue
            vid_id = e["id"]
            out.append({
                "id":        vid_id,
                "title":     e.get("title") or 'Nomalum',
                "uploader":  e.get("uploader") or e.get("channel") or "",
                "duration":  fmt_dur(dur),
                "dur_secs":  dur,
                "views":     fmt_views(e.get("view_count")),
                "thumbnail": f"https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg",
                "url":       f"https://www.youtube.com/watch?v={vid_id}",
            })
    except Exception as ex:
        log.warning("[ZAXIRA QIDIRUV]  %s", ex)
    return out

async def search_tracks(query: str) -> list[dict]:
    key = query.lower().strip()
    if cached := _cache_get(_search_cache, key):
        log.info("[KESH]  \"%s\"", query)
        return cached["tracks"]
    
    tracks = await _search_innertube(query)
    
    if not tracks:
        log.info("[ZAXIRA]  yt-dlp ishlatilmoqda")
        tracks = await asyncio.get_event_loop().run_in_executor(_pool, _search_ytdlp_fallback, query)
    
    if tracks:
        _cache_set(_search_cache, key, {"tracks": tracks})
        log.info("[TOPILDI]  \"%s\"  ->  %d ta", query, len(tracks))
    else:
        log.info("[TOPILMADI]  \"%s\"", query)
    return tracks

# ═══════════════════════════════════════════════════════
# 9. YT-DLP YUKLAB OLISH
# ═══════════════════════════════════════════════════════
def _ydl_base_opts() -> dict:
    """yt-dlp uchun optimal sozlamalar - YouTube bot detection bypass"""
    opts = {
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": False,
        "noplaylist": True,
        "socket_timeout": 30,
        "retries": 10,
        "fragment_retries": 10,
        "no_check_certificate": True,
        "geo_bypass": True,
        # YouTube bot detection bypass - tv_embedded eng yaxshi
        "extractor_args": {
            "youtube": {
                "player_client": ["tv_embedded"],  # TV client - bot detection yo'q
                "skip": ["hls", "dash"],
            },
        },
        "http_chunk_size": 10_485_760,
        "concurrent_fragment_downloads": 4,
    }
    if COOKIES_FILE.exists() and COOKIES_FILE.stat().st_size > 100:
        opts["cookiefile"] = str(COOKIES_FILE)
        log.info("[COOKIE]  cookies.txt ishlatilmoqda")
    return opts

def _url_info_sync(url: str) -> Optional[dict]:
    opts = {
        "quiet":          True,
        "no_warnings":    True,
        "ignoreerrors":   False,
        "noplaylist":     True,
        "socket_timeout": 8,  # 10 -> 8 (tezroq)
        "retries":        2,  # 3 -> 2 (tezroq)
        "skip_download": True, 
        "extract_flat": False,
        "no_check_certificate": True,
        "geo_bypass": True,
    }
    try:
        log.info("[URL INFO]  Tekshirilmoqda: %s", url[:60])
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
        if not info:
            log.warning("[URL INFO]  Ma'lumot topilmadi")
            return None
        
        vid_id = info.get("id", "")
        title = info.get("title") or 'Nomalum'
        log.info("[URL INFO]  Topildi: %s", title[:50])
        
        # Thumbnail olish (turli manbalar)
        thumbnail = ""
        if vid_id and "youtube" in url.lower():
            thumbnail = f"https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg"
        elif info.get("thumbnail"):
            thumbnail = info["thumbnail"]
        elif info.get("thumbnails") and len(info["thumbnails"]) > 0:
            thumbnail = info["thumbnails"][-1].get("url", "")
        
        return {
            "title":     title,
            "uploader":  info.get("uploader") or info.get("channel") or info.get("creator") or "",
            "duration":  fmt_dur(info.get("duration")),
            "views":     fmt_views(info.get("view_count")),
            "thumbnail": thumbnail,
            "url":       url,
            "formats":   _extract_heights(info.get("formats", [])),
        }
    except Exception as ex:
        log.error("[URL INFO XATO]  %s: %s", type(ex).__name__, str(ex))
        return None

def _extract_heights(formats: list) -> list[int]:
    heights = set()
    for f in formats:
        h = f.get("height")
        if h and isinstance(h, int):
            heights.add(h)
    return sorted(heights)

async def get_url_info(url: str) -> Optional[dict]:
    return await asyncio.get_event_loop().run_in_executor(_pool, _url_info_sync, url)

def _download_audio_sync(url: str) -> Optional[dict]:
    """
    Audio yuklab olish va MP3 ga konvertatsiya qilish
    
    Returns:
        dict: {"file_path": str, "title": str, ...} yoki {"error": str}
        None: Fayl topilmadi
    """
    fname = f"navo_{int(time.time()*1000)}"
    output_template = str(TEMP_DIR / f"{fname}.%(ext)s")
    
    # yt-dlp sozlamalari
    opts = {
        **_ydl_base_opts(),
        "outtmpl": output_template,
        "format": "bestaudio/best",  # Eng yaxshi audio
    }
    
    # FFmpeg bilan MP3 konvertatsiya
    if _FFMPEG:
        opts["ffmpeg_location"] = str(Path(_FFMPEG).parent)
        opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "128",
        }]
        log.info(f"[FFMPEG] Ishlatilmoqda: {_FFMPEG}")
    else:
        log.warning("[FFMPEG] Topilmadi - audio formatda yuklanadi")
    
    # Yuklab olish
    try:
        log.info(f"[DOWNLOAD START] URL: {url[:70]}")
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
        
        if not info:
            log.error("[DOWNLOAD] info=None - video topilmadi")
            return {"error": "not_found"}
        
        title = info.get('title', 'Nomalum')
        log.info(f"[DOWNLOAD SUCCESS] {title[:50]}")
        
    except yt_dlp.utils.DownloadError as ex:
        error_msg = str(ex)
        log.error(f"[DOWNLOAD ERROR] {error_msg}", exc_info=True)
        
        # YouTube bot detection
        if "Sign in" in error_msg or "bot" in error_msg.lower():
            log.error("[YOUTUBE BOT DETECTION] Cookies kerak!")
            return {"error": "bot_detected"}
        
        return {"error": "download_failed"}
        
    except Exception as ex:
        log.error(f"[UNEXPECTED ERROR] {str(ex)}", exc_info=True)
        return {"error": "failed"}
    
    # Yuklab olingan faylni topish
    possible_extensions = ["mp3", "m4a", "webm", "opus", "ogg", "mp4"]
    found_file = None
    
    for ext in possible_extensions:
        fp = TEMP_DIR / f"{fname}.{ext}"
        if fp.exists():
            found_file = fp
            log.info(f"[FILE FOUND] {fp.name} ({fp.stat().st_size / 1_048_576:.1f} MB)")
            break
    
    if not found_file:
        log.error(f"[FILE NOT FOUND] Qidirildi: {fname}.{{mp3,m4a,webm,...}}")
        log.error(f"[TEMP DIR] {TEMP_DIR}")
        # Temp papkadagi fayllarni ko'rsatish
        try:
            files = list(TEMP_DIR.glob(f"{fname}*"))
            log.error(f"[TEMP FILES] {[f.name for f in files]}")
        except Exception:
            pass
        return {"error": "file_not_found"}
    
    # Fayl hajmini tekshirish
    size_mb = found_file.stat().st_size / 1_048_576
    if size_mb > MAX_FILE_MB:
        log.warning(f"[FILE TOO LARGE] {size_mb:.1f} MB > {MAX_FILE_MB} MB")
        found_file.unlink()
        return {"error": "too_large", "size": round(size_mb, 1)}
    
    # Muvaffaqiyatli natija
    return {
        "file_path": str(found_file),
        "title": info.get("title", "Nomalum"),
        "uploader": info.get("uploader") or info.get("channel") or "",
        "duration": fmt_dur(info.get("duration")),
        "dur_secs": info.get("duration") or 0,
        "size_mb": round(size_mb, 1),
        "thumbnail": f"https://i.ytimg.com/vi/{info.get('id','')}/hqdefault.jpg",
    }

def _download_video_sync(url: str, quality: int) -> Optional[dict]:
    """Video yuklab olish (FFmpeg lazy loading bilan)"""
    global _FFMPEG
    
    # FFmpeg yo'q bo'lsa, hozir o'rnatish
    if not _FFMPEG:
        log.info("[FFMPEG]  Video uchun kerak - o'rnatilmoqda...")
        _FFMPEG = _install_ffmpeg()
        if not _FFMPEG:
            return {"error": "ffmpeg_required", "message": "FFmpeg o'rnatilmadi"}
    
    fname = f"navo_{int(time.time()*1000)}"
    opts  = {
        **_ydl_base_opts(),
        "outtmpl": str(TEMP_DIR / f"{fname}.%(ext)s"),
        "merge_output_format": "mp4",
    }
    if quality == 0:
        opts["format"] = "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best"  # Max 1080p (tezroq)
    else:
        opts["format"] = (
            f"bestvideo[height<={quality}]+bestaudio/"
            f"bestvideo[height<={quality}]/best[height<={quality}]/best"
        )
    if _FFMPEG:
        opts["ffmpeg_location"] = str(Path(_FFMPEG).parent)
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
        if not info:
            return None
    except Exception as ex:
        log.error("[VIDEO XATO]  %s", ex)
        return {"error": "failed"}

    for ext in ("mp4", "mkv", "webm", "mov"):
        fp = TEMP_DIR / f"{fname}.{ext}"
        if fp.exists():
            size = fp.stat().st_size / 1_048_576
            if size > MAX_FILE_MB:
                fp.unlink()
                return {"error": "too_large", "size": round(size, 1)}
            return {
                "file_path": str(fp),
                "title":     info.get("title") or 'Nomalum',
                "uploader":  info.get("uploader") or info.get("channel") or "",
                "duration":  fmt_dur(info.get("duration")),
                "dur_secs":  info.get("duration") or 0,
                "size_mb":   round(size, 1),
                "ext":       ext,
            }
    return None

async def download_audio(url: str) -> Optional[dict]:
    if cached := _cache_get(_dl_cache, url, check_file=True):
        log.info("[KESH]  Audio: %s", url[:50])
        return cached
    result = await asyncio.get_event_loop().run_in_executor(_pool, _download_audio_sync, url)
    if result and not result.get("error"):
        _cache_set(_dl_cache, url, dict(result))
    return result

async def download_video(url: str, quality: int) -> Optional[dict]:
    return await asyncio.get_event_loop().run_in_executor(
        _pool, _download_video_sync, url, quality
    )

# ═══════════════════════════════════════════════════════
# 10. TUGMALAR (KEYBOARDS)
# ═══════════════════════════════════════════════════════
def kb_tracks(count: int, page: int = 0) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    start = page * PER_PAGE
    end = min(start + PER_PAGE, count)
    
    for i in range(start + 1, end + 1):
        b.button(text=str(i), callback_data=f"t:{i-1}", style="primary")
    b.adjust(5)
    
    if end < count:
        b.row(InlineKeyboardButton(text="📄 Keyingi →", callback_data=f"page:{page+1}", style="primary"))
    
    b.row(InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel", style="danger"))
    return b.as_markup()

def kb_video_formats(available_heights: list[int]) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    quality_buttons = [
        ("360p", 360),
        ("480p", 480),
        ("720p", 720),
    ]
    
    for label, h in quality_buttons:
        if not available_heights or any(ah >= h for ah in available_heights):
            b.button(text=f"🎬 {label}", callback_data=f"vf:{h}", style="primary")
    
    b.button(text="🎬 Original video", callback_data="vf:0", style="primary")
    b.adjust(4)
    b.row(
        InlineKeyboardButton(text="🎵 MP3 Audio", callback_data="vf:mp3", style="success"),
        InlineKeyboardButton(text="🖼 Preview rasm", callback_data="vf:pic", style="primary"),
    )
    b.row(InlineKeyboardButton(text="❌ Bekor", callback_data="cancel", style="danger"))
    return b.as_markup()

def kb_back(page: int = 0) -> InlineKeyboardMarkup:
    keyboard = [[]]
    if page > 0:
        keyboard[0].append(InlineKeyboardButton(text="← Oldingi", callback_data=f"page:{page-1}", style="primary"))
    keyboard[0].append(InlineKeyboardButton(text="🔍 Yangi qidiruv", callback_data="new_search", style="primary"))
    keyboard[0].append(InlineKeyboardButton(text="❌ Bekor", callback_data="cancel", style="danger"))
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# ═══════════════════════════════════════════════════════
# 11. XABAR MATNLARI
# ═══════════════════════════════════════════════════════
PM = "HTML"

def msg_welcome(name: str) -> str:
    return (
        f"👋 Xush kelibsiz, <b>{h(name)}</b>!\n\n"
        f"🎵 <b>NavoHub</b> — musiqa yuklovchi bot\n\n"
        f"📌 <b>Qanday foydalanish:</b>\n"
        f"• Qo'shiq nomini yozing\n"
        f"• YouTube, Instagram yoki TikTok havolasini yuboring\n"
        f"• Yoki Artist nomini yozing!\n\n"
        f"🚀 Boshlaylik!\n\n"
        f"👨‍💻 Dasturchi: {DEVELOPER}\n"
        f"👤 Admin: {ADMIN_USERNAME}"
    )

MSG_HELP = (
    f"ℹ️ <b>NavoHub — Qo'llanma</b>\n\n"
    f"🔍 <b>Musiqa qidirish:</b>\n"
    f"Qo'shiq nomini yozing, masalan: <code>Mirjalol Nematov Nozka</code>\n"
    f"Yoki artist nomini yozing: <code>Shahzoda</code>\n"
    f"Bot {SEARCH_LIMIT} ta natija ko'rsatadi, raqam bosib yuklab olasiz\n\n"
    f"🔗 <b>Havola yuborish:</b>\n"
    f"YouTube, TikTok yoki Instagram havolasini yuboring\n"
    f"Bot formatlarni ko'rsatadi: 144p dan 1080p gacha + MP3\n\n"
    f"📋 <b>Buyruqlar:</b>\n"
    f"/start — Boshlash\n"
    f"/help yoki /yordam — Qo'llanma\n"
    f"/hisobot — Kunlik hisobot\n\n"
    f"⚡ Tez • Bepul • Qulay\n\n"
    f"👨‍💻 Dasturchi: {DEVELOPER}\n"
    f"👤 Admin: {ADMIN_USERNAME}"
)

def msg_track_list(query: str, tracks: list[dict], page: int = 0) -> str:
    start = page * PER_PAGE
    end = min(start + PER_PAGE, len(tracks))
    total_pages = (len(tracks) + PER_PAGE - 1) // PER_PAGE
    
    lines = [f"🔍 <b>«{h(query)}»</b> — <b>{len(tracks)}</b> ta natija:\n"]
    if total_pages > 1:
        lines.append(f"📄 Sahifa {page + 1}/{total_pages}\n")
    
    for i, t in enumerate(tracks[start:end], start + 1):
        title = h(t["title"])
        upl   = h(t["uploader"]) if t.get("uploader") else ""
        dur   = t.get("duration", "?")
        views = t.get("views", "")
        meta  = "  ·  ".join(filter(None, [upl, f"⏱ {dur}", views]))
        lines.append(f"<b>{i}.</b> 🎵 <b>{title}</b>")
        if meta:
            lines.append(f"    <i>{meta}</i>")
    
    lines.append("\n👇 <b>Yuklab olish uchun raqamni tanlang:</b>")
    return "\n".join(lines)

def msg_url_info(info: dict) -> str:
    views = f"  {info['views']}" if info.get("views") else ""
    return (
        f"🎬 <b>{h(info['title'])}</b>\n\n"
        f"👤 {h(info.get('uploader',''))}\n"
        f"⏱ <code>{info.get('duration','?')}</code>{views}\n\n"
        f"👇 <b>Format tanlang:</b>"
    )

def msg_audio_caption(data: dict) -> str:
    return (
        f"🎵 <b>{h(data['title'])}</b>\n"
        f"👤 {h(data.get('uploader',''))}\n"
        f"⏱ <code>{data.get('duration','?')}</code>  "
        f"📦 {data.get('size_mb','?')} MB\n\n"
        f"📥 <a href='{BOT_LINK}'>NavoHub</a> orqali yuklab olindi"
    )

def msg_video_caption(data: dict, quality_label: str) -> str:
    return (
        f"🎬 <b>{h(data['title'])}</b>\n"
        f"👤 {h(data.get('uploader',''))}\n"
        f"⏱ <code>{data.get('duration','?')}</code>  "
        f"📦 {data.get('size_mb','?')} MB  🎞 {quality_label}\n\n"
        f"📥 <a href='{BOT_LINK}'>NavoHub</a> orqali yuklab olindi"
    )

# ═══════════════════════════════════════════════════════
# 12. HANDLERS
# ═══════════════════════════════════════════════════════
router = Router()

@router.message(CommandStart())
async def on_start(msg: Message) -> None:
    try:
        u     = msg.from_user
        name  = (u.first_name or "Do'stim") if u else "Do'stim"
        uid   = u.id if u else 0

        _track_user(uid, name)
        log.info(f"👤 {name} - /start")

        await msg.answer(msg_welcome(name), parse_mode=PM, disable_web_page_preview=True)
        
        # Qo'shimcha xabar
        await msg.answer(
            "💡 <b>Maslahat:</b>\n\n"
            "• Qo'shiq nomini yozing\n"
            "• YouTube, Instagram yoki TikTok havolasini yuboring\n"
            "• Yoki Artist nomini yozing!\n\n"
            "🎵 Musiqa qidirish uchun shunchaki yozing...",
            parse_mode=PM
        )
    except Exception as ex:
        log.error(f"❌ /start xato: {ex}")

@router.message(Command("help"))
async def on_help(msg: Message) -> None:
    await msg.answer(MSG_HELP, parse_mode=PM, disable_web_page_preview=True)

@router.message(Command("yordam"))
async def on_yordam(msg: Message) -> None:
    await msg.answer(MSG_HELP, parse_mode=PM, disable_web_page_preview=True)

@router.message(Command("hisobot"))
async def on_hisobot(msg: Message, bot: Bot) -> None:
    try:
        today = time.strftime("%Y-%m-%d")
        stats = _load_stats()
        
        total_downloads = 0
        total_users = set()
        all_formats = {}
        
        for date, data in stats.get("daily", {}).items():
            total_downloads += data.get("downloads", 0)
            total_users.update(data.get("users", set()))
            for fmt, cnt in data.get("formats", {}).items():
                all_formats[fmt] = all_formats.get(fmt, 0) + cnt
        
        lines = [
            f"📊 NavoHub — To'liq hisobot",
            f"📅 Boshidan: {list(stats.get('daily', {}).keys())[0] if stats.get('daily') else '?'}",
            f"📅 Hozir: {today}",
            "",
            f"📥 Jami yuklab olishlar: {total_downloads}",
            f"👥 Jami foydalanuvchilar: {len(total_users)}",
        ]
        
        if all_formats:
            lines.append("")
            lines.append("Formatlar:")
            for fmt, cnt in sorted(all_formats.items()):
                lines.append(f"  • {fmt}: {cnt}")
        
        if LOG_FILE.exists():
            lines.append("")
            lines.append("📝 So'nggi amallar:")
            try:
                log_content = LOG_FILE.read_text("utf-8")
                log_lines = []
                for line in reversed(log_content.split("\n")):
                    if line.strip() and not line.startswith("="):
                        log_lines.append(line)
                        if len(log_lines) >= 30:
                            break
                for line in reversed(log_lines):
                    lines.append(line)
            except Exception:
                pass
        
        lines.append("")
        lines.append(f"🤖 Bot: {BOT_LINK}")
        
        report = "\n".join(lines)
        
        now_str = time.strftime("%Y-%m-%d_%H-%M-%S")
        report_file = f"hisobot_{now_str}.txt"
        Path(report_file).write_text(report, "utf-8")
        await bot.send_document(msg.chat.id, document=FSInputFile(report_file))
        Path(report_file).unlink()
    except Exception as ex:
        log.error("[HISOBOT BUYRUQ XATO]  %s", ex)

@router.message(F.text)
async def on_text(msg: Message) -> None:
    try:
        u    = msg.from_user
        name = (u.first_name or "") if u else ""
        uid  = u.id if u else 0
        _track_user(uid, name)
        text = msg.text.strip()

        if m := URL_RE.search(text):
            log.info(f"🔗 {name} - {text[:40]}...")
            await _handle_url(msg, m.group())
        else:
            log.info(f"🔍 {name} - \"{text[:30]}...\"")
            await _handle_search(msg, text)
    except Exception as ex:
        log.error(f"❌ Xato: {ex}")

# ───────────────────────────────────────────────────────
async def _handle_search(msg: Message, query: str) -> None:
    status = await msg.answer(
        f"🔍 Qidirilmoqda...", parse_mode=PM
    )
    
    start_time = time.time()
    try:
        tracks = await search_tracks(query)
    except Exception as ex:
        log.error(f"[QIDIRUV XATO] {ex}", exc_info=True)
        await status.edit_text(
            f"❌ <b>Yuklab olishda xatolik yuz berdi.</b>\n\n"
            f"🔄 Qayta urinib ko'ring.",
            parse_mode=PM,
        )
        return
    
    elapsed = time.time() - start_time
    
    if not tracks:
        await status.edit_text(
            f"😔 <b>«{h(query)}»</b> bo'yicha hech narsa topilmadi.\n\n"
            "💡 Boshqacha nom yozib ko'ring.",
            parse_mode=PM,
        )
        log.info(f"❌ Topilmadi")
        return

    uid = msg.from_user.id if msg.from_user else 0
    user_sessions[uid] = {"tracks": tracks, "pending_url": None, "page": 0, "ts": time.time()}

    page = 0
    await status.edit_text(
        msg_track_list(query, tracks, page),
        parse_mode=PM,
        reply_markup=kb_tracks(len(tracks), page),
    )
    log.info(f"✅ {len(tracks)} ta natija ({elapsed:.1f}s)")

async def _handle_url(msg: Message, url: str) -> None:
    status = await msg.answer("⏳ Havola tekshirilmoqda...", parse_mode=PM)
    
    try:
        info = await get_url_info(url)
    except Exception as ex:
        log.error("[HANDLE URL XATO]  %s", ex)
        info = None

    if not info:
        await status.edit_text(
            "❌ <b>Link noto'g'ri yoki qo'llab-quvvatlanmaydi.</b>\n\n"
            "✅ Qo'llab-quvvatlanadigan platformalar:\n"
            "• YouTube (youtube.com, youtu.be)\n"
            "• TikTok (tiktok.com, vm.tiktok.com)\n"
            "• Instagram (instagram.com)\n\n"
            "💡 Havolani to'liq nusxalang va qayta yuboring.",
            parse_mode=PM,
        )
        return

    uid = msg.from_user.id if msg.from_user else 0
    user_sessions[uid] = {
        "tracks": [], "pending_url": url,
        "url_info": info, "ts": time.time()
    }

    caption = msg_url_info(info)
    kb      = kb_video_formats(info.get("formats", []))

    # Status xabarni o'chirish va yangi xabar yuborish (format tugmalari bilan)
    try:
        await status.delete()
    except Exception:
        pass
    
    await msg.answer(caption, parse_mode=PM, reply_markup=kb)

# ───────────────────────────────────────────────────────
@router.callback_query(F.data.startswith("page:"))
async def on_page(cb: CallbackQuery) -> None:
    uid  = cb.from_user.id
    page = int(cb.data.split(":")[1])
    sess = user_sessions.get(uid)
    
    if not sess:
        await cb.answer("⚠️ Sessiya tugadi. Qaytadan qidiring.", show_alert=True)
        return
    
    tracks = sess.get("tracks", [])
    sess["page"] = page
    
    query = cb.message.text.split("«")[1].split("»")[0] if cb.message else ""
    if not query:
        await cb.answer("Ma'lumot topilmadi.", show_alert=True)
        return
    
    await cb.message.edit_text(
        msg_track_list(query, tracks, page),
        parse_mode=PM,
        reply_markup=kb_tracks(len(tracks), page),
    )

# ───────────────────────────────────────────────────────
@router.callback_query(F.data.startswith("t:"))
async def on_track_select(cb: CallbackQuery, bot: Bot) -> None:
    uid  = cb.from_user.id
    idx  = int(cb.data.split(":")[1])
    sess = user_sessions.get(uid)

    if not sess or idx >= len(sess.get("tracks", [])):
        await cb.answer("⚠️ Sessiya tugadi. Qaytadan qidiring.", show_alert=True)
        return

    track = sess["tracks"][idx]
    await cb.answer(f"⬇️ {track['title'][:40]}")
    
    name = cb.from_user.first_name if cb.from_user else "Foydalanuvchi"
    log.info(f"📥 {name} - \"{track['title'][:30]}...\"")
    
    # Yangi xabar yuborish (eski xabarni o'chirmaslik)
    start_time = time.time()
    progress_msg = await bot.send_message(
        cb.message.chat.id,
        f"📥 <b>Yuklanmoqda...</b>\n\n"
        f"🎵 <b>{h(track['title'])}</b>\n"
        f"👤 {h(track.get('uploader', ''))}\n"
        f"⏱ {track.get('duration', '?')}\n\n"
        f"⏳ Jarayon: <code>0%</code>",
        parse_mode=PM,
    )
    
    # Progress update task (Optimizatsiya: umumiy funksiya)
    download_complete = [False]
    progress_task = asyncio.create_task(
        update_progress_bar(progress_msg, track, start_time, download_complete, "🎵")
    )
    
    result = await download_audio(track["url"])
    download_complete[0] = True
    progress_task.cancel()
    
    if not result:
        log.error(f"[YUKLAB OLISH] result=None, url={track['url']}")
    elif result.get("error"):
        log.error(f"[YUKLAB OLISH] error={result.get('error')}, url={track['url']}")
    
    elapsed = time.time() - start_time
    
    # 100% ko'rsatish (Optimizatsiya: umumiy funksiya)
    await show_completion(progress_msg, track, elapsed, "🎵")
    
    # Progress xabarni o'chirish (tez yuborish uchun)
    try:
        await progress_msg.delete()
    except Exception:
        pass
    
    # uid ni uzatish (statistika uchun)
    await _deliver_audio(bot, cb.message.chat.id, result, track, uid)
    
    if result and not result.get("error"):
        log.info(f"✅ Yuborildi ({elapsed:.1f}s)")

@router.callback_query(F.data.startswith("vf:"))
async def on_video_format(cb: CallbackQuery, bot: Bot) -> None:
    uid  = cb.from_user.id
    fmt  = cb.data.split(":", 1)[1]
    sess = user_sessions.get(uid)
    url  = sess.get("pending_url") if sess else None
    info = sess.get("url_info", {}) if sess else {}

    if not url:
        await cb.answer("⚠️ Sessiya tugadi. Havolani qayta yuboring.", show_alert=True)
        return

    await cb.answer("⬇️ Yuklanmoqda...")

    # Faqat rasm
    if fmt == "pic":
        thumb = info.get("thumbnail", "")
        if thumb:
            # Yangi xabar yuborish (eski xabarni o'chirmaslik)
            await bot.send_photo(
                cb.message.chat.id,
                photo=thumb,
                caption=f"🖼 <b>{h(info.get('title',''))}</b>\n\n"
                        f"📥 <a href='{BOT_LINK}'>NavoHub</a>",
                parse_mode=PM,
                has_spoiler=False
            )
        else:
            await bot.send_message(cb.message.chat.id, "❌ Rasm topilmadi.", parse_mode=PM)
        return

    # Progress xabari (rasm bilan) - YANGI XABAR yuborish
    start_time = time.time()
    thumb_url = info.get("thumbnail", "")
    
    if thumb_url:
        try:
            progress_msg = await bot.send_photo(
                cb.message.chat.id,
                photo=thumb_url,
                caption=f"📥 <b>Yuklanmoqda...</b>\n\n"
                        f"🎬 <b>{h(info.get('title', 'Nomalum'))}</b>\n"
                        f"👤 {h(info.get('uploader', ''))}\n"
                        f"⏱ {info.get('duration', '?')}\n\n"
                        f"⏳ Jarayon: <code>0%</code>\n"
                        f"⏱ Vaqt: <code>0s</code>",
                parse_mode=PM,
                has_spoiler=False
            )
        except Exception:
            progress_msg = await bot.send_message(
                cb.message.chat.id,
                f"📥 <b>Yuklanmoqda...</b>\n\n"
                f"🎬 <b>{h(info.get('title', 'Nomalum'))}</b>\n"
                f"👤 {h(info.get('uploader', ''))}\n"
                f"⏱ {info.get('duration', '?')}\n\n"
                f"⏳ Jarayon: <code>0%</code>\n"
                f"⏱ Vaqt: <code>0s</code>",
                parse_mode=PM
            )
    else:
        progress_msg = await bot.send_message(
            cb.message.chat.id,
            f"📥 <b>Yuklanmoqda...</b>\n\n"
            f"🎬 <b>{h(info.get('title', 'Nomalum'))}</b>\n"
            f"👤 {h(info.get('uploader', ''))}\n"
            f"⏱ {info.get('duration', '?')}\n\n"
            f"⏳ Jarayon: <code>0%</code>\n"
            f"⏱ Vaqt: <code>0s</code>",
            parse_mode=PM
        )

    # Audio
    if fmt == "mp3":
        # Progress update task
        download_complete = False
        async def update_progress():
            progress = 0
            while not download_complete and progress < 95:
                await asyncio.sleep(0.5)  # 1s -> 0.5s (tezroq)
                progress = min(95, progress + 20)  # 15 -> 20 (tezroq)
                elapsed = time.time() - start_time
                try:
                    if progress_msg.photo:
                        await progress_msg.edit_caption(
                            f"📥 <b>Yuklanmoqda...</b>\n\n"
                            f"🎵 <b>{h(info.get('title', 'Nomalum'))}</b>\n"
                            f"👤 {h(info.get('uploader', ''))}\n"
                            f"⏱ {info.get('duration', '?')}\n\n"
                            f"⏳ Jarayon: <code>{progress}%</code>\n"
                            f"⏱ Vaqt: <code>{int(elapsed)}s</code>",
                            parse_mode=PM
                        )
                    else:
                        await progress_msg.edit_text(
                            f"📥 <b>Yuklanmoqda...</b>\n\n"
                            f"🎵 <b>{h(info.get('title', 'Nomalum'))}</b>\n"
                            f"👤 {h(info.get('uploader', ''))}\n"
                            f"⏱ {info.get('duration', '?')}\n\n"
                            f"⏳ Jarayon: <code>{progress}%</code>\n"
                            f"⏱ Vaqt: <code>{int(elapsed)}s</code>",
                            parse_mode=PM
                        )
                except Exception:
                    break
        
        # Start progress updates
        progress_task = asyncio.create_task(update_progress())
        
        result = await download_audio(url)
        download_complete = True
        progress_task.cancel()
        
        elapsed = time.time() - start_time
        
        try:
            if progress_msg.photo:
                await progress_msg.edit_caption(
                    f"✅ <b>Tayyor!</b>\n\n"
                    f"🎵 <b>{h(info.get('title', 'Nomalum'))}</b>\n"
                    f"👤 {h(info.get('uploader', ''))}\n"
                    f"⏱ {info.get('duration', '?')}\n\n"
                    f"⏳ Jarayon: <code>100%</code>\n"
                    f"⏱ Vaqt: <code>{int(elapsed)}s</code>",
                    parse_mode=PM
                )
            else:
                await progress_msg.edit_text(
                    f"✅ <b>Tayyor!</b>\n\n"
                    f"🎵 <b>{h(info.get('title', 'Nomalum'))}</b>\n"
                    f"👤 {h(info.get('uploader', ''))}\n"
                    f"⏱ {info.get('duration', '?')}\n\n"
                    f"⏳ Jarayon: <code>100%</code>\n"
                    f"⏱ Vaqt: <code>{int(elapsed)}s</code>",
                    parse_mode=PM
                )
        except Exception:
            pass
        
        # Progress xabarni o'chirish
        try:
            await progress_msg.delete()
        except Exception:
            pass
        
        await _deliver_audio(bot, cb.message.chat.id, result, info, uid)
        return

    # Video
    try:
        quality = int(fmt)
    except ValueError:
        quality = 0

    format_label = f"{quality}p" if quality else "Original"
    format_type = format_label
    
    # Progress update task
    download_complete = False
    async def update_progress():
        progress = 0
        while not download_complete and progress < 95:
            await asyncio.sleep(0.5)  # 1s -> 0.5s (tezroq)
            progress = min(95, progress + 20)  # 15 -> 20 (tezroq)
            elapsed = time.time() - start_time
            try:
                if progress_msg.photo:
                    await progress_msg.edit_caption(
                        f"📥 <b>Yuklanmoqda...</b>\n\n"
                        f"🎬 <b>{h(info.get('title', 'Nomalum'))}</b>\n"
                        f"👤 {h(info.get('uploader', ''))}\n"
                        f"⏱ {info.get('duration', '?')}\n\n"
                        f"⏳ Jarayon: <code>{progress}%</code>\n"
                        f"⏱ Vaqt: <code>{int(elapsed)}s</code>",
                        parse_mode=PM
                    )
                else:
                    await progress_msg.edit_text(
                        f"📥 <b>Yuklanmoqda...</b>\n\n"
                        f"🎬 <b>{h(info.get('title', 'Nomalum'))}</b>\n"
                        f"👤 {h(info.get('uploader', ''))}\n"
                        f"⏱ {info.get('duration', '?')}\n\n"
                        f"⏳ Jarayon: <code>{progress}%</code>\n"
                        f"⏱ Vaqt: <code>{int(elapsed)}s</code>",
                        parse_mode=PM
                    )
            except Exception:
                break
    
    # Start progress updates
    progress_task = asyncio.create_task(update_progress())
    
    result = await download_video(url, quality)
    download_complete = True
    progress_task.cancel()
    
    elapsed = time.time() - start_time
    
    try:
        if progress_msg.photo:
            await progress_msg.edit_caption(
                f"✅ <b>Yuklab olindi!</b>\n\n"
                f"🎬 <b>{h(info.get('title', 'Nomalum'))}</b>\n"
                f"👤 {h(info.get('uploader', ''))}\n"
                f"⏱ {info.get('duration', '?')}\n\n"
                f"⏳ Jarayon: <code>100%</code>\n"
                f"⏱ Vaqt: <code>{int(elapsed)}s</code>\n\n"
                f"📤 Yuborilmoqda...",
                parse_mode=PM
            )
        else:
            await progress_msg.edit_text(
                f"✅ <b>Yuklab olindi!</b>\n\n"
                f"🎬 <b>{h(info.get('title', 'Nomalum'))}</b>\n"
                f"👤 {h(info.get('uploader', ''))}\n"
                f"⏱ {info.get('duration', '?')}\n\n"
                f"⏳ Jarayon: <code>100%</code>\n"
                f"⏱ Vaqt: <code>{int(elapsed)}s</code>",
                parse_mode=PM
            )
    except Exception:
        pass
    
    # Progress xabarni o'chirish
    try:
        await progress_msg.delete()
    except Exception:
        pass
    
    await _deliver_video(bot, cb.message.chat.id, result, quality_label, uid)

@router.callback_query(F.data == "cancel")
async def on_cancel(cb: CallbackQuery) -> None:
    await cb.answer("Bekor qilindi.")
    try:
        await cb.message.delete()
    except Exception:
        pass

@router.callback_query(F.data == "new_search")
async def on_new_search(cb: CallbackQuery) -> None:
    await cb.answer()
    try:
        await cb.message.delete()
    except Exception:
        pass
    await cb.message.answer(
        "🔍 Qidirmoqchi bo'lgan qo'shiq yoki video nomini yozing:",
        parse_mode=PM,
    )

# ───────────────────────────────────────────────────────
async def _deliver_audio(bot: Bot, chat_id: int, result: Optional[dict], meta: dict, uid: int = 0, format_type: str = "MP3") -> None:
    # Qidiruv natijalarini o'chirmaslik uchun faqat chat_id ishlatamiz
    
    if result and uid:
        _record_download(uid, meta.get("title", ""), format_type)

    if not result:
        await bot.send_message(
            chat_id,
            "❌ <b>Yuklab olishda xatolik.</b>\n"
            "🔄 Qayta urinib ko'ring yoki boshqa qo'shiq tanlang.",
            parse_mode=PM, reply_markup=kb_back()
        )
        return

    if result.get("error") == "too_large":
        await bot.send_message(
            chat_id,
            f"⚠️ Fayl juda katta: <b>{result['size']} MB</b>\n"
            f"Telegram maksimal: <b>2000 MB</b>\n\n"
            f"💡 Kichikroq sifat tanlang yoki MP3 yuklab oling.",
            parse_mode=PM, reply_markup=kb_back()
        )
        return

    if result.get("error") == "failed":
        await bot.send_message(
            chat_id,
            "❌ <b>Yuklab olishda xatolik yuz berdi.</b>\n"
            "🔄 Qayta urinib ko'ring.",
            parse_mode=PM, reply_markup=kb_back()
        )
        return

    fp       = Path(result["file_path"])
    filename = f"{safe_name(result['title'])}.mp3"
    caption  = msg_audio_caption(result)
    thumb_url = result.get("thumbnail") or meta.get("thumbnail", "")

    try:
        # Thumbnail yuklab olish (agar URL bo'lsa)
        thumb_file = None
        if thumb_url and thumb_url.startswith("http"):
            try:
                thumb_path = TEMP_DIR / f"thumb_{int(time.time()*1000)}.jpg"
                async with _get_http().get(thumb_url) as resp:
                    if resp.status == 200:
                        thumb_path.write_bytes(await resp.read())
                        thumb_file = FSInputFile(str(thumb_path))
            except Exception as ex:
                log.warning("[THUMB XATO]  %s", ex)
                thumb_file = None
        
        # Audio faylni thumbnail bilan yuborish (timeout oshirilgan)
        await bot.send_audio(
            chat_id=chat_id,
            audio=FSInputFile(str(fp), filename=filename),
            caption=caption,
            parse_mode=PM,
            thumbnail=thumb_file,
            title=result.get("title", 'Nomalum'),
            performer=result.get("uploader", ""),
            duration=result.get("dur_secs", 0),
            request_timeout=300  # 5 daqiqa timeout
        )
        log.info("[YUBORILDI]  %s  (%.1f MB)", result["title"][:50], result["size_mb"])
        
        # Thumbnail faylni o'chirish
        if thumb_file:
            try:
                thumb_path.unlink()
            except Exception:
                pass
    except Exception as ex:
        log.error("[YUBORISH XATO]  %s", ex)
        # Agar thumbnail bilan xato bo'lsa, thumbnail siz yuborish
        try:
            await bot.send_audio(
                chat_id=chat_id,
                audio=FSInputFile(str(fp), filename=filename),
                caption=caption,
                parse_mode=PM,
                title=result.get("title", 'Nomalum'),
                performer=result.get("uploader", ""),
                duration=result.get("dur_secs", 0),
                request_timeout=300  # 5 daqiqa timeout
            )
            log.info("[YUBORILDI (thumbnail siz)]  %s", result["title"][:50])
        except Exception as ex2:
            log.error("[YUBORISH XATO 2]  %s", ex2)
            await bot.send_message(chat_id,
                "❌ Faylni yuborishda xatolik.", parse_mode=PM)
    finally:
        try:
            fp.unlink()
        except Exception:
            pass

async def _deliver_video(bot: Bot, chat_id: int, result: Optional[dict], quality_label: str, uid: int = 0, format_type: str = "Video") -> None:
    # Qidiruv natijalarini o'chirmaslik uchun faqat chat_id ishlatamiz
    
    if result and uid:
        _record_download(uid, "", format_type)

    if not result:
        await bot.send_message(
            chat_id,
            "❌ <b>Yuklab olishda xatolik.</b>\n🔄 Qayta urinib ko'ring.",
            parse_mode=PM, reply_markup=kb_back()
        )
        return

    if result.get("error") == "too_large":
        await bot.send_message(
            chat_id,
            f"⚠️ Video juda katta: <b>{result['size']} MB</b>\n"
            f"Telegram maksimal: <b>2000 MB</b>\n\n"
            f"💡 Kichikroq sifat tanlang yoki MP3 yuklab oling.",
            parse_mode=PM, reply_markup=kb_back()
        )
        return

    if result.get("error") == "failed":
        await bot.send_message(
            chat_id,
            "❌ <b>Yuklab olishda xatolik yuz berdi.</b>\n"
            "🔄 Boshqa sifat tanlang.",
            parse_mode=PM, reply_markup=kb_back()
        )
        return

    fp       = Path(result["file_path"])
    filename = f"{safe_name(result['title'])}.{result.get('ext','mp4')}"
    caption  = msg_video_caption(result, quality_label)

    try:
        # Video sifatida yuborish (document emas!) - timeout oshirilgan
        await bot.send_video(
            chat_id=chat_id,
            video=FSInputFile(str(fp), filename=filename),
            caption=caption,
            parse_mode=PM,
            supports_streaming=True,
            width=1920,
            height=1080,
            duration=result.get("dur_secs", 0) if result.get("dur_secs") else None,
            request_timeout=300  # 5 daqiqa timeout
        )
        log.info("[VIDEO]  %s  %s  (%.1f MB)", result["title"][:40], quality_label, result["size_mb"])
    except Exception as ex:
        log.error("[VIDEO YUBORISH XATO]  %s", ex)
        # Agar video juda katta bo'lsa, document sifatida yuborish
        try:
            await bot.send_document(
                chat_id=chat_id,
                document=FSInputFile(str(fp), filename=filename),
                caption=caption,
                parse_mode=PM,
                request_timeout=300  # 5 daqiqa timeout
            )
            log.info("[VIDEO DOCUMENT]  %s  (%.1f MB)", result["title"][:40], result["size_mb"])
        except Exception as ex2:
            log.error("[DOCUMENT XATO]  %s", ex2)
            await bot.send_message(chat_id,
                "❌ Videoni yuborishda xatolik.\n"
                f"Fayl hajmi: {result['size_mb']} MB\n\n"
                f"💡 Kichikroq sifat tanlang.", parse_mode=PM)
    finally:
        try:
            fp.unlink()
        except Exception:
            pass

# ═══════════════════════════════════════════════════════
# 13. FONDA TOZALASH VA KANALGA HISOBOT
# ═══════════════════════════════════════════════════════
async def _cleanup_loop() -> None:
    while True:
        await asyncio.sleep(1800)
        now = time.time()
        old = [uid for uid, s in user_sessions.items()
               if now - s.get("ts", 0) > SESSION_TTL]
        for uid in old:
            del user_sessions[uid]
        if old:
            log.info("[TOZALASH]  %d sessiya o'chirildi", len(old))
        
        # Vaqtinchalik fayllarni tozalash (eski fayllar)
        try:
            removed = 0
            for fp in TEMP_DIR.iterdir():
                if fp.is_file() and now - fp.stat().st_mtime > CACHE_TTL:
                    try:
                        fp.unlink()
                        removed += 1
                    except Exception:
                        pass
            if removed:
                log.info("[TOZALASH]  %d fayl o'chirildi", removed)
        except Exception as ex:
            log.warning("[TOZALASH XATO]  %s", ex)

async def _send_daily_report(bot: Bot) -> None:
    try:
        yesterday = time.strftime("%Y-%m-%d", time.localtime(time.time() - 86400))
        today = time.strftime("%Y-%m-%d")
        now_str = time.strftime("%Y-%m-%d_%H-%M-%d")
        
        stats = _load_stats()
        day_data = stats.get("daily", {}).get(yesterday, {})
        
        downloads = day_data.get("downloads", 0) if day_data else 0
        users = len(day_data.get("users", set())) if day_data else 0
        formats = day_data.get("formats", {}) if day_data else {}
        
        lines = [
            f"📊 NavoHub — {today} kunlik hisobot",
            "═" * 30,
            "",
            f"📥 Yuklab olishlar: {downloads}",
            f"👥 Foydalanuvchilar: {users}",
        ]
        if formats:
            lines.append("")
            lines.append("Formatlar:")
            for fmt, cnt in sorted(formats.items()):
                lines.append(f"  • {fmt}: {cnt}")
        
        if LOG_FILE.exists():
            lines.append("")
            lines.append("📝 Amallar logi:")
            try:
                log_content = LOG_FILE.read_text("utf-8")
                log_lines = []
                for line in log_content.split("\n"):
                    if line.startswith(yesterday):
                        log_lines.append(line)
                for line in log_lines[:50]:
                    lines.append(line)
            except Exception:
                pass
        
        lines.append("")
        lines.append("═" * 30)
        lines.append(f"🤖 Bot: {BOT_LINK}")
        
        report = "\n".join(lines)
        
        report_file = f"hisobot_{today}.txt"
        Path(report_file).write_text(report, "utf-8")
        await bot.send_document(CHANNEL_LINK, document=FSInputFile(report_file))
        Path(report_file).unlink()
        log.info("[HISOBOT]  %s uchun hisobot yuborildi", yesterday)
    except Exception as ex:
        log.error("[HISOBOT XATO]  %s", ex)

async def _report_scheduler(bot: Bot) -> None:
    while True:
        now = datetime.now()
        target = now.replace(hour=23, minute=59, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
        wait = (target - now).total_seconds()
        await asyncio.sleep(wait)
        await _send_daily_report(bot)

# ═══════════════════════════════════════════════════════
# 14. MAIN
# ═══════════════════════════════════════════════════════
async def health_check_server():
    """Render uchun HTTP health check server"""
    from aiohttp import web
    
    async def health(request):
        return web.Response(text="OK", status=200)
    
    app = web.Application()
    app.router.add_get('/health', health)
    app.router.add_get('/', health)
    
    port = int(os.getenv('PORT', 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    log.info(f"🌐 HTTP server ishga tushdi: port {port}")

async def main() -> None:
    log.info("⚙️  Bot sozlanmoqda...")
    
    # BOT_TOKEN tekshirish
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        log.error("❌ BOT_TOKEN topilmadi! Environment variable sozlang.")
        print("\n❌ XATO: BOT_TOKEN environment variable sozlanmagan!\n")
        print("Render.com'da Environment Variables bo'limiga kiring va qo'shing:")
        print("  Key: BOT_TOKEN")
        print("  Value: 8619790841:AAHq4PRVLsltrM4AUwX3RyLGX4MAFqUW7FM\n")
        return
    
    log.info(f"🔑 BOT_TOKEN: {BOT_TOKEN[:20]}...")
    
    bot = Bot(token=BOT_TOKEN)
    dp  = Dispatcher()
    dp.include_router(router)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        log.error(f"❌ Webhook o'chirishda xato: {e}")
        print(f"\n❌ XATO: Bot Telegram'ga ulanolmadi!\n")
        print(f"Sabab: {e}\n")
        print("BOT_TOKEN to'g'ri ekanligini tekshiring.\n")
        return

    me = await bot.get_me()
    log.info(f"✅ Bot tayyor: @{me.username}")
    log.info("👂 Xabarlar kutilmoqda...\n")

    # HTTP server ishga tushirish (Render uchun)
    asyncio.create_task(health_check_server())
    
    asyncio.create_task(_cleanup_loop())
    asyncio.create_task(_report_scheduler(bot))
    try:
        await dp.start_polling(bot, drop_pending_updates=True)
    finally:
        if _http_session and not _http_session.closed:
            await _http_session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⛔ Bot to'xtatildi\n", flush=True)
    except Exception as e:
        print(f"\n❌ Xato: {e}\n", flush=True)
