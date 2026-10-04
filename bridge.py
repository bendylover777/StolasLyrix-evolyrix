"""EvoLyrics bridge: сам видит, что играет в Spotify, и пишет это в bridge.json для мода.

Тексты песен берутся автоматически с бесплатного сервиса LRCLIB (ключи не нужны)
и сохраняются в lyrics.json с таймингами. Нужен интернет.

Установка (один раз):  pip install winsdk
Запуск: двойной клик по start_bridge.bat (или: python bridge.py)
"""
import asyncio
import datetime
import json
import os
import re
import threading
import time
import urllib.parse
import urllib.request

# Папка конфига мода. Если у тебя другая сборка/лаунчер, поменяй путь.
CONFIG_DIR = os.path.join(os.environ.get("APPDATA", "."), ".minecraft", "config", "evolyrics")
BRIDGE_FILE = os.path.join(CONFIG_DIR, "bridge.json")
SONGS_DIR = os.path.join(CONFIG_DIR, "songs")
INTERVAL = 0.2          # как часто обновлять файл, секунды
AUTO_CREATE_SONGS = True  # создавать папку песни, когда она играет впервые
AUTO_LYRICS = True        # сами скачивать текст с LRCLIB
WORDS_PER_CHUNK = 2       # сколько слов показывать за раз (1 = по одному слову)
MAX_LINE_SECONDS = 5.0    # максимум времени на одну строку текста
EFFECTS = ["FADE", "RISE", "SCALE_IN", "SLIDE_LEFT", "SLIDE_RIGHT", "POP", "FLOAT", "ROTATE"]

from winsdk.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager as SessionManager,
    GlobalSystemMediaTransportControlsSessionPlaybackStatus as PlaybackStatus,
)


def safe_name(text):
    text = re.sub(r'[\\/:*?"<>|]', "", text).strip().rstrip(".")
    return text[:80] or "unknown"


LRC_RE = re.compile(r"\[(\d+):(\d+(?:\.\d+)?)\]\s*(.*)")


def parse_lrc(text):
    """'[01:23.45] слова' -> [(83.45, 'слова'), ...]"""
    rows = []
    for raw in text.splitlines():
        m = LRC_RE.match(raw.strip())
        if not m:
            continue
        t = int(m.group(1)) * 60 + float(m.group(2))
        words = m.group(3).strip()
        rows.append((t, words))
    rows.sort(key=lambda r: r[0])
    return rows


def build_lines(rows):
    """Режет строки LRC на кусочки по WORDS_PER_CHUNK слов и распределяет время."""
    out = []
    n = 0
    for i, (t, text) in enumerate(rows):
        if not text:
            continue
        end = rows[i + 1][0] if i + 1 < len(rows) else t + MAX_LINE_SECONDS
        span = max(0.5, min(end - t, MAX_LINE_SECONDS))
        words = text.split()
        chunks = [" ".join(words[j:j + WORDS_PER_CHUNK]) for j in range(0, len(words), WORDS_PER_CHUNK)]
        total = sum(len(c) for c in chunks) or 1
        cur = t
        for c in chunks:
            dur = span * len(c) / total
            out.append({
                "time": round(cur, 2),
                "text": c,
                "effect": EFFECTS[n % len(EFFECTS)],
                "out": "FADE",
                "duration": round(max(0.8, dur + 0.4), 2),
            })
            cur += dur
            n += 1
    return out


def http_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "EvoLyricsBridge/1.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode("utf-8"))


def fetch_synced(title, artist, duration):
    """Ищет синхронный текст на LRCLIB. Возвращает строку LRC или None."""
    base = "https://lrclib.net/api/"
    q = {"track_name": title, "artist_name": artist}
    if duration:
        q["duration"] = str(int(round(duration)))
    try:
        data = http_json(base + "get?" + urllib.parse.urlencode(q))
        if data.get("syncedLyrics"):
            return data["syncedLyrics"]
    except Exception:
        pass
    try:
        results = http_json(base + "search?" + urllib.parse.urlencode({"q": f"{artist} {title}".strip()}))
        best = None
        for r in results:
            if not r.get("syncedLyrics"):
                continue
            diff = abs((r.get("duration") or 0) - duration) if duration else 0
            if best is None or diff < best[0]:
                best = (diff, r["syncedLyrics"])
        if best and (not duration or best[0] <= 5):
            return best[1]
    except Exception:
        pass
    return None


