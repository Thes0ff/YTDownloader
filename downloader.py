#!/usr/bin/env python3
"""
YouTube Downloader — полноценный GUI на tkinter/ttk с переключением тем,
локализацией RU/EN, рекламным сайдбаром и агрессивными сетевыми настройками.
Использует yt-dlp для загрузки лучшего качества видео+аудио в MP4.
"""

import os
import io
import threading
import queue
import urllib.request
import urllib.error
from tkinter import (
    Tk, BooleanVar, StringVar, Frame, Label, Button, Entry, Menu,
    scrolledtext, filedialog, messagebox, ttk
)
from tkinter import ttk as ttk2
from PIL import Image, ImageTk
import yt_dlp


# URL для загрузки картинки-баннера из интернета
AD_IMAGE_URL = "https://raw.githubusercontent.com/ThreePex/ytd-ad/main/ad.png"


# ===== Конфигурация цветов для двух тем =====

THEMES = {
    'dark': {
        'bg':            '#1e1e1e',
        'fg':            '#d4d4d4',
        'input_bg':      '#2d2d2d',
        'input_fg':      '#d4d4d4',
        'button_bg':     '#0e639c',
        'button_fg':     '#ffffff',
        'button_active': '#1177bb',
        'log_bg':        '#1a1a1a',
        'log_fg':        '#cccccc',
        'accent':        '#4EC9B0',
        'select_bg':     '#264f78',
        'frame_bg':      '#252526',
        'disabled_bg':   '#3c3c3c',
        'disabled_fg':   '#6e6e6e',
        'sidebar_bg':    '#252526',
    },
    'light': {
        'bg':            '#f5f5f5',
        'fg':            '#1a1a1a',
        'input_bg':      '#ffffff',
        'input_fg':      '#1a1a1a',
        'button_bg':     '#0078d4',
        'button_fg':     '#ffffff',
        'button_active': '#106ebe',
        'log_bg':        '#fafafa',
        'log_fg':        '#333333',
        'accent':        '#0078d4',
        'select_bg':     '#cce8ff',
        'frame_bg':      '#e8e8e8',
        'disabled_bg':   '#cccccc',
        'disabled_fg':   '#888888',
        'sidebar_bg':    '#e8e8e8',
    },
}


# ===== ЛОКАЛИЗАЦИЯ RU / EN =====

