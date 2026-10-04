<div align="center">

# 🎵 Stolas Lyrics

**Синхронные 3D-тексты песен прямо в мире Minecraft**

![Minecraft](https://img.shields.io/badge/Minecraft-1.20.1-62B47A?style=for-the-badge)
![Forge](https://img.shields.io/badge/Forge-47.4.23-DF6B2A?style=for-the-badge)
![Side](https://img.shields.io/badge/Side-Client-5865F2?style=for-the-badge)
![Version](https://img.shields.io/badge/Version-1.0.0-B14CFF?style=for-the-badge)

</div>

---

## ✨ Возможности

- 🎤 Слова песни появляются в игровом мире в такт музыке
- 🎧 Автоматически видит, что играет в **Spotify**, и подхватывает трек
- 🌐 Тексты с таймингами скачиваются сами с [LRCLIB](https://lrclib.net) (ключи не нужны)
- 🎨 Эффекты появления: `fade` · `rise` · `scale_in` · `slide_left` · `slide_right` · `pop` · `float` · `rotate`
- ⚙️ Меню настроек в игре
- 🖥️ Только клиентский мод: на сервер ставить не нужно

---

## 📦 Установка

1. Установи **Minecraft 1.20.1** и **Forge 47.4.23** или новее.
2. Скачай `StolasLyrics-1.0.0.jar` и положи в папку `mods`.
3. Запусти игру.

---

## 🌉 Bridge (связь со Spotify)

Мод сам не видит Spotify. Для этого есть маленькая программа **bridge**, которая пишет, что сейчас играет, в `bridge.json`.

> Работает только на **Windows** (нужен Windows 10/11 и десктопный Spotify).

**Установка (один раз):**

```bash
pip install winsdk
```

**Запуск:**

```bash
python bridge.py
```

или двойной клик по `start_bridge.bat`. Окно можно свернуть. Остановка: `Ctrl+C`.

Файлы лежат в `%APPDATA%\.minecraft\config\evolyrics\`:

| Файл | Что это |
|------|---------|
| `bridge.json` | текущий трек и позиция |
| `songs/<Исполнитель - Название>/lyrics.json` | тексты песен |
| `bridge.log` | журнал работы bridge |

Когда текст скачан, в игре нажми **K → Reload songs** (или команду `/stolaslyrics reload`).

---

## 🎮 Управление

| Клавиша | Действие |
|---------|----------|
| `K` | Открыть меню Stolas Lyrics |

---

## 💬 Команды

Основная команда: `/stolaslyrics`

| Команда | Описание |
|---------|----------|
| `/stolaslyrics list` | список загруженных песен |
| `/stolaslyrics reload` | перечитать песни с диска |
| `/stolaslyrics play <песня>` | включить песню |
| `/stolaslyrics pause` | пауза |
| `/stolaslyrics resume` | продолжить |
| `/stolaslyrics stop` | остановить |
| `/stolaslyrics seek <секунды>` | перемотать |
| `/stolaslyrics add <эффект> <текст>` | добавить строку в активную песню на текущей секунде |

---

## 📝 Свои тексты

Каждая песня это папка `songs/<Исполнитель - Название>/` с файлом `lyrics.json`:

```json
{
  "title": "Название",
  "artist": "Исполнитель",
  "lyrics": [
    { "time": 12.5, "text": "первые слова", "effect": "FADE", "out": "FADE", "duration": 2.0 }
  ]
}
```

---

## 🔧 Сборка

```bash
gradle build
```

Готовый .jar появится в `build/libs/`. Сборка также запускается автоматически через GitHub Actions.

---

<div align="center">

Сделано с ♥ · Stolas Lyrics

</div>