def song_folder(title, artist):
    return os.path.join(SONGS_DIR, safe_name(f"{artist} - {title}" if artist else title))


def download_lyrics(title, artist, duration):
    folder = song_folder(title, artist)
    path = os.path.join(folder, "lyrics.json")
    # не перезаписываем, если там уже есть строки (свои или скачанные раньше)
    try:
        with open(path, encoding="utf-8") as f:
            if json.load(f).get("lyrics"):
                return
    except Exception:
        pass
    lrc = fetch_synced(title, artist, duration)
    if not lrc:
        print(f"[-] Текст не найден: {artist} - {title}")
        return
    lines = build_lines(parse_lrc(lrc))
    if not lines:
        print(f"[-] Пустой текст: {artist} - {title}")
        return
    os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"title": title, "artist": artist, "lyrics": lines}, f, ensure_ascii=False, indent=2)
    print(f"[+] Текст скачан ({len(lines)} строк): {artist} - {title}. В игре: K -> Reload songs")


def ensure_song_stub(title, artist):
    folder = os.path.join(SONGS_DIR, safe_name(f"{artist} - {title}" if artist else title))
    path = os.path.join(folder, "lyrics.json")
    if os.path.exists(path):
        return
    os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"title": title, "artist": artist, "lyrics": []}, f, ensure_ascii=False, indent=2)
    print(f"[+] Создана заготовка песни: {folder}")


def pick_session(manager):
    sessions = list(manager.get_sessions())
    for s in sessions:
        if "spotify" in (s.source_app_user_model_id or "").lower():
            return s
    return manager.get_current_session()


def write_atomic(data):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    text = json.dumps(data, ensure_ascii=False)
    tmp = BRIDGE_FILE + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, BRIDGE_FILE)
        return
    except OSError:
        pass  # Windows иногда блокирует файл, пишем напрямую
    try:
        with open(BRIDGE_FILE, "w", encoding="utf-8") as f:
            f.write(text)
    except OSError:
        pass  # файл занят, повторим на следующем тике


async def main():
    manager = await SessionManager.request_async()
    last_key = None
    print("EvoLyrics bridge v2 (автотекст LRCLIB) запущен. Окно можно свернуть. Остановка: Ctrl+C")
    while True:
        try:
            session = pick_session(manager)
            if session is None:
                write_atomic({"title": "", "artist": "", "position_ms": 0, "playing": False})
            else:
                props = await session.try_get_media_properties_async()
                title = props.title or ""
                artist = props.artist or ""
                playing = session.get_playback_info().playback_status == PlaybackStatus.PLAYING
                tl = session.get_timeline_properties()
                pos = tl.position.total_seconds()
                try:
                    length = (tl.end_time - tl.start_time).total_seconds()
                except Exception:
                    length = 0
                if playing:
                    try:
                        now = datetime.datetime.now(datetime.timezone.utc)
                        pos += max(0.0, (now - tl.last_updated_time).total_seconds())
                    except Exception:
                        pass
                write_atomic({
                    "title": title,
                    "artist": artist,
                    "position_ms": int(pos * 1000),
                    "playing": bool(playing),
                })
                key = (title, artist)
                if AUTO_CREATE_SONGS and title and key != last_key:
                    ensure_song_stub(title, artist)
                    if AUTO_LYRICS:
                        threading.Thread(target=download_lyrics, args=(title, artist, length), daemon=True).start()
                    last_key = key
        except Exception as e:  # не падаем из-за разовых ошибок
            print("Ошибка:", e)
        await asyncio.sleep(INTERVAL)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