L10N = {
    'ru': {
        'window_title':       "YouTube Downloader",
        'app_title':          "YouTube Downloader",
        'dark_theme':         "Тёмная тема",
        'lang_label':         "Язык:",
        'save_folder':        "Папка сохранения:",
        'browse':             "Обзор",
        'urls_label':         "Ссылки на YouTube (каждая с новой строки):",
        'download':           "Скачать",
        'downloading':        "Скачивание...",
        'log_label':          "Лог скачивания:",
        'ad_placeholder':     "По вопросам рекламы обращаться в Telegram: @ThreePex",
        'status_ready':       "Готов к работе",
        'status_downloading': "Скачивание: {}",
        'status_finished':    "Завершено!",
        'already_downloading_title': "Уже идёт скачивание",
        'already_downloading_msg':   "Дождитесь завершения текущего скачивания.",
        'no_urls_title':      "Нет ссылок",
        'no_urls_msg':        "Вставьте хотя бы одну ссылку на YouTube.",
        'starting':           "Начинаю скачивание {} видео...",
        'processing':         "[{}/{}] Обрабатываю: {}",
        'error':              "[ERROR] {}: {}",
        'skip':               "[INFO] Перехожу к следующей ссылке...",
        'done':               "[OK] Все видео сохранены в: {}",
        'done_file':          "[OK] Загрузка завершена: {}",
        'progress':           "  Прогресс: {}",
        'speed':              " | Скорость: {}",
        'eta':                " | Осталось: {}",
        'ctx_paste':          "Вставить",
        'ctx_copy':           "Копировать",
        'ctx_clear':          "Очистить",
        'cancel_btn':         "Отмена",
        'cancel_log':         "[INFO] Скачивание отменяется...",
    },
    'en': {
        'window_title':       "YouTube Downloader",
        'app_title':          "YouTube Downloader",
        'dark_theme':         "Dark theme",
        'lang_label':         "Language:",
        'save_folder':        "Save folder:",
        'browse':             "Browse",
        'urls_label':         "YouTube links (one per line):",
        'download':           "Download",
        'downloading':        "Downloading...",
        'log_label':          "Download log:",
        'ad_placeholder':     "For advertising inquiries, contact Telegram: @ThreePex",
        'status_ready':       "Ready",
        'status_downloading': "Downloading: {}",
        'status_finished':    "Finished!",
        'already_downloading_title': "Already downloading",
        'already_downloading_msg':   "Please wait for the current download to finish.",
        'no_urls_title':      "No URLs",
        'no_urls_msg':        "Please paste at least one YouTube link.",
        'starting':           "Starting download of {} videos...",
        'processing':         "[{}/{}] Processing: {}",
        'error':              "[ERROR] {}: {}",
        'skip':               "[INFO] Skipping to next link...",
        'done':               "[OK] All videos saved to: {}",
        'done_file':          "[OK] Download finished: {}",
        'progress':           "  Progress: {}",
        'speed':              " | Speed: {}",
        'eta':                " | ETA: {}",
        'ctx_paste':          "Paste",
        'ctx_copy':           "Copy",
        'ctx_clear':          "Clear",
        'cancel_btn':         "Cancel",
        'cancel_log':         "[INFO] Canceling download...",
    },
}


class YtdlCustomLogger:
    """Кастомный логгер для yt-dlp, направляющий логи напрямую в GUI."""
    def __init__(self, gui):
        self.gui = gui
    def debug(self, msg):
        msg_lower = msg.lower()
        if "proxy" in msg_lower or "timeout" in msg_lower or "retry" in msg_lower:
            self.gui._log(f"  [DEBUG] {msg}")
    def warning(self, msg):
        self.gui._log(f"  [WARNING] {msg}")
    def error(self, msg):
        self.gui._log(f"  [ERROR] {msg}")


