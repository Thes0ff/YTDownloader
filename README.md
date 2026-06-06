# YouTube Downloader GUI

**Ультимативный кроссплатформенный загрузчик видео и аудио с YouTube в максимальном качестве (1440p/1080p 60FPS).**  
Написан на Python (Tkinter) с использованием `yt-dlp`. Имеет динамический фото-сайдбар рекламы, управляемый удалённо, плавный прогресс-бар, встроенный спидометр скорости и полную поддержку горячих клавиш Ctrl+C/Ctrl+V на русской раскладке Windows.

---

## Возможности

- 🎬 Скачивание видео в лучшем качестве (bestvideo+bestaudio → MP4)
- 🌗 Переключение тем (Тёмная / Светлая)
- 🌐 Локализация (RU / EN)
- 🚫 Кнопка мгновенной отмены загрузки
- 📊 Плавный прогресс-бар + спидометр скорости
- 🧹 Умная очистка ANSI-кодов лога
- 🛡️ Защита от обрывов сети (15 ретраев)
- 📦 Консольный режим: `python downloader.py "https://..."`

---

## Системные требования

- **Python 3.8+**
- **ffmpeg** (для склейки видео и аудио)
- **deno** (опционально, для некоторых расширенных функций)

---

## Установка зависимостей

### Все ОС
```bash
pip install yt-dlp Pillow
```

### Windows
1. Скачайте готовый `.exe` во вкладке **Releases**.
2. Положите рядом `ffmpeg.exe` и `deno.exe`.

### macOS
```bash
brew install python ffmpeg deno
```

### Linux (Debian/Ubuntu)
```bash
sudo apt install python3 ffmpeg
curl -fsSL https://deno.land/x/install/install.sh | sh
```

---

## Запуск из исходников

```bash
python downloader.py
```

Ссылки можно передавать и напрямую (консольный режим):

```bash
python downloader.py "https://youtube.com/watch?v=..." "https://youtube.com/watch?v=..."
```

---

## Сборка в .exe

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --clean downloader.py
```

Готовый файл появится в папке `dist/`.

---

## Структура проекта

```
YTDownloader/
├── downloader.py       # Основной скрипт (GUI + консоль)
├── requirements.txt    # Зависимости Python
├── .gitignore          # Игнорируемые файлы Git
├── README.md           # Этот файл
├── downloads/          # Скачанные видео (создаётся автоматически)
├── build/              # Временные файлы PyInstaller (игнорируются)
└── dist/               # Готовый .exe (игнорируется)
```

---

## Лицензия

MIT

---

# YouTube Downloader GUI

**The ultimate cross-platform YouTube video and audio downloader in maximum quality (1440p/1080p 60FPS).**  
Written in Python (Tkinter) using `yt-dlp`. Features a dynamic photo ad sidebar (remotely controlled), smooth progress bar, built-in speedometer, and full support for Ctrl+C/Ctrl+V hotkeys on Russian Windows keyboard layouts.

---

## Features

- 🎬 Download videos in best quality (bestvideo+bestaudio → MP4)
- 🌗 Theme switching (Dark / Light)
- 🌐 Localization (RU / EN)
- 🚫 Instant cancel button
- 📊 Smooth progress bar + speedometer
- 🧹 Smart ANSI code cleanup in logs
- 🛡️ Network failure protection (15 retries)
- 📦 Console mode: `python downloader.py "https://..."`

---

## System Requirements

- **Python 3.8+**
- **ffmpeg** (for merging video and audio)
- **deno** (optional, for some advanced features)

---

## Installing Dependencies

### All OS
```bash
pip install yt-dlp Pillow
```

### Windows
1. Download the ready `.exe` from the **Releases** tab.
2. Place `ffmpeg.exe` and `deno.exe` next to it.

### macOS
```bash
brew install python ffmpeg deno
```

### Linux (Debian/Ubuntu)
```bash
sudo apt install python3 ffmpeg
curl -fsSL https://deno.land/x/install/install.sh | sh
```

---

## Running from Source

```bash
python downloader.py
```

You can also pass URLs directly (console mode):

```bash
python downloader.py "https://youtube.com/watch?v=..." "https://youtube.com/watch?v=..."
```

---

## Building to .exe

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --clean downloader.py
```

The ready file will appear in the `dist/` folder.

---

## Project Structure

```
YTDownloader/
├── downloader.py       # Main script (GUI + console)
├── requirements.txt    # Python dependencies
├── .gitignore          # Git ignored files
├── README.md           # This file
├── downloads/          # Downloaded videos (auto-created)
├── build/              # PyInstaller temp files (ignored)
└── dist/               # Ready .exe (ignored)
```

---

## License

MIT
