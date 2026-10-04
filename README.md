# EvoLyrics (Forge 1.20.1-47.4.23, клиентский мод)

## Как получить .jar (без установки чего-либо)
1. Зарегистрируйся на github.com, нажми New repository (любое имя, Public).
2. Add file -> Upload files, перетащи ВСЁ содержимое этой папки (включая папку .github).
   Если .github не загрузилась: Add file -> Create new file, имя `.github/workflows/build.yml`, вставь содержимое файла.
3. Вкладка Actions -> Build EvoLyrics -> Run workflow (или просто дождись автозапуска).
4. Через 3-6 минут открой завершённый запуск -> Artifacts -> EvoLyrics-jar. Внутри EvoLyrics-1.0.0.jar.
5. Положи jar в .minecraft/mods. Если сборка красная, скопируй текст ошибки и пришли мне.

## Игра
- Клавиша K: меню (там же включается "островок" с названием песни сверху). Команды: /evolyrics list | play <песня> | pause | resume | stop | seek <сек> | reload
- При первом запуске создаётся песня `example` (config/evolyrics/songs/example/lyrics.json): /evolyrics play example
- Мини-редактор: /evolyrics add <эффект> <текст> добавляет строку на текущий момент и сохраняет файл.

## Формат
config/evolyrics/songs/<имя>/lyrics.json
{ "title": "", "artist": "",
  "lyrics": [ { "time": 12.4, "text": "...", "effect": "rise", "out": "fade", "duration": 2.0, "position": "left" } ] }
effect/out: fade, rise, scale_in, scale_out, slide_left, slide_right, pop, float, rotate.
position (необязательно): left, right, center, top, bottom, random.

## Music bridge
Внешняя программа пишет файл config/evolyrics/bridge.json каждые 100-250 мс:
{ "title": "...", "artist": "...", "position_ms": 84320, "playing": true }
В меню Source -> Bridge. Песня подбирается по title/artist (или имени папки).