class YouTubeDownloaderGUI:
    """Главное окно приложения."""

    def __init__(self, root: Tk) -> None:
        self.root = root
        self.root.title("YouTube Downloader")
        self.root.geometry("1050x620")
        self.root.minsize(850, 500)

        # Папка по умолчанию
        self.output_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'downloads'
        )
        os.makedirs(self.output_dir, exist_ok=True)

        # Переменные состояния
        self.is_dark = BooleanVar(value=True)
        self.theme_name = StringVar(value='dark')
        self.current_theme = THEMES['dark'].copy()
        self.lang = StringVar(value='ru')
        self.log_queue: queue.Queue = queue.Queue()
        self.is_downloading = False
        self.cancel_requested = False
        self._progress_value = 0.0
        self.ad_image = None  # будет установлено после загрузки картинки

        # Стили ttk
        self.style = ttk2.Style()
        self.style.theme_use('clam')

        # Создаём UI
        self._build_ui()

        # Универсальные биндинги для копирования, вставки и выделения по кодам клавиш
        self.root.bind_class("Text", "<Control-KeyPress>",
                             lambda event: self._handle_global_shortcuts(event))
        self.root.bind_class("Entry", "<Control-KeyPress>",
                             lambda event: self._handle_global_shortcuts(event))

        # Применяем начальную тему
        self._apply_theme()

        # Запускаем опрос очереди логов
        self._poll_log_queue()

        # Навешиваем отслеживание переключателя темы
        self.is_dark.trace_add('write', lambda *_: self._toggle_theme())

        # Навешиваем отслеживание языка
        self.lang.trace_add('write', lambda *_: self._apply_language())

        # Загружаем динамическую рекламу из интернета (фоновый поток)
        self._load_ad_network()

    # =====================================================================
    #  ПОСТРОЕНИЕ ИНТЕРФЕЙСА
    # =====================================================================

    def _build_ui(self) -> None:
        # --- Главный контейнер (горизонтальный split) ---
        self.main_paned = Frame(self.root)
        self.main_paned.pack(fill='both', expand=True, padx=14, pady=14)

        # === ЛЕВАЯ ПАНЕЛЬ (~75%) ===
        self.left_frame = Frame(self.main_paned)
        self.left_frame.pack(side='left', fill='both', expand=True, padx=(0, 8))

        # === ПРАВАЯ ПАНЕЛЬ (сайдбар, ~220px) ===
        self.right_frame = Frame(self.main_paned, width=220)
        self.right_frame.pack(side='right', fill='y', padx=(8, 0))
        self.right_frame.pack_propagate(False)

        # --- Наполняем левую панель ---

        # === Верхняя панель: переключатель темы + язык ===
        top_bar = Frame(self.left_frame)
        top_bar.pack(fill='x', pady=(0, 10))

        self.app_title_label = Label(
            top_bar, text="YouTube Downloader",
            font=('Segoe UI', 16, 'bold')
        )
        self.app_title_label.pack(side='left')

        # Переключатель языка
        lang_frame = Frame(top_bar)
        lang_frame.pack(side='right', padx=(6, 0))
        self.lang_label = Label(lang_frame, text="Язык:",
                                font=('Segoe UI', 9))
        self.lang_label.pack(side='left', padx=(0, 4))
        self.lang_combo = ttk2.Combobox(
            lang_frame, values=['RU', 'EN'], state='readonly',
            width=4, font=('Segoe UI', 9),
            textvariable=StringVar(value='RU')
        )
        self.lang_combo.current(0)
        self.lang_combo.pack(side='left')
        self.lang_combo.bind('<<ComboboxSelected>>',
                             lambda e: self._on_lang_change())

        # Переключатель темы
        theme_frame = Frame(top_bar)
        theme_frame.pack(side='right', padx=(10, 0))
        self.dark_theme_label = Label(theme_frame, text="Тёмная тема",
                                      font=('Segoe UI', 9))
        self.dark_theme_label.pack(side='left', padx=(0, 6))
        ttk2.Checkbutton(
            theme_frame, variable=self.is_dark,
            style='ThemeSwitch.TCheckbutton'
        ).pack(side='left')

        # === Выбор папки ===
        folder_frame = Frame(self.left_frame)
        folder_frame.pack(fill='x', pady=(0, 8))

        self.folder_label = Label(folder_frame, text="Папка сохранения:",
                                  font=('Segoe UI', 10))
        self.folder_label.pack(side='left', padx=(0, 6))
        self.folder_entry = Entry(folder_frame, font=('Consolas', 9))
        self.folder_entry.insert(0, self.output_dir)
        self.folder_entry.pack(side='left', fill='x', expand=True, padx=(0, 6))
        self.browse_btn = Button(
            folder_frame, text="Обзор", font=('Segoe UI', 9),
            command=self._choose_folder, relief='flat', cursor='hand2',
            padx=12, pady=2
        )
        self.browse_btn.pack(side='left')

        # === Поле ввода ссылок ===
        self.urls_label = Label(
            self.left_frame,
            text="Ссылки на YouTube (каждая с новой строки):",
            font=('Segoe UI', 10)
        )
        self.urls_label.pack(anchor='w', pady=(6, 2))
        self.urls_text = scrolledtext.ScrolledText(
            self.left_frame, height=7, font=('Consolas', 10),
            wrap='word', relief='flat', borderwidth=1,
            state='normal'
        )
        self.urls_text.pack(fill='both', pady=(0, 8), expand=True)

        # Контекстное меню (ПКМ) для поля ввода ссылок
        self._build_context_menu()

        # === Прогресс-бар и статус ===
        progress_frame = Frame(self.left_frame)
        progress_frame.pack(fill='x', pady=(0, 4))
        self.progress_bar = ttk2.Progressbar(
            progress_frame, mode='determinate', value=0
        )
        self.progress_bar.pack(fill='x', side='left', expand=True, padx=(0, 8))
        self.status_label = Label(
            progress_frame, text="Готов к работе",
            font=('Segoe UI', 9), anchor='w', width=35
        )
        self.status_label.pack(side='left')

        # === Кнопка Скачать / Отмена ===
        btn_frame = Frame(self.left_frame)
        btn_frame.pack(fill='x', pady=(0, 8))
        self.download_btn = Button(
            btn_frame, text="Скачать", font=('Segoe UI', 12, 'bold'),
            relief='flat', cursor='hand2',
            padx=30, pady=6, command=self._start_download
        )
        self.download_btn.pack(side='left', padx=(0, 8))
        self.cancel_btn = Button(
            btn_frame, text="Отмена", font=('Segoe UI', 12, 'bold'),
            relief='flat', cursor='hand2',
            padx=30, pady=6, state='disabled',
            command=self._request_cancel
        )
        self.cancel_btn.pack(side='left')

        # === Лог процесса ===
        self.log_label = Label(self.left_frame, text="Лог скачивания:",
                               font=('Segoe UI', 10))
        self.log_label.pack(anchor='w', pady=(0, 2))
        self.log_text = scrolledtext.ScrolledText(
            self.left_frame, height=9, state='disabled',
            font=('Consolas', 9), wrap='word', relief='flat', borderwidth=1
        )
        self.log_text.pack(fill='both', pady=(0, 0), expand=True)

        # --- Наполняем правую панель (сайдбар) ---
        self._build_sidebar()

    def _build_sidebar(self) -> None:
        """Создаёт рекламный сайдбар."""
        # Рамка с закруглённым видом
        self.ad_frame = Frame(self.right_frame, relief='flat', borderwidth=1)
        self.ad_frame.pack(fill='both', expand=True, pady=0)

        self.ad_label = Label(
            self.ad_frame,
            text="Здесь могла бы быть ваша реклама @ThreePex",
            font=('Segoe UI', 10, 'italic'),
            wraplength=180, justify='center'
        )
        self.ad_label.pack(fill='both', expand=True, padx=10, pady=10)

    # =====================================================================
    #  ДИНАМИЧЕСКАЯ РЕКЛАМА ИЗ ИНТЕРНЕТА
    # =====================================================================

    def _load_ad_network(self) -> None:
        """В фоновом потоке скачивает картинку-баннер по URL и отображает в ad_label."""
        def _fetch():
            try:
                req = urllib.request.Request(
                    AD_IMAGE_URL,
                    headers={'User-Agent': 'Mozilla/5.0'},
                    method='GET'
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    if resp.status == 200:
                        raw_data = resp.read()
                        if raw_data:
                            # Открываем картинку из байтов
                            img = Image.open(io.BytesIO(raw_data))
                            # Масштабируем под ширину сайдбара (200px), сохраняя пропорции
                            img.thumbnail((200, 600), Image.LANCZOS)
                            photo = ImageTk.PhotoImage(img)
                            # Сохраняем ссылку, чтобы GC не удалил
                            self.ad_image = photo
                            # Обновляем лейбл в главном потоке
                            self.root.after(0, lambda: self.ad_label.configure(
                                image=self.ad_image, text=''
                            ))
                            return
            except Exception:
                pass
            # Если не получилось — оставляем стандартный текст (он уже стоит)
        threading.Thread(target=_fetch, daemon=True).start()

    # =====================================================================
    #  КОНТЕКСТНОЕ МЕНЮ
    # =====================================================================

    def _build_context_menu(self) -> None:
        """Создаёт контекстное меню для поля ввода ссылок."""
        self.context_menu = Menu(self.root, tearoff=False)

        self.ctx_paste_cmd = self.context_menu.add_command(
            label="Вставить", command=self._paste_from_clipboard
        )
        self.ctx_copy_cmd = self.context_menu.add_command(
            label="Копировать", command=self._copy_selection
        )
        self.context_menu.add_separator()
        self.ctx_clear_cmd = self.context_menu.add_command(
            label="Очистить", command=self._clear_urls
        )

        self.urls_text.bind("<Button-3>", self._show_context_menu)
        self.urls_text.bind("<Button-2>", self._show_context_menu)

    def _show_context_menu(self, event) -> None:
        """Показывает контекстное меню в позиции курсора."""
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def _paste_from_clipboard(self) -> None:
        """Вставляет текст из буфера обмена в поле ввода."""
        try:
            text = self.root.clipboard_get()
            self.urls_text.insert('insert', text)
        except Exception:
            pass

    def _copy_selection(self) -> None:
        """Копирует выделенный текст в буфер обмена."""
        try:
            selected = self.urls_text.selection_get()
            self.root.clipboard_clear()
            self.root.clipboard_append(selected)
        except Exception:
            pass

    def _clear_urls(self) -> None:
        """Очищает поле ввода ссылок."""
        self.urls_text.delete('1.0', 'end')

    def _handle_global_shortcuts(self, event) -> str | None:
        """Обрабатывает Ctrl+C, Ctrl+V, Ctrl+A по скан-кодам клавиш, полностью игнорируя раскладку."""
        key = event.keysym.lower()

        # event.keycode 86 = V, event.keycode 67 = C, event.keycode 65 = A
        if key == 'v' or event.keycode == 86:
            event.widget.event_generate("<<Paste>>")
            return "break"
        elif key == 'c' or event.keycode == 67:
            event.widget.event_generate("<<Copy>>")
            return "break"
        elif key == 'a' or event.keycode == 65:
            event.widget.event_generate("<<SelectAll>>")
            return "break"

    # =====================================================================
    #  ЛОКАЛИЗАЦИЯ
    # =====================================================================

    def _on_lang_change(self) -> None:
        """Срабатывает при выборе языка в ComboBox."""
        val = self.lang_combo.get().lower()
        self.lang.set(val)

    def _apply_language(self) -> None:
        """Переводит все надписи в интерфейсе."""
        lang = self.lang.get()
        l = L10N.get(lang, L10N['ru'])

        self.root.title(l['window_title'])
        self.app_title_label.configure(text=l['app_title'])
        self.dark_theme_label.configure(text=l['dark_theme'])
        self.lang_label.configure(text=l['lang_label'])
        self.folder_label.configure(text=l['save_folder'])
        self.browse_btn.configure(text=l['browse'])
        self.urls_label.configure(text=l['urls_label'])
        self.download_btn.configure(
            text=l['downloading'] if self.is_downloading else l['download']
        )
        self.log_label.configure(text=l['log_label'])
        self.ad_label.configure(text=l['ad_placeholder'])

        # Контекстное меню
        if hasattr(self, 'context_menu'):
            self.context_menu.entryconfig(0, label=l['ctx_paste'])
            self.context_menu.entryconfig(1, label=l['ctx_copy'])
            self.context_menu.entryconfig(3, label=l['ctx_clear'])

    # =====================================================================
    #  ТЕМЫ
    # =====================================================================

    def _toggle_theme(self) -> None:
        """Переключает тему между тёмной и светлой."""
        name = 'dark' if self.is_dark.get() else 'light'
        self.theme_name.set(name)
        self.current_theme = THEMES[name].copy()
        self._apply_theme()

    def _apply_theme(self) -> None:
        """Применяет текущую тему ко всем виджетам."""
        t = self.current_theme

        # Корневое окно и контейнеры
        self.root.configure(bg=t['bg'])
        self._apply_to_children(self.root, t)

        # Настраиваем стили ttk
        self.style.configure('ThemeSwitch.TCheckbutton',
                             background=t['bg'],
                             foreground=t['fg'],
                             indicatorbackground=t['input_bg'],
                             indicatormargin=0)
        self.style.configure('TCombobox',
                             fieldbackground=t['input_bg'],
                             foreground=t['input_fg'],
                             background=t['button_bg'],
                             arrowcolor=t['fg'])
        self.style.map('TCombobox',
                       fieldbackground=[('readonly', t['input_bg'])],
                       foreground=[('readonly', t['input_fg'])])

        # Контекстное меню
        if hasattr(self, 'context_menu'):
            self.context_menu.configure(
                bg=t['input_bg'],
                fg=t['fg'],
                activebackground=t['select_bg'],
                activeforeground=t['fg'],
                disabledforeground=t['disabled_fg'],
                selectcolor=t['accent']
            )

        # Поле ввода ссылок
        self.urls_text.configure(
            bg=t['input_bg'], fg=t['input_fg'],
            insertbackground=t['fg'],
            selectbackground=t['select_bg'],
            selectforeground=t['fg']
        )

        # Поле лога
        self.log_text.configure(
            bg=t['log_bg'], fg=t['log_fg'],
            insertbackground=t['fg'],
            selectbackground=t['select_bg'],
            selectforeground=t['fg']
        )

        # Поле папки
        self.folder_entry.configure(
            bg=t['input_bg'], fg=t['input_fg'],
            insertbackground=t['fg'],
            selectbackground=t['select_bg'],
            selectforeground=t['fg'],
            relief='flat', borderwidth=1
        )

        # Кнопки
        self.download_btn.configure(
            bg=t['button_bg'], fg=t['button_fg'],
            activebackground=t['button_active'],
            activeforeground=t['button_fg']
        )
        self.cancel_btn.configure(
            bg=t['disabled_bg'] if self.cancel_btn['state'] == 'disabled' else t['button_bg'],
            fg=t['disabled_fg'] if self.cancel_btn['state'] == 'disabled' else t['button_fg'],
            activebackground=t['button_active'],
            activeforeground=t['button_fg']
        )
        self.browse_btn.configure(
            bg=t['button_bg'], fg=t['button_fg'],
            activebackground=t['button_active'],
            activeforeground=t['button_fg']
        )

        # Стиль прогресс-бара
        self.style.configure(
            'TProgressbar',
            background=t['accent'],
            troughcolor=t['input_bg'],
            bordercolor=t['bg'],
            lightcolor=t['accent'],
            darkcolor=t['accent']
        )

        # Сайдбар
        self.right_frame.configure(bg=t['sidebar_bg'])
        self.ad_frame.configure(bg=t['sidebar_bg'])
        self.ad_label.configure(
            bg=t['sidebar_bg'],
            fg=t['fg']
        )

        # Статус-лейбл
        if hasattr(self, 'status_label'):
            self.status_label.configure(
                bg=t['bg'],
                fg=t['fg']
            )

    def _apply_to_children(self, parent, t: dict) -> None:
        """Рекурсивно применяет тему к Frame/Label, не ломая текстовые поля."""
        for child in parent.winfo_children():
            cls = child.winfo_class()

            # Если это текстовое поле или лог, их внутренности трогать нельзя
            if cls in ('Text', 'ScrolledText'):
                continue

            if cls in ('Frame', 'TLabelframe'):
                child.configure(bg=t['bg'])
            elif cls == 'Label':
                child.configure(bg=t['bg'], fg=t['fg'])

            if hasattr(child, 'winfo_children'):
                self._apply_to_children(child, t)

    # =====================================================================
    #  ВЫБОР ПАПКИ
    # =====================================================================

    def _choose_folder(self) -> None:
        folder = filedialog.askdirectory(
            initialdir=self.output_dir,
            title="Выберите папку для сохранения видео"
        )
        if folder:
            self.output_dir = folder
            self.folder_entry.delete(0, 'end')
            self.folder_entry.insert(0, folder)

    # =====================================================================
    #  ЛОГИРОВАНИЕ
    # =====================================================================

    def _log(self, message: str) -> None:
        """Добавляет сообщение в очередь лога (из любого потока)."""
        self.log_queue.put(message)

    def _poll_log_queue(self) -> None:
        """Периодически проверяет очередь и выводит сообщения в лог."""
        while not self.log_queue.empty():
            msg = self.log_queue.get_nowait()
            self.log_text.configure(state='normal')
            self.log_text.insert('end', msg + '\n')
            self.log_text.see('end')
            self.log_text.configure(state='disabled')
        self.root.after(80, self._poll_log_queue)

    # =====================================================================
    #  СКАЧИВАНИЕ
    # =====================================================================

    def _request_cancel(self) -> None:
        """Запрашивает отмену текущего скачивания."""
        self.cancel_requested = True
        self.cancel_btn.configure(state='disabled')
        l = L10N.get(self.lang.get(), L10N['ru'])
        self._log(l['cancel_log'])

    def _start_download(self) -> None:
        if self.is_downloading:
            l = L10N.get(self.lang.get(), L10N['ru'])
            messagebox.showwarning(
                l['already_downloading_title'],
                l['already_downloading_msg']
            )
            return

        raw = self.urls_text.get('1.0', 'end').strip()
        if not raw:
            l = L10N.get(self.lang.get(), L10N['ru'])
            messagebox.showerror(l['no_urls_title'], l['no_urls_msg'])
            return

        urls = [line.strip() for line in raw.splitlines() if line.strip()]

        # Очищаем лог перед новым скачиванием
        self.log_text.configure(state='normal')
        self.log_text.delete('1.0', 'end')
        self.log_text.configure(state='disabled')

        l = L10N.get(self.lang.get(), L10N['ru'])
        self._log(l['starting'].format(len(urls)))
        self.is_downloading = True
        self.cancel_requested = False
        self.download_btn.configure(state='disabled', text=l['downloading'])
        self.cancel_btn.configure(state='normal')

        # Сбрасываем прогресс
        self._progress_value = 0.0
        self.progress_bar['value'] = 0
        l10n = L10N.get(self.lang.get(), L10N['ru'])
        self.status_label.configure(text=l10n['status_downloading'].format('0%'))

        threading.Thread(
            target=self._download_all,
            args=(urls,),
            daemon=True
        ).start()

    def _download_all(self, urls: list) -> None:
        l = L10N.get(self.lang.get(), L10N['ru'])
        try:
            for i, url in enumerate(urls, start=1):
                self._log(f"\n" + l['processing'].format(i, len(urls), url))
                try:
                    self._download_single(url)
                except Exception as e:
                    self._log(l['error'].format(url, e))
                    self._log(l['skip'])
                    continue
            self._log(f"\n" + l['done'].format(self.output_dir))
        finally:
            self.is_downloading = False
            self.root.after(0, self._enable_download_button)

    def _enable_download_button(self) -> None:
        l = L10N.get(self.lang.get(), L10N['ru'])
        self.download_btn.configure(state='normal', text=l['download'])
        self.cancel_btn.configure(state='disabled')
        # Обновляем цвета cancel_btn в соответствии с темой
        self._retheme_cancel()
        # Прогресс 100%
        self.progress_bar['value'] = 100
        self.status_label.configure(text=l['status_finished'])

    def _retheme_cancel(self) -> None:
        """Применяет тему к cancel_btn (вызывается при смене состояния disabled/normal)."""
        t = self.current_theme
        if self.cancel_btn['state'] == 'disabled':
            self.cancel_btn.configure(
                bg=t['disabled_bg'], fg=t['disabled_fg']
            )
        else:
            self.cancel_btn.configure(
                bg=t['button_bg'], fg=t['button_fg']
            )

    def _download_single(self, url: str) -> None:
        """Скачивает одно видео с агрессивными сетевыми настройками."""
        l = L10N.get(self.lang.get(), L10N['ru'])

        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'no_warnings': False,
            'logger': YtdlCustomLogger(self),
            'progress_hooks': [self._progress_hook],
            'retries': 15,
            'fragment_retries': 15,
            'socket_timeout': 30,
            'file_access_retries': 5,
            'noprogress': True,
            'noplaylist': True,
            'remote_components': ['ejs:github'],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    def _progress_hook(self, d: dict) -> None:
        """Хук прогресса — очищает ANSI-коды и плавно двигает прогресс-бар."""
        import re

        if self.cancel_requested:
            raise Exception("Canceled by user")

        if d['status'] == 'downloading':
            percent = 0.0
            percent_str = "0%"
            speed_str = d.get('_speed_str', '?')

            if '_percent_str' in d:
                try:
                    # Регуляркой полностью вырезаем любые ANSI-escape последовательности (типа \x1b[0;94m)
                    raw_str = d['_percent_str']
                    clean_str = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', raw_str).strip()
                    
                    percent_str = clean_str
                    percent = float(clean_str.replace('%', '').strip())
                except ValueError:
                    pass
            elif 'downloaded_bytes' in d:
                downloaded = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                if total > 0:
                    percent = (downloaded / total) * 100
                    percent_str = f"{percent:.1f}%"

            # Очищаем строку скорости от возможных ANSI-кодов
            if speed_str and speed_str != '?':
                speed_str = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', speed_str).strip()

            # Безопасно передаем чистые данные в GUI поток
            self.root.after(0, self._update_progress, percent, percent_str, speed_str)

        elif d['status'] == 'finished':
            self._log(L10N.get(self.lang.get(), L10N['ru'])['done_file'].format(os.path.basename(d['filename'])))

    def _update_progress(self, percent: float, percent_str: str, speed_str: str = '?') -> None:
        """Безопасно и принудительно обновляет значение прогресс-бара и текст статуса."""
        # Ограничиваем процент строго от 0 до 100
        pct = min(max(percent, 0.0), 100.0)
        
        # Явно обновляем значение виджета
        self.progress_bar.configure(value=pct)
        self._progress_value = pct
        
        # Формируем и выводим чистый текст статуса
        l = L10N.get(self.lang.get(), L10N['ru'])
        status_text = l['status_downloading'].format(percent_str)
        if speed_str and speed_str != '?':
            status_text += f" | {l['speed'].format(speed_str)}"
        self.status_label.configure(text=status_text)


def console_download(urls: list) -> None:
    """Консольный режим: скачивает переданные ссылки без GUI."""
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
    os.makedirs(output_dir, exist_ok=True)

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'progress': True,
        'retries': 15,
        'fragment_retries': 15,
        'socket_timeout': 60,
        'file_access_retries': 5,
    }

    total = len(urls)
    for i, url in enumerate(urls, start=1):
        print(f"\n[{i}/{total}] Обрабатываю: {url}")
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print(f"[OK] Загрузка завершена: {url}")
        except Exception as e:
            print(f"[ERROR] {url}: {e}")
            print("[INFO] Перехожу к следующей ссылке...")
            continue

    print(f"\n[OK] Все видео сохранены в: {output_dir}")


def main() -> None:
    import sys

    if len(sys.argv) > 1:
        # Консольный режим: ссылки переданы как аргументы
        urls = [url for url in sys.argv[1:] if url.strip()]
        console_download(urls)
    else:
        # GUI режим
        root = Tk()
        YouTubeDownloaderGUI(root)
        root.mainloop()


if __name__ == '__main__':
    main()
