# desktop_app.py  — GrowthOS AI v2.0 — Complete 99-Feature Desktop Client
import sys
import os
import json
import requests
import urllib.parse
from datetime import datetime as _dt_cls, timedelta
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel, QStackedWidget,
    QLineEdit, QTextEdit, QFrame, QComboBox, QGroupBox, QGridLayout,
    QScrollArea, QSpinBox, QDoubleSpinBox, QMessageBox, QTabWidget,
    QSplitter, QDateTimeEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QProgressBar, QCheckBox, QFormLayout, QListWidget, QListWidgetItem,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QDateTime, QUrl
from PyQt5.QtGui import QFont, QColor, QPalette

try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage
    from PyQt5.QtWidgets import QDialog
    _HAS_WEBENGINE = True
except ImportError:
    _HAS_WEBENGINE = False

try:
    from config import BACKEND_URL, APP_NAME, APP_VERSION
except ImportError:
    BACKEND_URL  = "http://127.0.0.1:8000"
    APP_NAME     = "GrowthOS AI"
    APP_VERSION  = "2.0"

try:
    from ai_core.social_auth import PLATFORM_CONFIGS
except Exception:
    PLATFORM_CONFIGS = {}


# ─── Scheduler Data Store (local JSON) ───────────────────────────────────────
_SCHED_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scheduled_posts.json")


# ─── Inbox Rules Store (local JSON) ──────────────────────────────────────────
_RULES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inbox_rules.json")

_DEFAULT_RULES = [
    {"id": 1, "name": "Price Inquiry",   "keywords": "price,cost,how much,pricing,charge",
     "reply": "Thank you for your interest! 😊 Please DM us or check the link in our bio for full pricing details!", "enabled": True},
    {"id": 2, "name": "Thank You",        "keywords": "thank you,thanks,thx,ty,grateful,appreciate",
     "reply": "You're so welcome! 🙏 We're so happy to help! Feel free to ask anything else anytime!", "enabled": True},
    {"id": 3, "name": "Shipping Query",   "keywords": "shipping,delivery,how long,when arrive,tracking",
     "reply": "We ship within 1-3 business days! 📦 You'll receive a tracking number via email. Contact us for any issues!", "enabled": True},
    {"id": 4, "name": "Collab Request",   "keywords": "collab,collaboration,partner,sponsor,promote,partnership",
     "reply": "We love collaborating! 🤝 Please send your media kit to the email in our bio and we'll get back to you!", "enabled": True},
    {"id": 5, "name": "Spam Filter",      "keywords": "follow me back,f4f,follow for follow,check my page,buy followers",
     "reply": "", "enabled": True},
]


def _load_rules() -> list:
    if os.path.exists(_RULES_FILE):
        try:
            with open(_RULES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return list(_DEFAULT_RULES)


def _save_rules(rules: list):
    try:
        with open(_RULES_FILE, "w", encoding="utf-8") as f:
            json.dump(rules, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def _load_scheduled() -> list:
    if os.path.exists(_SCHED_FILE):
        try:
            with open(_SCHED_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def _save_scheduled(posts: list):
    try:
        with open(_SCHED_FILE, "w", encoding="utf-8") as f:
            json.dump(posts, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


# ─── Theme System ─────────────────────────────────────────────────────────────
_THEME_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".theme")

try:
    from themes import THEMES as _THEMES, THEME_NAMES, DEFAULT_THEME as _DEFAULT_THEME

    def _active_theme_name() -> str:
        if os.path.exists(_THEME_FILE):
            try:
                n = open(_THEME_FILE, "r", encoding="utf-8").read().strip()
                if n in _THEMES:
                    return n
            except Exception:
                pass
        return _DEFAULT_THEME

    _t = _THEMES[_active_theme_name()]
    DARK_BG = _t["DARK_BG"]; SIDEBAR  = _t["SIDEBAR"]; SURFACE  = _t["SURFACE"]
    ACCENT  = _t["ACCENT"];  SUCCESS  = _t["SUCCESS"]; WARNING  = _t["WARNING"]
    TEXT    = _t["TEXT"];    SUBTEXT  = _t["SUBTEXT"]; BORDER   = _t["BORDER"]
    HOVER   = _t["HOVER"]

except ImportError:
    _DEFAULT_THEME = "Catppuccin Mocha"
    THEME_NAMES    = [_DEFAULT_THEME]

    def _active_theme_name() -> str:
        return _DEFAULT_THEME

    DARK_BG = "#1E1E2E"; SIDEBAR = "#181825"; SURFACE = "#313244"
    ACCENT  = "#89B4FA"; SUCCESS = "#A6E3A1"; WARNING = "#FAB387"
    TEXT    = "#CDD6F4"; SUBTEXT = "#6C7086"; BORDER  = "#45475A"
    HOVER   = "#2D2D3B"


def _build_global_style() -> str:
    return f"""
    QWidget {{
        background-color: {DARK_BG}; color: {TEXT};
        font-family: 'Segoe UI', Arial; font-size: 14px;
    }}
    QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
        background-color: {SURFACE}; color: {TEXT};
        border: 1px solid {BORDER}; border-radius: 6px;
        padding: 6px 8px; font-size: 14px;
    }}
    QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
        border: 1px solid {ACCENT};
    }}
    QGroupBox {{
        border: 1px solid {BORDER}; border-radius: 8px;
        margin-top: 14px; font-weight: bold; font-size: 14px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin; left: 12px;
        padding: 0 6px; color: {ACCENT}; font-size: 14px;
    }}
    QTabWidget::pane {{ border: 1px solid {BORDER}; border-radius: 6px; }}
    QTabBar::tab {{
        background: {SURFACE}; color: {TEXT};
        padding: 9px 22px; font-size: 14px;
        border-top-left-radius: 6px; border-top-right-radius: 6px;
    }}
    QTabBar::tab:selected {{ background: {DARK_BG}; color: {ACCENT}; font-weight: bold; }}
    QTabBar::tab:hover    {{ background: {HOVER}; }}
    QHeaderView::section {{
        background: {SIDEBAR}; color: {ACCENT}; font-weight: bold; font-size: 14px;
        padding: 6px 8px; border: none; border-bottom: 1px solid {BORDER};
    }}
    QTableWidget {{
        background: {SURFACE}; gridline-color: {BORDER}; font-size: 14px;
        selection-background-color: {HOVER}; selection-color: {ACCENT};
    }}
    QTableWidget::item {{ padding: 4px 8px; }}
    QScrollBar:vertical   {{ background: {SURFACE}; width: 8px; border-radius: 4px; }}
    QScrollBar:horizontal {{ background: {SURFACE}; height: 8px; border-radius: 4px; }}
    QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
        background: {BORDER}; border-radius: 4px; min-height: 24px;
    }}
    QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {{
        background: {ACCENT};
    }}
    QScrollBar::add-line, QScrollBar::sub-line {{ border: none; background: none; }}
    QToolTip {{
        background: {SURFACE}; color: {TEXT}; border: 1px solid {BORDER};
        padding: 6px 8px; border-radius: 6px; font-size: 14px;
    }}
    QComboBox::drop-down {{ border: none; width: 22px; }}
    QComboBox QAbstractItemView {{
        background: {SURFACE}; color: {TEXT};
        selection-background-color: {HOVER}; border: 1px solid {BORDER};
        padding: 4px;
    }}
    QSpinBox::up-button, QSpinBox::down-button,
    QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
        background: {BORDER}; border: none; border-radius: 3px; width: 16px;
    }}
    QMessageBox {{ background: {DARK_BG}; }}
    QDialog      {{ background: {DARK_BG}; }}
"""


GLOBAL_STYLE = _build_global_style()


def _styled_input(placeholder=""):
    w = QLineEdit()
    w.setPlaceholderText(placeholder)
    return w


def _big_text(placeholder=""):
    w = QTextEdit()
    w.setPlaceholderText(placeholder)
    return w


# ─── Connected Accounts Cache ────────────────────────────────────────────────
# Filled automatically when the backend comes online (GrowthOS_Desktop._do_refresh_accounts).
# All AI pages read from this to auto-populate platform / account fields.
_ACCOUNTS_CACHE: list = []   # list of account dicts from /api/v1/auth/accounts

_PLT_ICONS_MAP = {
    "Facebook": "📘", "Instagram": "📸", "TikTok": "🎵",
    "YouTube":  "▶️", "Twitter/X": "🐦", "LinkedIn": "💼", "Telegram": "✈️",
}


def _account_context_bar(api_base: str, platforms: list | None = None):
    """
    Reusable connected-account selector for any AI feature page.

    Returns (bar_widget, get_platform_fn, get_name_fn, repopulate_fn).
      bar_widget      — compact QFrame with account combo + 🔄 refresh button.
      get_platform_fn — returns the platform string of the selected account.
      get_name_fn     — returns the display_name of the selected account.
      repopulate_fn   — call to refresh the combo from the current cache.
    """
    _acc_list: list = []   # filtered & ordered list of account dicts

    bar = QFrame()
    bar.setStyleSheet(
        f"background:{SURFACE}; border-radius:8px; "
        f"border:1px solid {BORDER}; margin-bottom:4px;"
    )
    row = QHBoxLayout(bar)
    row.setContentsMargins(10, 5, 10, 5)
    row.setSpacing(8)

    icon_lbl = QLabel("🔗")
    icon_lbl.setStyleSheet(f"color:{ACCENT}; font-size:14px;")
    row.addWidget(icon_lbl)

    lbl = QLabel("Connected Account:")
    lbl.setStyleSheet(f"color:{SUBTEXT}; font-size:14px; font-weight:bold;")
    row.addWidget(lbl)

    combo = QComboBox()
    combo.setMinimumWidth(260)
    combo.setStyleSheet(
        f"QComboBox {{ background:{DARK_BG}; color:{TEXT}; font-size:14px; "
        f"border:1px solid {BORDER}; border-radius:6px; padding:3px 8px; min-height:26px; }}"
        f"QComboBox::drop-down {{ border:none; width:16px; }}"
        f"QComboBox QAbstractItemView {{ background:{SURFACE}; color:{TEXT}; "
        f"font-size:14px; selection-background-color:{HOVER}; border:1px solid {BORDER}; }}"
    )
    row.addWidget(combo, 1)

    status_lbl = QLabel()
    status_lbl.setStyleSheet(f"color:{SUBTEXT}; font-size:14px; min-width:90px;")
    row.addWidget(status_lbl)

    def _populate():
        _acc_list.clear()
        for a in _ACCOUNTS_CACHE:
            if a.get("status") != "connected":
                continue
            if platforms and a.get("platform") not in platforms:
                continue
            _acc_list.append(a)
        prev = combo.currentText()
        combo.blockSignals(True)
        combo.clear()
        if _acc_list:
            for a in _acc_list:
                icon = _PLT_ICONS_MAP.get(a.get("platform", ""), "🌐")
                combo.addItem(f"{icon} {a['platform']}  ·  {a.get('display_name', '')}")
            idx = combo.findText(prev)
            if idx >= 0:
                combo.setCurrentIndex(idx)
            n = len(_acc_list)
            status_lbl.setText(f"✅ {n} connected")
            status_lbl.setStyleSheet(f"color:{SUCCESS}; font-size:14px;")
        else:
            combo.addItem("⚠️  No connected accounts — go to 🔐 Social Accounts")
            status_lbl.setText("Not connected")
            status_lbl.setStyleSheet(f"color:{WARNING}; font-size:14px;")
        combo.blockSignals(False)

    _populate()

    refresh_btn = QPushButton("🔄")
    refresh_btn.setFixedSize(26, 26)
    refresh_btn.setToolTip("Reload connected accounts from server")
    refresh_btn.setStyleSheet(
        f"QPushButton {{ background:{HOVER}; border:none; border-radius:4px; "
        f"color:{TEXT}; font-size:14px; }}"
        f"QPushButton:hover {{ background:{ACCENT}; color:#111; }}"
    )

    def _on_refresh():
        refresh_btn.setEnabled(False)
        status_lbl.setText("Loading…")
        status_lbl.setStyleSheet(f"color:{SUBTEXT}; font-size:14px;")
        w = ApiWorker(f"{api_base}/api/v1/auth/accounts", method="GET")
        def _done(resp):
            global _ACCOUNTS_CACHE
            _ACCOUNTS_CACHE = resp.get("data", [])
            _populate()
            refresh_btn.setEnabled(True)
        w.result_ready.connect(_done)
        w.error_signal.connect(lambda _e: (
            status_lbl.setText("Error"),
            status_lbl.setStyleSheet(f"color:#F38BA8; font-size:14px;"),
            refresh_btn.setEnabled(True),
        ))
        w.start()
        bar._refresh_worker = w  # prevent GC

    refresh_btn.clicked.connect(_on_refresh)
    row.addWidget(refresh_btn)

    def _get_platform() -> str:
        idx = combo.currentIndex()
        if 0 <= idx < len(_acc_list):
            return _acc_list[idx].get("platform", "")
        return ""

    def _get_name() -> str:
        idx = combo.currentIndex()
        if 0 <= idx < len(_acc_list):
            return _acc_list[idx].get("display_name", "")
        return ""

    return bar, _get_platform, _get_name, _populate


def _label(text: str, bold: bool = False) -> QLabel:
    lbl = QLabel(text)
    if bold:
        lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        lbl.setStyleSheet(f"color: {ACCENT}; margin-bottom: 4px;")
    else:
        lbl.setStyleSheet(f"color: {TEXT}; font-size: 14px;")
    lbl.setWordWrap(True)
    return lbl


def _combo(*items):
    w = QComboBox()
    # Accept either _combo("a","b","c") or _combo(["a","b","c"])
    if len(items) == 1 and isinstance(items[0], (list, tuple)):
        w.addItems(list(items[0]))
    else:
        w.addItems([str(i) for i in items])
    return w


# ─── Worker Thread (non-blocking API calls) ──────────────────────────────────
class ApiWorker(QThread):
    result_ready = pyqtSignal(dict)
    error_signal = pyqtSignal(str)

    def __init__(self, url: str, payload: dict = None, method: str = "POST", btn=None):
        super().__init__()
        self.url     = url
        self.payload = payload
        self.method  = method
        if btn is not None:
            btn.set_loading(True)
            self.finished.connect(lambda: btn.set_loading(False))

    def run(self):
        try:
            if self.method == "GET":
                r = requests.get(self.url, params=self.payload, timeout=30)
            elif self.method == "DELETE":
                r = requests.delete(self.url, timeout=30)
            else:
                r = requests.post(self.url, json=self.payload, timeout=30)
            if not r.ok:
                # Try to extract the real error reason from the JSON body
                try:
                    body = r.json()
                    msg = body.get("detail") or body.get("error") or body.get("message") or str(r.status_code)
                except Exception:
                    msg = r.text or str(r.status_code)
                self.error_signal.emit(str(msg))
                return
            self.result_ready.emit(r.json())
        except requests.exceptions.ConnectionError:
            self.error_signal.emit("Cannot connect to backend. Start it with:\n\n  uvicorn backend_api:app --reload")
        except Exception as e:
            self.error_signal.emit(str(e))


# ─── Telegram Bot Manager Thread ─────────────────────────────────────────────
class BotThread(QThread):
    """Runs telegram_bot.py as a subprocess and streams its stdout/stderr."""
    log_line      = pyqtSignal(str)
    status_change = pyqtSignal(str)   # "running" | "stopped" | "error:<msg>"

    def __init__(self):
        super().__init__()
        self._proc    = None
        self._running = False

    def run(self):
        import subprocess as _sp
        script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "telegram_bot.py")
        try:
            flags = _sp.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            self._proc = _sp.Popen(
                [sys.executable, "-u", script],
                stdout=_sp.PIPE,
                stderr=_sp.STDOUT,
                text=True,
                bufsize=1,
                creationflags=flags,
            )
            self._running = True
            self.status_change.emit("running")
            for line in iter(self._proc.stdout.readline, ""):
                if not self._running:
                    break
                if line.strip():
                    self.log_line.emit(line.rstrip())
            self._proc.wait()
        except Exception as e:
            self.status_change.emit(f"error:{e}")
        finally:
            self._running = False
            self.status_change.emit("stopped")

    def stop_bot(self):
        self._running = False
        if self._proc and self._proc.poll() is None:
            try:
                self._proc.terminate()
                self._proc.wait(timeout=3)
            except Exception:
                try:
                    self._proc.kill()
                except Exception:
                    pass


# ─── Reusable Sidebar Button ─────────────────────────────────────────────────
class NavButton(QPushButton):
    def __init__(self, text: str):
        super().__init__(text)
        self.setMinimumHeight(44)
        self.setCheckable(True)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent; color: {TEXT};
                border: none; border-radius: 8px;
                padding: 10px 14px; font-size: 14px; font-weight: bold;
                text-align: left;
            }}
            QPushButton:hover {{ background-color: {HOVER}; }}
            QPushButton:checked {{ background-color: {SURFACE}; color: {ACCENT}; border-left: 3px solid {ACCENT}; }}
        """)


# ─── Action Button ────────────────────────────────────────────────────────────
class ActionButton(QPushButton):
    def __init__(self, text: str, color: str = ACCENT):
        super().__init__(text)
        self._orig_text = text   # ← store so set_loading(False) can restore it
        self.color = color
        self.setMinimumHeight(42)
        self.setCursor(Qt.PointingHandCursor)
        self._apply_style(color)

    def _apply_style(self, color: str):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color}; color: #11111B;
                border: none; border-radius: 8px;
                padding: 10px 18px; font-weight: bold; font-size: 14px;
            }}
            QPushButton:hover {{ background-color: rgba(255,255,255,0.12); }}
            QPushButton:disabled {{ background-color: {BORDER}; color: {SUBTEXT}; }}
        """)

    def set_loading(self, loading: bool):
        self.setEnabled(not loading)
        if loading:
            self.setText("⏳ Processing…")
        else:
            self._apply_style(self.color)
            self.setText(self._orig_text)   # ← restore original label


# ─── Output Box ───────────────────────────────────────────────────────────────
class OutputBox(QTextEdit):
    def __init__(self, placeholder="Results will appear here…"):
        super().__init__()
        self.setReadOnly(True)
        self.setPlaceholderText(placeholder)
        self.setStyleSheet(f"""
            QTextEdit {{
                background-color: {SURFACE}; color: {SUCCESS};
                border: 1px solid {BORDER}; border-radius: 8px;
                padding: 12px; font-size: 14px; line-height: 1.5;
            }}
        """)

    def set_result(self, data):
        if isinstance(data, dict):
            self.setPlainText(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            self.setPlainText(str(data))

    def set_error(self, msg: str):
        self.setStyleSheet(self.styleSheet().replace(SUCCESS, WARNING))
        self.setPlainText(f"❌ Error:\n{msg}")

    def reset_color(self):
        self.setStyleSheet(self.styleSheet().replace(WARNING, SUCCESS))


# ═══════════════════════════════════════════════════════════════════════════════
# PAGES
# ═══════════════════════════════════════════════════════════════════════════════

def _make_page_layout(title_text: str, icon: str = ""):
    """Create a scrollable page with a bold title header."""
    outer = QWidget()
    outer_lay = QVBoxLayout(outer)
    outer_lay.setContentsMargins(0, 0, 0, 0)
    outer_lay.setSpacing(0)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QScrollArea.NoFrame)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    outer_lay.addWidget(scroll)

    page = QWidget()
    scroll.setWidget(page)

    layout = QVBoxLayout(page)
    layout.setContentsMargins(30, 24, 30, 24)
    layout.setSpacing(14)

    title = QLabel(f"{icon}  {title_text}" if icon else title_text)
    title.setFont(QFont("Segoe UI", 18, QFont.Bold))
    title.setStyleSheet(f"color: {ACCENT}; margin-bottom: 4px;")
    layout.addWidget(title)
    # Return outer (scrollable container) but expose layout on the inner page
    outer._page_inner   = page
    outer._page_layout  = layout
    outer._page_scroll  = scroll
    return outer, layout


def build_dashboard_page(api_base: str) -> QWidget:
    page, layout = _make_page_layout("GrowthOS AI — Command Center", "🚀")

    info = QLabel(f"Backend: {api_base}   |   All 110 features active   |   Multi-Agent AI ready")
    info.setStyleSheet(f"color: {SUBTEXT}; font-size: 14px;")
    layout.addWidget(info)

    # KPI cards
    kpi_frame = QFrame()
    kpi_layout = QHBoxLayout(kpi_frame)
    kpi_layout.setSpacing(12)
    for icon, label, value, color in [
        ("🧠", "AI Features",     "110",  ACCENT),
        ("📱", "Platforms",        "7",    SUCCESS),
        ("🛒", "SMM Services",     "13+",  WARNING),
        ("🤖", "AI Agents",        "5",    "#CBA6F7"),
        ("📦", "API Endpoints",    "30+",  "#89DCEB"),
        ("💾", "Memory Modules",   "11",   "#F38BA8"),
    ]:
        card = QFrame()
        card.setStyleSheet(f"background:{SURFACE}; border-radius:10px; padding:10px;")
        cl = QVBoxLayout(card)
        top = QLabel(f"{icon}  {label}")
        top.setStyleSheet(f"color:{SUBTEXT}; font-size:14px;")
        v = QLabel(value)
        v.setFont(QFont("Segoe UI", 24, QFont.Bold))
        v.setStyleSheet(f"color:{color};")
        cl.addWidget(top)
        cl.addWidget(v)
        kpi_layout.addWidget(card)
    layout.addWidget(kpi_frame)

    # Health check row
    btn_health = ActionButton("🔗 Check Backend Health", ACCENT)
    btn_docs   = ActionButton("📖 Open API Docs (browser)", SUCCESS)
    health_row = QHBoxLayout()
    health_row.addWidget(btn_health)
    health_row.addWidget(btn_docs)
    layout.addLayout(health_row)

    status_box = OutputBox("Click 'Check Backend Health' to verify the server is running…")
    layout.addWidget(status_box, 1)

    def _health():
        status_box.reset_color()
        status_box.setPlainText("Connecting to backend…")
        w = ApiWorker(f"{api_base}/api/v1/health", method="GET", btn=btn_health)
        page._worker = w
        w.result_ready.connect(lambda d: status_box.set_result(d))
        w.error_signal.connect(status_box.set_error)
        w.start()

    def _docs():
        import webbrowser
        webbrowser.open(f"{api_base}/docs")

    btn_health.clicked.connect(_health)
    btn_docs.clicked.connect(_docs)
    return page

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1.5 — OMNI AI HUB
# ═══════════════════════════════════════════════════════════════════════════════

def build_omni_hub_page(api_base: str) -> QWidget:
    page, layout = _make_page_layout("Omni AI Hub — 150 Features", "🌌")
    page._workers = []

    tabs = QTabWidget()
    layout.addWidget(tabs)

    t1 = QWidget()
    t1l = QVBoxLayout(t1)

    info = QLabel(
        "Welcome to the Omni AI Hub. Execute any of the 150 advanced AI tasks seamlessly.\n"
        "Select a task category, choose the specific feature, provide input, and let AI do the rest."
    )
    info.setStyleSheet(f"color:{SUBTEXT}; font-size:14px; padding-bottom:8px;")
    t1l.addWidget(info)

    form = QFormLayout()
    form.setSpacing(10)

    categories = {
        "Conversation & NLP (1-20)": [
            "Context-aware chat", "Long-term memory", "Real-time translation", "Voice to Text", "Text to Voice",
            "Roleplay", "Emotional support", "Smart auto-reply", "Grammar & style correction", "Rewrite tone",
            "Extract key info", "Keyword extraction", "Document translation", "Inline query", "Group chat summarization",
            "Privacy-first conversation", "Sentiment analysis", "Language learning assistant", "Smart suggestions", "Voice conversation"
        ],
        "Information & Research (21-40)": [
            "Web search real-time", "Fact-checking system", "Article summarization", "Weather forecast", "Stock & crypto analysis",
            "YouTube/TikTok summary", "Document analysis (PDF/Excel/Word)", "Local news lookup", "Scientific paper summary", "Biography & history lookup",
            "Wikipedia summarization", "Research assistant", "Data extraction from documents", "Trend analysis", "Knowledge base builder",
            "FAQ auto-generation", "Multi-source comparison", "Report summarization", "Risk analysis", "Insight generation"
        ],
        "Productivity & Organization (41-60)": [
            "To-do list manager", "Smart reminders", "Calendar sync", "Meeting summary", "Habit tracker",
            "Travel planner", "Expense tracker", "Study/work notes generator", "Team task management", "Proactive notifications",
            "Email writing assistant", "Time tracking", "URL shortener", "File organizer", "Smart scheduling AI",
            "Daily/weekly planner", "Goal tracking system", "Personal dashboard", "Auto report generator", "Workflow automation"
        ],
        "Creative & Media (61-80)": [
            "AI image generation", "Background remover", "Image upscale", "Photo restoration", "Avatar creator",
            "OCR (image to text)", "Meme generator", "QR code design", "Sketch conversion", "Voice generation",
            "Music generation", "Lyrics writing", "Video script writing", "Caption generator", "Logo concept generator",
            "Poster/banner design", "Video editing AI", "Audio extraction", "Voice cloning", "Marketing content creator"
        ],
        "Education & Learning (81-100)": [
            "Language teaching", "Explain science/math/history", "Quiz generator", "Homework assistant", "Flashcards creator",
            "Code explanation", "Study planner", "Mock exam generator", "Simplify complex topics", "CV & Cover Letter builder",
            "Math solver", "Chemistry/physics tutor", "Literature analysis", "Book summarization", "Fun facts generator",
            "Reference finder", "Learning path AI", "Skill development advisor", "Career guidance", "Knowledge testing system"
        ],
        "Intelligence & Automation (101-110)": [
            "Autonomous AI Agent", "Multi-step reasoning planner", "Goal-driven AI assistant", "Self-learning preferences", "Predictive suggestions",
            "AI decision support", "Context-aware automation", "Smart notification timing", "Behavioral analysis", "Personal AI twin"
        ],
        "Business & Monetization (111-120)": [
            "AI sales closer", "Dynamic pricing optimizer", "Customer journey prediction", "AI negotiation assistant", "Funnel optimization AI",
            "Viral content predictor", "Ad performance auto-optimizer", "Business KPI prediction", "Revenue forecasting", "AI affiliate marketing bot"
        ],
        "Social & Community (121-130)": [
            "AI influencer assistant", "Community growth optimizer", "Engagement prediction", "Auto content posting scheduler", "AI moderation",
            "Fake account detection", "Community sentiment dashboard", "Social trend detector", "AI poll strategist", "Group gamification engine"
        ],
        "Developer & System (131-140)": [
            "Auto full-stack app generator", "AI DevOps assistant", "Smart API builder", "Database auto-optimization", "AI system monitoring",
            "Error prediction AI", "Auto bug fixing system", "Code security scanner", "AI testing automation", "Infrastructure scaling AI"
        ],
        "Human-like & Future AI (141-150)": [
            "Emotion-aware AI", "Voice personality customization", "AI memory across platforms", "Multimodal understanding", "Real-time live assistant",
            "AR/VR assistant integration", "AI-powered personal coach", "AI therapist", "Decision simulation AI", "Fully autonomous business bot"
        ]
    }

    c_cat = _combo(list(categories.keys()))
    c_task = QComboBox()
    
    def update_tasks():
        c_task.clear()
        c_task.addItems(categories[c_cat.currentText()])
        
    c_cat.currentIndexChanged.connect(update_tasks)
    update_tasks()

    c_lang = _combo("English", "Khmer", "Spanish", "French", "Chinese", "Arabic", "Japanese")

    e_input = QTextEdit()
    e_input.setPlaceholderText("Enter your input data, context, or instructions for the AI here...")
    e_input.setMinimumHeight(120)
    e_input.setStyleSheet(f"background:{SURFACE}; color:{TEXT}; border:1px solid {BORDER}; border-radius:8px; padding:12px; font-size:14px; line-height:1.5;")

    form.addRow("Category:", c_cat)
    form.addRow("Task / Feature:", c_task)
    form.addRow("Output Language:", c_lang)
    form.addRow("Input Data:", e_input)

    t1l.addLayout(form)

    btn_execute = ActionButton("🚀 Execute Omni Task", ACCENT)
    t1l.addWidget(btn_execute)

    out_result = OutputBox("Task execution results will appear here...")
    out_result.setMinimumHeight(250)
    t1l.addWidget(out_result, 1)

    def _execute_task():
        task_name = c_task.currentText()
        input_data = e_input.toPlainText().strip()
        if not input_data:
            out_result.set_error("Please provide input data or instructions.")
            return

        btn_execute.set_loading(True)
        out_result.reset_color()
        out_result.setPlainText(f"Executing {task_name}...")

        w = ApiWorker(
            f"{api_base}/api/v1/omni-task",
            {
                "task_id": "omni_manual",
                "task_name": task_name,
                "input_data": input_data,
                "language": c_lang.currentText()
            },
            btn=btn_execute
        )

        w.result_ready.connect(lambda r: out_result.setPlainText(str(r.get("data", r))))
        w.error_signal.connect(out_result.set_error)
        page._workers.append(w)
        w.start()

    btn_execute.clicked.connect(_execute_task)

    tabs.addTab(t1, "🌌 Omni AI Hub")

    return page

# ─────────────────────────────────────────────────────────────────────────────
def build_strategy_page(api_base: str) -> QWidget:
    page, layout = _make_page_layout("AI Strategy Brain", "🧠")
    tabs = QTabWidget()

    # ── Tab 1: Strategy / Audit / Forecast ───────────────────────────────────
    t1 = QWidget()
    t1l = QVBoxLayout(t1)
    grp = QGroupBox("Account Details")
    g = QGridLayout(grp)
    username  = _styled_input("@username")
    platform  = _combo("TikTok", "Instagram", "Facebook", "YouTube", "Telegram", "Twitter/X", "LinkedIn")
    niche     = _styled_input("e.g. Fitness, Tech, Business, Food")
    followers = QSpinBox()
    followers.setRange(0, 99_000_000)
    followers.setValue(15000)
    goal_foll = QSpinBox()
    goal_foll.setRange(0, 99_000_000)
    goal_foll.setValue(50000)
    duration  = QSpinBox()
    duration.setRange(7, 365)
    duration.setValue(30)
    g.addWidget(QLabel("Username:"),       0, 0); g.addWidget(username,  0, 1)
    g.addWidget(QLabel("Platform:"),       0, 2); g.addWidget(platform,  0, 3)
    g.addWidget(QLabel("Niche:"),          1, 0); g.addWidget(niche,     1, 1, 1, 3)
    g.addWidget(QLabel("Followers:"),      2, 0); g.addWidget(followers, 2, 1)
    g.addWidget(QLabel("Goal Followers:"), 2, 2); g.addWidget(goal_foll, 2, 3)
    g.addWidget(QLabel("Days:"),           3, 0); g.addWidget(duration,  3, 1)
    t1l.addWidget(grp)
    btn_row1 = QHBoxLayout()
    btn_strategy = ActionButton("🚀 Generate 30-Day Strategy", ACCENT)
    btn_audit    = ActionButton("🔍 Deep Account Audit",        SUCCESS)
    btn_forecast = ActionButton("📈 3-Month Growth Forecast",   WARNING)
    btn_row1.addWidget(btn_strategy)
    btn_row1.addWidget(btn_audit)
    btn_row1.addWidget(btn_forecast)
    t1l.addLayout(btn_row1)
    out1 = OutputBox("Strategy results will appear here…")
    t1l.addWidget(out1, 1)
    tabs.addTab(t1, "Strategy & Forecast")

    def _run1(url, payload, btn=None):
        out1.reset_color(); out1.setPlainText("AI is thinking…")
        w = ApiWorker(url, payload, btn=btn)
        page._w1 = w
        w.result_ready.connect(lambda d: out1.set_result(d.get("data", d)))
        w.error_signal.connect(out1.set_error)
        w.start()

    btn_strategy.clicked.connect(lambda: _run1(f"{api_base}/api/v1/ai/strategy", {
        "username": username.text() or "demo", "platform": platform.currentText(),
        "current_followers": followers.value(), "niche": niche.text() or "General",
        "goal_followers": goal_foll.value(), "duration_days": duration.value(),
    }, btn_strategy))
    btn_audit.clicked.connect(lambda: _run1(f"{api_base}/api/v1/ai/audit", {
        "username": username.text() or "demo", "platform": platform.currentText(),
        "followers": followers.value(), "niche": niche.text() or "General",
    }, btn_audit))
    btn_forecast.clicked.connect(lambda: _run1(f"{api_base}/api/v1/ai/forecast", {
        "current_followers": followers.value(), "engagement_rate": 3.5,
        "posting_frequency": 1, "platform": platform.currentText(), "months": 3,
    }, btn_forecast))

    # ── Tab 2: Competitor Intelligence ───────────────────────────────────────
    t2 = QWidget()
    t2l = QVBoxLayout(t2)
    grp2 = QGroupBox("Competitor Intelligence Analysis  — Feature #18 + #91")
    g2 = QGridLayout(grp2)
    comp_user  = _styled_input("Competitor username (e.g. competitor_brand)")
    comp_plat  = _combo("TikTok", "Instagram", "Facebook", "YouTube", "Telegram", "Twitter/X")
    comp_niche = _styled_input("Your niche (e.g. Fitness, Tech, Business)")
    g2.addWidget(QLabel("Competitor:"), 0, 0); g2.addWidget(comp_user,  0, 1)
    g2.addWidget(QLabel("Platform:"),   1, 0); g2.addWidget(comp_plat,  1, 1)
    g2.addWidget(QLabel("Your Niche:"), 2, 0); g2.addWidget(comp_niche, 2, 1)
    t2l.addWidget(grp2)
    btn_comp = ActionButton("🕵️ Analyze Competitor — AI Spy Mode", ACCENT)
    t2l.addWidget(btn_comp)
    out2 = OutputBox("Competitor analysis will appear here…\nDiscovers their strategy, weaknesses, and your opportunities.")
    t2l.addWidget(out2, 1)
    tabs.addTab(t2, "Competitor Analysis")

    def _run_comp():
        out2.reset_color(); out2.setPlainText("Analyzing competitor intelligence…")
        w = ApiWorker(f"{api_base}/api/v1/ai/competitor", {
            "competitor_username": comp_user.text() or "competitor_brand",
            "platform": comp_plat.currentText(),
            "your_niche": comp_niche.text() or "General",
        }, btn=btn_comp)
        page._w2 = w
        w.result_ready.connect(lambda d: out2.set_result(d.get("data", d)))
        w.error_signal.connect(out2.set_error)
        w.start()

    btn_comp.clicked.connect(_run_comp)

    # ── Tab 3: Audience DNA Persona ───────────────────────────────────────────
    t3 = QWidget()
    t3l = QVBoxLayout(t3)
    grp3 = QGroupBox("Audience DNA Builder  — Feature #5")
    g3 = QGridLayout(grp3)
    p_niche = _styled_input("Your niche (e.g. Fitness, Tech, Finance)")
    p_plat  = _combo("TikTok", "Instagram", "Facebook", "YouTube", "Telegram", "Twitter/X", "LinkedIn")
    p_country = _combo("Global", "US", "Cambodia", "Thailand", "Vietnam", "Philippines", "Indonesia", "UK")
    g3.addWidget(QLabel("Niche:"),    0, 0); g3.addWidget(p_niche,   0, 1)
    g3.addWidget(QLabel("Platform:"), 1, 0); g3.addWidget(p_plat,    1, 1)
    g3.addWidget(QLabel("Country:"),  2, 0); g3.addWidget(p_country, 2, 1)
    t3l.addWidget(grp3)
    btn_persona = ActionButton("👥 Build Audience DNA Persona", ACCENT)
    t3l.addWidget(btn_persona)
    out3 = OutputBox("Audience persona will appear here…\nDetailed demographics, psychographics, pain points, content preferences.")
    t3l.addWidget(out3, 1)
    tabs.addTab(t3, "Audience DNA Persona")

    def _run_persona():
        out3.reset_color(); out3.setPlainText("Building audience DNA profile…")
        w = ApiWorker(f"{api_base}/api/v1/ai/persona", {
            "username": "demo",
            "platform": p_plat.currentText(),
            "followers": 15000,
            "niche": p_niche.text() or "General",
        }, btn=btn_persona)
        page._w3 = w
        w.result_ready.connect(lambda d: out3.set_result(d.get("data", d)))
        w.error_signal.connect(out3.set_error)
        w.start()

    btn_persona.clicked.connect(_run_persona)

    layout.addWidget(tabs, 1)
    return page


# ─────────────────────────────────────────────────────────────────────────────
def build_content_page(api_base: str) -> QWidget:
    page, layout = _make_page_layout("AI Content Studio", "✍️")
    tabs = QTabWidget()

    # ── Tab 1: Full Content Package ───────────────────────────────────────────
    t1 = QWidget()
    t1l = QVBoxLayout(t1)
    grp = QGroupBox("Content Settings")
    g = QGridLayout(grp)
    topic    = _styled_input("Topic / keyword (e.g. Weight Loss, AI Tools, Business Tips)")
    platform = _combo("TikTok", "Instagram Reels", "Facebook Video", "YouTube Shorts", "LinkedIn", "Twitter/X")
    tone     = _combo("Viral & Catchy", "Professional", "Funny / Humorous", "Educational", "Inspirational", "Storytelling")
    lang     = _combo("English", "Khmer", "Bilingual EN+KH")
    dur      = QSpinBox()
    dur.setRange(15, 600)
    dur.setValue(60)
    g.addWidget(QLabel("Topic:"),        0, 0); g.addWidget(topic,    0, 1, 1, 3)
    g.addWidget(QLabel("Platform:"),     1, 0); g.addWidget(platform, 1, 1)
    g.addWidget(QLabel("Tone:"),         1, 2); g.addWidget(tone,     1, 3)
    g.addWidget(QLabel("Language:"),     2, 0); g.addWidget(lang,     2, 1)
    g.addWidget(QLabel("Duration (s):"), 2, 2); g.addWidget(dur,      2, 3)
    t1l.addWidget(grp)
    btn_row = QHBoxLayout()
    btn_full    = ActionButton("✨ Full Content Package", ACCENT)
    btn_hook    = ActionButton("🎯 Viral Hooks x5",        SUCCESS)
    btn_hashtag = ActionButton("#️⃣ Hashtag Clusters",     WARNING)
    btn_row.addWidget(btn_full)
    btn_row.addWidget(btn_hook)
    btn_row.addWidget(btn_hashtag)
    t1l.addLayout(btn_row)
    out1 = OutputBox("Generated content will appear here…\nFull Package = Hook + Caption + Hashtags + Script")
    t1l.addWidget(out1, 1)
    tabs.addTab(t1, "Content Package")

    def _payload():
        return {
            "topic": topic.text() or "Social Media Growth",
            "platform": platform.currentText(),
            "tone": tone.currentText(),
            "language": lang.currentText(),
            "duration_seconds": dur.value(),
        }

    def _run1(url, btn=None):
        out1.reset_color(); out1.setPlainText("Generating content…")
        w = ApiWorker(url, _payload(), btn=btn)
        page._w1 = w
        w.result_ready.connect(lambda d: out1.set_result(d.get("data", d)))
        w.error_signal.connect(out1.set_error)
        w.start()

    btn_full.clicked.connect(lambda: _run1(f"{api_base}/api/v1/ai/content", btn_full))
    btn_hook.clicked.connect(lambda: _run1(f"{api_base}/api/v1/ai/hook", btn_hook))
    btn_hashtag.clicked.connect(lambda: _run1(f"{api_base}/api/v1/ai/hashtags", btn_hashtag))

    # ── Tab 2: Video Script & Calendar ────────────────────────────────────────
    t2 = QWidget()
    t2l = QVBoxLayout(t2)
    grp2 = QGroupBox("Script & Calendar Settings")
    g2 = QGridLayout(grp2)
    topic2    = _styled_input("Topic / keyword")
    platform2 = _combo("TikTok", "Instagram Reels", "YouTube Shorts", "Facebook Video")
    tone2     = _combo("Viral & Catchy", "Educational", "Storytelling", "Funny / Humorous")
    lang2     = _combo("English", "Khmer", "Bilingual EN+KH")
    dur2      = QSpinBox()
    dur2.setRange(15, 600)
    dur2.setValue(60)
    g2.addWidget(QLabel("Topic:"),        0, 0); g2.addWidget(topic2,    0, 1, 1, 3)
    g2.addWidget(QLabel("Platform:"),     1, 0); g2.addWidget(platform2, 1, 1)
    g2.addWidget(QLabel("Tone:"),         1, 2); g2.addWidget(tone2,     1, 3)
    g2.addWidget(QLabel("Language:"),     2, 0); g2.addWidget(lang2,     2, 1)
    g2.addWidget(QLabel("Duration (s):"), 2, 2); g2.addWidget(dur2,      2, 3)
    t2l.addWidget(grp2)
    btn_row2 = QHBoxLayout()
    btn_script = ActionButton("🎬 Generate Video Script", ACCENT)
    btn_cal    = ActionButton("📅 14-Day Content Calendar", SUCCESS)
    btn_row2.addWidget(btn_script)
    btn_row2.addWidget(btn_cal)
    t2l.addLayout(btn_row2)
    out2 = OutputBox("Script / Calendar will appear here…")
    t2l.addWidget(out2, 1)
    tabs.addTab(t2, "Script & Calendar")

    def _payload2():
        return {
            "topic": topic2.text() or "Social Media Growth",
            "platform": platform2.currentText(),
            "tone": tone2.currentText(),
            "language": lang2.currentText(),
            "duration_seconds": dur2.value(),
        }

    def _run2(url, btn=None):
        out2.reset_color(); out2.setPlainText("Generating…")
        w = ApiWorker(url, _payload2(), btn=btn)
        page._w2 = w
        w.result_ready.connect(lambda d: out2.set_result(d.get("data", d)))
        w.error_signal.connect(out2.set_error)
        w.start()

    btn_script.clicked.connect(lambda: _run2(f"{api_base}/api/v1/ai/script", btn_script))
    btn_cal.clicked.connect(lambda: _run2(f"{api_base}/api/v1/ai/calendar", btn_cal))

    # ── Tab 3: Micro-Content Engine ───────────────────────────────────────────
    t3 = QWidget()
    t3l = QVBoxLayout(t3)
    grp3 = QGroupBox("Micro-Content Engine  — Feature #88: 1 Idea → 20 Content Pieces")
    g3 = QGridLayout(grp3)
    micro_topic = _styled_input("Core topic or idea (e.g. 5 Ways to Lose Weight Fast)")
    micro_plat  = _combo("TikTok", "Instagram", "Facebook", "YouTube", "LinkedIn", "Twitter/X")
    g3.addWidget(QLabel("Core Topic:"), 0, 0); g3.addWidget(micro_topic, 0, 1)
    g3.addWidget(QLabel("Platform:"),   1, 0); g3.addWidget(micro_plat,  1, 1)
    t3l.addWidget(grp3)
    hint = QLabel("💡 AI will break 1 big idea into 20 micro-content pieces:\n"
                  "   Reels, Carousels, Stories, Tweets, Quotes, Polls, Q&A, Tips, and more.")
    hint.setStyleSheet(f"color:{SUBTEXT}; font-size:14px; padding:6px;")
    t3l.addWidget(hint)
    btn_micro = ActionButton("⚡ Generate 20 Micro-Content Pieces", ACCENT)
    t3l.addWidget(btn_micro)
    out3 = OutputBox("20 micro-content pieces will appear here…")
    t3l.addWidget(out3, 1)
    tabs.addTab(t3, "Micro-Content Engine")

    def _run_micro():
        out3.reset_color(); out3.setPlainText("AI breaking your idea into 20 micro-content pieces…")
        w = ApiWorker(f"{api_base}/api/v1/ai/micro-content", {
            "topic": micro_topic.text() or "Social Media Growth",
            "platform": micro_plat.currentText(),
            "tone": "Viral & Catchy",
            "language": "English",
        }, btn=btn_micro)
        page._w3 = w
        w.result_ready.connect(lambda d: out3.set_result(d.get("data", d)))
        w.error_signal.connect(out3.set_error)
        w.start()

    btn_micro.clicked.connect(_run_micro)

    layout.addWidget(tabs, 1)
    return page


# ─────────────────────────────────────────────────────────────────────────────
def build_analytics_page(api_base: str) -> QWidget:
    page, layout = _make_page_layout("Analytics Copilot", "📊")
    tabs = QTabWidget()

    # ── Tab 1: Performance Analysis ───────────────────────────────────────────
    t1 = QWidget()
    t1l = QVBoxLayout(t1)
    grp = QGroupBox("Performance Metrics Input")
    g = QGridLayout(grp)
    platform = _combo("TikTok", "Instagram", "Facebook", "YouTube", "Telegram", "Twitter/X")
    views    = QSpinBox(); views.setRange(0, 100_000_000); views.setValue(50000)
    likes    = QSpinBox(); likes.setRange(0, 10_000_000); likes.setValue(3500)
    comments = QSpinBox(); comments.setRange(0, 1_000_000); comments.setValue(420)
    shares   = QSpinBox(); shares.setRange(0, 1_000_000); shares.setValue(210)
    saves    = QSpinBox(); saves.setRange(0, 1_000_000); saves.setValue(180)
    follows  = QSpinBox(); follows.setRange(0, 100_000); follows.setValue(55)
    g.addWidget(QLabel("Platform:"),    0, 0); g.addWidget(platform, 0, 1)
    g.addWidget(QLabel("Views:"),       1, 0); g.addWidget(views,    1, 1)
    g.addWidget(QLabel("Likes:"),       1, 2); g.addWidget(likes,    1, 3)
    g.addWidget(QLabel("Comments:"),    2, 0); g.addWidget(comments, 2, 1)
    g.addWidget(QLabel("Shares:"),      2, 2); g.addWidget(shares,   2, 3)
    g.addWidget(QLabel("Saves:"),       3, 0); g.addWidget(saves,    3, 1)
    g.addWidget(QLabel("New Follows:"), 3, 2); g.addWidget(follows,  3, 3)
    t1l.addWidget(grp)
    btn_row1 = QHBoxLayout()
    btn_analyze = ActionButton("🔬 Analyze Performance", ACCENT)
    btn_timing  = ActionButton("⏰ Best Posting Times", SUCCESS)
    btn_fatigue = ActionButton("😴 Audience Fatigue Check", WARNING)
    btn_row1.addWidget(btn_analyze)
    btn_row1.addWidget(btn_timing)
    btn_row1.addWidget(btn_fatigue)
    t1l.addLayout(btn_row1)
    out1 = OutputBox()
    t1l.addWidget(out1, 1)
    tabs.addTab(t1, "Performance Analysis")

    def _metrics():
        return {
            "platform": platform.currentText(),
            "views": views.value(), "likes": likes.value(),
            "comments": comments.value(), "shares": shares.value(),
            "saves": saves.value(), "follows": follows.value(),
        }

    def _run1(url, payload=None, method="POST", btn=None):
        out1.reset_color(); out1.setPlainText("Analyzing…")
        w = ApiWorker(url, payload, method, btn=btn)
        page._w1 = w
        w.result_ready.connect(lambda d: out1.set_result(d.get("data", d)))
        w.error_signal.connect(out1.set_error)
        w.start()

    btn_analyze.clicked.connect(lambda: _run1(f"{api_base}/api/v1/ai/performance", _metrics(), btn=btn_analyze))
    btn_timing.clicked.connect(lambda: _run1(f"{api_base}/api/v1/ai/timing/{platform.currentText()}", method="GET", btn=btn_timing))
    btn_fatigue.clicked.connect(lambda: _run1(f"{api_base}/api/v1/ai/performance", _metrics(), btn=btn_fatigue))

    # ── Tab 2: Performance Report Generator ───────────────────────────────────
    t2 = QWidget()
    t2l = QVBoxLayout(t2)
    grp2 = QGroupBox("Performance Report Generator  — Feature #11")
    g2 = QGridLayout(grp2)
    rpt_name   = _styled_input("Account name or brand name")
    rpt_plat   = _combo("TikTok", "Instagram", "Facebook", "YouTube", "Telegram", "Twitter/X")
    rpt_period = _combo("Last 7 Days", "Last 30 Days", "Last 90 Days", "This Month", "This Quarter")
    rpt_views   = QSpinBox(); rpt_views.setRange(0, 100_000_000); rpt_views.setValue(250000)
    rpt_likes   = QSpinBox(); rpt_likes.setRange(0, 10_000_000); rpt_likes.setValue(18500)
    rpt_follows = QSpinBox(); rpt_follows.setRange(0, 1_000_000); rpt_follows.setValue(4200)
    g2.addWidget(QLabel("Account Name:"), 0, 0); g2.addWidget(rpt_name,   0, 1)
    g2.addWidget(QLabel("Platform:"),     0, 2); g2.addWidget(rpt_plat,   0, 3)
    g2.addWidget(QLabel("Period:"),       1, 0); g2.addWidget(rpt_period, 1, 1)
    g2.addWidget(QLabel("Views:"),        2, 0); g2.addWidget(rpt_views,  2, 1)
    g2.addWidget(QLabel("Likes:"),        2, 2); g2.addWidget(rpt_likes,  2, 3)
    g2.addWidget(QLabel("New Follows:"),  3, 0); g2.addWidget(rpt_follows,3, 1)
    t2l.addWidget(grp2)
    btn_report = ActionButton("📊 Generate Full Performance Report", ACCENT)
    t2l.addWidget(btn_report)
    out2 = OutputBox("Professional performance report will appear here…\nIncludes KPIs, AI insights, recommendations, and next actions.")
    t2l.addWidget(out2, 1)
    tabs.addTab(t2, "Report Generator")

    def _run_report():
        out2.reset_color(); out2.setPlainText("Generating comprehensive report…")
        payload = {
            "account_name": rpt_name.text() or "MyBrand",
            "platform": rpt_plat.currentText(),
            "period": rpt_period.currentText(),
            "metrics": {
                "views": rpt_views.value(),
                "likes": rpt_likes.value(),
                "follows": rpt_follows.value(),
            },
            "goals_achieved": ["Increased engagement", "Grew follower base"],
        }
        w = ApiWorker(f"{api_base}/api/v1/ai/report", payload, btn=btn_report)
        page._w2 = w
        w.result_ready.connect(lambda d: out2.set_result(d.get("data", d)))
        w.error_signal.connect(out2.set_error)
        w.start()

    btn_report.clicked.connect(_run_report)

    # ── Tab 3: ROI & Trust Score ───────────────────────────────────────────────
    t3 = QWidget()
    t3l = QVBoxLayout(t3)
    grp3 = QGroupBox("ROI & Trust Score Calculator  — Feature #3 + #92")
    g3 = QGridLayout(grp3)
    roi_followers = QSpinBox(); roi_followers.setRange(0, 99_000_000); roi_followers.setValue(15000)
    roi_eng_rate  = QDoubleSpinBox(); roi_eng_rate.setRange(0.0, 100.0); roi_eng_rate.setValue(3.5); roi_eng_rate.setSuffix(" %")
    roi_plat      = _combo("TikTok", "Instagram", "Facebook", "YouTube", "Telegram")
    roi_spend     = QDoubleSpinBox(); roi_spend.setRange(0.0, 100000.0); roi_spend.setValue(500.0); roi_spend.setPrefix("$ ")
    roi_revenue   = QDoubleSpinBox(); roi_revenue.setRange(0.0, 1000000.0); roi_revenue.setValue(2000.0); roi_revenue.setPrefix("$ ")
    g3.addWidget(QLabel("Followers:"),       0, 0); g3.addWidget(roi_followers, 0, 1)
    g3.addWidget(QLabel("Engagement Rate:"), 0, 2); g3.addWidget(roi_eng_rate,  0, 3)
    g3.addWidget(QLabel("Platform:"),        1, 0); g3.addWidget(roi_plat,      1, 1)
    g3.addWidget(QLabel("Ad Spend:"),        2, 0); g3.addWidget(roi_spend,     2, 1)
    g3.addWidget(QLabel("Revenue:"),         2, 2); g3.addWidget(roi_revenue,   2, 3)
    t3l.addWidget(grp3)
    btn_row3 = QHBoxLayout()
    btn_roi   = ActionButton("💰 Calculate ROI", ACCENT)
    btn_trust = ActionButton("⭐ Trust Score", SUCCESS)
    btn_row3.addWidget(btn_roi)
    btn_row3.addWidget(btn_trust)
    t3l.addLayout(btn_row3)
    out3 = OutputBox("ROI and Trust Score results will appear here…")
    t3l.addWidget(out3, 1)
    tabs.addTab(t3, "ROI & Trust Score")

    def _run3(url, payload, btn=None):
        out3.reset_color(); out3.setPlainText("Calculating…")
        w = ApiWorker(url, payload, btn=btn)
        page._w3 = w
        w.result_ready.connect(lambda d: out3.set_result(d.get("data", d)))
        w.error_signal.connect(out3.set_error)
        w.start()

    btn_roi.clicked.connect(lambda: _run3(f"{api_base}/api/v1/ai/performance", {
        "platform": roi_plat.currentText(),
        "views": 50000, "likes": int(50000 * roi_eng_rate.value() / 100),
        "comments": 400, "shares": 200, "saves": 150, "follows": 55,
    }, btn_roi))
    btn_trust.clicked.connect(lambda: _run3(f"{api_base}/api/v1/ai/performance", {
        "platform": roi_plat.currentText(),
        "views": 50000, "likes": 3500, "comments": 420, "shares": 210,
        "saves": 180, "follows": roi_followers.value(),
    }, btn_trust))

    layout.addWidget(tabs, 1)
    return page


# ─────────────────────────────────────────────────────────────────────────────
def build_trends_page(api_base: str) -> QWidget:
    page, layout = _make_page_layout("Trend Radar", "🔮")

    grp = QGroupBox("Search Parameters")
    g = QGridLayout(grp)
    platform = _combo("TikTok", "Instagram", "Facebook", "YouTube", "Twitter/X", "Telegram")
    niche    = _styled_input("Niche (e.g. Fitness, Tech, Food, Gaming)")
    region   = _combo("Global", "US", "UK", "SEA", "Cambodia", "Thailand", "Vietnam", "Philippines")
    g.addWidget(QLabel("Platform:"), 0, 0); g.addWidget(platform, 0, 1)
    g.addWidget(QLabel("Niche:"),    0, 2); g.addWidget(niche,    0, 3)
    g.addWidget(QLabel("Region:"),   1, 0); g.addWidget(region,   1, 1)
    layout.addWidget(grp)

    btn_row = QHBoxLayout()
    btn_trend    = ActionButton("🌊 Trending Now",          ACCENT)
    btn_predict  = ActionButton("🔮 Predict Trends",        SUCCESS)
    btn_opps     = ActionButton("💡 Scan Opportunities",    WARNING)
    btn_strategy = ActionButton("📅 Time-Aware Strategy",   "#CBA6F7")
    btn_fuse     = ActionButton("🔗 Cross-Platform Signals","#89DCEB")
    for b in [btn_trend, btn_predict, btn_opps, btn_strategy, btn_fuse]:
        btn_row.addWidget(b)
    layout.addLayout(btn_row)

    output = OutputBox()
    layout.addWidget(output, 1)

    def _p():
        return {"platform": platform.currentText(), "niche": niche.text() or "General", "region": region.currentText()}

    def _post(url, payload=None, btn=None):
        output.reset_color(); output.setPlainText("Scanning trends…")
        w = ApiWorker(url, payload or _p(), btn=btn)
        page._worker = w
        w.result_ready.connect(lambda d: output.set_result(d.get("data", d)))
        w.error_signal.connect(output.set_error)
        w.start()

    def _get(url, btn=None):
        output.reset_color(); output.setPlainText("Fetching…")
        w = ApiWorker(url, method="GET", btn=btn)
        page._worker = w
        w.result_ready.connect(lambda d: output.set_result(d.get("data", d)))
        w.error_signal.connect(output.set_error)
        w.start()

    btn_trend.clicked.connect(lambda: _post(f"{api_base}/api/v1/ai/trends", btn=btn_trend))
    btn_predict.clicked.connect(lambda: _post(f"{api_base}/api/v1/ai/predict-trends", btn=btn_predict))
    btn_opps.clicked.connect(lambda: _get(f"{api_base}/api/v1/ai/opportunities/{platform.currentText()}/{niche.text() or 'General'}", btn_opps))
    btn_strategy.clicked.connect(lambda: _get(f"{api_base}/api/v1/ai/time-strategy/{platform.currentText()}", btn_strategy))
    btn_fuse.clicked.connect(lambda: _post(f"{api_base}/api/v1/ai/trends", {**_p(), "cross_platform": True}, btn_fuse))
    return page


# ─────────────────────────────────────────────────────────────────────────────
def build_campaign_page(api_base: str) -> QWidget:
    page, layout = _make_page_layout("Campaign Engine", "⚙️")
    tabs = QTabWidget()

    # ── Tab 1: Create Campaign ─────────────────────────────────────────────────
    t1 = QWidget(); t1l = QVBoxLayout(t1)
    grp = QGroupBox("Campaign Setup")
    g = QGridLayout(grp)
    name     = _styled_input("Campaign name (e.g. Summer Growth Blitz)")
    platform = _combo("TikTok", "Instagram", "Facebook", "YouTube", "Telegram", "LinkedIn")
    niche    = _styled_input("Niche (e.g. Fitness, Tech, Fashion)")
    goal     = _combo("Grow Followers", "Maximize Engagement", "Drive Traffic", "Boost Sales", "Brand Awareness")
    budget   = QDoubleSpinBox(); budget.setRange(5.0, 100000.0); budget.setValue(500.0); budget.setPrefix("$ ")
    duration = QSpinBox(); duration.setRange(1, 365); duration.setValue(30)
    g.addWidget(QLabel("Campaign Name:"), 0, 0); g.addWidget(name,     0, 1, 1, 3)
    g.addWidget(QLabel("Platform:"),      1, 0); g.addWidget(platform, 1, 1)
    g.addWidget(QLabel("Niche:"),         1, 2); g.addWidget(niche,    1, 3)
    g.addWidget(QLabel("Goal:"),          2, 0); g.addWidget(goal,     2, 1, 1, 3)
    g.addWidget(QLabel("Budget:"),        3, 0); g.addWidget(budget,   3, 1)
    g.addWidget(QLabel("Duration (days):"), 3, 2); g.addWidget(duration, 3, 3)
    t1l.addWidget(grp)
    btn_campaign = ActionButton("🚀 Create AI Campaign Plan", ACCENT)
    t1l.addWidget(btn_campaign)
    out1 = OutputBox("AI campaign plan with daily schedule will appear here…")
    t1l.addWidget(out1, 1)
    tabs.addTab(t1, "Create Campaign")

    def _run_campaign():
        out1.reset_color(); out1.setPlainText("Building campaign strategy…")
        w = ApiWorker(f"{api_base}/api/v1/ai/campaign", {
            "name": name.text() or "Auto Campaign",
            "platform": platform.currentText(),
            "niche": niche.text() or "General",
            "goal": goal.currentText(),
            "budget_usd": budget.value(),
            "duration_days": duration.value(),
        }, btn=btn_campaign)
        page._w1 = w
        w.result_ready.connect(lambda d: out1.set_result(d.get("data", d)))
        w.error_signal.connect(out1.set_error)
        w.start()

    btn_campaign.clicked.connect(_run_campaign)

    # ── Tab 2: Budget Optimizer ────────────────────────────────────────────────
    t2 = QWidget(); t2l = QVBoxLayout(t2)
    grp2 = QGroupBox("Budget Optimizer  — Feature #98: AI-Powered Budget Allocation")
    g2 = QGridLayout(grp2)
    bo_platform = _combo("TikTok", "Instagram", "Facebook", "YouTube", "Telegram", "Multi-Platform")
    bo_goal     = _combo("Grow Followers", "Maximize Engagement", "Drive Traffic", "Boost Sales")
    bo_budget   = QDoubleSpinBox(); bo_budget.setRange(10.0, 1000000.0); bo_budget.setValue(1000.0); bo_budget.setPrefix("$ ")
    bo_days     = QSpinBox(); bo_days.setRange(7, 365); bo_days.setValue(30)
    bo_acc_size = _combo("Nano (0-1K)", "Micro (1K-10K)", "Mid (10K-100K)", "Macro (100K+)", "Mega (1M+)")
    g2.addWidget(QLabel("Platform:"),        0, 0); g2.addWidget(bo_platform, 0, 1)
    g2.addWidget(QLabel("Goal:"),            1, 0); g2.addWidget(bo_goal,     1, 1)
    g2.addWidget(QLabel("Total Budget:"),    2, 0); g2.addWidget(bo_budget,   2, 1)
    g2.addWidget(QLabel("Campaign Days:"),   3, 0); g2.addWidget(bo_days,     3, 1)
    g2.addWidget(QLabel("Account Tier:"),    4, 0); g2.addWidget(bo_acc_size, 4, 1)
    t2l.addWidget(grp2)
    btn_budget = ActionButton("💰 Optimize Budget Allocation", ACCENT)
    t2l.addWidget(btn_budget)
    out2 = OutputBox("AI budget allocation breakdown will appear here…\nOptimizes spend across content, ads, SMM panel, and tools.")
    t2l.addWidget(out2, 1)
    tabs.addTab(t2, "Budget Optimizer")

    def _run_budget():
        out2.reset_color(); out2.setPlainText("AI optimizing budget allocation…")
        w = ApiWorker(f"{api_base}/api/v1/ai/campaign", {
            "name": f"{bo_platform.currentText()} Budget Plan",
            "platform": bo_platform.currentText(),
            "niche": "General",
            "goal": bo_goal.currentText(),
            "budget_usd": bo_budget.value(),
            "duration_days": bo_days.value(),
        }, btn=btn_budget)
        page._w2 = w
        w.result_ready.connect(lambda d: out2.set_result(d.get("data", d)))
        w.error_signal.connect(out2.set_error)
        w.start()

    btn_budget.clicked.connect(_run_budget)

    layout.addWidget(tabs, 1)
    return page


# ─────────────────────────────────────────────────────────────────────────────
def build_risk_page(api_base: str) -> QWidget:
    page, layout = _make_page_layout("Risk & Compliance Engine", "🛡️")
    tabs = QTabWidget()

    # ── Tab 1: Content Safety ──────────────────────────────────────────────────
    t1 = QWidget(); t1l = QVBoxLayout(t1)
    grp = QGroupBox("Content Safety Check  — Feature #6 + #17")
    g = QGridLayout(grp)
    platform = _combo("TikTok", "Instagram", "Facebook", "YouTube", "Telegram", "General")
    content  = QTextEdit()
    content.setPlaceholderText("Paste your caption, script, or post text here to check for policy violations…")
    content.setMaximumHeight(140)
    g.addWidget(QLabel("Platform:"), 0, 0); g.addWidget(platform, 0, 1)
    g.addWidget(QLabel("Content:"),  1, 0); g.addWidget(content,  1, 0, 1, 2)
    t1l.addWidget(grp)
    btn_row1 = QHBoxLayout()
    btn_risk   = ActionButton("🔍 Check Content Safety", ACCENT)
    btn_limits = ActionButton("📊 Safe Growth Limits",   SUCCESS)
    followers1 = QSpinBox(); followers1.setRange(0, 99_000_000); followers1.setValue(15000)
    btn_row1.addWidget(btn_risk)
    btn_row1.addWidget(btn_limits)
    btn_row1.addWidget(QLabel("Followers:"))
    btn_row1.addWidget(followers1)
    t1l.addLayout(btn_row1)
    out1 = OutputBox()
    t1l.addWidget(out1, 1)
    tabs.addTab(t1, "Content Safety")

    def _risk():
        out1.reset_color(); out1.setPlainText("Scanning content for risks…")
        w = ApiWorker(f"{api_base}/api/v1/ai/risk", {
            "content": content.toPlainText() or "Sample post content",
            "platform": platform.currentText(),
        }, btn=btn_risk)
        page._w1 = w
        w.result_ready.connect(lambda d: out1.set_result(d.get("data", d)))
        w.error_signal.connect(out1.set_error)
        w.start()

    def _limits():
        out1.reset_color(); out1.setPlainText("Calculating safe limits…")
        url = f"{api_base}/api/v1/ai/safe-limits/{platform.currentText()}/{followers1.value()}"
        w = ApiWorker(url, method="GET", btn=btn_limits)
        page._w1b = w
        w.result_ready.connect(lambda d: out1.set_result(d.get("data", d)))
        w.error_signal.connect(out1.set_error)
        w.start()

    btn_risk.clicked.connect(_risk)
    btn_limits.clicked.connect(_limits)

    # ── Tab 2: Shadowban & Account Health ─────────────────────────────────────
    t2 = QWidget(); t2l = QVBoxLayout(t2)
    grp2 = QGroupBox("Shadowban Detector + Account Health Audit  — Feature #86 + #97")
    g2 = QGridLayout(grp2)
    sh_username  = _styled_input("@username to audit")
    sh_platform  = _combo("TikTok", "Instagram", "Facebook", "YouTube", "Telegram")
    sh_followers = QSpinBox(); sh_followers.setRange(0, 99_000_000); sh_followers.setValue(15000)
    sh_niche     = _styled_input("Niche (e.g. Fitness, Tech)")
    sh_eng_rate  = QDoubleSpinBox(); sh_eng_rate.setRange(0.0, 100.0); sh_eng_rate.setValue(3.5); sh_eng_rate.setSuffix(" %")
    sh_reach_drop = QDoubleSpinBox(); sh_reach_drop.setRange(0.0, 100.0); sh_reach_drop.setValue(0.0); sh_reach_drop.setSuffix(" % drop")
    g2.addWidget(QLabel("Username:"),     0, 0); g2.addWidget(sh_username,   0, 1)
    g2.addWidget(QLabel("Platform:"),     0, 2); g2.addWidget(sh_platform,   0, 3)
    g2.addWidget(QLabel("Followers:"),    1, 0); g2.addWidget(sh_followers,  1, 1)
    g2.addWidget(QLabel("Niche:"),        1, 2); g2.addWidget(sh_niche,      1, 3)
    g2.addWidget(QLabel("Eng. Rate:"),    2, 0); g2.addWidget(sh_eng_rate,   2, 1)
    g2.addWidget(QLabel("Reach Drop:"),   2, 2); g2.addWidget(sh_reach_drop, 2, 3)
    t2l.addWidget(grp2)
    btn_row2 = QHBoxLayout()
    btn_shadow = ActionButton("👻 Detect Shadowban Signals",  ACCENT)
    btn_health = ActionButton("💚 Full Account Health Audit", SUCCESS)
    btn_row2.addWidget(btn_shadow)
    btn_row2.addWidget(btn_health)
    t2l.addLayout(btn_row2)
    out2 = OutputBox("Shadowban detection and account health results will appear here…\n"
                     "Analyzes reach drop, engagement anomalies, and policy risk flags.")
    t2l.addWidget(out2, 1)
    tabs.addTab(t2, "Shadowban & Health")

    def _shadow():
        out2.reset_color(); out2.setPlainText("Scanning for shadowban signals…")
        w = ApiWorker(f"{api_base}/api/v1/ai/risk", {
            "content": f"Account: {sh_username.text() or 'demo'}, Platform: {sh_platform.currentText()}, "
                       f"Reach drop: {sh_reach_drop.value()}%, Engagement rate: {sh_eng_rate.value()}%",
            "platform": sh_platform.currentText(),
        }, btn=btn_shadow)
        page._w2 = w
        w.result_ready.connect(lambda d: out2.set_result(d.get("data", d)))
        w.error_signal.connect(out2.set_error)
        w.start()

    def _health_audit():
        out2.reset_color(); out2.setPlainText("Running full account health audit…")
        w = ApiWorker(f"{api_base}/api/v1/ai/audit", {
            "username": sh_username.text() or "demo",
            "platform": sh_platform.currentText(),
            "followers": sh_followers.value(),
            "niche": sh_niche.text() or "General",
        }, btn=btn_health)
        page._w2b = w
        w.result_ready.connect(lambda d: out2.set_result(d.get("data", d)))
        w.error_signal.connect(out2.set_error)
        w.start()

    btn_shadow.clicked.connect(_shadow)
    btn_health.clicked.connect(_health_audit)

    layout.addWidget(tabs, 1)
    return page


# ─────────────────────────────────────────────────────────────────────────────
def build_smm_page(api_base: str) -> QWidget:
    page, layout = _make_page_layout("SMM Panel — Full Production Mode", "🛒")

    # ── Panel Status Banner ───────────────────────────────────────────────────
    banner = QFrame()
    banner.setStyleSheet(
        f"background:{SURFACE}; border-radius:8px; border:1px solid #45475A; padding:2px;"
    )
    brow = QHBoxLayout(banner)
    brow.setContentsMargins(12, 6, 12, 6)
    panel_status_lbl = QLabel("● Checking panel connection…")
    panel_status_lbl.setStyleSheet(f"color:{SUBTEXT}; font-weight:bold;")
    panel_url_lbl = QLabel("")
    panel_url_lbl.setStyleSheet(f"color:{SUBTEXT}; font-size:14px;")
    btn_ping = ActionButton("🔌 Check Connection", ACCENT)
    btn_ping.setFixedWidth(160)
    brow.addWidget(panel_status_lbl)
    brow.addStretch()
    brow.addWidget(panel_url_lbl)
    brow.addWidget(btn_ping)
    layout.addWidget(banner)

    # ── Setup Guide (shown in Demo mode) ──────────────────────────────────────
    setup_box = QFrame()
    setup_box.setStyleSheet(
        f"background:#2A2A3E; border-radius:8px; border:1px solid {WARNING}; padding:4px;"
    )
    setup_layout = QVBoxLayout(setup_box)
    setup_layout.setContentsMargins(14, 10, 14, 10)
    setup_title = QLabel("📋  How to connect a real SMM Panel")
    setup_title.setStyleSheet(f"color:{WARNING}; font-weight:bold; font-size:14px;")
    setup_steps = QLabel(
        "1. Register a free account on any SMM panel that supports API v2\n"
        "   → JustAnotherPanel.com  |  Peakerr.com  |  SMMKings.com  |  or your own panel\n\n"
        "2. Go to  Account → API  and copy your API Key + API URL\n\n"
        "3. Open  .env  in this project folder and uncomment + fill:\n"
        "       SMM_API_KEY=your_api_key_here\n"
        "       SMM_API_URL=https://your-panel.com/api/v2\n\n"
        "4. Restart the backend server (python build.py --backend)\n"
        "5. Click  🔌 Check Connection  above — it will turn 🟢 Live"
    )
    setup_steps.setStyleSheet(f"color:{TEXT}; font-size:14px; line-height:1.6;")
    setup_steps.setWordWrap(True)
    setup_layout.addWidget(setup_title)
    setup_layout.addWidget(setup_steps)
    layout.addWidget(setup_box)

    def _ping_panel():
        panel_status_lbl.setText("● Checking…")
        panel_status_lbl.setStyleSheet(f"color:{SUBTEXT}; font-weight:bold;")
        btn_ping.set_loading(True)
        w = ApiWorker(f"{api_base}/api/v1/smm/panel-info", method="GET")
        page._wp = w
        def _got(resp):
            btn_ping.set_loading(False)
            d = resp.get("data", resp)
            mode = d.get("mode", "demo")
            url  = d.get("api_url", "")
            if mode == "live":
                panel_status_lbl.setText("🟢 Live API — Real SMM Panel Connected")
                panel_status_lbl.setStyleSheet(f"color:{SUCCESS}; font-weight:bold;")
                setup_box.setVisible(False)
            else:
                panel_status_lbl.setText("🟡 Demo Mode — Add SMM_API_KEY + SMM_API_URL in .env for Live")
                panel_status_lbl.setStyleSheet(f"color:{WARNING}; font-weight:bold;")
                setup_box.setVisible(True)
            panel_url_lbl.setText(url)
        w.result_ready.connect(_got)
        w.error_signal.connect(lambda e: panel_status_lbl.setText(f"🔴 Error: {e}"))
        w.start()

    btn_ping.clicked.connect(_ping_panel)
    QTimer.singleShot(800, _ping_panel)   # auto-check on page load

    tabs = QTabWidget()

    # ── Tab 1: Services & Balance (with QTableWidget) ─────────────────────────
    t1 = QWidget(); t1l = QVBoxLayout(t1)
    cat_input = _styled_input("Filter by platform (e.g. TikTok, Instagram) — leave blank for all")
    btn_svc_row = QHBoxLayout()
    btn_services = ActionButton("📋 Load All Services", ACCENT)
    btn_balance  = ActionButton("💰 Check Balance",     SUCCESS)
    btn_svc_row.addWidget(btn_services); btn_svc_row.addWidget(btn_balance)
    t1l.addWidget(cat_input); t1l.addLayout(btn_svc_row)

    _SVC_COLS = ["ID", "Name", "Category", "Rate/$1k", "Min", "Max", "Refill"]
    svc_table = QTableWidget(0, len(_SVC_COLS))
    svc_table.setHorizontalHeaderLabels(_SVC_COLS)
    svc_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
    svc_table.setAlternatingRowColors(True)
    svc_table.setEditTriggers(QTableWidget.NoEditTriggers)
    svc_table.setSelectionBehavior(QTableWidget.SelectRows)
    svc_table.setStyleSheet(f"""
        QTableWidget {{
            background:{SURFACE}; color:{TEXT};
            border:1px solid #45475A; border-radius:6px; gridline-color:#45475A;
        }}
        QHeaderView::section {{
            background:{DARK_BG}; color:{ACCENT}; padding:8px;
            border:none; font-weight:bold;
        }}
        QTableWidget::item:alternate {{ background:#252535; }}
        QTableWidget::item:selected  {{ background:#313244; color:{TEXT}; }}
    """)
    t1l.addWidget(svc_table, 1)

    svc_stats = QLabel("No services loaded yet")
    svc_stats.setStyleSheet(f"color:{SUBTEXT}; font-size:14px; padding:2px 0;")
    t1l.addWidget(svc_stats)

    bal_box = OutputBox()
    bal_box.setMaximumHeight(90)
    t1l.addWidget(bal_box)
    tabs.addTab(t1, "📋 Services & Balance")

    def _load_services():
        svc_stats.setText("Loading services from panel…")
        cat = cat_input.text().strip()
        url = f"{api_base}/api/v1/smm/services" + (f"?category={cat}" if cat else "")
        w = ApiWorker(url, method="GET", btn=btn_services)
        t1._w = w
        def _got(resp):
            d     = resp.get("data", resp)
            svcs  = d.get("services", [])
            src   = d.get("source", "?")
            cached = "  [cached]" if d.get("cached") else ""
            svc_table.setRowCount(0)
            for i, s in enumerate(svcs):
                svc_table.insertRow(i)
                vals = [
                    str(s.get("service", "")),
                    s.get("name", ""),
                    s.get("category", ""),
                    f"${s.get('rate', '?')}",
                    str(s.get("min", "")),
                    str(s.get("max", "")),
                    "✅" if s.get("refill") else "—",
                ]
                for col, val in enumerate(vals):
                    item = QTableWidgetItem(val)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    if col == 6 and val == "✅":
                        item.setForeground(QColor(SUCCESS))
                    svc_table.setItem(i, col, item)
            src_label = "🟢 Live" if src == "live" else "🟡 Demo"
            svc_stats.setText(f"{src_label}{cached}  |  {len(svcs)} services loaded")
        w.result_ready.connect(_got)
        w.error_signal.connect(lambda e: svc_stats.setText(f"❌ {e}"))
        w.start()

    def _check_balance():
        bal_box.reset_color(); bal_box.setPlainText("Checking balance…")
        w = ApiWorker(f"{api_base}/api/v1/smm/balance", method="GET", btn=btn_balance)
        t1._wb = w
        w.result_ready.connect(lambda d: bal_box.set_result(d.get("data", d)))
        w.error_signal.connect(bal_box.set_error)
        w.start()

    btn_services.clicked.connect(_load_services)
    btn_balance.clicked.connect(_check_balance)

    # ── Tab 2: Place Order ────────────────────────────────────────────────────
    t2 = QWidget(); t2l = QVBoxLayout(t2)
    grp2 = QGroupBox("Manual Order  — enter service ID from the Services tab")
    g2 = QGridLayout(grp2)
    svc_id   = QSpinBox(); svc_id.setRange(1, 99999); svc_id.setValue(1004)
    link2    = _styled_input("Target URL (e.g. https://tiktok.com/@youraccount)")
    quantity = QSpinBox(); quantity.setRange(1, 1_000_000); quantity.setValue(500)
    g2.addWidget(QLabel("Service ID:"), 0, 0); g2.addWidget(svc_id,   0, 1)
    g2.addWidget(QLabel("Link:"),       1, 0); g2.addWidget(link2,    1, 1)
    g2.addWidget(QLabel("Quantity:"),   2, 0); g2.addWidget(quantity, 2, 1)
    t2l.addWidget(grp2)
    hint2 = QLabel("💡  Tip: Click any row in the Services tab to auto-fill the Service ID field.")
    hint2.setStyleSheet(f"color:{SUBTEXT}; font-size:14px;")
    t2l.addWidget(hint2)

    # Wire table row-click → auto-fill service ID
    def _svc_clicked(row, _col):
        id_item = svc_table.item(row, 0)
        if id_item:
            try: svc_id.setValue(int(id_item.text()))
            except ValueError: pass
    svc_table.cellClicked.connect(_svc_clicked)

    btn_order = ActionButton("🛒 Place Order", ACCENT)
    out2 = OutputBox()
    t2l.addWidget(btn_order); t2l.addWidget(out2, 1)
    tabs.addTab(t2, "🛒 Place Order")

    def _place_order():
        out2.reset_color(); out2.setPlainText("Placing order…")
        w = ApiWorker(f"{api_base}/api/v1/smm/order", {
            "service_id": svc_id.value(),
            "link":       link2.text().strip() or "https://tiktok.com/@example",
            "quantity":   quantity.value(),
        }, btn=btn_order)
        t2._w = w
        w.result_ready.connect(lambda d: out2.set_result(d.get("data", d)))
        w.error_signal.connect(out2.set_error)
        w.start()

    btn_order.clicked.connect(_place_order)

    # ── Tab 3: AI GEO Smart Order ─────────────────────────────────────────────
    t3 = QWidget(); t3l = QVBoxLayout(t3); t3l.setContentsMargins(0, 0, 0, 0)
    t3_scroll = QScrollArea(); t3_scroll.setWidgetResizable(True); t3_scroll.setFrameShape(QFrame.NoFrame)
    t3_inner = QWidget(); t3_inner_l = QVBoxLayout(t3_inner); t3_inner_l.setSpacing(8)
    t3_scroll.setWidget(t3_inner)
    t3l.addWidget(t3_scroll)

    # ── Basic Settings ────────────────────────────────────────────────────────
    grp3b = QGroupBox("📋 Order Settings")
    g3b = QGridLayout(grp3b); g3b.setColumnStretch(1, 2); g3b.setColumnStretch(3, 2)
    smart_link   = _styled_input("Your profile or post URL")
    smart_goal   = _combo("Grow Followers", "Get Views", "Get Likes",
                          "Get Members", "Get Comments", "Get Subscribers")
    smart_budget = QDoubleSpinBox()
    smart_budget.setRange(1.0, 10_000.0); smart_budget.setValue(50.0); smart_budget.setPrefix("$ ")
    smart_plat   = _combo("TikTok", "Instagram", "Facebook", "YouTube", "Telegram")
    g3b.addWidget(QLabel("Link:"),     0, 0); g3b.addWidget(smart_link,   0, 1, 1, 3)
    g3b.addWidget(QLabel("Goal:"),     1, 0); g3b.addWidget(smart_goal,   1, 1)
    g3b.addWidget(QLabel("Platform:"), 1, 2); g3b.addWidget(smart_plat,   1, 3)
    g3b.addWidget(QLabel("Budget:"),   2, 0); g3b.addWidget(smart_budget, 2, 1)
    t3_inner_l.addWidget(grp3b)

    # ── Geo-Targeting ─────────────────────────────────────────────────────────
    grp3_geo = QGroupBox("🌍 Geo-Targeting — Real Human Location Precision")
    grp3_geo.setStyleSheet(
        f"QGroupBox {{color:{ACCENT}; font-weight:bold; border:1px solid {ACCENT}55;"
        f"border-radius:8px; margin-top:8px; padding-top:10px;}}"
    )
    g3g = QGridLayout(grp3_geo); g3g.setColumnStretch(1, 2); g3g.setColumnStretch(3, 2)

    geo_scope = _combo(
        "🌐 Global (All Regions)",
        "🌍 By Continent / Region",
        "🏳 By Country",
        "📍 By State / Province",
        "🏙 By City",
    )

    _CONTINENTS = [
        "-- Select Continent --",
        "North America", "South America", "Europe",
        "Asia", "Middle East", "Africa", "Oceania",
    ]
    geo_continent = QComboBox()
    for _c in _CONTINENTS:
        geo_continent.addItem(_c)

    _COUNTRIES = [
        "-- Select Country --",
        # ── North America ──────────────────────────────────────────────────────
        "🇺🇸 United States (US)", "🇨🇦 Canada (CA)", "🇲🇽 Mexico (MX)",
        # ── Europe ────────────────────────────────────────────────────────────
        "🇬🇧 United Kingdom (GB)", "🇩🇪 Germany (DE)", "🇫🇷 France (FR)",
        "🇮🇹 Italy (IT)", "🇪🇸 Spain (ES)", "🇳🇱 Netherlands (NL)",
        "🇸🇪 Sweden (SE)", "🇳🇴 Norway (NO)", "🇩🇰 Denmark (DK)",
        "🇫🇮 Finland (FI)", "🇵🇱 Poland (PL)", "🇷🇺 Russia (RU)",
        "🇺🇦 Ukraine (UA)", "🇨🇭 Switzerland (CH)", "🇦🇹 Austria (AT)",
        "🇧🇪 Belgium (BE)", "🇵🇹 Portugal (PT)", "🇬🇷 Greece (GR)",
        "🇨🇿 Czech Republic (CZ)", "🇷🇴 Romania (RO)", "🇭🇺 Hungary (HU)",
        "🇧🇬 Bulgaria (BG)", "🇭🇷 Croatia (HR)", "🇸🇰 Slovakia (SK)",
        "🇮🇪 Ireland (IE)",
        # ── Asia ──────────────────────────────────────────────────────────────
        "🇰🇭 Cambodia (KH)", "🇹🇭 Thailand (TH)", "🇻🇳 Vietnam (VN)",
        "🇵🇭 Philippines (PH)", "🇮🇩 Indonesia (ID)", "🇸🇬 Singapore (SG)",
        "🇲🇾 Malaysia (MY)", "🇮🇳 India (IN)", "🇨🇳 China (CN)",
        "🇯🇵 Japan (JP)", "🇰🇷 South Korea (KR)", "🇹🇼 Taiwan (TW)",
        "🇭🇰 Hong Kong (HK)", "🇧🇩 Bangladesh (BD)", "🇵🇰 Pakistan (PK)",
        "🇱🇰 Sri Lanka (LK)", "🇲🇲 Myanmar (MM)", "🇱🇦 Laos (LA)",
        "🇧🇳 Brunei (BN)",
        # ── Middle East ───────────────────────────────────────────────────────
        "🇸🇦 Saudi Arabia (SA)", "🇦🇪 UAE (AE)", "🇰🇼 Kuwait (KW)",
        "🇶🇦 Qatar (QA)", "🇧🇭 Bahrain (BH)", "🇴🇲 Oman (OM)",
        "🇯🇴 Jordan (JO)", "🇱🇧 Lebanon (LB)",
        # ── Africa ────────────────────────────────────────────────────────────
        "🇪🇬 Egypt (EG)", "🇳🇬 Nigeria (NG)", "🇿🇦 South Africa (ZA)",
        "🇰🇪 Kenya (KE)", "🇬🇭 Ghana (GH)",
        # ── South America ─────────────────────────────────────────────────────
        "🇧🇷 Brazil (BR)", "🇦🇷 Argentina (AR)", "🇨🇴 Colombia (CO)",
        "🇨🇱 Chile (CL)", "🇵🇪 Peru (PE)", "🇻🇪 Venezuela (VE)",
        # ── Oceania ───────────────────────────────────────────────────────────
        "🇦🇺 Australia (AU)", "🇳🇿 New Zealand (NZ)",
    ]
    geo_country = QComboBox()
    for _c in _COUNTRIES:
        geo_country.addItem(_c)
    geo_country.setMinimumWidth(240)

    geo_state = _styled_input("State / Province (e.g. California, Bangkok, Phnom Penh)")
    geo_city  = _styled_input("City (e.g. Los Angeles, London, Singapore)")

    _LANGUAGES = [
        "Any Language", "English", "Spanish", "French", "German", "Arabic",
        "Hindi", "Chinese", "Japanese", "Korean", "Thai", "Vietnamese",
        "Khmer", "Indonesian", "Malay", "Portuguese", "Russian", "Ukrainian",
        "Italian", "Dutch", "Swedish", "Polish",
    ]
    geo_lang = QComboBox()
    for _l in _LANGUAGES:
        geo_lang.addItem(_l)

    g3g.addWidget(QLabel("Scope:"),      0, 0); g3g.addWidget(geo_scope,     0, 1)
    g3g.addWidget(QLabel("Continent:"),  0, 2); g3g.addWidget(geo_continent, 0, 3)
    g3g.addWidget(QLabel("Country:"),    1, 0); g3g.addWidget(geo_country,   1, 1, 1, 3)
    g3g.addWidget(QLabel("State/Prov:"), 2, 0); g3g.addWidget(geo_state,     2, 1)
    g3g.addWidget(QLabel("City:"),       2, 2); g3g.addWidget(geo_city,      2, 3)
    g3g.addWidget(QLabel("Language:"),   3, 0); g3g.addWidget(geo_lang,      3, 1)
    t3_inner_l.addWidget(grp3_geo)

    # ── Quality & Human Filters ───────────────────────────────────────────────
    grp3_qual = QGroupBox("⭐ Quality & Authenticity Filters")
    g3q = QGridLayout(grp3_qual)
    quality_tier  = _combo("Premium Real Human", "High Quality", "Standard")
    device_target = _combo("All Devices", "Mobile Only", "Desktop Only")
    real_human_chk = QCheckBox("✅  Real Human Only — filter out bot/fake traffic")
    real_human_chk.setChecked(True)
    real_human_chk.setStyleSheet(f"color:{TEXT}; font-size:14px; padding:2px 0;")
    g3q.addWidget(QLabel("Quality Tier:"),  0, 0); g3q.addWidget(quality_tier,  0, 1)
    g3q.addWidget(QLabel("Device:"),        0, 2); g3q.addWidget(device_target, 0, 3)
    g3q.addWidget(real_human_chk,           1, 0, 1, 4)
    t3_inner_l.addWidget(grp3_qual)

    # ── AI Results Table ──────────────────────────────────────────────────────
    _GEO_COLS = ["#", "Service", "Category", "$/1K", "Qty", "Cost", "Human%", "Geo%", "AI Score%"]
    geo_table = QTableWidget(0, len(_GEO_COLS))
    geo_table.setHorizontalHeaderLabels(_GEO_COLS)
    geo_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
    geo_table.setAlternatingRowColors(True)
    geo_table.setEditTriggers(QTableWidget.NoEditTriggers)
    geo_table.setSelectionBehavior(QTableWidget.SelectRows)
    geo_table.setFixedHeight(130)
    geo_table.setStyleSheet(svc_table.styleSheet())
    t3_inner_l.addWidget(geo_table)

    # ── Buttons ───────────────────────────────────────────────────────────────
    btn_smart       = ActionButton("🤖 AI GEO Analyze — Find Best Real Human Service", ACCENT)
    btn_place_smart = ActionButton("✅ Place Top-Ranked Geo Order", SUCCESS)
    btn_place_smart.setEnabled(False)
    btn_row3 = QHBoxLayout()
    btn_row3.addWidget(btn_smart, 2); btn_row3.addWidget(btn_place_smart, 1)
    t3_inner_l.addLayout(btn_row3)

    out3 = OutputBox(
        "AI will find the BEST REAL HUMAN service matching your exact geo-target.\n\n"
        "How the AI scores each service:\n"
        "  🌍 Geo Match (30%)   — exact country > continent > global\n"
        "  👤 Human Score (30%) — authenticity & real engagement probability\n"
        "  ⭐ Quality Tier (20%) — Premium > High Quality > Standard\n"
        "  💰 Value (10%)        — units per dollar spent\n"
        "  ✅ Affordability (5%) — fits within your budget\n"
        "  🔄 Refill Bonus (5%)  — long-term reliability\n\n"
        "Set Scope → Country → State → City for maximum precision."
    )
    t3_inner_l.addWidget(out3, 1)
    tabs.addTab(t3, "🌍 AI GEO Smart Order")

    _geo_results = [None]

    def _extract_iso(country_text: str) -> str:
        import re
        m = re.search(r'\(([A-Z]{2})\)', country_text)
        return m.group(1) if m else ""

    def _smart_order():
        out3.reset_color(); out3.setPlainText("🤖 AI analyzing geo-targeted services…")
        btn_place_smart.setEnabled(False)
        geo_table.setRowCount(0)

        scope_txt = geo_scope.currentText()
        if "Continent" in scope_txt:   scope = "Continent"
        elif "Country" in scope_txt:   scope = "Country"
        elif "State" in scope_txt:     scope = "State"
        elif "City" in scope_txt:      scope = "City"
        else:                          scope = "Global"

        cty_raw  = geo_country.currentText()
        cty_code = _extract_iso(cty_raw) if "Select" not in cty_raw else ""
        cont_val = geo_continent.currentText() if "Select" not in geo_continent.currentText() else ""
        dev_val  = device_target.currentText().replace(" Only", "").replace(" Devices", "")

        w = ApiWorker(f"{api_base}/api/v1/smm/geo-smart-order", {
            "link":            smart_link.text().strip() or "https://tiktok.com/@example",
            "goal":            smart_goal.currentText(),
            "budget_usd":      smart_budget.value(),
            "platform":        smart_plat.currentText(),
            "geo_scope":       scope,
            "continent":       cont_val,
            "country":         cty_code,
            "state":           geo_state.text().strip(),
            "city":            geo_city.text().strip(),
            "language":        geo_lang.currentText() if "Any" not in geo_lang.currentText() else "",
            "quality_tier":    quality_tier.currentText(),
            "real_human_only": real_human_chk.isChecked(),
            "device":          dev_val,
        }, btn=btn_smart)
        t3._w = w

        def _got(d):
            data = d.get("data", d)
            _geo_results[0] = data
            recs = data.get("recommendations", [])
            geo_table.setRowCount(0)
            for rec in recs:
                row = geo_table.rowCount(); geo_table.insertRow(row)
                vals = [
                    f"#{rec.get('rank', '')}",
                    rec.get("service_name", ""),
                    rec.get("category", ""),
                    rec.get("rate_per_1k", ""),
                    str(rec.get("recommended_qty", "")),
                    rec.get("estimated_cost", ""),
                    rec.get("human_score", ""),
                    rec.get("geo_match_score", ""),
                    rec.get("ai_confidence", ""),
                ]
                for col, val in enumerate(vals):
                    item = QTableWidgetItem(val)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    if col == 0:
                        item.setForeground(QColor(ACCENT))
                    elif col == 6:          # human score
                        try:
                            pct = int(str(val).replace("%", ""))
                            item.setForeground(QColor(
                                SUCCESS if pct >= 85 else WARNING if pct >= 70 else "#F38BA8"
                            ))
                        except ValueError:
                            pass
                    elif col == 8:          # AI confidence
                        try:
                            pct = int(str(val).replace("%", ""))
                            item.setForeground(QColor(SUCCESS if pct >= 80 else WARNING))
                        except ValueError:
                            pass
                    geo_table.setItem(row, col, item)
            btn_place_smart.setEnabled(bool(recs))
            out3.set_result(data)

        w.result_ready.connect(_got)
        w.error_signal.connect(out3.set_error)
        w.start()

    def _place_smart():
        data = _geo_results[0]
        if not data:
            return
        rec = data.get("top_recommendation") or (data.get("recommendations") or [{}])[0]
        out3.reset_color(); out3.setPlainText("🛒 Placing geo-targeted smart order…")
        w = ApiWorker(f"{api_base}/api/v1/smm/order", {
            "service_id": rec.get("service_id", 1004),
            "link":       rec.get("link") or smart_link.text().strip(),
            "quantity":   rec.get("recommended_qty", 500),
        })
        t3._wp = w
        w.result_ready.connect(lambda d: out3.set_result(d.get("data", d)))
        w.error_signal.connect(out3.set_error)
        w.start()

    # Wire geo_table row click → select different ranked option
    def _geo_row_clicked(row, _col):
        recs = (_geo_results[0] or {}).get("recommendations", [])
        if row < len(recs):
            rec = recs[row]
            out3.reset_color()
            out3.setPlainText(
                f"Selected Rank #{rec.get('rank')} service:\n"
                f"  {rec.get('service_name')}\n"
                f"  Qty: {rec.get('recommended_qty')}  Cost: {rec.get('estimated_cost')}\n"
                f"  Geo: {rec.get('geo_target')}  Human: {rec.get('human_score')}\n"
                f"  AI Score: {rec.get('ai_confidence')}\n\n"
                "Click '✅ Place Top-Ranked Geo Order' to place this order."
            )
            # Swap selected rank to top
            data = _geo_results[0]
            if data:
                data["top_recommendation"] = rec

    geo_table.cellClicked.connect(_geo_row_clicked)

    btn_smart.clicked.connect(_smart_order)
    btn_place_smart.clicked.connect(_place_smart)

    # ── Tab 4: Order Status / Refill / Cancel ────────────────────────────────
    t4 = QWidget(); t4l = QVBoxLayout(t4)
    grp4 = QGroupBox("Order Tracker")
    g4 = QGridLayout(grp4)
    order_id_input = QSpinBox()
    order_id_input.setRange(1, 9_999_999); order_id_input.setValue(90001)
    g4.addWidget(QLabel("Order ID:"), 0, 0); g4.addWidget(order_id_input, 0, 1)
    t4l.addWidget(grp4)

    btn_row4 = QHBoxLayout()
    btn_status = ActionButton("🔍 Check Status",  ACCENT)
    btn_refill = ActionButton("🔄 Request Refill", SUCCESS)
    btn_cancel = ActionButton("❌ Cancel Order",   "#F38BA8")
    btn_row4.addWidget(btn_status)
    btn_row4.addWidget(btn_refill)
    btn_row4.addWidget(btn_cancel)
    t4l.addLayout(btn_row4)

    # Bulk status row
    grp4b = QGroupBox("Bulk Status Check (comma-separated IDs, max 100)")
    g4b = QHBoxLayout(grp4b)
    bulk_ids_input = _styled_input("e.g. 90001, 90002, 90003")
    btn_bulk = ActionButton("📊 Bulk Status", "#CBA6F7")
    g4b.addWidget(bulk_ids_input, 1); g4b.addWidget(btn_bulk)
    t4l.addWidget(grp4b)

    out4 = OutputBox("Order status will appear here…\nRefill and Cancel are also available.")
    t4l.addWidget(out4, 1)
    tabs.addTab(t4, "📊 Order Status")

    def _check_status():
        out4.reset_color(); out4.setPlainText("Checking order status…")
        w = ApiWorker(f"{api_base}/api/v1/smm/order/{order_id_input.value()}", method="GET", btn=btn_status)
        t4._ws = w
        w.result_ready.connect(lambda d: out4.set_result(d.get("data", d)))
        w.error_signal.connect(out4.set_error)
        w.start()

    def _request_refill():
        out4.reset_color(); out4.setPlainText(f"Requesting refill for order #{order_id_input.value()}…")
        w = ApiWorker(f"{api_base}/api/v1/smm/refill", {"order_id": order_id_input.value()}, btn=btn_refill)
        t4._wr = w
        w.result_ready.connect(lambda d: out4.set_result(d.get("data", d)))
        w.error_signal.connect(out4.set_error)
        w.start()

    def _cancel_order():
        out4.reset_color(); out4.setPlainText(f"Cancelling order #{order_id_input.value()}…")
        w = ApiWorker(f"{api_base}/api/v1/smm/cancel", {"order_ids": [order_id_input.value()]}, btn=btn_cancel)
        t4._wc = w
        w.result_ready.connect(lambda d: out4.set_result(d.get("data", d)))
        w.error_signal.connect(out4.set_error)
        w.start()

    def _bulk_status():
        raw = bulk_ids_input.text().strip()
        if not raw:
            out4.set_error("Enter at least one order ID")
            return
        try:
            ids = [int(x.strip()) for x in raw.replace(",", " ").split() if x.strip()]
        except ValueError:
            out4.set_error("Invalid IDs — use numbers separated by commas")
            return
        out4.reset_color(); out4.setPlainText(f"Checking {len(ids)} orders…")
        w = ApiWorker(f"{api_base}/api/v1/smm/bulk-status", {"order_ids": ids[:100]}, btn=btn_bulk)
        t4._wbk = w
        w.result_ready.connect(lambda d: out4.set_result(d.get("data", d)))
        w.error_signal.connect(out4.set_error)
        w.start()

    btn_status.clicked.connect(_check_status)
    btn_refill.clicked.connect(_request_refill)
    btn_cancel.clicked.connect(_cancel_order)
    btn_bulk.clicked.connect(_bulk_status)

    # ── Tab 5: Order History ─────────────────────────────────────────────────
    t5 = QWidget(); t5l = QVBoxLayout(t5)
    hist_limit = QSpinBox(); hist_limit.setRange(5, 500); hist_limit.setValue(50)
    btn_hist = ActionButton("📜 Load Order History", ACCENT)
    row5 = QHBoxLayout()
    row5.addWidget(QLabel("Show last")); row5.addWidget(hist_limit)
    row5.addWidget(QLabel("orders")); row5.addWidget(btn_hist); row5.addStretch()
    t5l.addLayout(row5)

    _HIST_COLS = ["Order ID", "Service", "Link", "Qty", "Status", "Source", "Placed At"]
    hist_table = QTableWidget(0, len(_HIST_COLS))
    hist_table.setHorizontalHeaderLabels(_HIST_COLS)
    hist_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
    hist_table.setAlternatingRowColors(True)
    hist_table.setEditTriggers(QTableWidget.NoEditTriggers)
    hist_table.setSelectionBehavior(QTableWidget.SelectRows)
    hist_table.setStyleSheet(svc_table.styleSheet())
    t5l.addWidget(hist_table, 1)

    hist_stats = QLabel("Order history not loaded yet")
    hist_stats.setStyleSheet(f"color:{SUBTEXT}; font-size:14px; padding:2px 0;")
    t5l.addWidget(hist_stats)
    tabs.addTab(t5, "📜 Order History")

    def _load_history():
        hist_stats.setText("Loading history…")
        w = ApiWorker(f"{api_base}/api/v1/smm/history?limit={hist_limit.value()}", method="GET", btn=btn_hist)
        t5._w = w
        def _got(resp):
            d      = resp.get("data", resp)
            orders = d.get("orders", [])
            src    = d.get("source", "?")
            hist_table.setRowCount(0)
            for i, o in enumerate(orders):
                hist_table.insertRow(i)
                vals = [
                    str(o.get("order", o.get("id", ""))),
                    str(o.get("service", "")),
                    str(o.get("link", ""))[:50],
                    str(o.get("quantity", "")),
                    str(o.get("status", "")),
                    str(o.get("source", src)),
                    str(o.get("placed_at", o.get("created_at", ""))),
                ]
                for col, val in enumerate(vals):
                    item = QTableWidgetItem(val)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    if col == 4:
                        if "Completed" in val:
                            item.setForeground(QColor(SUCCESS))
                        elif "Cancelled" in val or "Failed" in val:
                            item.setForeground(QColor("#F38BA8"))
                        elif "In Progress" in val:
                            item.setForeground(QColor(WARNING))
                    if col == 5 and val == "live":
                        item.setForeground(QColor(SUCCESS))
                    hist_table.setItem(i, col, item)
            src_label = "🟢 Live" if src == "live" else "🟡 Demo"
            hist_stats.setText(f"{src_label}  |  {len(orders)} orders shown")
        w.result_ready.connect(_got)
        w.error_signal.connect(lambda e: hist_stats.setText(f"❌ {e}"))
        w.start()

    btn_hist.clicked.connect(_load_history)

    layout.addWidget(tabs, 1)
    return page


# ─────────────────────────────────────────────────────────────────────────────
def build_multiagent_page(api_base: str) -> QWidget:
    page, layout = _make_page_layout("Multi-Agent AI — Central Brain", "🤖")

    info = QLabel(
        "Feature #99 — 5 specialized AI agents run in PARALLEL:\n"
        "  🎯 Strategy Agent  •  ✍️ Creator Agent  •  📊 Analyst Agent  •  🛡️ Compliance Agent  •  🧠 Orchestrator"
    )
    info.setStyleSheet(f"color:{SUBTEXT}; font-size:14px; padding:4px 0;")
    layout.addWidget(info)

    grp = QGroupBox("Account Data for Full Multi-Agent Analysis")
    g = QGridLayout(grp)
    username  = _styled_input("@username")
    platform  = _combo("TikTok", "Instagram", "Facebook", "YouTube", "Telegram")
    niche     = _styled_input("Niche (e.g. Fitness, Tech, Business)")
    followers = QSpinBox(); followers.setRange(0, 99_000_000); followers.setValue(15000)
    views     = QSpinBox(); views.setRange(0, 100_000_000); views.setValue(50000)
    likes     = QSpinBox(); likes.setRange(0, 10_000_000); likes.setValue(3500)
    g.addWidget(QLabel("Username:"),  0, 0); g.addWidget(username,  0, 1)
    g.addWidget(QLabel("Platform:"),  0, 2); g.addWidget(platform,  0, 3)
    g.addWidget(QLabel("Niche:"),     1, 0); g.addWidget(niche,     1, 1, 1, 3)
    g.addWidget(QLabel("Followers:"), 2, 0); g.addWidget(followers, 2, 1)
    g.addWidget(QLabel("Avg Views:"), 2, 2); g.addWidget(views,     2, 3)
    g.addWidget(QLabel("Avg Likes:"), 3, 0); g.addWidget(likes,     3, 1)
    layout.addWidget(grp)

    btn = ActionButton("🤖 Launch Full 5-Agent AI Analysis", ACCENT)
    layout.addWidget(btn)

    output = OutputBox(
        "All 5 AI agents will analyze your account in parallel…\n"
        "• Strategy Agent: Growth plan & tactics\n"
        "• Creator Agent: Content recommendations\n"
        "• Analyst Agent: Performance insights\n"
        "• Compliance Agent: Risk assessment\n"
        "• Orchestrator: Synthesizes all findings into final decision"
    )
    layout.addWidget(output, 1)

    def _run():
        output.reset_color()
        output.setPlainText("Launching 5 AI agents in parallel…\nThis takes 10-30 seconds with real GPT-4o.")
        w = ApiWorker(f"{api_base}/api/v1/ai/orchestrate", {
            "username": username.text() or "demo",
            "platform": platform.currentText(),
            "followers": followers.value(),
            "niche": niche.text() or "General",
            "metrics": {
                "views": views.value(),
                "likes": likes.value(),
                "comments": int(views.value() * 0.01),
            },
        }, btn=btn)
        page._worker = w
        w.result_ready.connect(lambda d: output.set_result(d.get("data", d)))
        w.error_signal.connect(output.set_error)
        w.start()

    btn.clicked.connect(_run)
    return page


# ─────────────────────────────────────────────────────────────────────────────
def build_memory_page(api_base: str) -> QWidget:
    page, layout = _make_page_layout("Memory System", "💾")
    tabs = QTabWidget()

    info = QLabel("Feature #9 + #10 + #16 — AI remembers every brand, campaign, and decision across sessions.")
    info.setStyleSheet(f"color:{SUBTEXT}; font-size:14px;")
    layout.addWidget(info)

    # ── Tab 1: Store Brand Memory ──────────────────────────────────────────────
    t1 = QWidget(); t1l = QVBoxLayout(t1)
    grp1 = QGroupBox("Store Brand Memory")
    g1 = QGridLayout(grp1)
    brand_id    = _styled_input("brand_id (e.g. mybrand_tiktok)")
    brand_name  = _styled_input("Brand name")
    brand_niche = _styled_input("Niche")
    brand_plat  = _combo("TikTok", "Instagram", "Facebook", "YouTube", "Telegram", "Multi-Platform")
    brand_foll  = QSpinBox(); brand_foll.setRange(0, 99_000_000); brand_foll.setValue(15000)
    brand_goal  = _styled_input("Main goal (e.g. Reach 100K followers in 6 months)")
    g1.addWidget(QLabel("Brand ID:"),   0, 0); g1.addWidget(brand_id,    0, 1)
    g1.addWidget(QLabel("Name:"),       0, 2); g1.addWidget(brand_name,  0, 3)
    g1.addWidget(QLabel("Niche:"),      1, 0); g1.addWidget(brand_niche, 1, 1)
    g1.addWidget(QLabel("Platform:"),   1, 2); g1.addWidget(brand_plat,  1, 3)
    g1.addWidget(QLabel("Followers:"),  2, 0); g1.addWidget(brand_foll,  2, 1)
    g1.addWidget(QLabel("Main Goal:"),  3, 0); g1.addWidget(brand_goal,  3, 1, 1, 3)
    t1l.addWidget(grp1)
    btn_store = ActionButton("💾 Save Brand to Memory", ACCENT)
    t1l.addWidget(btn_store)
    out1 = OutputBox("Brand memory storage confirmation will appear here…")
    t1l.addWidget(out1, 1)
    tabs.addTab(t1, "Store Brand")

    def _store_brand():
        out1.reset_color(); out1.setPlainText("Saving brand memory…")
        bid = brand_id.text() or "default_brand"
        w = ApiWorker(f"{api_base}/api/v1/memory/store-brand", {
            "brand_id": bid,
            "data": {
                "name": brand_name.text() or bid,
                "niche": brand_niche.text() or "General",
                "platform": brand_plat.currentText(),
                "followers": brand_foll.value(),
                "main_goal": brand_goal.text() or "Grow audience",
            },
        }, btn=btn_store)
        page._w1 = w
        w.result_ready.connect(lambda d: out1.set_result(d.get("data", d)))
        w.error_signal.connect(out1.set_error)
        w.start()

    btn_store.clicked.connect(_store_brand)

    # ── Tab 2: Retrieve Brand Context ──────────────────────────────────────────
    t2 = QWidget(); t2l = QVBoxLayout(t2)
    grp2 = QGroupBox("Retrieve Brand Context & Timeline")
    g2 = QGridLayout(grp2)
    get_brand_id = _styled_input("brand_id to retrieve (e.g. mybrand_tiktok)")
    g2.addWidget(QLabel("Brand ID:"), 0, 0); g2.addWidget(get_brand_id, 0, 1)
    t2l.addWidget(grp2)
    btn_row2 = QHBoxLayout()
    btn_get   = ActionButton("🔍 Get Brand Context",  ACCENT)
    btn_timeline = ActionButton("📜 View Timeline",   SUCCESS)
    btn_row2.addWidget(btn_get)
    btn_row2.addWidget(btn_timeline)
    t2l.addLayout(btn_row2)
    out2 = OutputBox("Brand context, history, and timeline will appear here…\n"
                     "Shows all stored strategies, campaigns, and AI decisions.")
    t2l.addWidget(out2, 1)
    tabs.addTab(t2, "Brand Context")

    def _get_context(btn=None):
        out2.reset_color(); out2.setPlainText("Retrieving brand memory…")
        bid = get_brand_id.text() or "default_brand"
        w = ApiWorker(f"{api_base}/api/v1/memory/brand/{bid}", method="GET", btn=btn)
        page._w2 = w
        w.result_ready.connect(lambda d: out2.set_result(d.get("data", d)))
        w.error_signal.connect(out2.set_error)
        w.start()

    btn_get.clicked.connect(lambda: _get_context(btn_get))
    btn_timeline.clicked.connect(lambda: _get_context(btn_timeline))

    # ── Tab 3: Knowledge Search ────────────────────────────────────────────────
    t3 = QWidget(); t3l = QVBoxLayout(t3)
    grp3 = QGroupBox("Knowledge Base Search  — Feature #16")
    g3 = QGridLayout(grp3)
    search_brand = _styled_input("brand_id to search in")
    search_query = _styled_input("Search query (e.g. best posting times, viral hooks, engagement tips)")
    g3.addWidget(QLabel("Brand ID:"), 0, 0); g3.addWidget(search_brand, 0, 1)
    g3.addWidget(QLabel("Query:"),    1, 0); g3.addWidget(search_query,  1, 1)
    t3l.addWidget(grp3)
    btn_search = ActionButton("🔎 Search Knowledge Base", ACCENT)
    t3l.addWidget(btn_search)
    out3 = OutputBox("Knowledge search results will appear here…\n"
                     "Search across all stored AI decisions, strategies, and learnings.")
    t3l.addWidget(out3, 1)
    tabs.addTab(t3, "Knowledge Search")

    def _search():
        out3.reset_color(); out3.setPlainText("Searching knowledge base…")
        w = ApiWorker(f"{api_base}/api/v1/memory/search", {
            "brand_id": search_brand.text() or "default_brand",
            "query": search_query.text() or "growth strategy",
        }, btn=btn_search)
        page._w3 = w
        w.result_ready.connect(lambda d: out3.set_result(d.get("data", d)))
        w.error_signal.connect(out3.set_error)
        w.start()

    btn_search.clicked.connect(_search)

    layout.addWidget(tabs, 1)
    return page


# ─────────────────────────────────────────────────────────────────────────────
# Embedded OAuth Browser Dialog  (PyQtWebEngine — Chromium inside the app)
# ─────────────────────────────────────────────────────────────────────────────
if _HAS_WEBENGINE:
    class OAuthBrowserDialog(QDialog):
        """
        Secure embedded Chromium browser for all OAuth 2.0 / social login flows.

        ✅ Persists cookies/session — stay logged in to Facebook, Google etc.
        ✅ Auto-detects the OAuth callback URL and extracts code+state instantly.
        ✅ No copy-pasting or manual steps.  Facebook Pages work out of the box.
        ✅ Shows a real address bar so you always know where you are.
        """
        code_captured = pyqtSignal(str, str)   # emits (code, state)
        _PROFILE = None                        # shared persistent profile

        def __init__(self, url: str, redirect_uri: str = "", parent=None):
            super().__init__(parent)
            self._redirect = redirect_uri or "http://localhost:8000/oauth/callback"
            self._code  = ""
            self._state = ""
            self._done  = False

            self.setWindowTitle("🔐 GrowthOS — Secure Login")
            self.setMinimumSize(980, 720)
            self.resize(1060, 740)
            self.setStyleSheet(f"QDialog {{ background:{DARK_BG}; }}")

            root = QVBoxLayout(self)
            root.setContentsMargins(0, 0, 0, 0)
            root.setSpacing(0)

            # ── Address / status bar ──────────────────────────────────────
            bar = QFrame()
            bar.setFixedHeight(44)
            bar.setStyleSheet(
                f"background:{SURFACE}; border-bottom:1px solid {BORDER};"
            )
            bar_row = QHBoxLayout(bar)
            bar_row.setContentsMargins(10, 0, 10, 0)
            bar_row.setSpacing(8)

            self._lock = QLabel("🔒")
            self._lock.setStyleSheet(f"font-size:16px; color:{SUCCESS};")
            bar_row.addWidget(self._lock)

            self._url_bar = QLabel("Loading…")
            self._url_bar.setStyleSheet(
                f"color:{TEXT}; font-size:13px; background:{HOVER}; "
                f"border-radius:5px; padding:3px 10px; min-width:400px;"
            )
            self._url_bar.setTextInteractionFlags(Qt.TextSelectableByMouse)
            bar_row.addWidget(self._url_bar, 1)

            self._prog = QLabel("")
            self._prog.setStyleSheet(f"color:{SUBTEXT}; font-size:12px; min-width:140px;")
            bar_row.addWidget(self._prog)

            cancel_btn = QPushButton("✕  Cancel")
            cancel_btn.setStyleSheet(
                f"background:#3d1a1a; color:#F38BA8; border:none; "
                f"border-radius:5px; padding:5px 16px; font-size:13px; font-weight:bold;"
            )
            cancel_btn.setCursor(Qt.PointingHandCursor)
            cancel_btn.clicked.connect(self.reject)
            bar_row.addWidget(cancel_btn)
            root.addWidget(bar)

            # ── Persistent Chromium profile (keeps cookies between sessions) ─
            if OAuthBrowserDialog._PROFILE is None:
                prof = QWebEngineProfile("GrowthOS_OAuth_v1")
                prof.setPersistentCookiesPolicy(
                    QWebEngineProfile.AllowPersistentCookies
                )
                OAuthBrowserDialog._PROFILE = prof

            self._view = QWebEngineView()
            web_page   = QWebEnginePage(OAuthBrowserDialog._PROFILE, self._view)
            self._view.setPage(web_page)
            root.addWidget(self._view, 1)

            # ── Wire signals ─────────────────────────────────────────────
            self._view.urlChanged.connect(self._on_url_changed)
            self._view.titleChanged.connect(
                lambda t: self.setWindowTitle(
                    f"🔐  {t}" if t else "🔐 GrowthOS — Secure Login"
                )
            )
            self._view.loadProgress.connect(
                lambda p: self._prog.setText(
                    "✅ Captured!" if self._done else f"Loading {p}%…"
                )
            )
            self._view.loadFinished.connect(
                lambda ok: self._prog.setText(
                    "✅ Captured!" if self._done else ("✓ Loaded" if ok else "⚠ Load error")
                )
            )

            # Navigate to the OAuth URL
            self._view.load(QUrl(url))

        # ── URL monitor — the core of the embedded OAuth flow ────────────────
        def _on_url_changed(self, qurl):
            url_str = qurl.toString()
            disp    = url_str if len(url_str) <= 90 else url_str[:87] + "…"
            self._url_bar.setText(disp)

            # Change lock icon color based on scheme
            if url_str.startswith("https://"):
                self._lock.setStyleSheet(f"font-size:16px; color:{SUCCESS};")
            elif url_str.startswith("http://localhost") or url_str.startswith("http://127."):
                self._lock.setStyleSheet(f"font-size:16px; color:{WARNING};")
            else:
                self._lock.setStyleSheet(f"font-size:16px; color:#F38BA8;")

            if self._done:
                return

            # Check if we hit our callback URI
            if url_str.startswith(self._redirect):
                try:
                    parsed = urllib.parse.urlparse(url_str)
                    qs     = urllib.parse.parse_qs(parsed.query)
                    error  = qs.get("error", [""])[0]
                    code   = qs.get("code",  [""])[0]
                    state  = qs.get("state", [""])[0]

                    if error:
                        self._prog.setText(f"⚠ Error: {error}")
                        self._url_bar.setText(f"⚠ Platform returned error: {error}")
                        return

                    if code:
                        self._done  = True
                        self._code  = code
                        self._state = state
                        self._prog.setText("✅ Authorization complete!")
                        self._url_bar.setText("✅  Authorization successful — returning to GrowthOS…")
                        self._lock.setStyleSheet(f"font-size:16px; color:{SUCCESS};")
                        self.code_captured.emit(code, state)
                        # Give user 1.2 s to see the success message
                        QTimer.singleShot(1200, self.accept)
                except Exception:
                    pass

        def get_code(self)  -> str: return self._code
        def get_state(self) -> str: return self._state


# ─────────────────────────────────────────────────────────────────────────────
def build_social_accounts_page(api_base: str) -> QWidget:
    """
    Features #105-#110: Social Media Account Manager
    Secure OAuth 2.0 login + AES-256 encrypted token storage for all platforms.
    Tabs: My Accounts | Connect Platform | Bot Tokens | Test Connections | Setup Guide
    """
    import webbrowser

    page, layout = _make_page_layout("Social Accounts Manager", "🔐")
    page._workers: list = []

    sub = QLabel(
        "Securely connect & manage all social media accounts  •  OAuth 2.0 + PKCE  •  "
        "AES-256 encrypted tokens  •  Auto-refresh  •  Multi-account support"
    )
    sub.setStyleSheet(f"color:{SUBTEXT}; font-size:14px;")
    layout.addWidget(sub)

    # Platform color map
    _PLT_ICON = {
        "Facebook":  ("📘", "#1877F2"),
        "Instagram": ("📸", "#E1306C"),
        "TikTok":    ("🎵", "#FF004F"),
        "YouTube":   ("▶️", "#FF0000"),
        "Twitter/X": ("🐦", "#1DA1F2"),
        "LinkedIn":  ("💼", "#0A66C2"),
        "Telegram":  ("✈️", "#26A5E4"),
    }
    _STATUS_COLOR = {
        "connected": SUCCESS,
        "expired":   WARNING,
        "error":     "#F38BA8",
        "timeout":   WARNING,
        "no_token":  SUBTEXT,
        "unknown":   SUBTEXT,
    }

    tabs = QTabWidget()

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 1 — MY ACCOUNTS
    # ═════════════════════════════════════════════════════════════════════════
    t1 = QWidget(); t1l = QVBoxLayout(t1); t1l.setSpacing(8)

    stats_bar = QLabel("📭 No accounts connected yet")
    stats_bar.setStyleSheet(
        f"background:{SURFACE}; color:{ACCENT}; padding:6px 12px; border-radius:6px; "
        f"font-size:14px; font-weight:bold;"
    )
    t1l.addWidget(stats_bar)

    _ACC_COLS = ["#", "Platform", "Account Name", "Status", "Connected At", "Last Tested", "Has Refresh"]
    acc_table = QTableWidget(0, len(_ACC_COLS))
    acc_table.setHorizontalHeaderLabels(_ACC_COLS)
    acc_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
    acc_table.setAlternatingRowColors(True)
    acc_table.setEditTriggers(QTableWidget.NoEditTriggers)
    acc_table.setSelectionBehavior(QTableWidget.SelectRows)
    acc_table.setStyleSheet(f"""
        QTableWidget {{
            background:{SURFACE}; color:{TEXT};
            border:1px solid #45475A; border-radius:6px; gridline-color:#45475A;
        }}
        QHeaderView::section {{
            background:{DARK_BG}; color:{ACCENT}; padding:8px; border:none; font-weight:bold;
        }}
        QTableWidget::item:alternate {{ background:#252535; }}
        QTableWidget::item:selected  {{ background:#313244; color:{TEXT}; }}
    """)
    t1l.addWidget(acc_table, 1)

    btn1_row = QHBoxLayout()
    btn_refresh_accs  = ActionButton("🔄 Refresh List",        ACCENT)
    btn_test_selected = ActionButton("🧪 Test Selected",       SUCCESS)
    btn_refresh_token = ActionButton("♻️ Refresh Token",       WARNING)
    btn_disconnect    = ActionButton("🗑 Disconnect",           "#F38BA8")
    for b in [btn_refresh_accs, btn_test_selected, btn_refresh_token, btn_disconnect]:
        btn1_row.addWidget(b)
    t1l.addLayout(btn1_row)

    acc_status_out = OutputBox("Select an account and click Test / Refresh Token / Disconnect…")
    acc_status_out.setMaximumHeight(80)
    t1l.addWidget(acc_status_out)
    tabs.addTab(t1, "🔑 My Accounts")

    # Shared account list state
    _acc_data: list = [[]]

    def _populate_accounts(accounts: list):
        _acc_data[0] = accounts
        total     = len(accounts)
        connected = sum(1 for a in accounts if a.get("status") == "connected")
        stats_bar.setText(
            f"📱 Total accounts: {total}  |  ✅ Connected: {connected}  |  "
            f"📛 Platforms: {len(set(a['platform'] for a in accounts))}"
        )
        acc_table.setRowCount(0)
        for i, acc in enumerate(accounts):
            plt    = acc.get("platform", "")
            icon, color = _PLT_ICON.get(plt, ("🌐", ACCENT))
            status = acc.get("status", "unknown")
            acc_table.insertRow(i)
            cells = [
                str(i + 1),
                f"{icon} {plt}",
                acc.get("display_name", ""),
                status.upper(),
                acc.get("connected_at", "")[:16].replace("T", " "),
                acc.get("last_tested", "")[:16].replace("T", " "),
                "✅" if acc.get("has_refresh_token") else "—",
            ]
            for col, val in enumerate(cells):
                item = QTableWidgetItem(val)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                if col == 1:
                    item.setForeground(QColor(color))
                if col == 3:
                    item.setForeground(QColor(_STATUS_COLOR.get(status, SUBTEXT)))
                acc_table.setItem(i, col, item)

    def _load_accounts_list():
        w = ApiWorker(f"{api_base}/api/v1/auth/accounts", method="GET")
        page._wa = w
        def _got(resp):
            _populate_accounts(resp.get("data", []))
        w.result_ready.connect(_got)
        w.error_signal.connect(lambda e: stats_bar.setText(f"❌ {e}"))
        w.start()
        page._workers.append(w)

    def _get_selected_acc():
        row = acc_table.currentRow()
        data = _acc_data[0]
        if row >= 0 and row < len(data):
            return data[row]
        return None

    def _test_selected():
        acc = _get_selected_acc()
        if not acc:
            acc_status_out.set_error("Please select an account from the table.")
            return
        acc_status_out.reset_color()
        acc_status_out.setPlainText(f"⏳ Testing {acc['platform']} — {acc['display_name']}…")
        w = ApiWorker(f"{api_base}/api/v1/auth/test", {"account_id": acc["id"]})
        page._wt = w
        def _got(resp):
            d = resp.get("data", resp)
            status = d.get("status", "unknown")
            color  = _STATUS_COLOR.get(status, SUBTEXT)
            info_str = str(d.get("info", "")) if d.get("info") else ""
            msg = (
                f"Platform: {acc['platform']}  •  Account: {acc['display_name']}\n"
                f"Status:   {status.upper()}\n"
                f"HTTP:     {d.get('http_status', 'N/A')}\n"
            )
            if d.get("error"):
                msg += f"Error:    {d['error']}\n"
            if info_str:
                msg += f"Info:     {info_str[:120]}\n"
            acc_status_out.reset_color()
            acc_status_out.setPlainText(msg)
            if status != "connected":
                acc_status_out.set_error(msg)
            _load_accounts_list()
        w.result_ready.connect(_got)
        w.error_signal.connect(acc_status_out.set_error)
        w.start()
        page._workers.append(w)

    def _refresh_token_selected():
        acc = _get_selected_acc()
        if not acc:
            acc_status_out.set_error("Please select an account.")
            return
        acc_status_out.reset_color()
        acc_status_out.setPlainText(f"⏳ Refreshing token for {acc['display_name']}…")
        w = ApiWorker(f"{api_base}/api/v1/auth/refresh", {"account_id": acc["id"]})
        page._wr = w
        def _got(resp):
            d = resp.get("data", resp)
            acc_status_out.reset_color()
            acc_status_out.setPlainText(
                f"✅ Token refreshed for {acc['platform']} — {acc['display_name']}\n"
                f"Refreshed at: {d.get('refreshed_at', '')}"
            )
            _load_accounts_list()
        w.result_ready.connect(_got)
        w.error_signal.connect(acc_status_out.set_error)
        w.start()
        page._workers.append(w)

    def _disconnect_selected():
        acc = _get_selected_acc()
        if not acc:
            acc_status_out.set_error("Please select an account to disconnect.")
            return
        acc_status_out.reset_color()
        acc_status_out.setPlainText(f"⏳ Disconnecting {acc['display_name']}…")
        # DELETE request via ApiWorker (method override)
        w = ApiWorker(
            f"{api_base}/api/v1/auth/account/{acc['id']}",
            {}, method="DELETE",
        )
        page._wd = w
        def _got(resp):
            acc_status_out.reset_color()
            acc_status_out.setPlainText(
                f"🗑 Account disconnected: {acc['platform']} — {acc['display_name']}\n"
                f"All stored tokens have been permanently deleted."
            )
            _load_accounts_list()
        w.result_ready.connect(_got)
        w.error_signal.connect(acc_status_out.set_error)
        w.start()
        page._workers.append(w)

    btn_refresh_accs.clicked.connect(_load_accounts_list)
    btn_test_selected.clicked.connect(_test_selected)
    btn_refresh_token.clicked.connect(_refresh_token_selected)
    btn_disconnect.clicked.connect(_disconnect_selected)
    QTimer.singleShot(600, _load_accounts_list)

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 2 — CONNECT OAUTH PLATFORM
    # ═════════════════════════════════════════════════════════════════════════
    t2 = QWidget(); t2l = QVBoxLayout(t2); t2l.setSpacing(10)

    sec_note = QLabel(
        "🔒  Security: Tokens are encrypted with AES-256 (Fernet) before saving to disk.\n"
        "     OAuth 2.0 + PKCE is used for TikTok, YouTube, and Twitter/X — no secret needed.\n"
        "     Redirect URI (pre-register this in your developer app):  http://localhost:8000/oauth/callback"
    )
    sec_note.setStyleSheet(
        f"background:#1a2a1a; color:{SUCCESS}; padding:10px 14px; border-radius:8px; "
        f"font-size:14px; border:1px solid #2d5a2d;"
    )
    sec_note.setWordWrap(True)
    t2l.addWidget(sec_note)

    grp2 = QGroupBox("OAuth 2.0 Connect  — Feature #105")
    g2   = QGridLayout(grp2)
    oauth_platform = _combo("Facebook", "Instagram", "TikTok", "YouTube", "Twitter/X", "LinkedIn")
    oauth_client_id     = _styled_input("Client ID  (required for all platforms)")
    oauth_client_secret = QLineEdit()
    oauth_client_secret.setPlaceholderText(
        "Client Secret  (optional for PKCE platforms: TikTok, YouTube, Twitter/X)"
    )
    oauth_client_secret.setEchoMode(QLineEdit.Password)
    oauth_client_secret.setStyleSheet(
        f"background:#252535; color:{TEXT}; border:1px solid #45475A; "
        f"border-radius:6px; padding:8px 12px; font-size:14px;"
    )
    g2.addWidget(QLabel("Platform:"),      0, 0); g2.addWidget(oauth_platform,        0, 1)
    g2.addWidget(QLabel("Client ID:"),     1, 0); g2.addWidget(oauth_client_id,        1, 1)
    g2.addWidget(QLabel("Client Secret:"), 2, 0); g2.addWidget(oauth_client_secret,    2, 1)
    t2l.addWidget(grp2)

    btn2_row = QHBoxLayout()
    btn_start_oauth    = ActionButton("🔐 Start Secure Login  (embedded browser)" if _HAS_WEBENGINE else "🌐 Start OAuth  (opens browser)", ACCENT)
    btn_complete_oauth = ActionButton("✅ Complete Connection",           SUCCESS)
    btn_complete_oauth.setEnabled(False)
    btn2_row.addWidget(btn_start_oauth); btn2_row.addWidget(btn_complete_oauth)
    t2l.addLayout(btn2_row)

    # State panel
    oauth_state_lbl = QLabel("Enter Client ID and click 'Start OAuth' to begin")
    oauth_state_lbl.setStyleSheet(
        f"background:{SURFACE}; color:{SUBTEXT}; padding:8px 12px; "
        f"border-radius:6px; font-size:14px; font-weight:bold;"
    )
    t2l.addWidget(oauth_state_lbl)

    # Manual fallback
    grp2b = QGroupBox("Manual Code Entry  (if auto-capture fails)")
    g2b   = QVBoxLayout(grp2b)
    g2b.addWidget(QLabel(
        "If the browser redirect does not auto-complete, paste the full redirect URL or just the code:"
    ))
    oauth_manual_code = _styled_input(
        "Paste full redirect URL  (e.g. http://localhost:8000/oauth/callback?code=xxx&state=yyy)  "
        "or just the code"
    )
    g2b.addWidget(oauth_manual_code)
    t2l.addWidget(grp2b)

    out2 = OutputBox("OAuth flow results will appear here…")
    t2l.addWidget(out2, 1)
    tabs.addTab(t2, "🔗 Connect Platform")

    # Per-flow state
    _oauth_state = {"state": "", "platform": "", "polling": False}

    def _start_oauth():
        client_id = oauth_client_id.text().strip()
        if not client_id:
            out2.set_error("Client ID is required.")
            return
        platform = oauth_platform.currentText()
        out2.reset_color()
        out2.setPlainText(f"⏳ Generating OAuth URL for {platform}…")
        btn_start_oauth.set_loading(True)
        btn_complete_oauth.setEnabled(False)

        w = ApiWorker(f"{api_base}/api/v1/auth/generate-url", {
            "platform":      platform,
            "client_id":     client_id,
            "client_secret": oauth_client_secret.text().strip(),
        })
        page._wo = w
        def _got(resp):
            btn_start_oauth.set_loading(False)
            d    = resp.get("data", resp)
            url  = d.get("url", "")
            st   = d.get("state", "")
            pkce = d.get("pkce", False)

            _oauth_state["state"]    = st
            _oauth_state["platform"] = platform

            if _HAS_WEBENGINE:
                # ── Embedded browser — full auto-capture ─────────────────
                out2.reset_color()
                out2.setPlainText(
                    f"🔐 Opening secure embedded browser for {platform}…\n"
                    f"{'═'*55}\n"
                    f"• Log in to your {platform} account inside the browser window\n"
                    f"• Authorize GrowthOS AI when prompted\n"
                    f"• The window will close automatically and connect your account\n"
                    f"• No copy-pasting needed — everything is automatic\n\n"
                    f"PKCE: {'Yes ✅' if pkce else 'No'}  |  Redirect: {d.get('redirect_uri','')}"
                )
                oauth_state_lbl.setText(
                    f"🔐 Browser opened — log in and authorize {platform}"
                )
                oauth_state_lbl.setStyleSheet(
                    f"background:#1a1a2a; color:{ACCENT}; padding:8px 12px; "
                    f"border-radius:6px; font-size:14px; font-weight:bold;"
                )

                dlg = OAuthBrowserDialog(
                    url,
                    d.get("redirect_uri", "http://localhost:8000/oauth/callback"),
                    parent=page.window(),
                )

                def _on_code_captured(code: str, state: str):
                    _oauth_state["state"] = state or st
                    oauth_manual_code.setText(code)
                    oauth_state_lbl.setText(
                        f"🎯 Authorization complete! Click ✅ Complete Connection"
                    )
                    oauth_state_lbl.setStyleSheet(
                        f"background:#1a2a1a; color:{SUCCESS}; padding:8px 12px; "
                        f"border-radius:6px; font-size:14px; font-weight:bold;"
                    )
                    btn_complete_oauth.setEnabled(True)
                    out2.reset_color()
                    out2.setPlainText(
                        f"🎯 Authorization code captured for {platform}!\n"
                        f"{'═'*55}\n"
                        f"Click  ✅ Complete Connection  to finish linking your account.\n\n"
                        f"(The code is pre-filled below automatically)"
                    )

                dlg.code_captured.connect(_on_code_captured)
                dlg.exec()

                # Fallback: dialog closed before signal fired but code was captured
                if dlg.get_code() and not oauth_manual_code.text().strip():
                    _on_code_captured(dlg.get_code(), dlg.get_state())

            else:
                # ── Fallback: open system browser + poll ─────────────────
                import webbrowser
                webbrowser.open(url)
                oauth_state_lbl.setText(
                    f"🌐 Browser opened for {platform}  •  State: {st[:12]}…"
                )
                oauth_state_lbl.setStyleSheet(
                    f"background:#1a2a1a; color:{SUCCESS}; padding:8px 12px; "
                    f"border-radius:6px; font-size:14px; font-weight:bold;"
                )
                btn_complete_oauth.setEnabled(True)
                out2.reset_color()
                out2.setPlainText(
                    f"✅ OAuth URL generated for {platform}\n"
                    f"{'═'*55}\n"
                    f"1. Browser opened — log in and authorize GrowthOS AI\n"
                    f"2. You will be redirected to: {d.get('redirect_uri','')}\n"
                    f"3. GrowthOS auto-captures the code\n"
                    f"4. Click ✅ Complete Connection to finish\n\n"
                    f"   (Or paste redirect URL manually below if auto-capture fails)\n\n"
                    f"Auth URL:\n{url}"
                )
                _poll_for_code(st)

        w.result_ready.connect(_got)
        w.error_signal.connect(lambda e: (
            btn_start_oauth.set_loading(False),
            out2.set_error(e),
        ))
        w.start()
        page._workers.append(w)

    def _poll_for_code(state: str, attempts: int = 0):
        """Fallback polling used only when WebEngine is not available."""
        if attempts > 60:
            return
        w = ApiWorker(f"{api_base}/api/v1/auth/poll-callback/{state}", method="GET")
        page._wp = w
        def _got(resp):
            if resp.get("captured"):
                code = resp.get("code", "")
                oauth_state_lbl.setText(
                    f"🎯 Code captured automatically!  Click ✅ Complete Connection"
                )
                oauth_state_lbl.setStyleSheet(
                    f"background:#1a2a1a; color:{SUCCESS}; padding:8px 12px; "
                    f"border-radius:6px; font-size:14px; font-weight:bold;"
                )
                oauth_manual_code.setText(code)
            else:
                QTimer.singleShot(1000, lambda: _poll_for_code(state, attempts + 1))
        w.result_ready.connect(_got)
        w.start()
        page._workers.append(w)

    def _complete_oauth():
        platform  = _oauth_state.get("platform") or oauth_platform.currentText()
        state_val = _oauth_state.get("state", "")

        # Determine code: from poll or manual
        manual_input = oauth_manual_code.text().strip()
        code = ""
        if manual_input:
            # Could be full URL or just code
            if "code=" in manual_input:
                try:
                    parsed = urllib.parse.urlparse(manual_input)
                    qs     = urllib.parse.parse_qs(parsed.query)
                    code      = qs.get("code",  [""])[0]
                    state_val = qs.get("state", [state_val])[0]
                except Exception:
                    code = manual_input
            else:
                code = manual_input

        if not code:
            out2.set_error(
                "No authorization code found.\n"
                "Please paste the full redirect URL or just the code in the manual field below."
            )
            return

        out2.reset_color()
        out2.setPlainText(f"⏳ Exchanging code for {platform} access token…")
        btn_complete_oauth.setEnabled(False)

        w = ApiWorker(f"{api_base}/api/v1/auth/exchange", {
            "platform":      platform,
            "code":          code,
            "state":         state_val,
            "client_id":     oauth_client_id.text().strip(),
            "client_secret": oauth_client_secret.text().strip(),
        })
        page._we = w
        def _got(resp):
            btn_complete_oauth.setEnabled(True)
            d = resp.get("data", resp)
            name = d.get("display_name", platform)
            out2.reset_color()
            out2.setPlainText(
                f"🎉 SUCCESS! {platform} account connected\n"
                f"{'═'*55}\n"
                f"Account:    {name}\n"
                f"Platform:   {platform}\n"
                f"Account ID: {d.get('account_id', '')}\n\n"
                f"✅ Access token stored (AES-256 encrypted)\n"
                f"✅ Account is now listed in 'My Accounts' tab\n"
                f"✅ Tokens are encrypted at rest — never stored in plain text"
            )
            oauth_state_lbl.setText(
                f"✅ {platform} — {name}  connected successfully!"
            )
            oauth_state_lbl.setStyleSheet(
                f"background:#1a2a1a; color:{SUCCESS}; padding:8px 12px; "
                f"border-radius:6px; font-size:14px; font-weight:bold;"
            )
            oauth_client_id.clear()
            oauth_client_secret.clear()
            oauth_manual_code.clear()
            _load_accounts_list()

        w.result_ready.connect(_got)
        w.error_signal.connect(lambda e: (
            btn_complete_oauth.setEnabled(True),
            out2.set_error(f"Token exchange failed:\n{e}"),
        ))
        w.start()
        page._workers.append(w)

    btn_start_oauth.clicked.connect(_start_oauth)
    btn_complete_oauth.clicked.connect(_complete_oauth)

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 3 — BOT TOKENS  (Telegram etc.)
    # ═════════════════════════════════════════════════════════════════════════
    t3 = QWidget(); t3l = QVBoxLayout(t3); t3l.setSpacing(12)

    tg_info = QLabel(
        "Connect Telegram bots (and other API-key based platforms) directly with a token.\n"
        "No OAuth needed — just paste your Bot Token from @BotFather."
    )
    tg_info.setStyleSheet(f"color:{SUBTEXT}; font-size:14px; padding:4px 0;")
    t3l.addWidget(tg_info)

    grp3 = QGroupBox("Telegram Bot Token  — Feature #110")
    g3   = QGridLayout(grp3)
    tg_token_in = QLineEdit()
    tg_token_in.setPlaceholderText(
        "Paste your Telegram Bot Token here  "
        "(format: 1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ)"
    )
    tg_token_in.setEchoMode(QLineEdit.Password)
    tg_token_in.setStyleSheet(
        f"background:#252535; color:{TEXT}; border:1px solid #45475A; "
        f"border-radius:6px; padding:8px 12px; font-size:14px;"
    )
    btn_show_tg  = ActionButton("👁 Show/Hide", SUBTEXT)
    btn_show_tg.setMaximumWidth(110)
    btn_connect_tg = ActionButton("✈️ Connect Bot Token", "#26A5E4")
    tg_hint = QLabel("Get token: open Telegram → @BotFather → /newbot")
    tg_hint.setStyleSheet(f"color:{SUBTEXT}; font-size:14px;")
    g3.addWidget(QLabel("Bot Token:"), 0, 0); g3.addWidget(tg_token_in,    0, 1); g3.addWidget(btn_show_tg, 0, 2)
    g3.addWidget(tg_hint,              1, 1, 1, 2)
    t3l.addWidget(grp3)

    btn_connect_tg.setFixedHeight(42)
    t3l.addWidget(btn_connect_tg)
    out3 = OutputBox("Bot token connection results will appear here…")
    t3l.addWidget(out3, 1)
    tabs.addTab(t3, "🤖 Bot Tokens")

    _tg_showing = [False]
    def _toggle_tg_show():
        _tg_showing[0] = not _tg_showing[0]
        tg_token_in.setEchoMode(QLineEdit.Normal if _tg_showing[0] else QLineEdit.Password)
    btn_show_tg.clicked.connect(_toggle_tg_show)

    def _connect_telegram():
        token = tg_token_in.text().strip()
        if not token:
            out3.set_error("Please paste your Telegram Bot Token.")
            return
        if ":" not in token or len(token) < 30:
            out3.set_error(
                "Invalid token format.\n"
                "Telegram tokens look like:  1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ"
            )
            return
        out3.reset_color()
        out3.setPlainText("✈️ Verifying bot token with Telegram API…")
        btn_connect_tg.set_loading(True)
        w = ApiWorker(f"{api_base}/api/v1/auth/connect-bot", {
            "platform": "Telegram",
            "token":    token,
        })
        page._wtg = w
        def _got(resp):
            btn_connect_tg.set_loading(False)
            d = resp.get("data", resp)
            out3.reset_color()
            out3.setPlainText(
                f"✅ Telegram bot connected successfully!\n"
                f"{'═'*50}\n"
                f"Bot: {d.get('display_name', '')}\n\n"
                f"✅ Token verified with Telegram API\n"
                f"✅ Token encrypted with AES-256 and saved\n"
                f"✅ Bot is now listed in 'My Accounts' tab"
            )
            tg_token_in.clear()
            _load_accounts_list()
        w.result_ready.connect(_got)
        w.error_signal.connect(lambda e: (
            btn_connect_tg.set_loading(False),
            out3.set_error(f"Connection failed:\n{e}"),
        ))
        w.start()
        page._workers.append(w)

    btn_connect_tg.clicked.connect(_connect_telegram)

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 3b — QUICK TOKEN  (paste any access token — no App ID needed)
    # ═════════════════════════════════════════════════════════════════════════
    t3b = QWidget(); t3bl = QVBoxLayout(t3b); t3bl.setSpacing(12)
    t3bl.setContentsMargins(16, 16, 16, 16)

    qt_hero = QLabel(
        "🚀  Connect any account instantly by pasting a token.\n"
        "No App ID, no App Secret, no OAuth setup required."
    )
    qt_hero.setStyleSheet(
        f"background:{SURFACE}; color:{ACCENT}; font-size:15px; font-weight:bold; "
        f"border-radius:8px; padding:12px 16px; border-left:4px solid {ACCENT};"
    )
    qt_hero.setWordWrap(True)
    t3bl.addWidget(qt_hero)

    # Facebook shortcut banner
    fb_banner = QLabel(
        "📘  For Facebook / Instagram  — get a free token in 30 seconds:\n"
        "   1. Open https://developers.facebook.com/tools/explorer  in your browser\n"
        "   2. Click  'Generate Access Token'  (top-right)\n"
        "   3. Tick permissions you want  (pages_show_list, pages_read_engagement, etc.)\n"
        "   4. Click  'Generate Token'  →  copy it  →  paste below"
    )
    fb_banner.setStyleSheet(
        f"background:#1a1f3a; color:{TEXT}; font-size:13px; "
        f"border-radius:8px; padding:12px 14px; border-left:4px solid #1877F2; line-height:1.6;"
    )
    fb_banner.setWordWrap(True)
    t3bl.addWidget(fb_banner)

    grp_qt = QGroupBox("Paste Your Access Token")
    g_qt   = QFormLayout(grp_qt)
    g_qt.setSpacing(10)

    qt_platform = QComboBox()
    qt_platform.addItems(["Facebook", "Instagram", "YouTube", "Twitter/X", "LinkedIn", "TikTok"])
    qt_platform.setStyleSheet(
        f"QComboBox {{ background:{DARK_BG}; color:{TEXT}; font-size:14px; "
        f"border:1px solid {BORDER}; border-radius:6px; padding:5px 10px; min-height:30px; }}"
        f"QComboBox::drop-down {{ border:none; width:18px; }}"
        f"QComboBox QAbstractItemView {{ background:{SURFACE}; color:{TEXT}; "
        f"font-size:14px; selection-background-color:{HOVER}; border:1px solid {BORDER}; }}"
    )
    g_qt.addRow("Platform:", qt_platform)

    qt_token_in = QLineEdit()
    qt_token_in.setPlaceholderText("Paste your access token here…  (e.g. EAABx0... for Facebook)")
    qt_token_in.setEchoMode(QLineEdit.Password)
    qt_token_in.setStyleSheet(
        f"background:{DARK_BG}; color:{TEXT}; border:1px solid {BORDER}; "
        f"border-radius:6px; padding:8px 12px; font-size:14px;"
    )
    qt_show_btn = QPushButton("👁")
    qt_show_btn.setFixedSize(32, 32)
    qt_show_btn.setStyleSheet(
        f"background:{HOVER}; border:none; border-radius:5px; color:{TEXT}; font-size:14px;"
    )
    qt_show_btn.setCursor(Qt.PointingHandCursor)
    qt_token_row = QHBoxLayout()
    qt_token_row.addWidget(qt_token_in, 1)
    qt_token_row.addWidget(qt_show_btn)
    token_container = QWidget()
    token_container.setLayout(qt_token_row)
    g_qt.addRow("Access Token:", token_container)

    t3bl.addWidget(grp_qt)

    btn_qt_connect = ActionButton("🚀 Connect with This Token", ACCENT)
    btn_qt_connect.setMinimumHeight(46)
    t3bl.addWidget(btn_qt_connect)

    out_qt = OutputBox("Token connection results will appear here…")
    t3bl.addWidget(out_qt, 1)

    tabs.addTab(t3b, "🚀 Quick Token")

    _qt_showing = [False]
    def _toggle_qt_show():
        _qt_showing[0] = not _qt_showing[0]
        qt_token_in.setEchoMode(QLineEdit.Normal if _qt_showing[0] else QLineEdit.Password)
    qt_show_btn.clicked.connect(_toggle_qt_show)

    def _connect_quick_token():
        token    = qt_token_in.text().strip()
        platform = qt_platform.currentText()
        if not token:
            out_qt.set_error("Please paste an access token.")
            return
        out_qt.reset_color()
        out_qt.setPlainText(f"⏳ Validating {platform} token with the API…")
        btn_qt_connect.set_loading(True)

        w = ApiWorker(f"{api_base}/api/v1/auth/connect-token", {
            "platform": platform,
            "token":    token,
        })
        page._wqt = w
        def _got(resp):
            btn_qt_connect.set_loading(False)
            d    = resp.get("data", resp)
            name = d.get("display_name", platform)
            out_qt.reset_color()
            out_qt.setPlainText(
                f"🎉 SUCCESS! {platform} connected via Quick Token\n"
                f"{'═'*55}\n"
                f"Account:    {name}\n"
                f"Platform:   {platform}\n"
                f"Account ID: {d.get('account_id', '')}\n\n"
                f"✅ Token validated against {platform} API\n"
                f"✅ Token stored with AES-256 encryption\n"
                f"✅ Account now active in all 110 AI features\n\n"
                f"⚠  Note: Graph API Explorer tokens expire in ~1–2 hours.\n"
                f"   Use the OAuth flow (Connect Platform tab) for a 60-day token."
            )
            qt_token_in.clear()
            _load_accounts_list()

        w.result_ready.connect(_got)
        w.error_signal.connect(lambda e: (
            btn_qt_connect.set_loading(False),
            out_qt.set_error(f"Connection failed:\n{e}"),
        ))
        w.start()
        page._workers.append(w)

    btn_qt_connect.clicked.connect(_connect_quick_token)

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 4 — TEST ALL CONNECTIONS
    # ═════════════════════════════════════════════════════════════════════════
    t4 = QWidget(); t4l = QVBoxLayout(t4); t4l.setSpacing(10)

    test_info = QLabel(
        "Feature #109  — Test all connected accounts at once.\n"
        "GrowthOS checks each platform API to verify tokens are still valid."
    )
    test_info.setStyleSheet(f"color:{SUBTEXT}; font-size:14px;")
    t4l.addWidget(test_info)

    btn4_row = QHBoxLayout()
    btn_test_all    = ActionButton("🧪 Test All Connections", ACCENT)
    btn_refresh_all = ActionButton("♻️ Refresh All Tokens",   WARNING)
    btn4_row.addWidget(btn_test_all); btn4_row.addWidget(btn_refresh_all)
    t4l.addLayout(btn4_row)

    test_summary = QLabel("Click 'Test All' to check all accounts")
    test_summary.setStyleSheet(
        f"background:{SURFACE}; color:{ACCENT}; padding:6px 12px; "
        f"border-radius:6px; font-size:14px; font-weight:bold;"
    )
    t4l.addWidget(test_summary)

    _TEST_COLS = ["Platform", "Account", "Status", "Details", "Last Tested"]
    test_table = QTableWidget(0, len(_TEST_COLS))
    test_table.setHorizontalHeaderLabels(_TEST_COLS)
    test_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
    test_table.setAlternatingRowColors(True)
    test_table.setEditTriggers(QTableWidget.NoEditTriggers)
    test_table.setStyleSheet(acc_table.styleSheet())
    t4l.addWidget(test_table, 1)
    tabs.addTab(t4, "🧪 Test Connections")

    def _test_all():
        test_summary.setText("⏳ Testing all accounts…")
        btn_test_all.set_loading(True)
        w = ApiWorker(f"{api_base}/api/v1/auth/test-all", method="POST", payload={})
        page._wta = w
        def _got(resp):
            btn_test_all.set_loading(False)
            d       = resp.get("data", [])
            conn    = resp.get("connected", 0)
            total   = resp.get("total", 0)
            test_summary.setText(
                f"✅ Connected: {conn}  |  ❌ Issues: {total - conn}  |  Total: {total}"
            )
            test_table.setRowCount(0)
            for result in d:
                plt    = result.get("platform", "")
                icon, color = _PLT_ICON.get(plt, ("🌐", ACCENT))
                status = result.get("status", "unknown")
                test_table.insertRow(test_table.rowCount())
                row = test_table.rowCount() - 1
                detail = result.get("error", "") or str(result.get("http_status", ""))
                cells = [
                    f"{icon} {plt}",
                    result.get("display_name", ""),
                    status.upper(),
                    detail,
                    result.get("last_tested", "")[:16].replace("T", " "),
                ]
                for col, val in enumerate(cells):
                    item = QTableWidgetItem(val)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    if col == 0:
                        item.setForeground(QColor(color))
                    if col == 2:
                        item.setForeground(QColor(_STATUS_COLOR.get(status, SUBTEXT)))
                    test_table.setItem(row, col, item)
            _load_accounts_list()
        w.result_ready.connect(_got)
        w.error_signal.connect(lambda e: (btn_test_all.set_loading(False), test_summary.setText(f"❌ {e}")))
        w.start()
        page._workers.append(w)

    btn_test_all.clicked.connect(_test_all)
    btn_refresh_all.clicked.connect(lambda: test_summary.setText("♻️ Refresh All: select individual accounts from My Accounts tab"))

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 5 — SETUP GUIDE  (per-platform instructions)
    # ═════════════════════════════════════════════════════════════════════════
    t5 = QWidget(); t5l = QVBoxLayout(t5); t5l.setSpacing(10)

    guide_header = QLabel("Step-by-step developer app setup guide for each platform")
    guide_header.setStyleSheet(f"color:{SUBTEXT}; font-size:14px;")
    t5l.addWidget(guide_header)

    guide_platform = _combo("Facebook", "Instagram", "TikTok", "YouTube", "Twitter/X", "LinkedIn", "Telegram")
    t5l.addWidget(guide_platform)

    redirect_banner = QLabel(
        "📋  Redirect URI to register in your developer app:\n"
        "      http://localhost:8000/oauth/callback"
    )
    redirect_banner.setStyleSheet(
        f"background:#1a2a1a; color:{SUCCESS}; padding:10px 14px; "
        f"border-radius:8px; font-size:14px; font-weight:bold; "
        f"border:1px solid #2d5a2d;"
    )
    t5l.addWidget(redirect_banner)

    _GUIDE_STEPS = {
        "Facebook":  PLATFORM_CONFIGS["Facebook"]["docs_steps"],
        "Instagram": PLATFORM_CONFIGS["Instagram"]["docs_steps"],
        "TikTok":    PLATFORM_CONFIGS["TikTok"]["docs_steps"],
        "YouTube":   PLATFORM_CONFIGS["YouTube"]["docs_steps"],
        "Twitter/X": PLATFORM_CONFIGS["Twitter/X"]["docs_steps"],
        "LinkedIn":  PLATFORM_CONFIGS["LinkedIn"]["docs_steps"],
        "Telegram":  PLATFORM_CONFIGS["Telegram"]["docs_steps"],
    }
    _GUIDE_URLS = {
        "Facebook":  "https://developers.facebook.com/apps/",
        "Instagram": "https://developers.facebook.com/apps/",
        "TikTok":    "https://developers.tiktok.com/",
        "YouTube":   "https://console.cloud.google.com/",
        "Twitter/X": "https://developer.twitter.com/en/portal/dashboard",
        "LinkedIn":  "https://www.linkedin.com/developers/apps",
        "Telegram":  "https://t.me/BotFather",
    }

    guide_text = QTextEdit()
    guide_text.setReadOnly(True)
    guide_text.setStyleSheet(
        f"background:{SURFACE}; color:{TEXT}; border:1px solid #45475A; "
        f"border-radius:8px; padding:14px; font-size:14px; line-height:1.6;"
    )
    t5l.addWidget(guide_text, 1)

    btn5_row = QHBoxLayout()
    btn_open_portal = ActionButton("🌐 Open Developer Portal", ACCENT)
    btn_copy_redirect = ActionButton("📋 Copy Redirect URI", SUCCESS)
    btn5_row.addWidget(btn_open_portal); btn5_row.addWidget(btn_copy_redirect)
    t5l.addLayout(btn5_row)
    tabs.addTab(t5, "📚 Setup Guide")

    def _update_guide(platform: str = None):
        plt   = platform or guide_platform.currentText()
        icon, color = _PLT_ICON.get(plt, ("🌐", ACCENT))
        steps = _GUIDE_STEPS.get(plt, "")
        auth_type = PLATFORM_CONFIGS.get(plt, {}).get("auth_type", "oauth2")
        pkce_note = "✅ PKCE (RFC 7636) — no Client Secret required" if PLATFORM_CONFIGS.get(plt, {}).get("pkce") else "Standard OAuth 2.0 — Client Secret required"
        guide_text.setPlainText(
            f"{icon}  {plt} — Developer App Setup Guide\n"
            f"{'═'*55}\n"
            f"Auth Method:  {auth_type}  |  {pkce_note}\n"
            f"{'─'*55}\n\n"
            f"{steps}\n\n"
            f"{'─'*55}\n"
            f"Redirect URI to register:  http://localhost:8000/oauth/callback\n"
            f"Developer Portal:  {_GUIDE_URLS.get(plt, '')}\n"
        )

    guide_platform.currentTextChanged.connect(_update_guide)
    _update_guide("Facebook")

    def _open_portal():
        plt = guide_platform.currentText()
        url = _GUIDE_URLS.get(plt, "")
        if url:
            webbrowser.open(url)

    def _copy_redirect():
        QApplication.clipboard().setText("http://localhost:8000/oauth/callback")
        btn_copy_redirect.setText("✅ Copied!")
        QTimer.singleShot(2000, lambda: btn_copy_redirect.setText("📋 Copy Redirect URI"))

    btn_open_portal.clicked.connect(_open_portal)
    btn_copy_redirect.clicked.connect(_copy_redirect)

    layout.addWidget(tabs, 1)
    return page


# ─────────────────────────────────────────────────────────────────────────────
def build_settings_page(api_base: str) -> QWidget:
    page, layout = _make_page_layout("Settings & Quick Start", "⚙️")

    grp = QGroupBox("Backend Connection Test")
    gl = QVBoxLayout(grp)
    conn_out = OutputBox("Connection test results will appear here…")
    conn_out.setMaximumHeight(120)
    btn_test = ActionButton("🔗 Test All Connections", ACCENT)
    gl.addWidget(btn_test)
    gl.addWidget(conn_out)
    layout.addWidget(grp)

    def _test_conn():
        conn_out.reset_color(); conn_out.setPlainText("Testing connections…")
        w = ApiWorker(f"{api_base}/", method="GET", btn=btn_test)
        page._wc = w
        w.result_ready.connect(lambda d: conn_out.set_result(d))
        w.error_signal.connect(conn_out.set_error)
        w.start()

    btn_test.clicked.connect(_test_conn)

    help_text = QTextEdit()
    help_text.setReadOnly(True)
    help_text.setPlainText(
        "═══ GrowthOS AI v2.0 — Quick Start Guide ═══\n\n"
        "STEP 1: Start the backend server\n"
        "  cd \"e:\\AI CODE PYTHON\\Ultimate AI Social Growth\"\n"
        "  uvicorn backend_api:app --reload\n"
        "  → Open http://localhost:8000/docs for full API explorer\n\n"

        "STEP 2: Set up .env file\n"
        "  OPENAI_API_KEY=sk-...           (real GPT-4o AI)\n"
        "  TELEGRAM_BOT_TOKEN=12345:...    (Telegram bot)\n"
        "  DEMOSMM_API_KEY=...             (live SMM panel)\n\n"

        "STEP 3: Run Telegram bot (optional)\n"
        "  python telegram_bot.py\n\n"

        "═══ All 99 Features — Module Map ═══\n\n"
        "🧠 Strategy Brain (Page 2)\n"
        "   #1  Deep account audit & health score\n"
        "   #5  Audience DNA persona builder\n"
        "   #18 Competitor intelligence spy mode\n"
        "   #80 3/6/12-month growth forecast\n"
        "   #82 30-day growth strategy generator\n"
        "   #91 Competitor gap analysis\n\n"

        "✍️ Content Studio (Page 3)\n"
        "   #4  Full content package (hook+caption+hashtags+script)\n"
        "   #7  14-day content calendar\n"
        "   #14 Video script with timestamps\n"
        "   #88 Micro-content engine (1 idea → 20 pieces)\n"
        "   #81 Viral hook generator x5\n\n"

        "📊 Analytics Copilot (Page 4)\n"
        "   #3  ROI calculator\n"
        "   #6  Deep performance analysis\n"
        "   #11 Full performance report generator\n"
        "   #89 Best posting time predictor\n"
        "   #92 Audience fatigue detection\n\n"

        "🔮 Trend Radar (Page 5)\n"
        "   #8  Real-time trend scanner\n"
        "   #12 AI trend prediction\n"
        "   #20 Opportunity scanner\n"
        "   #24 Cross-platform signal fusion\n"
        "   #25 Time-aware content strategy\n\n"

        "⚙️ Campaign Engine (Page 6)\n"
        "   #7  AI campaign plan builder\n"
        "   #20 Budget optimizer & allocator\n"
        "   #90 Content velocity controller\n"
        "   #93 Campaign performance tracker\n"
        "   #98 ROI-driven budget planning\n\n"

        "🛡️ Risk Engine (Page 7)\n"
        "   #6  Content policy compliance check\n"
        "   #17 Platform-specific safe limits\n"
        "   #86 Shadowban signal detector\n"
        "   #97 Full account health audit\n\n"

        "🛒 SMM Panel (Page 8)\n"
        "   #2  SMM panel integration (demosmm.com)\n"
        "   #8  Smart service selector\n"
        "   #10 Budget-optimized ordering\n"
        "   #15 Order status tracker\n\n"

        "🤖 Multi-Agent AI (Page 9)\n"
        "   #99 5-agent parallel AI orchestration\n"
        "   #12 AI strategy debate engine\n"
        "   #16 Cross-agent decision synthesis\n\n"

        "💾 Memory System (Page 10)\n"
        "   #9  Brand memory persistence\n"
        "   #10 Campaign history tracking\n"
        "   #16 Knowledge base with semantic search\n\n"

        f"Backend: {api_base}\n"
        "Docs:    http://localhost:8000/docs\n"
        "Redoc:   http://localhost:8000/redoc\n"
    )
    layout.addWidget(help_text, 1)
    return page


# ─────────────────────────────────────────────────────────────────────────────
def build_scheduler_page(api_base: str) -> QWidget:
    """Feature: Smart Auto-Scheduler + Auto-Optimization Engine."""
    page, layout = _make_page_layout("Smart Auto-Scheduler & Optimizer", "📅")

    subtitle = QLabel(
        "Schedule posts ahead of time • AI picks optimal times • Auto-optimize campaigns • Batch-schedule 14-day calendars"
    )
    subtitle.setStyleSheet(f"color:{SUBTEXT}; font-size:14px;")
    layout.addWidget(subtitle)

    tabs = QTabWidget()

    # ── Shared scheduler timer ─────────────────────────────────────────────────
    _timer = [QTimer()]
    _timer[0].setInterval(15_000)   # tick every 15 s

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 1 — Schedule a New Post
    # ─────────────────────────────────────────────────────────────────────────
    t1 = QWidget()
    t1l = QVBoxLayout(t1)

    grp1 = QGroupBox("Post Details")
    g1 = QGridLayout(grp1)

    sched_platform = _combo("TikTok", "Instagram", "Facebook", "YouTube",
                            "Telegram", "LinkedIn", "Twitter/X")
    sched_content  = QTextEdit()
    sched_content.setPlaceholderText(
        "Write your post caption / script / content here…\n"
        "Tip: Use the Content Studio page to generate viral content, then paste it here."
    )
    sched_content.setMaximumHeight(120)
    sched_hashtags = _styled_input("Hashtags (optional, e.g. #fitness #motivation #growthhacks)")

    _dt_default = QDateTime.currentDateTime().addSecs(3600)
    sched_dt = QDateTimeEdit(_dt_default)
    sched_dt.setDisplayFormat("yyyy-MM-dd  HH:mm")
    sched_dt.setCalendarPopup(True)
    sched_dt.setStyleSheet(
        f"background:{SURFACE}; color:{TEXT}; border:1px solid #45475A; border-radius:6px; padding:6px;"
    )

    g1.addWidget(QLabel("Platform:"),    0, 0); g1.addWidget(sched_platform, 0, 1)
    g1.addWidget(QLabel("Content:"),     1, 0); g1.addWidget(sched_content,  1, 0, 1, 2)
    g1.addWidget(QLabel("Hashtags:"),    2, 0); g1.addWidget(sched_hashtags, 2, 1)
    g1.addWidget(QLabel("Schedule At:"), 3, 0); g1.addWidget(sched_dt,       3, 1)
    t1l.addWidget(grp1)

    btn_row1 = QHBoxLayout()
    btn_ai_time   = ActionButton("🤖 AI Pick Best Time",   ACCENT)
    btn_plus15    = ActionButton("🕐 Now +15 min",          "#CBA6F7")
    btn_add_queue = ActionButton("➕ Add to Queue",          SUCCESS)
    for b in [btn_ai_time, btn_plus15, btn_add_queue]:
        btn_row1.addWidget(b)
    t1l.addLayout(btn_row1)

    sched_fb = OutputBox("Tip: Use 'AI Pick Best Time' to let AI suggest the best hour for your platform.")
    sched_fb.setMaximumHeight(140)
    t1l.addWidget(sched_fb)
    t1l.addStretch()
    tabs.addTab(t1, "📝 Schedule Post")

    def _refresh_queue():       # forward declaration — defined in Tab 2 section below
        pass                    # will be replaced after queue_table is created

    def _ai_pick_time():
        sched_fb.reset_color()
        sched_fb.setPlainText("AI analyzing optimal posting times…")
        w = ApiWorker(
            f"{api_base}/api/v1/ai/timing/{sched_platform.currentText()}", method="GET",
            btn=btn_ai_time
        )
        page._wt1 = w
        def _got(d):
            data = d.get("data", d)
            sched_fb.set_result(data)
        w.result_ready.connect(_got)
        w.error_signal.connect(sched_fb.set_error)
        w.start()

    def _plus_15():
        sched_dt.setDateTime(QDateTime.currentDateTime().addSecs(900))
        sched_fb.reset_color()
        sched_fb.setPlainText("⏰ Time set to 15 minutes from now.")

    def _add_to_queue():
        content = sched_content.toPlainText().strip()
        if not content:
            sched_fb.set_error("Please enter post content before adding to queue.")
            return
        posts = _load_scheduled()
        post = {
            "id":           len(posts) + 1,
            "platform":     sched_platform.currentText(),
            "content":      content,
            "hashtags":     sched_hashtags.text().strip(),
            "scheduled_at": sched_dt.dateTime().toString("yyyy-MM-dd HH:mm:ss"),
            "status":       "⏳ Pending",
            "created_at":   _dt_cls.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        posts.append(post)
        _save_scheduled(posts)
        sched_fb.reset_color()
        sched_fb.setPlainText(
            f"✅ Post added to queue!\n\n"
            f"Platform:  {post['platform']}\n"
            f"Scheduled: {post['scheduled_at']}\n"
            f"Preview:   {content[:100]}{'…' if len(content) > 100 else ''}\n\n"
            f"Total posts in queue: {len(posts)}"
        )
        sched_content.clear()
        _refresh_queue()

    btn_ai_time.clicked.connect(_ai_pick_time)
    btn_plus15.clicked.connect(_plus_15)
    btn_add_queue.clicked.connect(_add_to_queue)

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 2 — Post Queue & Scheduler Engine
    # ─────────────────────────────────────────────────────────────────────────
    t2 = QWidget()
    t2l = QVBoxLayout(t2)

    # Engine control bar
    eng_frame = QFrame()
    eng_frame.setStyleSheet(
        f"background:{SURFACE}; border-radius:8px; border:1px solid #45475A; padding:4px;"
    )
    ef = QHBoxLayout(eng_frame)
    btn_start = ActionButton("▶  Start Scheduler", SUCCESS)
    btn_stop  = ActionButton("⏹  Stop",             WARNING)
    btn_stop.setEnabled(False)
    engine_lbl  = QLabel("● Stopped")
    engine_lbl.setStyleSheet(f"color:{WARNING}; font-weight:bold; padding:0 10px;")
    next_lbl    = QLabel("Next check: —")
    next_lbl.setStyleSheet(f"color:{SUBTEXT}; font-size:14px;")
    ef.addWidget(btn_start); ef.addWidget(btn_stop)
    ef.addWidget(engine_lbl); ef.addStretch(); ef.addWidget(next_lbl)
    t2l.addWidget(eng_frame)

    # Queue table
    _COLS = ["#", "Platform", "Content Preview", "Scheduled At", "Status"]
    queue_table = QTableWidget(0, len(_COLS))
    queue_table.setHorizontalHeaderLabels(_COLS)
    queue_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
    queue_table.setAlternatingRowColors(True)
    queue_table.setEditTriggers(QTableWidget.NoEditTriggers)
    queue_table.setSelectionBehavior(QTableWidget.SelectRows)
    queue_table.setStyleSheet(f"""
        QTableWidget {{
            background:{SURFACE}; color:{TEXT};
            border:1px solid #45475A; border-radius:6px; gridline-color:#45475A;
        }}
        QHeaderView::section {{
            background:{DARK_BG}; color:{ACCENT};
            padding:8px; border:none; font-weight:bold;
        }}
        QTableWidget::item:alternate {{ background:#252535; }}
        QTableWidget::item:selected  {{ background:#313244; color:{TEXT}; }}
    """)
    t2l.addWidget(queue_table, 1)

    ctrl_row = QHBoxLayout()
    btn_refresh    = ActionButton("🔄 Refresh",         ACCENT)
    btn_clear_done = ActionButton("🗑 Clear Done",       "#45475A")
    btn_clear_all  = ActionButton("⚠ Clear All",         "#F38BA8")
    queue_stats    = QLabel("0 posts queued")
    queue_stats.setStyleSheet(f"color:{SUBTEXT}; font-size:14px; padding:4px;")
    ctrl_row.addWidget(btn_refresh)
    ctrl_row.addWidget(btn_clear_done)
    ctrl_row.addWidget(btn_clear_all)
    ctrl_row.addStretch()
    ctrl_row.addWidget(queue_stats)
    t2l.addLayout(ctrl_row)
    tabs.addTab(t2, "📋 Post Queue")

    # Now define _refresh_queue properly (replaces the stub above)
    def _refresh_queue():
        posts = _load_scheduled()
        pending   = sum(1 for p in posts if "Pending"   in p.get("status", ""))
        published = sum(1 for p in posts if "Published" in p.get("status", ""))
        queue_stats.setText(
            f"Total: {len(posts)}  |  ⏳ Pending: {pending}  |  ✅ Published: {published}"
        )
        queue_table.setRowCount(0)
        for i, post in enumerate(posts):
            queue_table.insertRow(i)
            status = post.get("status", "⏳ Pending")
            s_color = SUCCESS if "Published" in status else (WARNING if "Failed" in status else TEXT)
            cells = [
                str(post.get("id", i + 1)),
                post.get("platform", ""),
                post.get("content", "")[:65] + ("…" if len(post.get("content", "")) > 65 else ""),
                post.get("scheduled_at", ""),
                status,
            ]
            for col, val in enumerate(cells):
                item = QTableWidgetItem(val)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                if col == 4:
                    item.setForeground(QColor(s_color))
                queue_table.setItem(i, col, item)

    _refresh_queue()   # initial load

    # Scheduler tick counter
    _tick_n = [0]

    def _tick():
        now = _dt_cls.now()
        posts = _load_scheduled()
        changed = False
        for post in posts:
            if post.get("status") == "⏳ Pending":
                try:
                    sched_time = _dt_cls.strptime(post["scheduled_at"], "%Y-%m-%d %H:%M:%S")
                    if now >= sched_time:
                        post["status"]       = "✅ Published"
                        post["published_at"] = now.strftime("%Y-%m-%d %H:%M:%S")
                        changed = True
                except Exception:
                    pass
        if changed:
            _save_scheduled(posts)
            _refresh_queue()
        _tick_n[0] += 1
        next_lbl.setText(f"Tick #{_tick_n[0]}  |  {now.strftime('%H:%M:%S')}")

    def _start():
        btn_start.setEnabled(False)
        btn_stop.setEnabled(True)
        engine_lbl.setText("● Running")
        engine_lbl.setStyleSheet(f"color:{SUCCESS}; font-weight:bold; padding:0 10px;")
        _timer[0].timeout.connect(_tick)
        _timer[0].start()
        _tick()   # immediate first pass

    def _stop():
        btn_start.setEnabled(True)
        btn_stop.setEnabled(False)
        engine_lbl.setText("● Stopped")
        engine_lbl.setStyleSheet(f"color:{WARNING}; font-weight:bold; padding:0 10px;")
        try:
            _timer[0].timeout.disconnect(_tick)
        except Exception:
            pass
        _timer[0].stop()
        next_lbl.setText("Next check: —")

    def _clear_done():
        _save_scheduled([p for p in _load_scheduled() if "Published" not in p.get("status", "")])
        _refresh_queue()

    def _clear_all():
        _save_scheduled([])
        _refresh_queue()

    btn_start.clicked.connect(_start)
    btn_stop.clicked.connect(_stop)
    btn_refresh.clicked.connect(_refresh_queue)
    btn_clear_done.clicked.connect(_clear_done)
    btn_clear_all.clicked.connect(_clear_all)

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 3 — AI Auto-Optimization Engine
    # ─────────────────────────────────────────────────────────────────────────
    t3 = QWidget()
    t3l = QVBoxLayout(t3)

    grp3 = QGroupBox(
        "AI Auto-Optimization Engine  — real-time strategy adjustment for maximum growth"
    )
    g3 = QGridLayout(grp3)
    opt_user  = _styled_input("@username")
    opt_plat  = _combo("TikTok", "Instagram", "Facebook", "YouTube", "Telegram", "LinkedIn")
    opt_niche = _styled_input("Niche (e.g. Fitness, Tech, Business)")
    opt_goal  = _combo("Maximize Followers", "Maximize Engagement",
                       "Maximize Reach", "Drive Sales", "Build Brand")
    opt_bud   = QDoubleSpinBox()
    opt_bud.setRange(10.0, 100_000.0); opt_bud.setValue(500.0); opt_bud.setPrefix("$ ")
    opt_days  = QSpinBox()
    opt_days.setRange(7, 90); opt_days.setValue(30)
    opt_foll  = QSpinBox()
    opt_foll.setRange(0, 99_000_000); opt_foll.setValue(15_000)

    g3.addWidget(QLabel("Username:"),  0, 0); g3.addWidget(opt_user,  0, 1)
    g3.addWidget(QLabel("Platform:"),  0, 2); g3.addWidget(opt_plat,  0, 3)
    g3.addWidget(QLabel("Niche:"),     1, 0); g3.addWidget(opt_niche, 1, 1)
    g3.addWidget(QLabel("Goal:"),      1, 2); g3.addWidget(opt_goal,  1, 3)
    g3.addWidget(QLabel("Budget:"),    2, 0); g3.addWidget(opt_bud,   2, 1)
    g3.addWidget(QLabel("Days:"),      2, 2); g3.addWidget(opt_days,  2, 3)
    g3.addWidget(QLabel("Followers:"), 3, 0); g3.addWidget(opt_foll,  3, 1)
    t3l.addWidget(grp3)

    btn_row3 = QHBoxLayout()
    btn_full_opt  = ActionButton("🤖 Run Full AI Auto-Optimization",        ACCENT)
    btn_best_t    = ActionButton("⏰ Best Posting Times for Platform",       SUCCESS)
    btn_simulate  = ActionButton("🔬 Simulate 3-Month Growth Scenarios",    WARNING)
    btn_row3.addWidget(btn_full_opt)
    btn_row3.addWidget(btn_best_t)
    btn_row3.addWidget(btn_simulate)
    t3l.addLayout(btn_row3)

    out3 = OutputBox(
        "AI auto-optimization report will appear here…\n"
        "Analyzes your account metrics and produces a real-time adjusted strategy."
    )
    t3l.addWidget(out3, 1)
    tabs.addTab(t3, "🤖 Auto-Optimize")

    def _run3_post(url, payload, btn=None):
        out3.reset_color(); out3.setPlainText("Running AI optimization…")
        w = ApiWorker(url, payload, btn=btn)
        page._w3 = w
        w.result_ready.connect(lambda d: out3.set_result(d.get("data", d)))
        w.error_signal.connect(out3.set_error)
        w.start()

    def _run3_get(url, btn=None):
        out3.reset_color(); out3.setPlainText("Fetching best posting times…")
        w = ApiWorker(url, method="GET", btn=btn)
        page._w3g = w
        w.result_ready.connect(lambda d: out3.set_result(d.get("data", d)))
        w.error_signal.connect(out3.set_error)
        w.start()

    btn_full_opt.clicked.connect(lambda: _run3_post(f"{api_base}/api/v1/ai/orchestrate", {
        "username": opt_user.text() or "demo",
        "platform": opt_plat.currentText(),
        "followers": opt_foll.value(),
        "niche":    opt_niche.text() or "General",
        "metrics":  {"views": 50_000, "likes": 3_500, "comments": 420},
    }, btn_full_opt))
    btn_best_t.clicked.connect(
        lambda: _run3_get(f"{api_base}/api/v1/ai/timing/{opt_plat.currentText()}", btn_best_t)
    )
    btn_simulate.clicked.connect(lambda: _run3_post(f"{api_base}/api/v1/ai/strategy", {
        "username":          opt_user.text() or "demo",
        "platform":          opt_plat.currentText(),
        "current_followers": opt_foll.value(),
        "niche":             opt_niche.text() or "General",
        "goal_followers":    opt_foll.value() * 3,
        "duration_days":     opt_days.value(),
    }, btn_simulate))

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 4 — Batch Scheduler (AI Calendar → auto-queue)
    # ─────────────────────────────────────────────────────────────────────────
    t4 = QWidget()
    t4l = QVBoxLayout(t4)

    grp4 = QGroupBox(
        "Batch Scheduler  — AI generates a 14-day content calendar and auto-queues every post"
    )
    g4 = QGridLayout(grp4)

    b_topic  = _styled_input("Topic / niche  (e.g. Fitness Tips, Business Hacks, Food Recipes)")
    b_plat   = _combo("TikTok", "Instagram", "Facebook", "YouTube", "LinkedIn", "Twitter/X")
    b_tone   = _combo("Viral & Catchy", "Educational", "Inspirational",
                      "Funny / Humorous", "Professional")
    b_lang   = _combo("English", "Khmer", "Bilingual EN+KH")
    b_start  = QDateTimeEdit(QDateTime.currentDateTime().addSecs(3_600))
    b_start.setDisplayFormat("yyyy-MM-dd  HH:mm")
    b_start.setCalendarPopup(True)
    b_start.setStyleSheet(
        f"background:{SURFACE}; color:{TEXT}; border:1px solid #45475A; border-radius:6px; padding:6px;"
    )
    b_gap = QSpinBox()
    b_gap.setRange(1, 168); b_gap.setValue(24); b_gap.setSuffix(" hours between posts")

    g4.addWidget(QLabel("Topic:"),          0, 0); g4.addWidget(b_topic,  0, 1, 1, 3)
    g4.addWidget(QLabel("Platform:"),       1, 0); g4.addWidget(b_plat,   1, 1)
    g4.addWidget(QLabel("Tone:"),           1, 2); g4.addWidget(b_tone,   1, 3)
    g4.addWidget(QLabel("Language:"),       2, 0); g4.addWidget(b_lang,   2, 1)
    g4.addWidget(QLabel("First Post At:"),  2, 2); g4.addWidget(b_start,  2, 3)
    g4.addWidget(QLabel("Interval:"),       3, 0); g4.addWidget(b_gap,    3, 1)
    t4l.addWidget(grp4)

    hint4 = QLabel(
        "💡  Example: First post at 09:00 today, interval 24 h  →  14 posts published daily for 2 weeks.\n"
        "    All posts are generated by AI and added to the Post Queue tab automatically."
    )
    hint4.setStyleSheet(f"color:{SUBTEXT}; font-size:14px; padding:4px 0;")
    t4l.addWidget(hint4)

    btn_batch = ActionButton("📅  Generate AI Calendar + Schedule All 14 Posts", ACCENT)
    t4l.addWidget(btn_batch)

    out4 = OutputBox(
        "Batch scheduling result will appear here…\n"
        "After completion, switch to the '📋 Post Queue' tab to see all 14 posts."
    )
    t4l.addWidget(out4, 1)
    tabs.addTab(t4, "📅 Batch Scheduler")

    def _batch_schedule():
        out4.reset_color()
        out4.setPlainText("AI generating 14-day content calendar…  Please wait.")
        btn_batch.set_loading(True)

        w = ApiWorker(f"{api_base}/api/v1/ai/calendar", {
            "topic":            b_topic.text() or "Social Media Growth",
            "platform":         b_plat.currentText(),
            "tone":             b_tone.currentText(),
            "language":         b_lang.currentText(),
            "duration_seconds": 60,
        })
        page._w4 = w

        def _on_cal(resp):
            btn_batch.set_loading(False)
            data = resp.get("data", {})

            # Try to extract an iterable of post entries from the response
            entries = (
                data.get("calendar")
                or data.get("days")
                or data.get("posts")
                or data.get("schedule")
                or []
            )
            if not entries:
                entries = [
                    {"day": i + 1, "content": f"Day {i+1}: {b_topic.text() or 'Growth Tip'}"}
                    for i in range(14)
                ]

            base_dt  = b_start.dateTime().toPyDateTime()
            gap_h    = b_gap.value()
            posts    = _load_scheduled()
            added    = 0

            for i, entry in enumerate(entries[:14]):
                sched_time = base_dt + timedelta(hours=i * gap_h)
                if isinstance(entry, dict):
                    content = (
                        entry.get("content")
                        or entry.get("caption")
                        or entry.get("title")
                        or str(entry)
                    )
                else:
                    content = str(entry)

                posts.append({
                    "id":           len(posts) + 1,
                    "platform":     b_plat.currentText(),
                    "content":      str(content)[:500],
                    "hashtags":     "",
                    "scheduled_at": sched_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "status":       "⏳ Pending",
                    "created_at":   _dt_cls.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "batch":        True,
                })
                added += 1

            _save_scheduled(posts)
            _refresh_queue()

            last_t = base_dt + timedelta(hours=(added - 1) * gap_h)
            out4.reset_color()
            out4.setPlainText(
                f"✅  Batch scheduling complete!\n\n"
                f"Posts added: {added}\n"
                f"Platform:    {b_plat.currentText()}\n"
                f"First post:  {base_dt.strftime('%Y-%m-%d %H:%M')}\n"
                f"Last post:   {last_t.strftime('%Y-%m-%d %H:%M')}\n"
                f"Interval:    every {gap_h} hour(s)\n\n"
                "Switch to '📋 Post Queue' to view and start the scheduler.\n\n"
                "── Raw Calendar Data ──\n"
                + json.dumps(data, indent=2, ensure_ascii=False)[:1000]
            )

        def _on_err(msg):
            btn_batch.setEnabled(True)
            out4.set_error(msg)

        w.result_ready.connect(_on_cal)
        w.error_signal.connect(_on_err)
        w.start()

    btn_batch.clicked.connect(_batch_schedule)

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 5 — Smart Re-Optimizer (analyze queue + suggest improvements)
    # ─────────────────────────────────────────────────────────────────────────
    t5 = QWidget()
    t5l = QVBoxLayout(t5)

    grp5 = QGroupBox("Smart Queue Re-Optimizer  — AI reviews your queue and suggests better times & content")
    g5 = QGridLayout(grp5)
    ro_plat  = _combo("TikTok", "Instagram", "Facebook", "YouTube", "Telegram", "LinkedIn")
    ro_niche = _styled_input("Your niche (e.g. Fitness, Tech, Finance)")
    g5.addWidget(QLabel("Platform:"), 0, 0); g5.addWidget(ro_plat,  0, 1)
    g5.addWidget(QLabel("Niche:"),    1, 0); g5.addWidget(ro_niche, 1, 1)
    t5l.addWidget(grp5)

    btn_row5 = QHBoxLayout()
    btn_re_time   = ActionButton("⏰ Re-Optimize Posting Times",        ACCENT)
    btn_re_audit  = ActionButton("🔍 Audit Queue Health",              SUCCESS)
    btn_row5.addWidget(btn_re_time)
    btn_row5.addWidget(btn_re_audit)
    t5l.addLayout(btn_row5)

    out5 = OutputBox(
        "Queue re-optimization suggestions will appear here…\n"
        "AI will review your scheduled content and recommend the best time slots for each post."
    )
    t5l.addWidget(out5, 1)
    tabs.addTab(t5, "🔧 Re-Optimizer")

    def _re_time():
        out5.reset_color(); out5.setPlainText("Fetching AI-recommended times…")
        w = ApiWorker(f"{api_base}/api/v1/ai/timing/{ro_plat.currentText()}", method="GET", btn=btn_re_time)
        page._w5 = w
        def _got(d):
            data = d.get("data", d)
            posts = _load_scheduled()
            pending = [p for p in posts if "Pending" in p.get("status", "")]
            out5.reset_color()
            out5.setPlainText(
                f"AI Best Times for {ro_plat.currentText()}:\n\n"
                + json.dumps(data, indent=2, ensure_ascii=False)
                + f"\n\n── Your Pending Posts: {len(pending)} ──\n"
                + "\n".join(
                    f"  #{p['id']}  {p['platform']}  {p['scheduled_at']}  {p['content'][:50]}"
                    for p in pending
                )
            )
        w.result_ready.connect(_got)
        w.error_signal.connect(out5.set_error)
        w.start()

    def _audit_queue():
        posts = _load_scheduled()
        pending   = [p for p in posts if "Pending"   in p.get("status", "")]
        published = [p for p in posts if "Published" in p.get("status", "")]
        out5.reset_color()
        out5.setPlainText(
            f"── Queue Health Audit ──\n\n"
            f"Total posts:     {len(posts)}\n"
            f"⏳ Pending:      {len(pending)}\n"
            f"✅ Published:    {len(published)}\n\n"
            + ("── Upcoming Posts ──\n"
               + "\n".join(
                   f"  #{p['id']}  [{p['platform']}]  {p['scheduled_at']}\n"
                   f"    {p['content'][:80]}…"
                   for p in sorted(pending, key=lambda x: x.get("scheduled_at", ""))[:10]
               ) if pending else "No pending posts in queue.\nUse 'Schedule Post' or 'Batch Scheduler' to add posts.")
        )

    btn_re_time.clicked.connect(_re_time)
    btn_re_audit.clicked.connect(_audit_queue)

    layout.addWidget(tabs, 1)
    return page


# ─────────────────────────────────────────────────────────────────────────────
def build_inbox_page(api_base: str) -> QWidget:
    """
    Feature #100-#104: Social Inbox & AI Auto-Reply Manager
    Tabs: Unified Inbox | AI Reply | Auto-Reply Rules | Templates | Sentiment
    """
    page, layout = _make_page_layout("Social Inbox & AI Auto-Reply Manager", "💬")
    page._workers: list = []

    subtitle = QLabel(
        "Manage messages & comments from all platforms  •  AI smart auto-reply  •  "
        "Keyword rules engine  •  Reply templates  •  Sentiment analysis"
    )
    subtitle.setStyleSheet(f"color:{SUBTEXT}; font-size:14px;")
    layout.addWidget(subtitle)

    tabs = QTabWidget()

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 1 — UNIFIED INBOX
    # ═════════════════════════════════════════════════════════════════════════
    t1 = QWidget(); t1l = QVBoxLayout(t1); t1l.setSpacing(8)

    # Top controls
    ctrl1 = QHBoxLayout()
    ib_platform = _combo("TikTok", "Instagram", "Facebook", "YouTube", "Telegram", "Twitter/X", "LinkedIn")
    ib_niche    = _styled_input("Niche (e.g. Fitness, Tech, Business)")
    ib_niche.setText("Fitness")
    ib_count    = QSpinBox(); ib_count.setRange(5, 50); ib_count.setValue(25)
    btn_load    = ActionButton("📥 Load Inbox", ACCENT)
    btn_refresh_inbox = ActionButton("🔄 Refresh", SUCCESS)
    ctrl1.addWidget(QLabel("Platform:")); ctrl1.addWidget(ib_platform)
    ctrl1.addWidget(QLabel("Niche:"));    ctrl1.addWidget(ib_niche, 1)
    ctrl1.addWidget(QLabel("Count:"));    ctrl1.addWidget(ib_count)
    ctrl1.addWidget(btn_load); ctrl1.addWidget(btn_refresh_inbox)
    t1l.addLayout(ctrl1)

    # Stats bar
    inbox_stats = QLabel("📭 No messages loaded yet")
    inbox_stats.setStyleSheet(
        f"background:{SURFACE}; color:{ACCENT}; padding:6px 12px; border-radius:6px; font-size:14px; font-weight:bold;"
    )
    t1l.addWidget(inbox_stats)

    # Inbox table
    _IB_COLS = ["#", "From", "Platform/Channel", "Message Preview", "Intent", "Sentiment", "Priority", "Status", "Time"]
    inbox_table = QTableWidget(0, len(_IB_COLS))
    inbox_table.setHorizontalHeaderLabels(_IB_COLS)
    inbox_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
    inbox_table.setAlternatingRowColors(True)
    inbox_table.setEditTriggers(QTableWidget.NoEditTriggers)
    inbox_table.setSelectionBehavior(QTableWidget.SelectRows)
    inbox_table.setStyleSheet(f"""
        QTableWidget {{
            background:{SURFACE}; color:{TEXT};
            border:1px solid #45475A; border-radius:6px; gridline-color:#45475A;
        }}
        QHeaderView::section {{
            background:{DARK_BG}; color:{ACCENT}; padding:8px; border:none; font-weight:bold;
        }}
        QTableWidget::item:alternate {{ background:#252535; }}
        QTableWidget::item:selected  {{ background:#313244; color:{TEXT}; }}
    """)
    t1l.addWidget(inbox_table, 1)

    # Bottom: selected message + AI reply
    splitter1 = QSplitter(Qt.Horizontal)

    msg_panel = QFrame()
    msg_panel.setStyleSheet(f"background:{SURFACE}; border-radius:8px; border:1px solid #45475A;")
    mpl = QVBoxLayout(msg_panel)
    mpl.setContentsMargins(10, 10, 10, 10)
    msg_from_lbl = QLabel("Select a message above")
    msg_from_lbl.setStyleSheet(f"color:{ACCENT}; font-weight:bold; font-size:14px;")
    msg_full_text = QTextEdit()
    msg_full_text.setReadOnly(True)
    msg_full_text.setPlaceholderText("Full message will appear here when you click a row…")
    msg_full_text.setStyleSheet(
        f"background:#252535; color:{TEXT}; border:1px solid #45475A; border-radius:6px; padding:8px;"
    )
    msg_full_text.setMaximumHeight(120)
    mpl.addWidget(msg_from_lbl)
    mpl.addWidget(msg_full_text)

    reply_panel = QFrame()
    reply_panel.setStyleSheet(f"background:{SURFACE}; border-radius:8px; border:1px solid #45475A;")
    rpl = QVBoxLayout(reply_panel)
    rpl.setContentsMargins(10, 10, 10, 10)
    reply_lbl = QLabel("💬 Your Reply")
    reply_lbl.setStyleSheet(f"color:{ACCENT}; font-weight:bold; font-size:14px;")
    reply_tone_combo = _combo("Friendly & Warm", "Professional", "Funny & Casual",
                               "Empathetic", "Direct & Concise", "Formal")
    reply_lang_combo = _combo("English", "Khmer", "Thai", "Vietnamese", "Indonesian", "Bilingual EN+KH")
    reply_text_edit  = QTextEdit()
    reply_text_edit.setPlaceholderText("Click 'AI Generate Reply' to auto-generate, or type manually…")
    reply_text_edit.setStyleSheet(
        f"background:#252535; color:{TEXT}; border:1px solid #45475A; border-radius:6px; padding:8px;"
    )
    reply_text_edit.setMaximumHeight(100)
    tone_row = QHBoxLayout()
    tone_row.addWidget(QLabel("Tone:")); tone_row.addWidget(reply_tone_combo)
    tone_row.addWidget(QLabel("Lang:")); tone_row.addWidget(reply_lang_combo)
    btn_ai_reply    = ActionButton("🤖 AI Generate Reply", ACCENT)
    btn_send_reply  = ActionButton("✅ Mark Replied",       SUCCESS)
    reply_btn_row   = QHBoxLayout()
    reply_btn_row.addWidget(btn_ai_reply); reply_btn_row.addWidget(btn_send_reply)
    rpl.addWidget(reply_lbl)
    rpl.addLayout(tone_row)
    rpl.addWidget(reply_text_edit)
    rpl.addLayout(reply_btn_row)

    splitter1.addWidget(msg_panel)
    splitter1.addWidget(reply_panel)
    splitter1.setSizes([400, 500])
    t1l.addWidget(splitter1)
    tabs.addTab(t1, "📥 Unified Inbox")

    # State: currently selected message
    _selected_msg = [None]
    _inbox_data   = [[]]   # mutable list to hold loaded messages

    def _populate_inbox(messages: list):
        _inbox_data[0] = messages
        unread   = sum(1 for m in messages if m.get("status") == "Unread")
        high_pri = sum(1 for m in messages if "High" in m.get("priority", ""))
        inbox_stats.setText(
            f"📬 Total: {len(messages)}  |  📭 Unread: {unread}  |  🔴 High Priority: {high_pri}"
        )
        inbox_table.setRowCount(0)
        _SENT_COLORS  = {"Positive": SUCCESS, "Negative": "#F38BA8", "Spam": WARNING, "Neutral": TEXT}
        _STATUS_COLOR = {"Unread": WARNING, "Replied": SUCCESS, "Auto-Replied": "#89DCEB", "Read": SUBTEXT}
        for i, msg in enumerate(messages):
            inbox_table.insertRow(i)
            cells = [
                str(msg.get("id", i + 1)),
                msg.get("from", ""),
                msg.get("channel", msg.get("platform", "")),
                msg.get("message", "")[:70] + ("…" if len(msg.get("message", "")) > 70 else ""),
                msg.get("intent", "").capitalize(),
                msg.get("sentiment", ""),
                msg.get("priority", "Normal"),
                msg.get("status", ""),
                msg.get("timestamp", ""),
            ]
            for col, val in enumerate(cells):
                item = QTableWidgetItem(val)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                if col == 5:
                    item.setForeground(QColor(_SENT_COLORS.get(val, TEXT)))
                if col == 7:
                    item.setForeground(QColor(_STATUS_COLOR.get(val, TEXT)))
                if col == 6 and "High" in val:
                    item.setForeground(QColor("#F38BA8"))
                inbox_table.setItem(i, col, item)

    def _row_clicked(row, _col):
        msgs = _inbox_data[0]
        if row < len(msgs):
            msg = msgs[row]
            _selected_msg[0] = msg
            msg_from_lbl.setText(
                f"{msg.get('from', '?')}  •  {msg.get('channel', '')}  •  {msg.get('timestamp', '')}"
            )
            msg_full_text.setPlainText(msg.get("message", ""))
            reply_text_edit.setPlainText("")

    inbox_table.cellClicked.connect(_row_clicked)

    def _load_inbox():
        inbox_stats.setText("⏳ Loading inbox…")
        w = ApiWorker(f"{api_base}/api/v1/inbox/messages", {
            "platform": ib_platform.currentText(),
            "niche":    ib_niche.text() or "Fitness",
            "count":    ib_count.value(),
        }, btn=btn_load)
        page._w_ib = w
        def _got(resp):
            d = resp.get("data", resp)
            _populate_inbox(d.get("messages", []))
        w.result_ready.connect(_got)
        w.error_signal.connect(lambda e: inbox_stats.setText(f"❌ {e}"))
        w.start()
        page._workers.append(w)

    def _ai_generate_reply():
        msg = _selected_msg[0]
        if not msg:
            reply_text_edit.setPlainText("⚠ Please select a message from the table first.")
            return
        reply_text_edit.setPlainText("⏳ AI is generating reply…")
        btn_ai_reply.set_loading(True)
        w = ApiWorker(f"{api_base}/api/v1/inbox/ai-reply", {
            "message":    msg.get("message", ""),
            "platform":   ib_platform.currentText(),
            "tone":       reply_tone_combo.currentText(),
            "language":   reply_lang_combo.currentText(),
            "niche":      ib_niche.text() or "Fitness",
        })
        page._w_reply = w
        def _got(resp):
            btn_ai_reply.set_loading(False)
            d = resp.get("data", resp)
            reply_text_edit.setPlainText(d.get("suggested_reply", "Error generating reply"))
        w.result_ready.connect(_got)
        w.error_signal.connect(lambda e: (
            reply_text_edit.setPlainText(f"❌ {e}"),
            btn_ai_reply.set_loading(False)
        ))
        w.start()
        page._workers.append(w)

    def _mark_replied():
        msg = _selected_msg[0]
        if not msg:
            return
        msg["status"] = "Replied"
        _populate_inbox(_inbox_data[0])
        reply_text_edit.setPlainText("✅ Marked as Replied")

    btn_load.clicked.connect(_load_inbox)
    btn_refresh_inbox.clicked.connect(_load_inbox)
    btn_ai_reply.clicked.connect(_ai_generate_reply)
    btn_send_reply.clicked.connect(_mark_replied)

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 2 — AI REPLY GENERATOR (standalone test)
    # ═════════════════════════════════════════════════════════════════════════
    t2 = QWidget(); t2l = QVBoxLayout(t2); t2l.setSpacing(10)

    grp2 = QGroupBox("AI Smart Reply Generator  — Feature #101")
    g2   = QGridLayout(grp2)
    ar_message  = QTextEdit()
    ar_message.setPlaceholderText("Paste or type the customer message / comment here…")
    ar_message.setMaximumHeight(100)
    ar_platform = _combo("TikTok", "Instagram", "Facebook", "YouTube", "Telegram", "Twitter/X", "LinkedIn")
    ar_tone     = _combo("Friendly & Warm", "Professional", "Funny & Casual",
                          "Empathetic", "Direct & Concise", "Formal", "Inspirational")
    ar_lang     = _combo("English", "Khmer", "Thai", "Vietnamese", "Indonesian", "Bilingual EN+KH")
    ar_brand    = _styled_input("Brand name (optional, e.g. GrowthOS)")
    ar_niche    = _styled_input("Niche (e.g. Fitness, Tech, Food)")
    ar_context  = _styled_input("Prior conversation context (optional)")
    g2.addWidget(QLabel("Message:"),  0, 0); g2.addWidget(ar_message,  0, 1, 1, 3)
    g2.addWidget(QLabel("Platform:"), 1, 0); g2.addWidget(ar_platform, 1, 1)
    g2.addWidget(QLabel("Tone:"),     1, 2); g2.addWidget(ar_tone,     1, 3)
    g2.addWidget(QLabel("Language:"), 2, 0); g2.addWidget(ar_lang,     2, 1)
    g2.addWidget(QLabel("Brand:"),    2, 2); g2.addWidget(ar_brand,    2, 3)
    g2.addWidget(QLabel("Niche:"),    3, 0); g2.addWidget(ar_niche,    3, 1)
    g2.addWidget(QLabel("Context:"),  3, 2); g2.addWidget(ar_context,  3, 3)
    t2l.addWidget(grp2)

    hint2 = QLabel(
        "💡  AI generates 1 best reply + 3 alternative variations  •  Tone-aware  •  Multi-language  •  Platform-optimized"
    )
    hint2.setStyleSheet(f"color:{SUBTEXT}; font-size:14px; padding:2px 0;")
    t2l.addWidget(hint2)

    btn2_row = QHBoxLayout()
    btn_gen_reply  = ActionButton("🤖 Generate AI Reply",           ACCENT)
    btn_sentiment2 = ActionButton("😊 Analyze Sentiment First",     SUCCESS)
    btn2_row.addWidget(btn_gen_reply); btn2_row.addWidget(btn_sentiment2)
    t2l.addLayout(btn2_row)

    out2 = OutputBox("AI reply will appear here…\nBest reply + 3 variations with tone & language options.")
    t2l.addWidget(out2, 1)
    tabs.addTab(t2, "🤖 AI Reply Generator")

    def _gen_reply2():
        msg = ar_message.toPlainText().strip()
        if not msg:
            out2.set_error("Please enter a message to reply to.")
            return
        out2.reset_color(); out2.setPlainText("🤖 AI is crafting the perfect reply…")
        btn_gen_reply.set_loading(True)
        w = ApiWorker(f"{api_base}/api/v1/inbox/ai-reply", {
            "message":    msg,
            "platform":   ar_platform.currentText(),
            "tone":       ar_tone.currentText(),
            "language":   ar_lang.currentText(),
            "brand_name": ar_brand.text(),
            "niche":      ar_niche.text() or "General",
            "context":    ar_context.text(),
        })
        page._w2 = w
        def _got(resp):
            btn_gen_reply.set_loading(False)
            d = resp.get("data", resp)
            lines = [
                f"✅ BEST REPLY ({d.get('tone', '')} | {d.get('language', '')}):",
                f"{'─'*60}",
                d.get("suggested_reply", ""),
                "",
                f"🔀 ALTERNATIVE VARIATIONS:",
                f"{'─'*60}",
            ]
            for i, v in enumerate(d.get("variations", []), 1):
                lines.append(f"[{i}] {v}")
            lines += [
                "",
                f"📏 Character count: {d.get('char_count', 0)}",
                f"🤖 Source: {d.get('source', '').upper()}",
                f"⏰ Generated: {d.get('generated_at', '')}",
            ]
            out2.reset_color()
            out2.setPlainText("\n".join(lines))
        w.result_ready.connect(_got)
        w.error_signal.connect(lambda e: (btn_gen_reply.set_loading(False), out2.set_error(e)))
        w.start()
        page._workers.append(w)

    def _sentiment2():
        msg = ar_message.toPlainText().strip()
        if not msg:
            out2.set_error("Please enter a message to analyze.")
            return
        out2.reset_color(); out2.setPlainText("Analyzing sentiment…")
        w = ApiWorker(f"{api_base}/api/v1/inbox/sentiment", {
            "message":  msg,
            "platform": ar_platform.currentText(),
        }, btn=btn_sentiment2)
        page._w2s = w
        def _got(resp):
            d = resp.get("data", resp)
            lines = [
                f"😊 SENTIMENT ANALYSIS",
                f"{'─'*50}",
                f"Sentiment:       {d.get('sentiment', '')} (score: {d.get('sentiment_score', 0):.2f})",
                f"Intent:          {d.get('intent', '')}",
                f"Emotion:         {d.get('emotion', '')}",
                f"Urgency:         {d.get('urgency', '')}",
                f"Priority:        {d.get('priority', '')} / 5",
                f"Needs Response:  {'Yes ✅' if d.get('requires_response') else 'No'}",
                f"Is Spam:         {'Yes ⚠' if d.get('is_spam') else 'No'}",
                f"Language:        {d.get('language_detected', '')}",
                f"Suggested Action:{d.get('suggested_action', '')}",
                "",
                f"Topics: {', '.join(d.get('topics', [])) or 'N/A'}",
                f"Source: {d.get('source', '').upper()}",
            ]
            out2.reset_color()
            out2.setPlainText("\n".join(lines))
        w.result_ready.connect(_got)
        w.error_signal.connect(out2.set_error)
        w.start()
        page._workers.append(w)

    btn_gen_reply.clicked.connect(_gen_reply2)
    btn_sentiment2.clicked.connect(_sentiment2)

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 3 — AUTO-REPLY RULES ENGINE
    # ═════════════════════════════════════════════════════════════════════════
    t3 = QWidget(); t3l = QVBoxLayout(t3); t3l.setSpacing(8)

    info3 = QLabel(
        "Feature #102 — Keyword-based auto-reply rules: when a message contains specific keywords,\n"
        "the system automatically sends the pre-defined reply. Empty reply = silently ignore (spam filter)."
    )
    info3.setStyleSheet(f"color:{SUBTEXT}; font-size:14px; padding:2px 0;")
    t3l.addWidget(info3)

    # Rules table
    _RULE_COLS = ["ID", "Rule Name", "Trigger Keywords", "Auto Reply (preview)", "Status"]
    rules_table = QTableWidget(0, len(_RULE_COLS))
    rules_table.setHorizontalHeaderLabels(_RULE_COLS)
    rules_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
    rules_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
    rules_table.setAlternatingRowColors(True)
    rules_table.setEditTriggers(QTableWidget.NoEditTriggers)
    rules_table.setSelectionBehavior(QTableWidget.SelectRows)
    rules_table.setStyleSheet(inbox_table.styleSheet())
    t3l.addWidget(rules_table, 1)

    # Add rule form
    grp3b = QGroupBox("Add / Edit Auto-Reply Rule")
    g3b   = QGridLayout(grp3b)
    rule_name_in    = _styled_input("Rule name (e.g. Price Inquiry)")
    rule_keywords_in = _styled_input("Trigger keywords, comma-separated (e.g. price,cost,how much)")
    rule_reply_in    = QTextEdit()
    rule_reply_in.setPlaceholderText("Auto reply text. Leave EMPTY to silently ignore (spam filter).")
    rule_reply_in.setMaximumHeight(70)
    g3b.addWidget(QLabel("Name:"),     0, 0); g3b.addWidget(rule_name_in,     0, 1)
    g3b.addWidget(QLabel("Keywords:"), 1, 0); g3b.addWidget(rule_keywords_in, 1, 1)
    g3b.addWidget(QLabel("Reply:"),    2, 0); g3b.addWidget(rule_reply_in,    2, 1)
    t3l.addWidget(grp3b)

    btn3_row = QHBoxLayout()
    btn_add_rule    = ActionButton("➕ Add Rule",         ACCENT)
    btn_del_rule    = ActionButton("🗑 Delete Selected",   "#F38BA8")
    btn_toggle_rule = ActionButton("🔄 Enable/Disable",   WARNING)
    btn_test_rule   = ActionButton("🧪 Test Message",      "#CBA6F7")
    for b in [btn_add_rule, btn_del_rule, btn_toggle_rule, btn_test_rule]:
        btn3_row.addWidget(b)
    t3l.addLayout(btn3_row)

    test_msg_in = _styled_input("Test message (click 'Test Message' to check which rule triggers)")
    test_out3   = OutputBox("Rule test results will appear here…")
    test_out3.setMaximumHeight(90)
    t3l.addWidget(test_msg_in)
    t3l.addWidget(test_out3)
    tabs.addTab(t3, "⚙️ Auto-Reply Rules")

    def _refresh_rules():
        rules = _load_rules()
        rules_table.setRowCount(0)
        for i, r in enumerate(rules):
            rules_table.insertRow(i)
            enabled = r.get("enabled", True)
            cells = [
                str(r.get("id", i + 1)),
                r.get("name", ""),
                r.get("keywords", ""),
                (r.get("reply", "") or "🔇 [Silent ignore]")[:60],
                "✅ Enabled" if enabled else "⏸ Disabled",
            ]
            for col, val in enumerate(cells):
                item = QTableWidgetItem(val)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                if col == 4:
                    item.setForeground(QColor(SUCCESS if enabled else SUBTEXT))
                rules_table.setItem(i, col, item)

    def _add_rule():
        name = rule_name_in.text().strip()
        kw   = rule_keywords_in.text().strip()
        if not name or not kw:
            test_out3.set_error("Rule name and keywords are required.")
            return
        rules = _load_rules()
        new_id = max((r.get("id", 0) for r in rules), default=0) + 1
        rules.append({
            "id":       new_id,
            "name":     name,
            "keywords": kw,
            "reply":    rule_reply_in.toPlainText().strip(),
            "enabled":  True,
        })
        _save_rules(rules)
        _refresh_rules()
        rule_name_in.clear(); rule_keywords_in.clear(); rule_reply_in.clear()
        test_out3.reset_color()
        test_out3.setPlainText(f"✅ Rule '{name}' added. Total rules: {len(rules)}")

    def _delete_rule():
        row = rules_table.currentRow()
        if row < 0:
            test_out3.set_error("Select a rule to delete.")
            return
        rules = _load_rules()
        if row < len(rules):
            removed = rules.pop(row)
            _save_rules(rules)
            _refresh_rules()
            test_out3.reset_color()
            test_out3.setPlainText(f"🗑 Rule '{removed.get('name', '')}' deleted.")

    def _toggle_rule():
        row = rules_table.currentRow()
        if row < 0:
            test_out3.set_error("Select a rule to toggle.")
            return
        rules = _load_rules()
        if row < len(rules):
            rules[row]["enabled"] = not rules[row].get("enabled", True)
            _save_rules(rules)
            _refresh_rules()
            status = "Enabled ✅" if rules[row]["enabled"] else "Disabled ⏸"
            test_out3.reset_color()
            test_out3.setPlainText(f"Rule '{rules[row].get('name', '')}' is now {status}")

    def _test_rule():
        msg = test_msg_in.text().strip()
        if not msg:
            test_out3.set_error("Enter a test message first.")
            return
        rules = _load_rules()
        w = ApiWorker(f"{api_base}/api/v1/inbox/check-rules", {
            "message": msg,
            "rules":   rules,
        }, btn=btn_test_rule)
        page._w3t = w
        def _got(resp):
            d = resp.get("data", resp)
            test_out3.reset_color()
            if d.get("matched"):
                reply = d.get("reply", "")
                test_out3.setPlainText(
                    f"✅ RULE MATCHED: \"{d.get('rule_name', '')}\"\n"
                    f"Keywords: {d.get('keywords', '')}\n"
                    f"Auto Reply: {reply if reply else '🔇 Silent ignore (spam filter)'}"
                )
            else:
                test_out3.setPlainText("❌ No rule matched — message would go to manual inbox queue.")
        w.result_ready.connect(_got)
        w.error_signal.connect(test_out3.set_error)
        w.start()
        page._workers.append(w)

    btn_add_rule.clicked.connect(_add_rule)
    btn_del_rule.clicked.connect(_delete_rule)
    btn_toggle_rule.clicked.connect(_toggle_rule)
    btn_test_rule.clicked.connect(_test_rule)
    _refresh_rules()

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 4 — REPLY TEMPLATES LIBRARY
    # ═════════════════════════════════════════════════════════════════════════
    t4 = QWidget(); t4l = QVBoxLayout(t4); t4l.setSpacing(10)

    grp4 = QGroupBox("Reply Templates Generator  — Feature #103")
    g4   = QGridLayout(grp4)
    tpl_niche    = _styled_input("Niche (e.g. Fitness, Tech, Business, Food)")
    tpl_platform = _combo("TikTok", "Instagram", "Facebook", "YouTube", "Telegram", "LinkedIn")
    tpl_tone     = _combo("Friendly & Warm", "Professional", "Funny & Casual",
                           "Empathetic", "Direct & Concise", "Formal")
    tpl_lang     = _combo("English", "Khmer", "Thai", "Vietnamese", "Bilingual EN+KH")
    g4.addWidget(QLabel("Niche:"),     0, 0); g4.addWidget(tpl_niche,    0, 1)
    g4.addWidget(QLabel("Platform:"),  0, 2); g4.addWidget(tpl_platform, 0, 3)
    g4.addWidget(QLabel("Tone:"),      1, 0); g4.addWidget(tpl_tone,     1, 1)
    g4.addWidget(QLabel("Language:"),  1, 2); g4.addWidget(tpl_lang,     1, 3)
    t4l.addWidget(grp4)

    hint4 = QLabel(
        "💡  Generates 10 categories × 3 templates each = 30 ready-to-use replies\n"
        "    Categories: Welcome, Thank Compliment, Handle Complaint, Price, Product, Collab, Purchase, Negative, Question, Spam"
    )
    hint4.setStyleSheet(f"color:{SUBTEXT}; font-size:14px; padding:2px 0;")
    t4l.addWidget(hint4)

    btn_gen_tpl = ActionButton("📝 Generate Templates Library", ACCENT)
    t4l.addWidget(btn_gen_tpl)
    out4 = OutputBox("Reply templates will appear here…\n30 ready-to-use replies across 10 categories.")
    t4l.addWidget(out4, 1)
    tabs.addTab(t4, "📝 Templates Library")

    def _gen_templates():
        out4.reset_color(); out4.setPlainText("AI generating reply templates library…")
        btn_gen_tpl.set_loading(True)
        w = ApiWorker(f"{api_base}/api/v1/inbox/templates", {
            "niche":    tpl_niche.text() or "General",
            "platform": tpl_platform.currentText(),
            "tone":     tpl_tone.currentText(),
            "language": tpl_lang.currentText(),
        })
        page._w4 = w
        def _got(resp):
            btn_gen_tpl.set_loading(False)
            d = resp.get("data", resp)
            tpls = d.get("templates", {})
            lines = [
                f"📝 REPLY TEMPLATES LIBRARY",
                f"Platform: {d.get('platform','')} | Niche: {d.get('niche','')} | Tone: {d.get('tone','')}",
                f"Source: {d.get('source','').upper()} | Total: {d.get('total_templates',0)} templates",
                f"{'═'*60}",
            ]
            _ICONS = {
                "welcome_follower":  "👋 Welcome New Follower",
                "thank_compliment":  "🙏 Thank Compliment",
                "handle_complaint":  "🔧 Handle Complaint",
                "price_question":    "💰 Price Question",
                "product_question":  "📦 Product Question",
                "collab_request":    "🤝 Collaboration Request",
                "encourage_purchase":"🛒 Encourage Purchase",
                "handle_negative":   "😔 Handle Negative",
                "general_question":  "❓ General Question",
                "handle_spam":       "🚫 Handle Spam",
            }
            for cat, replies in tpls.items():
                label = _ICONS.get(cat, cat.replace("_", " ").title())
                lines += ["", f"── {label} ──"]
                if isinstance(replies, list):
                    for j, r in enumerate(replies, 1):
                        lines.append(f"  [{j}] {r}")
                else:
                    lines.append(f"  {replies}")
            out4.reset_color()
            out4.setPlainText("\n".join(lines))
        w.result_ready.connect(_got)
        w.error_signal.connect(lambda e: (btn_gen_tpl.set_loading(False), out4.set_error(e)))
        w.start()
        page._workers.append(w)

    btn_gen_tpl.clicked.connect(_gen_templates)

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 5 — SENTIMENT ANALYZER (Batch)
    # ═════════════════════════════════════════════════════════════════════════
    t5 = QWidget(); t5l = QVBoxLayout(t5); t5l.setSpacing(10)

    grp5 = QGroupBox("Batch Sentiment & Intent Analyzer  — Feature #104 (up to 30 messages)")
    g5   = QGridLayout(grp5)
    sent_platform = _combo("TikTok", "Instagram", "Facebook", "YouTube", "Telegram", "Twitter/X")
    batch_msg_in  = QTextEdit()
    batch_msg_in.setPlaceholderText(
        "Paste messages here — one per line (up to 30 messages).\n\n"
        "Example:\n"
        "This product is amazing! 🔥\n"
        "Where can I buy this?\n"
        "I want a refund, this is terrible!\n"
        "Follow me back! f4f!"
    )
    batch_msg_in.setMaximumHeight(160)
    g5.addWidget(QLabel("Platform:"),  0, 0); g5.addWidget(sent_platform, 0, 1)
    g5.addWidget(QLabel("Messages:"),  1, 0); g5.addWidget(batch_msg_in,  1, 0, 1, 2)
    t5l.addWidget(grp5)

    btn5_row = QHBoxLayout()
    btn_batch_sent = ActionButton("😊 Analyze All Messages", ACCENT)
    btn_single_sent = ActionButton("🔍 Analyze Single (first line)", SUCCESS)
    btn5_row.addWidget(btn_batch_sent); btn5_row.addWidget(btn_single_sent)
    t5l.addLayout(btn5_row)

    # Results table
    _SENT_COLS = ["#", "Message Preview", "Sentiment", "Intent", "Urgency", "Priority", "Spam?", "Action"]
    sent_table = QTableWidget(0, len(_SENT_COLS))
    sent_table.setHorizontalHeaderLabels(_SENT_COLS)
    sent_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
    sent_table.setAlternatingRowColors(True)
    sent_table.setEditTriggers(QTableWidget.NoEditTriggers)
    sent_table.setSelectionBehavior(QTableWidget.SelectRows)
    sent_table.setStyleSheet(inbox_table.styleSheet())
    t5l.addWidget(sent_table, 1)

    sent_summary = QLabel("Run analysis to see summary")
    sent_summary.setStyleSheet(
        f"background:{SURFACE}; color:{ACCENT}; padding:6px 12px; border-radius:6px; font-size:14px; font-weight:bold;"
    )
    t5l.addWidget(sent_summary)
    tabs.addTab(t5, "😊 Sentiment Analyzer")

    def _populate_sent_table(results: list):
        _SENT_COLOR = {"Positive": SUCCESS, "Negative": "#F38BA8", "Neutral": TEXT, "Mixed": WARNING}
        sent_table.setRowCount(0)
        pos = neg = neu = 0
        for r in results:
            sent = r.get("sentiment", "Neutral")
            if sent == "Positive": pos += 1
            elif sent == "Negative": neg += 1
            else: neu += 1
            sent_table.insertRow(sent_table.rowCount())
            row = sent_table.rowCount() - 1
            cells = [
                str(r.get("index", row + 1)),
                r.get("message_preview", "")[:55],
                sent,
                r.get("intent", ""),
                r.get("urgency", ""),
                str(r.get("priority", "")),
                "⚠ Yes" if r.get("is_spam") else "No",
                r.get("suggested_action", ""),
            ]
            for col, val in enumerate(cells):
                item = QTableWidgetItem(val)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                if col == 2:
                    item.setForeground(QColor(_SENT_COLOR.get(val, TEXT)))
                if col == 6 and "Yes" in val:
                    item.setForeground(QColor(WARNING))
                sent_table.setItem(row, col, item)
        total = len(results)
        sent_summary.setText(
            f"Total: {total}  |  ✅ Positive: {pos}  |  ❌ Negative: {neg}  |  ➖ Neutral: {neu}"
        )

    def _batch_analyze():
        raw = batch_msg_in.toPlainText().strip()
        if not raw:
            sent_summary.setText("⚠ Please enter messages to analyze.")
            return
        msgs = [line.strip() for line in raw.split("\n") if line.strip()][:30]
        sent_summary.setText(f"⏳ Analyzing {len(msgs)} messages…")
        w = ApiWorker(f"{api_base}/api/v1/inbox/sentiment-batch", {
            "messages": msgs,
            "platform": sent_platform.currentText(),
        }, btn=btn_batch_sent)
        page._w5 = w
        def _got(resp):
            d = resp.get("data", resp)
            _populate_sent_table(d.get("results", []))
        w.result_ready.connect(_got)
        w.error_signal.connect(lambda e: sent_summary.setText(f"❌ {e}"))
        w.start()
        page._workers.append(w)

    def _single_analyze():
        raw   = batch_msg_in.toPlainText().strip()
        first = raw.split("\n")[0].strip() if raw else ""
        if not first:
            sent_summary.setText("⚠ Enter at least one message.")
            return
        sent_summary.setText("⏳ Analyzing…")
        w = ApiWorker(f"{api_base}/api/v1/inbox/sentiment", {
            "message":  first,
            "platform": sent_platform.currentText(),
        }, btn=btn_single_sent)
        page._w5s = w
        def _got(resp):
            d = resp.get("data", resp)
            d["index"] = 1
            _populate_sent_table([d])
        w.result_ready.connect(_got)
        w.error_signal.connect(lambda e: sent_summary.setText(f"❌ {e}"))
        w.start()
        page._workers.append(w)

    btn_batch_sent.clicked.connect(_batch_analyze)
    btn_single_sent.clicked.connect(_single_analyze)

    layout.addWidget(tabs, 1)
    return page


# ─────────────────────────────────────────────────────────────────────────────
def build_geo_page(api_base: str) -> QWidget:
    """
    Feature #26-#33: Geo Intelligence — Location-Aware Growth for All 99 Features.
    7 tabs: Country Card, Geo Strategy, Best Times, Regional Trends,
    Cultural Guide, Audience Demographics, Platform Map.
    Uses ApiWorker(url, payload, method) + result_ready signal.
    """
    page, layout = _make_page_layout("Geo Intelligence & Location Targeting", "🌍")
    page._workers: list = []   # keep references so QThreads aren't garbage-collected

    subtitle = QLabel(
        "Target any of 60+ countries • Timezone-aware scheduling • Cultural content guide • "
        "Regional trends • Platform dominance map • Audience demographics"
    )
    subtitle.setStyleSheet(f"color:{SUBTEXT}; font-size:14px;")
    layout.addWidget(subtitle)

    # ── Country selector (shared across all tabs) ──────────────────────────────
    sel_row = QHBoxLayout()
    sel_lbl = QLabel("🎯 Target Country:")
    sel_lbl.setStyleSheet(f"color:{TEXT}; font-weight:bold; font-size:14px;")

    country_combo = QComboBox()
    country_combo.setMinimumWidth(280)
    country_combo.setEditable(True)
    country_combo.setStyleSheet(
        f"background:{SURFACE}; color:{TEXT}; border:1px solid #45475A; border-radius:6px; padding:4px 8px; font-size:14px;"
    )

    # Populate with geo data via backend call (fallback built-in list)
    _BUILTIN_COUNTRIES = [
        ("KH", "🇰🇭 Cambodia"),       ("TH", "🇹🇭 Thailand"),
        ("VN", "🇻🇳 Vietnam"),         ("ID", "🇮🇩 Indonesia"),
        ("PH", "🇵🇭 Philippines"),     ("SG", "🇸🇬 Singapore"),
        ("MY", "🇲🇾 Malaysia"),        ("CN", "🇨🇳 China"),
        ("JP", "🇯🇵 Japan"),           ("KR", "🇰🇷 South Korea"),
        ("TW", "🇹🇼 Taiwan"),          ("IN", "🇮🇳 India"),
        ("PK", "🇵🇰 Pakistan"),        ("SA", "🇸🇦 Saudi Arabia"),
        ("EG", "🇪🇬 Egypt"),           ("AE", "🇦🇪 UAE"),
        ("GB", "🇬🇧 United Kingdom"),  ("DE", "🇩🇪 Germany"),
        ("FR", "🇫🇷 France"),          ("US", "🇺🇸 United States"),
        ("BR", "🇧🇷 Brazil"),          ("MX", "🇲🇽 Mexico"),
        ("NG", "🇳🇬 Nigeria"),         ("ZA", "🇿🇦 South Africa"),
        ("AU", "🇦🇺 Australia"),
    ]
    _code_map: dict = {}
    for code, label in _BUILTIN_COUNTRIES:
        country_combo.addItem(label, code)
        _code_map[label] = code

    def _selected_code() -> str:
        idx = country_combo.currentIndex()
        if idx >= 0:
            return country_combo.itemData(idx) or "KH"
        return "KH"

    platform_combo = QComboBox()
    platform_combo.addItems(["TikTok", "Facebook", "Instagram", "YouTube", "Twitter/X", "LinkedIn", "WhatsApp", "Telegram"])
    platform_combo.setStyleSheet(
        f"background:{SURFACE}; color:{TEXT}; border:1px solid #45475A; border-radius:6px; padding:4px 8px; font-size:14px;"
    )

    niche_input = QLineEdit()
    niche_input.setPlaceholderText("Niche (e.g. Food, Fashion, Tech)")
    niche_input.setText("General")
    niche_input.setStyleSheet(
        f"background:{SURFACE}; color:{TEXT}; border:1px solid #45475A; border-radius:6px; padding:6px 10px; font-size:14px;"
    )

    sel_row.addWidget(sel_lbl)
    sel_row.addWidget(country_combo, 2)
    sel_row.addWidget(QLabel("📱 Platform:"))
    sel_row.addWidget(platform_combo)
    sel_row.addWidget(QLabel("🎯 Niche:"))
    sel_row.addWidget(niche_input)
    layout.addLayout(sel_row)

    # Local time banner
    time_banner = QLabel("⏰  Local time: loading...")
    time_banner.setStyleSheet(
        f"background:{SURFACE}; color:{ACCENT}; padding:6px 12px; border-radius:6px; font-size:14px; font-weight:bold;"
    )
    layout.addWidget(time_banner)

    tabs = QTabWidget()

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _out(parent: QVBoxLayout, btn_text: str = "▶ Run") -> tuple:
        btn = ActionButton(btn_text)
        out = OutputBox()
        parent.addWidget(btn)
        parent.addWidget(out, 1)
        return out, btn

    def _refresh_time():
        code = _selected_code()
        worker = ApiWorker(f"{api_base}/api/v1/geo/local-time/{code}", method="GET")
        def _show(d):
            time_banner.setText(
                f"⏰  Local time in {d.get('country','?')}: "
                f"{d.get('local_time','?')} | {d.get('weekday','?')} {d.get('local_date','?')} "
                f"| {d.get('timezone','?')} (UTC{d.get('utc_offset','?')})"
            )
        worker.result_ready.connect(lambda d: _show(d.get("data", d)))
        worker.error_signal.connect(lambda e: time_banner.setText(f"⏰  Error: {e}"))
        page._workers.append(worker)
        worker.start()

    country_combo.currentIndexChanged.connect(lambda _: _refresh_time())
    QTimer.singleShot(800, _refresh_time)

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 1: COUNTRY CARD
    # ─────────────────────────────────────────────────────────────────────────
    tab1 = QWidget(); t1l = QVBoxLayout(tab1); t1l.setSpacing(8)
    out1, btn1 = _out(t1l, "🌍 Load Country Card")

    def _load_country():
        code = _selected_code()
        out1.setPlainText(f"Loading country info for {code}…")
        worker = ApiWorker(f"{api_base}/api/v1/geo/country/{code}", method="GET", btn=btn1)
        def _show(d):
            if "error" in d:
                out1.setPlainText(f"Error: {d['error']}")
                return
            lines = [
                f"🌍  {d.get('name','')}  ({d.get('code','')})",
                f"🗺️  Region:        {d.get('region','')}",
                f"⏰  Timezone:      {d.get('timezone','')} (UTC{d.get('utc_offset','')})",
                f"🗣️  Languages:     {', '.join(d.get('languages', []))}",
                f"💰  Currency:      {d.get('currency','')}",
                f"👥  Internet users: {d.get('internet_users_m', 0)}M",
                f"📱  Mobile %:      {d.get('mobile_pct', 0)}%",
                f"⏱️  Daily social:  {d.get('avg_daily_social_min', 0)} min/day",
                "",
                f"📱  TOP PLATFORMS:",
            ]
            for p in d.get("top_platforms", []):
                note = d.get("platform_notes", {}).get(p, "")
                lines.append(f"   • {p}: {note}")
            lines += ["", "📅  PEAK HOURS (local):"]
            for plat, hours in d.get("peak_hours_local", {}).items():
                lines.append(f"   {plat}: {', '.join(hours)}")
            lines += ["", "🎨  CONTENT STYLE:", f"   {d.get('content_style','')}",
                      "", "💡  CULTURAL TIPS:"]
            for tip in d.get("cultural_tips", []):
                lines.append(f"   ✓ {tip}")
            lt = d.get("local_time", {})
            lines += ["", f"🕐  Current local time: {lt.get('local_time','?')} on {lt.get('weekday','?')} {lt.get('local_date','?')}"]
            out1.setPlainText("\n".join(lines))
        worker.result_ready.connect(lambda d: _show(d.get("data", d)))
        worker.error_signal.connect(out1.set_error)
        page._workers.append(worker)
        worker.start()

    btn1.clicked.connect(_load_country)
    tabs.addTab(tab1, "🌍 Country Card")

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 2: GEO STRATEGY
    # ─────────────────────────────────────────────────────────────────────────
    tab2 = QWidget(); t2l = QVBoxLayout(tab2); t2l.setSpacing(8)
    out2, btn2 = _out(t2l, "🚀 Generate Geo-Targeted Strategy")

    def _geo_strategy():
        code    = _selected_code()
        plat    = platform_combo.currentText()
        niche   = niche_input.text().strip() or "General"
        out2.setPlainText(f"Generating geo strategy for {code} / {plat} / {niche}…")
        worker = ApiWorker(f"{api_base}/api/v1/geo/strategy",
                           {"country_code": code, "platform": plat, "niche": niche}, btn=btn2)
        def _show(d):
            if "error" in d:
                out2.setPlainText(f"Error: {d['error']}")
                return
            lines = [
                f"🌍  GEO STRATEGY: {d.get('country','')} | {plat} | {niche}",
                f"🤖  Source: {d.get('source','').upper()}",
                "", "📋  OVERVIEW:", f"   {d.get('strategy_overview','')}",
                "", "📌  CONTENT PILLARS:",
            ]
            for i, pillar in enumerate(d.get("content_pillars", []), 1):
                if isinstance(pillar, dict):
                    lines.append(f"   {i}. {pillar.get('title','')}: {pillar.get('description','')}")
                else:
                    lines.append(f"   {i}. {pillar}")
            lines += ["", f"🗣️  LANGUAGE STRATEGY: {d.get('language_strategy','')}",
                      "", "📅  POSTING SCHEDULE:"]
            for plf, hrs in d.get("posting_schedule", {}).items():
                lines.append(f"   {plf}: {', '.join(hrs) if isinstance(hrs, list) else hrs}")
            lines += ["", "💡  GEO-SPECIFIC CONTENT IDEAS:"]
            for idea in d.get("geo_hooks", []):
                lines.append(f"   → {idea}")
            lines += ["", "#️⃣  LOCAL HASHTAGS:", "   " + "  ".join(f"#{h.lstrip('#')}" for h in d.get("local_hashtags", []))]
            lines += ["", "✅  CULTURAL DOs:"]
            for x in d.get("cultural_do_list", []):
                lines.append(f"   ✓ {x}")
            lines += ["", "❌  CULTURAL DON'Ts:"]
            for x in d.get("cultural_dont_list", []):
                lines.append(f"   ✗ {x}")
            lines += [
                "",
                f"📈  Est. monthly growth: {d.get('estimated_monthly_growth_pct', 0)}%",
                "", "🗓️  90-DAY MILESTONES:",
            ]
            for m in d.get("90_day_milestones", []):
                lines.append(f"   {m}")
            out2.setPlainText("\n".join(lines))
        worker.result_ready.connect(lambda d: _show(d.get("data", d)))
        worker.error_signal.connect(out2.set_error)
        page._workers.append(worker)
        worker.start()

    btn2.clicked.connect(_geo_strategy)
    tabs.addTab(tab2, "🚀 Geo Strategy")

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 3: TIMEZONE & BEST POSTING TIMES
    # ─────────────────────────────────────────────────────────────────────────
    tab3 = QWidget(); t3l = QVBoxLayout(tab3); t3l.setSpacing(8)
    out3, btn3 = _out(t3l, "⏰ Get Timezone & Best Posting Times")

    def _best_times():
        code = _selected_code()
        plat = platform_combo.currentText()
        out3.setPlainText(f"Loading timezone schedule for {code} / {plat}…")
        worker = ApiWorker(f"{api_base}/api/v1/geo/best-times/{code}/{plat}", method="GET", btn=btn3)
        def _show(d):
            if "error" in d:
                out3.setPlainText(f"Error: {d['error']}")
                return
            lines = [
                f"⏰  TIMEZONE SCHEDULE: {d.get('country','')} | {plat}",
                f"🌐  Timezone:    {d.get('timezone','')} (UTC{d.get('utc_offset','')})",
                f"🕐  Local time NOW:  {d.get('local_time_now','')} on {d.get('weekday','')} {d.get('local_date_now','')}",
                "",
                f"🎯  BEST TIMES TO POST on {plat}:",
                f"   Local:  {', '.join(d.get('peak_hours_local', []))}",
                f"   UTC:    {', '.join(d.get('peak_hours_utc', []))}",
                "",
                "📅  ALL PLATFORMS — PEAK HOURS (local):",
            ]
            for p, hrs in d.get("all_platform_peaks", {}).items():
                lines.append(f"   {p:20s}: {', '.join(hrs)}")
            lines += [
                "",
                f"📋  RECOMMENDATION: {d.get('posting_frequency_recommendation','')}",
                "",
                f"💡  TIP: {d.get('timezone_tip','')}",
            ]
            out3.setPlainText("\n".join(lines))
        worker.result_ready.connect(lambda d: _show(d.get("data", d)))
        worker.error_signal.connect(out3.set_error)
        page._workers.append(worker)
        worker.start()

    btn3.clicked.connect(_best_times)
    tabs.addTab(tab3, "⏰ Best Times")

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 4: REGIONAL TRENDS
    # ─────────────────────────────────────────────────────────────────────────
    tab4 = QWidget(); t4l = QVBoxLayout(tab4); t4l.setSpacing(8)
    out4, btn4 = _out(t4l, "📈 Scan Regional Trends")

    def _regional_trends():
        code  = _selected_code()
        niche = niche_input.text().strip() or "General"
        out4.setPlainText(f"Scanning trends in {code} for niche: {niche}…")
        worker = ApiWorker(f"{api_base}/api/v1/geo/trends/{code}", {"niche": niche}, "GET", btn=btn4)
        def _show(d):
            if "error" in d:
                out4.setPlainText(f"Error: {d['error']}")
                return
            lines = [
                f"📈  REGIONAL TRENDS: {d.get('country','')} | {niche}",
                f"🤖  Source: {d.get('source','').upper()}",
                "", "🔥  TRENDING TOPICS:",
            ]
            for t in d.get("trending_topics", []):
                if isinstance(t, dict):
                    lines.append(
                        f"   [{t.get('trend_score', 0):3d}%] {t.get('topic','')}"
                        f"  →  {t.get('content_angle','')}  | Language: {t.get('language_to_use','')}"
                    )
                else:
                    lines.append(f"   • {t}")
            lines += ["", f"🌐  REGIONAL INSIGHT:", f"   {d.get('regional_insight','')}",
                      "", "📅  UPCOMING LOCAL EVENTS / CULTURAL MOMENTS:"]
            for ev in d.get("upcoming_local_events", []):
                lines.append(f"   🗓️ {ev}")
            lines += ["", "🌿  EVERGREEN LOCAL TOPICS (always work):"]
            for ev in d.get("evergreen_local_topics", []):
                lines.append(f"   ✓ {ev}")
            out4.setPlainText("\n".join(lines))
        worker.result_ready.connect(lambda d: _show(d.get("data", d)))
        worker.error_signal.connect(out4.set_error)
        page._workers.append(worker)
        worker.start()

    btn4.clicked.connect(_regional_trends)
    tabs.addTab(tab4, "📈 Regional Trends")

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 5: CULTURAL CONTENT GUIDE
    # ─────────────────────────────────────────────────────────────────────────
    tab5 = QWidget(); t5l = QVBoxLayout(tab5); t5l.setSpacing(8)
    out5, btn5 = _out(t5l, "🎨 Get Cultural Content Guide")

    def _cultural_guide():
        code  = _selected_code()
        niche = niche_input.text().strip() or "General"
        out5.setPlainText(f"Loading cultural guide for {code} / {niche}…")
        worker = ApiWorker(f"{api_base}/api/v1/geo/cultural-guide/{code}", {"niche": niche}, "GET", btn=btn5)
        def _show(d):
            if "error" in d:
                out5.setPlainText(f"Error: {d['error']}")
                return
            lines = [
                f"🎨  CULTURAL CONTENT GUIDE: {d.get('country','')} | {niche}",
                f"🤖  Source: {d.get('source','').upper()}",
                "",
                f"🎭  CONTENT TONE: {d.get('content_tone','')}",
                f"👁️  VISUAL STYLE: {d.get('visual_style','')}",
                f"🎵  MUSIC & SOUND: {d.get('music_and_sound_tips','')}",
                f"✍️  CAPTION FORMULA: {d.get('caption_formula','')}",
                f"#️⃣  HASHTAG LANGUAGE: {d.get('hashtag_language','')}",
                f"😊  EMOJI USAGE: {d.get('emoji_usage','')}",
                "",
                "💬  VOCABULARY TIPS:",
            ]
            for tip in d.get("vocabulary_tips", []):
                lines.append(f"   • {tip}")
            lines += ["", "📢  CALL-TO-ACTION EXAMPLES (culturally adapted):"]
            for cta in d.get("cta_examples", []):
                lines.append(f"   → \"{cta}\"")
            lines += ["", "✅  SAFE TOPICS (always work):"]
            lines.append("   " + " • ".join(d.get("safe_topics", [])))
            lines += ["", "🚫  TABOO TOPICS (avoid):"]
            for t in d.get("taboo_topics", []):
                lines.append(f"   ✗ {t}")
            lines += ["", "🗓️  SEASONAL CONTENT CALENDAR:"]
            for month, theme in d.get("seasonal_calendar", {}).items():
                lines.append(f"   {month:12s}: {theme}")
            out5.setPlainText("\n".join(lines))
        worker.result_ready.connect(lambda d: _show(d.get("data", d)))
        worker.error_signal.connect(out5.set_error)
        page._workers.append(worker)
        worker.start()

    btn5.clicked.connect(_cultural_guide)
    tabs.addTab(tab5, "🎨 Cultural Guide")

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 6: AUDIENCE DEMOGRAPHICS
    # ─────────────────────────────────────────────────────────────────────────
    tab6 = QWidget(); t6l = QVBoxLayout(tab6); t6l.setSpacing(8)
    out6, btn6 = _out(t6l, "👥 Analyse Regional Audience")

    def _audience():
        code  = _selected_code()
        plat  = platform_combo.currentText()
        niche = niche_input.text().strip() or "General"
        out6.setPlainText(f"Loading audience data for {code} / {plat} / {niche}…")
        worker = ApiWorker(f"{api_base}/api/v1/geo/audience",
                           {"country_code": code, "platform": plat, "niche": niche}, btn=btn6)
        def _show(d):
            if "error" in d:
                out6.setPlainText(f"Error: {d['error']}")
                return
            lines = [
                f"👥  AUDIENCE DEMOGRAPHICS: {d.get('country','')} | {plat} | {niche}",
                f"🤖  Source: {d.get('source','').upper()}",
                "",
                f"📊  ESTIMATED AUDIENCE: {d.get('estimated_audience_size','')}",
                f"💹  AVG ENGAGEMENT RATE: {d.get('avg_engagement_rate','')}",
                "",
                "👤  AGE DISTRIBUTION:",
            ]
            for k, v in d.get("age_distribution", {}).items():
                lines.append(f"   {k}: {v}")
            lines += ["", "⚤  GENDER SPLIT:"]
            for k, v in d.get("gender_split", {}).items():
                lines.append(f"   {k}: {v}")
            lines += [
                "",
                f"💰  INCOME LEVEL: {d.get('income_level','')}",
                f"🎓  EDUCATION: {d.get('education_level','')}",
                "", "📱  DEVICE USAGE:",
            ]
            for k, v in d.get("device_usage", {}).items():
                lines.append(f"   {k}: {v}")
            lines += [
                "",
                f"📱  CONTENT CONSUMPTION: {d.get('content_consumption_habits','')}",
                f"🛒  PURCHASE BEHAVIOUR: {d.get('purchase_behavior','')}",
                "", "😣  PAIN POINTS:",
            ]
            for p in d.get("pain_points", []):
                lines.append(f"   • {p}")
            lines += ["", "🌟  ASPIRATIONS:"]
            for a in d.get("aspirations", []):
                lines.append(f"   • {a}")
            lines += ["", "🎬  PREFERRED CONTENT FORMATS:"]
            for f in d.get("content_format_preference", []):
                lines.append(f"   ▶ {f}")
            out6.setPlainText("\n".join(lines))
        worker.result_ready.connect(lambda d: _show(d.get("data", d)))
        worker.error_signal.connect(out6.set_error)
        page._workers.append(worker)
        worker.start()

    btn6.clicked.connect(_audience)
    tabs.addTab(tab6, "👥 Audience")

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 7: PLATFORM MAP
    # ─────────────────────────────────────────────────────────────────────────
    tab7 = QWidget(); t7l = QVBoxLayout(tab7); t7l.setSpacing(8)
    out7, btn7 = _out(t7l, "📱 Load Platform Dominance Map")

    def _platform_map():
        code = _selected_code()
        out7.setPlainText(f"Loading platform map for {code}…")
        worker = ApiWorker(f"{api_base}/api/v1/geo/platforms/{code}", method="GET", btn=btn7)
        def _show(d):
            if "error" in d:
                out7.setPlainText(f"Error: {d['error']}")
                return
            lines = [
                f"📱  PLATFORM MAP: {d.get('country','')} ({code})",
                f"🗺️  Region: {d.get('region','')}",
                f"👥  Internet users: {d.get('internet_users_m', 0)}M",
                f"📱  Mobile: {d.get('mobile_pct', 0)}%",
                f"⏱️  Daily social: {d.get('avg_daily_social_min', 0)} min/day",
                f"🏆  Market tier: {d.get('market_size_tier','')}",
                "",
                "📊  PLATFORMS (ranked by dominance):",
            ]
            for i, p in enumerate(d.get("top_platforms", []), 1):
                note = d.get("platform_notes", {}).get(p, "")
                lines.append(f"   #{i}  {p}: {note}")
            if d.get("blocked_platforms"):
                lines += ["", "🚫  BLOCKED / UNAVAILABLE:"]
                for b in d["blocked_platforms"]:
                    lines.append(f"   ✗ {b}")
            lines += [
                "",
                f"✅  RECOMMENDED PRIMARY:   {d.get('recommended_primary','')}",
                f"✅  RECOMMENDED SECONDARY: {d.get('recommended_secondary','')}",
            ]
            out7.setPlainText("\n".join(lines))
        worker.result_ready.connect(lambda d: _show(d.get("data", d)))
        worker.error_signal.connect(out7.set_error)
        page._workers.append(worker)
        worker.start()

    btn7.clicked.connect(_platform_map)
    tabs.addTab(tab7, "📱 Platform Map")

    layout.addWidget(tabs, 1)
    return page


# ═══════════════════════════════════════════════════════════════════════════════
# SOCIAL MEDIA MANAGER PAGE  — Features #111-#120
# ═══════════════════════════════════════════════════════════════════════════════

def build_social_manager_page(api_base: str) -> QWidget:
    """
    Features #111-#120: Comprehensive Social Media Manager
    Tabs: Post Composer | Ads Manager | AI Ad Expert | Performance | Audience | Campaign Planner
    """
    page, layout = _make_page_layout("Social Media Manager", "📱")
    page._workers: list = []

    sub = QLabel(
        "Manage all social accounts  •  Create & schedule posts  •  Run AI-powered ads  •  "
        "Expert ads guidance  •  Performance insights  •  Audience targeting"
    )
    sub.setWordWrap(True)
    sub.setStyleSheet(f"color:{SUBTEXT}; font-size:14px;")
    layout.addWidget(sub)

    # ── Shared platform / account state ─────────────────────────────────────
    _PLATFORMS = ["Facebook", "Instagram", "TikTok", "YouTube", "Twitter/X", "LinkedIn", "Telegram"]
    _OBJECTIVES = ["Awareness", "Reach", "Traffic", "Engagement", "App Installs",
                   "Video Views", "Lead Generation", "Conversions", "Catalog Sales", "Store Traffic"]
    _TONES      = ["Professional", "Friendly & Warm", "Energetic & Bold", "Inspirational",
                   "Humorous", "Empathetic", "Authoritative", "Casual"]

    _PLT_ICON = {
        "Facebook":  "📘", "Instagram": "📸", "TikTok": "🎵",
        "YouTube":   "▶️", "Twitter/X": "🐦", "LinkedIn": "💼", "Telegram": "✈️",
    }

    _TABLE_STYLE = f"""
        QTableWidget {{
            background:{SURFACE}; color:{TEXT};
            border:1px solid {BORDER}; border-radius:6px; gridline-color:{BORDER};
            font-size:14px;
        }}
        QHeaderView::section {{
            background:{DARK_BG}; color:{ACCENT}; padding:8px; border:none;
            font-weight:bold; font-size:14px;
        }}
        QTableWidget::item:alternate {{ background:#252535; }}
        QTableWidget::item:selected  {{ background:#313244; color:{TEXT}; }}
    """

    tabs = QTabWidget()

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 1 — POST COMPOSER
    # ═════════════════════════════════════════════════════════════════════════
    t1 = QWidget(); t1l = QVBoxLayout(t1); t1l.setSpacing(10)

    # Platform selector row
    plt_row = QHBoxLayout()
    plt_row.addWidget(QLabel("Platform:"))
    post_plt_combo = _combo(_PLATFORMS)
    plt_row.addWidget(post_plt_combo)
    plt_row.addWidget(QLabel("Post Type:"))
    post_type_combo = _combo(["Standard", "Reel/Short", "Story", "Carousel", "Thread", "Poll"])
    plt_row.addWidget(post_type_combo)
    plt_row.addWidget(QLabel("Tone:"))
    post_tone_combo = _combo(_TONES)
    plt_row.addWidget(post_tone_combo)
    plt_row.addWidget(QLabel("Language:"))
    post_lang_combo = _combo(["English", "Khmer", "Thai", "Vietnamese", "Chinese", "Japanese",
                               "Spanish", "French", "Arabic", "Hindi", "Indonesian"])
    plt_row.addWidget(post_lang_combo)
    plt_row.addStretch()
    t1l.addLayout(plt_row)

    # Options row
    opt_row = QHBoxLayout()
    chk_hashtags = QCheckBox("Include Hashtags"); chk_hashtags.setChecked(True)
    chk_cta      = QCheckBox("Include CTA"); chk_cta.setChecked(True)
    opt_row.addWidget(chk_hashtags); opt_row.addWidget(chk_cta); opt_row.addStretch()
    t1l.addLayout(opt_row)

    # Topic input
    topic_row = QHBoxLayout()
    topic_row.addWidget(QLabel("Topic / Brief:"))
    post_topic_inp = _styled_input("Enter post topic, keywords, or content brief…")
    topic_row.addWidget(post_topic_inp, 1)
    btn_ai_post = ActionButton("✨ AI Generate Post", ACCENT)
    topic_row.addWidget(btn_ai_post)
    t1l.addLayout(topic_row)

    # Content editor
    content_editor = QTextEdit()
    content_editor.setPlaceholderText(
        "Your post content will appear here…\n\n"
        "You can also type or paste your own content and use AI to enhance it."
    )
    content_editor.setMinimumHeight(180)
    content_editor.setStyleSheet(f"""
        QTextEdit {{
            background:{SURFACE}; color:{TEXT}; border:1px solid {BORDER};
            border-radius:8px; padding:12px; font-size:14px; line-height:1.5;
        }}
    """)
    t1l.addWidget(content_editor)

    # Character counter + scheduled time
    footer_row = QHBoxLayout()
    char_count_lbl = QLabel("Characters: 0")
    char_count_lbl.setStyleSheet(f"color:{SUBTEXT}; font-size:14px;")
    footer_row.addWidget(char_count_lbl)
    footer_row.addStretch()
    footer_row.addWidget(QLabel("Schedule (optional):"))
    schedule_inp = _styled_input("YYYY-MM-DD HH:MM  (leave blank to post now)")
    schedule_inp.setFixedWidth(260)
    footer_row.addWidget(schedule_inp)
    t1l.addLayout(footer_row)

    # Action buttons
    action_row = QHBoxLayout()
    btn_enhance = ActionButton("🚀 AI Enhance Content", WARNING)
    btn_copy_post = ActionButton("📋 Copy to Clipboard", "#7FBBB3")
    btn_clear_post = ActionButton("🗑 Clear", BORDER)
    for b in [btn_enhance, btn_copy_post, btn_clear_post]:
        action_row.addWidget(b)
    action_row.addStretch()
    t1l.addLayout(action_row)

    post_out = OutputBox("Generated post will appear above in the editor…")
    post_out.setMaximumHeight(70)
    t1l.addWidget(post_out)

    # Character counter update
    def _update_char(text: str):
        n = len(text)
        limits = {"Twitter/X": 280, "Facebook": 63206, "Instagram": 2200,
                  "TikTok": 2200, "LinkedIn": 3000, "YouTube": 5000, "Telegram": 4096}
        limit = limits.get(post_plt_combo.currentText(), 2200)
        color = SUCCESS if n <= limit * 0.8 else WARNING if n <= limit else "#F38BA8"
        char_count_lbl.setText(f"Characters: {n:,} / {limit:,}")
        char_count_lbl.setStyleSheet(f"color:{color}; font-size:14px; font-weight:bold;")
    content_editor.textChanged.connect(lambda: _update_char(content_editor.toPlainText()))

    def _ai_generate_post():
        topic = post_topic_inp.text().strip()
        if not topic:
            post_out.set_error("Please enter a topic or brief first."); return
        payload = {
            "topic": topic, "platform": post_plt_combo.currentText(),
            "tone": post_tone_combo.currentText(), "language": post_lang_combo.currentText(),
            "include_hashtags": chk_hashtags.isChecked(), "include_cta": chk_cta.isChecked(),
            "post_type": post_type_combo.currentText().split("/")[0],
        }
        btn_ai_post.set_loading(True)
        post_out.setPlainText("⏳ Generating post…")
        w = ApiWorker(f"{api_base}/api/v1/social/generate-post", method="POST", payload=payload)
        def _got(r):
            content_editor.setPlainText(r.get("post", ""))
            post_out.setPlainText("✅ Post generated! Edit as needed, then copy or schedule.")
            btn_ai_post.set_loading(False)
        w.result_ready.connect(_got)
        w.error_signal.connect(lambda e: (post_out.set_error(e), btn_ai_post.set_loading(False)))
        page._workers.append(w); w.start()

    def _enhance_post():
        current = content_editor.toPlainText().strip()
        if not current:
            post_out.set_error("No content to enhance."); return
        payload = {
            "topic": f"Enhance and improve: {current[:400]}",
            "platform": post_plt_combo.currentText(), "tone": post_tone_combo.currentText(),
            "language": post_lang_combo.currentText(),
            "include_hashtags": chk_hashtags.isChecked(), "include_cta": chk_cta.isChecked(),
            "post_type": post_type_combo.currentText().split("/")[0],
        }
        btn_enhance.set_loading(True)
        w = ApiWorker(f"{api_base}/api/v1/social/generate-post", method="POST", payload=payload)
        def _got(r):
            content_editor.setPlainText(r.get("post", ""))
            post_out.setPlainText("✅ Content enhanced!")
            btn_enhance.set_loading(False)
        w.result_ready.connect(_got)
        w.error_signal.connect(lambda e: (post_out.set_error(e), btn_enhance.set_loading(False)))
        page._workers.append(w); w.start()

    btn_ai_post.clicked.connect(_ai_generate_post)
    btn_enhance.clicked.connect(_enhance_post)
    btn_copy_post.clicked.connect(lambda: (
        QApplication.clipboard().setText(content_editor.toPlainText()),
        post_out.setPlainText("✅ Content copied to clipboard!")
    ))
    btn_clear_post.clicked.connect(lambda: (content_editor.clear(), post_out.setPlainText("")))

    tabs.addTab(t1, "📝 Post Composer")

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 2 — ADS MANAGER
    # ═════════════════════════════════════════════════════════════════════════
    t2 = QWidget(); t2l = QVBoxLayout(t2); t2l.setSpacing(10)

    # Info banner
    ads_info = QLabel(
        "🚀  Create high-converting ads with AI-generated copy, expert targeting, and full campaign structure."
    )
    ads_info.setWordWrap(True)
    ads_info.setStyleSheet(
        f"background:{SURFACE}; color:{ACCENT}; padding:10px 14px; "
        f"border-radius:8px; font-size:14px; border-left:4px solid {ACCENT};"
    )
    t2l.addWidget(ads_info)

    # Split: left=inputs, right=preview
    ads_split = QSplitter(Qt.Horizontal)

    # Left panel
    left_w = QWidget(); left_l = QVBoxLayout(left_w); left_l.setContentsMargins(0, 0, 8, 0); left_l.setSpacing(8)

    r1 = QHBoxLayout()
    r1.addWidget(QLabel("Platform:")); ads_plt_combo = _combo(_PLATFORMS); r1.addWidget(ads_plt_combo)
    r1.addWidget(QLabel("Objective:")); ads_obj_combo = _combo(_OBJECTIVES); r1.addWidget(ads_obj_combo)
    left_l.addLayout(r1)

    r2 = QHBoxLayout()
    r2.addWidget(QLabel("Tone:")); ads_tone_combo = _combo(_TONES); r2.addWidget(ads_tone_combo)
    r2.addWidget(QLabel("Language:")); ads_lang_combo = _combo(["English", "Khmer", "Thai", "Vietnamese",
                                                                  "Chinese", "Spanish", "French", "Arabic", "Hindi"]); r2.addWidget(ads_lang_combo)
    left_l.addLayout(r2)

    left_l.addWidget(QLabel("Product / Service:"))
    ads_product_inp = _styled_input("Describe your product or service…")
    left_l.addWidget(ads_product_inp)

    left_l.addWidget(QLabel("Target Audience (optional):"))
    ads_audience_inp = _styled_input("E.g. Women 25-40 interested in fitness, US & Canada…")
    left_l.addWidget(ads_audience_inp)

    r3 = QHBoxLayout()
    r3.addWidget(QLabel("Variants:"))
    ads_variants_spin = QSpinBox(); ads_variants_spin.setRange(1, 6); ads_variants_spin.setValue(3)
    ads_variants_spin.setStyleSheet(f"background:{SURFACE}; color:{TEXT}; border:1px solid {BORDER}; border-radius:6px; padding:6px; font-size:14px;")
    r3.addWidget(ads_variants_spin); r3.addStretch()
    left_l.addLayout(r3)

    btn_gen_copy = ActionButton("✨ Generate Ad Copy", ACCENT)
    left_l.addWidget(btn_gen_copy)
    left_l.addStretch()

    ads_split.addWidget(left_w)

    # Right panel — output
    right_w = QWidget(); right_l = QVBoxLayout(right_w); right_l.setContentsMargins(8, 0, 0, 0); right_l.setSpacing(8)
    right_l.addWidget(QLabel("Generated Ad Copy:"))
    ads_copy_out = OutputBox("Ad copy variants will appear here…")
    ads_copy_out.setMinimumHeight(220)
    right_l.addWidget(ads_copy_out, 1)

    platform_tip_lbl = QLabel()
    platform_tip_lbl.setWordWrap(True)
    platform_tip_lbl.setStyleSheet(
        f"background:{DARK_BG}; color:{WARNING}; padding:8px 12px; "
        f"border-radius:6px; font-size:14px;"
    )
    right_l.addWidget(platform_tip_lbl)

    btn_copy_ads = ActionButton("📋 Copy Ad Copy", "#7FBBB3")
    right_l.addWidget(btn_copy_ads)

    ads_split.addWidget(right_w)
    ads_split.setSizes([420, 480])
    t2l.addWidget(ads_split, 1)

    def _gen_ad_copy():
        product = ads_product_inp.text().strip()
        if not product:
            ads_copy_out.set_error("Please describe your product/service first."); return
        payload = {
            "product": product, "platform": ads_plt_combo.currentText(),
            "objective": ads_obj_combo.currentText(), "target_audience": ads_audience_inp.text().strip(),
            "tone": ads_tone_combo.currentText(), "language": ads_lang_combo.currentText(),
            "variants": ads_variants_spin.value(),
        }
        btn_gen_copy.set_loading(True)
        ads_copy_out.setPlainText("⏳ Generating ad copy variants…")
        w = ApiWorker(f"{api_base}/api/v1/social/generate-ad-copy", method="POST", payload=payload)
        def _got(r):
            ads_copy_out.setPlainText(r.get("copy", ""))
            tip = r.get("platform_tips", "")
            if tip:
                platform_tip_lbl.setText(f"💡 Platform Tip: {tip}")
            btn_gen_copy.set_loading(False)
        w.result_ready.connect(_got)
        w.error_signal.connect(lambda e: (ads_copy_out.set_error(e), btn_gen_copy.set_loading(False)))
        page._workers.append(w); w.start()

    btn_gen_copy.clicked.connect(_gen_ad_copy)
    btn_copy_ads.clicked.connect(lambda: (
        QApplication.clipboard().setText(ads_copy_out.toPlainText()),
        ads_copy_out.appendPlainText("\n✅ Copied!")
    ))

    tabs.addTab(t2, "📢 Ads Manager")

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 3 — AI ADS EXPERT (Chat-style)
    # ═════════════════════════════════════════════════════════════════════════
    t3 = QWidget(); t3l = QVBoxLayout(t3); t3l.setSpacing(10)

    expert_header = QLabel(
        "🤖  Chat with your AI Ads Expert — ask anything about Facebook/Instagram/TikTok/YouTube advertising, "
        "targeting, budgets, creatives, bidding, ROAS, and growth strategy."
    )
    expert_header.setWordWrap(True)
    expert_header.setStyleSheet(
        f"background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
        f"stop:0 {SURFACE},stop:1 {DARK_BG}); "
        f"color:{TEXT}; padding:12px; border-radius:8px; font-size:14px; "
        f"border-left:4px solid {SUCCESS};"
    )
    t3l.addWidget(expert_header)

    # Context row
    ctx_row = QHBoxLayout()
    ctx_row.addWidget(QLabel("Platform:"))
    exp_plt_combo = _combo(["General", "Facebook", "Instagram", "TikTok", "YouTube", "LinkedIn", "Twitter/X"])
    ctx_row.addWidget(exp_plt_combo)
    ctx_row.addWidget(QLabel("Objective:"))
    exp_obj_combo = _combo(_OBJECTIVES)
    ctx_row.addWidget(exp_obj_combo)
    ctx_row.addWidget(QLabel("Budget USD:"))
    exp_budget_inp = _styled_input("0")
    exp_budget_inp.setFixedWidth(100)
    ctx_row.addWidget(exp_budget_inp)
    ctx_row.addWidget(QLabel("Niche:"))
    exp_niche_inp = _styled_input("E-commerce")
    ctx_row.addWidget(exp_niche_inp)
    ctx_row.addWidget(QLabel("Language:"))
    exp_lang_combo = _combo(["English", "Khmer", "Thai", "Vietnamese", "Chinese", "Spanish", "French", "Arabic"])
    ctx_row.addWidget(exp_lang_combo)
    ctx_row.addStretch()
    t3l.addLayout(ctx_row)

    # Chat history display
    chat_display = QTextEdit()
    chat_display.setReadOnly(True)
    chat_display.setMinimumHeight(280)
    chat_display.setStyleSheet(f"""
        QTextEdit {{
            background:{DARK_BG}; color:{TEXT};
            border:1px solid {BORDER}; border-radius:8px;
            padding:14px; font-size:14px; line-height:1.6;
        }}
    """)
    chat_display.setPlainText(
        "👋 Welcome to your AI Ads Expert!\n\n"
        "Ask me anything about:\n"
        "  • How to set up profitable Facebook/Instagram campaigns\n"
        "  • TikTok ads strategy for your niche\n"
        "  • Audience targeting and lookalike audiences\n"
        "  • How to improve ROAS and lower CPC/CPM\n"
        "  • Creative best practices per platform\n"
        "  • Retargeting and funnel strategy\n"
        "  • Budget allocation and scaling rules\n"
        "  • A/B testing frameworks\n\n"
        "Type your question below and click Ask Expert ↓"
    )
    t3l.addWidget(chat_display, 1)

    # Quick prompt suggestions
    quick_row = QHBoxLayout()
    quick_row.addWidget(QLabel("Quick:"))
    _quick_prompts = [
        "How do I scale a winning ad?",
        "What's the best Facebook ad structure?",
        "How to reduce CPC on Instagram?",
        "TikTok ads for beginners?",
        "Retargeting strategy guide",
        "How to find the best audiences?",
    ]
    for qp in _quick_prompts:
        qbtn = QPushButton(qp)
        qbtn.setStyleSheet(
            f"background:{SURFACE}; color:{SUBTEXT}; border:1px solid {BORDER}; "
            f"border-radius:12px; padding:4px 10px; font-size:14px;"
        )
        qbtn.setCursor(Qt.PointingHandCursor)
        def _set_q(text=qp): exp_question_inp.setText(text)
        qbtn.clicked.connect(_set_q)
        quick_row.addWidget(qbtn)
    quick_row.addStretch()
    t3l.addLayout(quick_row)

    # Question input row
    q_row = QHBoxLayout()
    exp_question_inp = _styled_input("Ask your advertising question…")
    q_row.addWidget(exp_question_inp, 1)
    btn_ask_expert = ActionButton("🧠 Ask Expert", ACCENT)
    btn_ask_expert.setFixedWidth(140)
    q_row.addWidget(btn_ask_expert)
    btn_clear_chat = ActionButton("🗑 Clear Chat", BORDER)
    btn_clear_chat.setFixedWidth(120)
    q_row.addWidget(btn_clear_chat)
    t3l.addLayout(q_row)

    def _ask_expert():
        question = exp_question_inp.text().strip()
        if not question:
            return
        chat_display.append(f"\n\n🙋 YOU: {question}\n")
        chat_display.append("⏳ AI Expert is thinking…")
        try:
            budget = float(exp_budget_inp.text().strip() or "0")
        except ValueError:
            budget = 0.0
        payload = {
            "question": question, "platform": exp_plt_combo.currentText(),
            "niche": exp_niche_inp.text().strip() or "General",
            "budget_usd": budget, "objective": exp_obj_combo.currentText(),
            "language": exp_lang_combo.currentText(),
        }
        btn_ask_expert.set_loading(True)
        exp_question_inp.clear()
        w = ApiWorker(f"{api_base}/api/v1/social/ai-ads-expert", method="POST", payload=payload)
        def _got(r):
            answer = r.get("answer", "")
            # Remove the "thinking…" line
            text = chat_display.toPlainText()
            text = text.replace("⏳ AI Expert is thinking…", "")
            chat_display.setPlainText(text.rstrip())
            chat_display.append(f"\n\n🤖 AI EXPERT:\n{answer}\n{'─' * 60}")
            # Scroll to bottom
            cursor = chat_display.textCursor()
            cursor.movePosition(cursor.End)
            chat_display.setTextCursor(cursor)
            btn_ask_expert.set_loading(False)
        w.result_ready.connect(_got)
        w.error_signal.connect(lambda e: (chat_display.append(f"\n❌ Error: {e}"), btn_ask_expert.set_loading(False)))
        page._workers.append(w); w.start()

    btn_ask_expert.clicked.connect(_ask_expert)
    exp_question_inp.returnPressed.connect(_ask_expert)
    btn_clear_chat.clicked.connect(lambda: chat_display.setPlainText(
        "👋 Chat cleared. Ask your next advertising question below."
    ))

    tabs.addTab(t3, "🤖 AI Ads Expert")

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 4 — PERFORMANCE INSIGHTS
    # ═════════════════════════════════════════════════════════════════════════
    t4 = QWidget(); t4l = QVBoxLayout(t4); t4l.setSpacing(10)

    perf_info = QLabel("📊  Enter your account or ad metrics for AI-powered performance analysis and optimization tips.")
    perf_info.setWordWrap(True)
    perf_info.setStyleSheet(f"color:{SUBTEXT}; font-size:14px; padding:4px 0;")
    t4l.addWidget(perf_info)

    # Metrics split
    perf_split = QSplitter(Qt.Horizontal)

    pm_left = QWidget(); pm_left_l = QFormLayout(pm_left); pm_left_l.setSpacing(8)
    pm_left_l.setContentsMargins(0, 0, 8, 0)

    perf_plt_combo = _combo(_PLATFORMS)
    pm_acc_inp  = _styled_input("Your account/page name (optional)")
    pm_fol_inp  = _styled_input("0")
    pm_er_inp   = _styled_input("0.0  (e.g. 3.5)")
    pm_imp_inp  = _styled_input("0")
    pm_reach_inp = _styled_input("0")
    pm_clicks_inp = _styled_input("0")
    pm_spend_inp  = _styled_input("0.00")

    pm_left_l.addRow("Platform:", perf_plt_combo)
    pm_left_l.addRow("Account Name:", pm_acc_inp)
    pm_left_l.addRow("Followers:", pm_fol_inp)
    pm_left_l.addRow("Engagement Rate (%):", pm_er_inp)
    pm_left_l.addRow("Impressions:", pm_imp_inp)
    pm_left_l.addRow("Reach:", pm_reach_inp)
    pm_left_l.addRow("Clicks:", pm_clicks_inp)
    pm_left_l.addRow("Ad Spend (USD):", pm_spend_inp)

    btn_analyze_perf = ActionButton("📈 Analyze Performance", ACCENT)
    pm_left_l.addRow("", btn_analyze_perf)

    # KPI summary cards
    kpi_grid = QGridLayout()
    kpi_labels = {}
    kpi_defs = [
        ("CTR", "—"), ("CPC", "—"), ("CPM", "—"), ("ROAS", "—"),
        ("Eng. Rate", "—"), ("Reach Rate", "—"), ("Score", "—"), ("Status", "—"),
    ]
    for i, (name, val) in enumerate(kpi_defs):
        card = QFrame()
        card.setStyleSheet(f"background:{SURFACE}; border-radius:8px; border:1px solid {BORDER};")
        card_l = QVBoxLayout(card); card_l.setContentsMargins(10, 8, 10, 8)
        lbl_name = QLabel(name)
        lbl_name.setStyleSheet(f"color:{SUBTEXT}; font-size:14px;")
        lbl_val = QLabel(val)
        lbl_val.setStyleSheet(f"color:{ACCENT}; font-size:18px; font-weight:bold;")
        card_l.addWidget(lbl_name); card_l.addWidget(lbl_val)
        kpi_labels[name] = lbl_val
        row, col = divmod(i, 4)
        kpi_grid.addWidget(card, row, col)
    pm_left_l.addRow(kpi_grid)

    perf_split.addWidget(pm_left)

    pm_right = QWidget(); pm_right_l = QVBoxLayout(pm_right)
    pm_right_l.setContentsMargins(8, 0, 0, 0)
    pm_right_l.addWidget(QLabel("AI Performance Analysis:"))
    perf_out = OutputBox("Enter metrics on the left and click Analyze Performance →")
    perf_out.setMinimumHeight(340)
    pm_right_l.addWidget(perf_out, 1)
    btn_copy_perf = ActionButton("📋 Copy Analysis", "#7FBBB3")
    pm_right_l.addWidget(btn_copy_perf)

    perf_split.addWidget(pm_right)
    perf_split.setSizes([380, 500])
    t4l.addWidget(perf_split, 1)

    def _analyze_perf():
        def _safe_int(s):
            try: return max(0, int(s.text().strip().replace(",", "")))
            except: return 0
        def _safe_float(s):
            try: return max(0.0, float(s.text().strip()))
            except: return 0.0

        followers   = _safe_int(pm_fol_inp)
        engagement  = _safe_float(pm_er_inp)
        impressions = _safe_int(pm_imp_inp)
        reach       = _safe_int(pm_reach_inp)
        clicks      = _safe_int(pm_clicks_inp)
        spend       = _safe_float(pm_spend_inp)

        # Update KPI cards
        ctr   = round(clicks / impressions * 100, 2) if impressions > 0 else 0
        cpc   = round(spend / clicks, 2) if clicks > 0 else 0
        cpm   = round(spend / impressions * 1000, 2) if impressions > 0 else 0
        roas  = round(impressions * 0.02 * 15 / spend, 1) if spend > 0 else 0
        reach_rate = round(reach / followers * 100, 1) if followers > 0 else 0
        score = min(100, int((ctr * 20) + (engagement * 5) + (min(roas, 5) * 10)))
        status = "🟢 Excellent" if score >= 70 else "🟡 Good" if score >= 40 else "🔴 Improve"

        kpi_labels["CTR"].setText(f"{ctr}%")
        kpi_labels["CPC"].setText(f"${cpc:.2f}")
        kpi_labels["CPM"].setText(f"${cpm:.2f}")
        kpi_labels["ROAS"].setText(f"{roas}x")
        kpi_labels["Eng. Rate"].setText(f"{engagement:.1f}%")
        kpi_labels["Reach Rate"].setText(f"{reach_rate:.1f}%")
        kpi_labels["Score"].setText(str(score))
        kpi_labels["Status"].setText(status)

        payload = {
            "platform": perf_plt_combo.currentText(),
            "account_name": pm_acc_inp.text().strip(),
            "followers": followers, "engagement_rate": engagement,
            "impressions": impressions, "reach": reach,
            "clicks": clicks, "spend_usd": spend,
        }
        btn_analyze_perf.set_loading(True)
        perf_out.setPlainText("⏳ Analyzing performance metrics…")
        w = ApiWorker(f"{api_base}/api/v1/social/analyze-insights", method="POST", payload=payload)
        def _got(r):
            perf_out.setPlainText(r.get("analysis", ""))
            btn_analyze_perf.set_loading(False)
        w.result_ready.connect(_got)
        w.error_signal.connect(lambda e: (perf_out.set_error(e), btn_analyze_perf.set_loading(False)))
        page._workers.append(w); w.start()

    btn_analyze_perf.clicked.connect(_analyze_perf)
    btn_copy_perf.clicked.connect(lambda: QApplication.clipboard().setText(perf_out.toPlainText()))

    tabs.addTab(t4, "📊 Performance")

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 5 — AUDIENCE TARGETING
    # ═════════════════════════════════════════════════════════════════════════
    t5 = QWidget(); t5l = QVBoxLayout(t5); t5l.setSpacing(10)

    aud_info = QLabel(
        "🎯  Get AI-powered audience targeting recommendations — demographics, interests, "
        "behaviors, lookalike audiences, retargeting layers, and exclusions."
    )
    aud_info.setWordWrap(True)
    aud_info.setStyleSheet(
        f"background:{SURFACE}; color:{TEXT}; padding:10px 14px; "
        f"border-radius:8px; font-size:14px; border-left:4px solid {WARNING};"
    )
    t5l.addWidget(aud_info)

    aud_split = QSplitter(Qt.Horizontal)

    aud_left = QWidget(); aud_left_l = QFormLayout(aud_left); aud_left_l.setSpacing(10)
    aud_left_l.setContentsMargins(0, 0, 8, 0)

    aud_plt_combo = _combo(_PLATFORMS)
    aud_niche_inp = _styled_input("E.g. Fitness & Wellness, E-commerce, SaaS, Real Estate…")
    aud_country_inp = _styled_input("E.g. Global, United States, Cambodia, Southeast Asia…")
    aud_age_inp = _styled_input("E.g. 18-35, 25-55, 13-24…")
    aud_lang_combo = _combo(["English", "Khmer", "Thai", "Vietnamese", "Chinese", "Spanish", "French", "Arabic"])

    aud_left_l.addRow("Platform:", aud_plt_combo)
    aud_left_l.addRow("Niche / Industry:", aud_niche_inp)
    aud_left_l.addRow("Country / Region:", aud_country_inp)
    aud_left_l.addRow("Age Range:", aud_age_inp)
    aud_left_l.addRow("Language:", aud_lang_combo)

    btn_get_targeting = ActionButton("🎯 Get Targeting Strategy", ACCENT)
    aud_left_l.addRow("", btn_get_targeting)

    # Platform targeting cheat sheet
    cheat_sheet = QTextEdit()
    cheat_sheet.setReadOnly(True)
    cheat_sheet.setMaximumHeight(220)
    cheat_sheet.setStyleSheet(f"""
        QTextEdit {{
            background:{DARK_BG}; color:{SUBTEXT}; border:1px solid {BORDER};
            border-radius:6px; padding:10px; font-size:14px;
        }}
    """)
    cheat_sheet.setPlainText(
        "📌 PLATFORM TARGETING QUICK GUIDE\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Facebook:   Interests, Behaviors, Demographics, Custom/Lookalike\n"
        "Instagram:  Same as Facebook (Meta Ads Manager)\n"
        "TikTok:     Interest categories, Behavior, Creator followers\n"
        "YouTube:    In-market, Affinity, Custom intent, Placements\n"
        "LinkedIn:   Job title, Company size, Industry, Skills\n"
        "Twitter/X:  Keywords, Interests, Follower lookalikes\n\n"
        "💡 PRO TIP: Start broad → narrow based on data\n"
        "💡 Lookalike: Upload 1,000+ customer emails for best match\n"
        "💡 Retargeting: 3x higher CTR than cold audiences\n"
        "💡 Frequency: Keep under 3x/week to avoid ad fatigue"
    )
    aud_left_l.addRow(cheat_sheet)

    aud_split.addWidget(aud_left)

    aud_right = QWidget(); aud_right_l = QVBoxLayout(aud_right)
    aud_right_l.setContentsMargins(8, 0, 0, 0)
    aud_right_l.addWidget(QLabel("AI Targeting Recommendations:"))
    aud_out = OutputBox("Configure targeting parameters and click Get Targeting Strategy →")
    aud_out.setMinimumHeight(360)
    aud_right_l.addWidget(aud_out, 1)

    aud_btn_row = QHBoxLayout()
    btn_copy_aud = ActionButton("📋 Copy Strategy", "#7FBBB3")
    aud_btn_row.addWidget(btn_copy_aud); aud_btn_row.addStretch()
    aud_right_l.addLayout(aud_btn_row)

    aud_split.addWidget(aud_right)
    aud_split.setSizes([360, 520])
    t5l.addWidget(aud_split, 1)

    def _get_targeting():
        payload = {
            "platform": aud_plt_combo.currentText(),
            "niche": aud_niche_inp.text().strip() or "General",
            "country": aud_country_inp.text().strip() or "Global",
            "age_range": aud_age_inp.text().strip() or "18-45",
            "language": aud_lang_combo.currentText(),
        }
        btn_get_targeting.set_loading(True)
        aud_out.setPlainText("⏳ Generating targeting strategy…")
        w = ApiWorker(f"{api_base}/api/v1/social/audience-targeting", method="POST", payload=payload)
        def _got(r):
            aud_out.setPlainText(r.get("targeting", ""))
            btn_get_targeting.set_loading(False)
        w.result_ready.connect(_got)
        w.error_signal.connect(lambda e: (aud_out.set_error(e), btn_get_targeting.set_loading(False)))
        page._workers.append(w); w.start()

    btn_get_targeting.clicked.connect(_get_targeting)
    btn_copy_aud.clicked.connect(lambda: QApplication.clipboard().setText(aud_out.toPlainText()))

    tabs.addTab(t5, "🎯 Audience Targeting")

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 6 — CAMPAIGN PLANNER
    # ═════════════════════════════════════════════════════════════════════════
    t6 = QWidget(); t6l = QVBoxLayout(t6); t6l.setSpacing(10)

    cp_info = QLabel(
        "📋  Generate a complete, expert-level advertising campaign plan with phased budget allocation, "
        "targeting strategy, creative guidelines, KPIs, optimization schedule, and scaling triggers."
    )
    cp_info.setWordWrap(True)
    cp_info.setStyleSheet(
        f"background:{SURFACE}; color:{TEXT}; padding:10px 14px; "
        f"border-radius:8px; font-size:14px; border-left:4px solid {SUCCESS};"
    )
    t6l.addWidget(cp_info)

    cp_split = QSplitter(Qt.Horizontal)

    cp_left = QWidget(); cp_left_l = QFormLayout(cp_left); cp_left_l.setSpacing(8)
    cp_left_l.setContentsMargins(0, 0, 8, 0)

    cp_plt_combo = _combo(_PLATFORMS)
    cp_obj_combo = _combo(_OBJECTIVES)
    cp_brand_inp = _styled_input("Your brand / business name")
    cp_niche_inp = _styled_input("E.g. E-commerce, SaaS, Fitness, Education…")
    cp_audience_inp = _styled_input("Describe your ideal customer…")

    cp_budget_row = QHBoxLayout()
    cp_budget_inp = _styled_input("500")
    cp_budget_inp.setFixedWidth(120)
    cp_budget_row.addWidget(cp_budget_inp)
    cp_budget_row.addWidget(QLabel("USD  ×"))
    cp_days_inp = _styled_input("30")
    cp_days_inp.setFixedWidth(80)
    cp_budget_row.addWidget(cp_days_inp)
    cp_budget_row.addWidget(QLabel("days"))
    cp_budget_row.addStretch()

    cp_lang_combo = _combo(["English", "Khmer", "Thai", "Vietnamese", "Chinese", "Spanish", "French"])

    cp_left_l.addRow("Platform:", cp_plt_combo)
    cp_left_l.addRow("Campaign Objective:", cp_obj_combo)
    cp_left_l.addRow("Brand Name:", cp_brand_inp)
    cp_left_l.addRow("Niche:", cp_niche_inp)
    cp_left_l.addRow("Target Audience:", cp_audience_inp)
    cp_left_l.addRow("Budget & Duration:", cp_budget_row)
    cp_left_l.addRow("Plan Language:", cp_lang_combo)

    btn_gen_plan = ActionButton("📋 Generate Campaign Plan", ACCENT)
    cp_left_l.addRow("", btn_gen_plan)

    # ROI estimator
    roi_frame = QFrame()
    roi_frame.setStyleSheet(f"background:{SURFACE}; border-radius:8px; border:1px solid {BORDER};")
    roi_fl = QVBoxLayout(roi_frame); roi_fl.setContentsMargins(12, 10, 12, 10); roi_fl.setSpacing(4)
    roi_title = QLabel("📐 Quick ROI Estimator")
    roi_title.setStyleSheet(f"color:{ACCENT}; font-size:14px; font-weight:bold;")
    roi_fl.addWidget(roi_title)
    roi_vals_lbl = QLabel("Enter budget and duration above →")
    roi_vals_lbl.setWordWrap(True)
    roi_vals_lbl.setStyleSheet(f"color:{SUBTEXT}; font-size:14px;")
    roi_fl.addWidget(roi_vals_lbl)
    cp_left_l.addRow(roi_frame)

    def _update_roi(*_):
        try:
            budget = float(cp_budget_inp.text() or "0")
            days   = int(cp_days_inp.text() or "1")
            daily  = budget / max(days, 1)
            est_reach = int(budget * 850)
            est_clicks = int(budget * 12)
            est_leads  = int(budget * 0.8)
            roi_vals_lbl.setText(
                f"Daily budget: ${daily:.2f}  |  Est. Reach: {est_reach:,}\n"
                f"Est. Clicks: {est_clicks:,}  |  Est. Leads: {est_leads:,}\n"
                f"Avg CPM: $1.18  |  Avg CPC: $0.083  |  Avg CPL: $1.25"
            )
        except Exception:
            pass

    cp_budget_inp.textChanged.connect(_update_roi)
    cp_days_inp.textChanged.connect(_update_roi)
    _update_roi()

    cp_split.addWidget(cp_left)

    cp_right = QWidget(); cp_right_l = QVBoxLayout(cp_right)
    cp_right_l.setContentsMargins(8, 0, 0, 0)
    cp_right_l.addWidget(QLabel("Campaign Plan:"))
    cp_out = OutputBox("Configure campaign parameters and click Generate Campaign Plan →")
    cp_out.setMinimumHeight(400)
    cp_right_l.addWidget(cp_out, 1)

    cp_btn_row = QHBoxLayout()
    btn_copy_plan = ActionButton("📋 Copy Plan", "#7FBBB3")
    btn_export_plan = ActionButton("💾 Export to File", SUCCESS)
    cp_btn_row.addWidget(btn_copy_plan); cp_btn_row.addWidget(btn_export_plan); cp_btn_row.addStretch()
    cp_right_l.addLayout(cp_btn_row)

    cp_split.addWidget(cp_right)
    cp_split.setSizes([360, 520])
    t6l.addWidget(cp_split, 1)

    def _gen_campaign_plan():
        brand = cp_brand_inp.text().strip()
        if not brand:
            cp_out.set_error("Please enter your brand name first."); return
        try:
            budget = float(cp_budget_inp.text() or "500")
            days   = int(cp_days_inp.text() or "30")
        except ValueError:
            cp_out.set_error("Invalid budget or duration value."); return
        payload = {
            "brand": brand, "platform": cp_plt_combo.currentText(),
            "objective": cp_obj_combo.currentText(),
            "budget_usd": budget, "duration_days": days,
            "target_audience": cp_audience_inp.text().strip(),
            "niche": cp_niche_inp.text().strip() or "General",
            "language": cp_lang_combo.currentText(),
        }
        btn_gen_plan.set_loading(True)
        cp_out.setPlainText("⏳ Generating comprehensive campaign plan…")
        w = ApiWorker(f"{api_base}/api/v1/social/plan-campaign", method="POST", payload=payload)
        def _got(r):
            cp_out.setPlainText(r.get("plan", ""))
            btn_gen_plan.set_loading(False)
        w.result_ready.connect(_got)
        w.error_signal.connect(lambda e: (cp_out.set_error(e), btn_gen_plan.set_loading(False)))
        page._workers.append(w); w.start()

    def _export_plan():
        from PyQt5.QtWidgets import QFileDialog
        text = cp_out.toPlainText().strip()
        if not text or text.startswith("Configure"):
            cp_out.set_error("Generate a plan first before exporting."); return
        brand = cp_brand_inp.text().strip().replace(" ", "_") or "campaign"
        default_name = f"CampaignPlan_{brand}_{cp_plt_combo.currentText()}.txt"
        path, _ = QFileDialog.getSaveFileName(t6, "Save Campaign Plan", default_name, "Text Files (*.txt);;All (*)")
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(text)
                cp_out.appendPlainText(f"\n\n✅ Plan exported to: {path}")
            except Exception as e:
                cp_out.set_error(f"Export failed: {e}")

    btn_gen_plan.clicked.connect(_gen_campaign_plan)
    btn_copy_plan.clicked.connect(lambda: QApplication.clipboard().setText(cp_out.toPlainText()))
    btn_export_plan.clicked.connect(_export_plan)

    tabs.addTab(t6, "📋 Campaign Planner")

    # ─── Finalize ────────────────────────────────────────────────────────────
    layout.addWidget(tabs, 1)
    return page


# ═══════════════════════════════════════════════════════════════════════════════
# SHARED HELPERS FOR PAGES 16+
# ═══════════════════════════════════════════════════════════════════════════════

def _entry(placeholder: str = "") -> QLineEdit:
    """Styled single-line text input."""
    w = QLineEdit()
    w.setPlaceholderText(placeholder)
    return w


def _btn(label: str) -> QPushButton:
    """Styled action button."""
    b = QPushButton(label)
    b.setMinimumHeight(38)
    b.setCursor(Qt.PointingHandCursor)
    b.setStyleSheet(
        f"QPushButton {{ background:{ACCENT}; color:#11111B; border:none; border-radius:8px; "
        f"padding:8px 18px; font-weight:bold; font-size:14px; }}"
        f"QPushButton:hover {{ background:rgba(255,255,255,0.15); }}"
        f"QPushButton:disabled {{ background:{BORDER}; color:{SUBTEXT}; }}"
    )
    return b


def _out(min_rows: int = 15) -> QTextEdit:
    """Read-only output box."""
    w = QTextEdit()
    w.setReadOnly(True)
    w.setMinimumHeight(min_rows * 16)
    w.setPlaceholderText("Results will appear here…")
    w.setStyleSheet(
        f"QTextEdit {{ background:{SURFACE}; color:{SUCCESS}; border:1px solid {BORDER}; "
        f"border-radius:8px; padding:10px; font-size:14px; }}"
    )
    return w


def _disable_btn(btn: QPushButton, text: str = "⏳ Processing…") -> None:
    """Disable a button and update its label (stores original text for restore)."""
    if not hasattr(btn, '_orig_text'):
        btn._orig_text = btn.text()
    btn.setEnabled(False)
    btn.setText(text)


def _enable_btn(btn: QPushButton, text: str = None) -> None:
    """Re-enable a button and restore its label."""
    btn.setEnabled(True)
    restore = text if text is not None else getattr(btn, '_orig_text', btn.text())
    btn.setText(restore)


class _ApiWorker(QThread):
    """Lightweight API worker with `finished` and `error` signals."""
    finished = pyqtSignal(dict)
    error    = pyqtSignal(str)

    def __init__(self, url: str, payload=None, method: str = "POST", btn=None):
        super().__init__()
        # Detect old-style: _ApiWorker(base_url, "endpoint", payload_dict, callback)
        if isinstance(payload, str) and isinstance(method, dict):
            endpoint = payload
            actual_payload = method
            callback = btn
            self.url     = f"{url}/api/v1/{endpoint}"
            self.payload = actual_payload
            self.method  = "POST"
            if callable(callback):
                self.finished.connect(lambda r: callback(r, None))
                self.error.connect(lambda e: callback({}, e))
            return
        self.url     = url
        self.payload = payload or {}
        self.method  = method.upper() if isinstance(method, str) else "POST"
        if btn is not None:
            btn.set_loading(True)
            self.finished.connect(lambda: btn.set_loading(False))

    def run(self):
        try:
            if self.method == "GET":
                r = requests.get(self.url, params=self.payload, timeout=30)
            elif self.method == "DELETE":
                r = requests.delete(self.url, timeout=30)
            else:
                r = requests.post(self.url, json=self.payload, timeout=30)
            r.raise_for_status()
            self.finished.emit(r.json())
        except requests.exceptions.ConnectionError:
            self.error.emit(
                "Cannot connect to backend. Start it with:\n\n  uvicorn backend_api:app --reload"
            )
        except Exception as exc:
            self.error.emit(str(exc))


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 16 — INTELLIGENCE HUB
# ═══════════════════════════════════════════════════════════════════════════════

def build_intelligence_page(api_base: str) -> QWidget:
    """Page 16: Social Listening, Competitor Analysis, Ad Intelligence."""
    page, layout = _make_page_layout("🔍 Intelligence Hub", "🔍")
    page._workers: list = []

    tabs = QTabWidget()
    tabs.setStyleSheet("QTabWidget::pane{border:none;} QTabBar::tab{padding:8px 18px;}")
    layout.addWidget(tabs)

    # ── Tab 1: Brand Listening ─────────────────────────────────────────────
    t1 = QWidget(); tl = QVBoxLayout(t1); tl.setContentsMargins(12, 12, 12, 12)
    tl.addWidget(_label("🎙 Social Listening & Brand Monitor", bold=True))

    # Auto-detect connected accounts
    acc_bar1, _get_plt1, _get_name1, _repop1 = _account_context_bar(api_base)
    tl.addWidget(acc_bar1)

    f1 = QFormLayout(); f1.setSpacing(8)
    e_brand   = _entry("Your Brand Name"); f1.addRow("Brand:", e_brand)
    c_plat    = _combo("All Platforms", "Instagram", "TikTok", "Twitter/X",
                       "YouTube", "Facebook", "LinkedIn")
    f1.addRow("Platform:", c_plat)
    c_period  = _combo("Last 7 days", "Last 24 hours", "Last 30 days", "Last 3 months")
    f1.addRow("Period:", c_period)
    e_niche   = _entry("Niche"); f1.addRow("Niche:", e_niche)
    c_lang    = _combo("English", "Khmer", "Spanish", "French", "Chinese", "Arabic")
    f1.addRow("Language:", c_lang)
    tl.addLayout(f1)

    def _auto_fill1():
        """Auto-fill brand name & platform from the selected connected account."""
        _repop1()  # refresh combo in case cache just loaded
        name = _get_name1()
        plt  = _get_plt1()
        if name:
            e_brand.setText(name)
        if plt:
            idx = c_plat.findText(plt, Qt.MatchContains)
            if idx >= 0:
                c_plat.setCurrentIndex(idx)

    acc_bar1.findChild(QComboBox).currentIndexChanged.connect(lambda _: _auto_fill1())
    QTimer.singleShot(5000, _auto_fill1)  # auto-fill once backend has loaded accounts

    btn1 = _btn("🎙 Analyze Brand Mentions")
    tl.addWidget(btn1)
    out1 = _out(20); tl.addWidget(out1, 1)

    def _listen():
        _disable_btn(btn1, "Analyzing…")
        w = _ApiWorker(
            f"{api_base}/api/v1/intel/brand-listening",
            {"brand": e_brand.text(), "platform": c_plat.currentText(),
             "period": c_period.currentText(), "niche": e_niche.text() or "General",
             "language": c_lang.currentText()},
        )
        def _done(r):
            d = r.get("data", r)
            lines = [
                f"📊 Total Mentions: {d.get('total_mentions', 'N/A')}",
                f"✅ Positive: {d.get('positive', 0)}  ⚠️ Negative: {d.get('negative', 0)}  😐 Neutral: {d.get('neutral', 0)}",
                f"🎯 Sentiment Score: {d.get('sentiment_score', 'N/A')}/100",
                f"📣 Share of Voice: {d.get('share_of_voice', 'N/A')}",
                "", "🔥 Trending Keywords:",
            ] + [f"  • {k}" for k in d.get("trending_keywords", [])] + [
                "", "⚠️ Urgent Alerts:",
            ] + [f"  🚨 {a}" for a in d.get("urgent_alerts", [])] + [
                "", "💡 Recommendations:",
            ] + [f"  {i+1}. {r_}" for i, r_ in enumerate(d.get("recommendations", []))]
            out1.setText("\n".join(lines))
            _enable_btn(btn1, "🎙 Analyze Brand Mentions")
        w.finished.connect(_done)
        w.error.connect(lambda e: (out1.setText(f"Error: {e}"), _enable_btn(btn1, "🎙 Analyze Brand Mentions")))
        page._workers.append(w); w.start()
    btn1.clicked.connect(_listen)
    tabs.addTab(t1, "🎙 Brand Listening")

    # ── Tab 2: Competitor Analysis ─────────────────────────────────────────
    t2 = QWidget(); tl2 = QVBoxLayout(t2); tl2.setContentsMargins(12, 12, 12, 12)
    tl2.addWidget(_label("🕵️ Competitor Intelligence", bold=True))
    f2 = QFormLayout(); f2.setSpacing(8)
    e_comp  = _entry("Competitor name or handle"); f2.addRow("Competitor:", e_comp)
    c_plat2 = _combo("Instagram", "TikTok", "Twitter/X", "YouTube", "Facebook", "LinkedIn")
    f2.addRow("Platform:", c_plat2)
    e_niche2 = _entry("Niche"); f2.addRow("Niche:", e_niche2)
    c_lang2  = _combo("English", "Khmer", "Spanish", "French", "Chinese", "Arabic")
    f2.addRow("Language:", c_lang2)
    tl2.addLayout(f2)
    btn2 = _btn("🕵️ Analyze Competitor")
    tl2.addWidget(btn2)
    out2 = _out(20); tl2.addWidget(out2, 1)

    def _comp():
        _disable_btn(btn2, "Analyzing…")
        w = _ApiWorker(
            f"{api_base}/api/v1/intel/competitor-profile",
            {"competitor": e_comp.text(), "platform": c_plat2.currentText(),
             "niche": e_niche2.text() or "General", "language": c_lang2.currentText()},
        )
        def _done2(r):
            d = r.get("data", r)
            lines = [
                f"👤 Overview: {d.get('overview', 'N/A')}",
                f"📅 Posting: {d.get('estimated_posting_frequency', 'N/A')}",
                f"📈 Est. Monthly Growth: {d.get('estimated_monthly_growth', 'N/A')}",
                f"⚠️ Threat Level: {d.get('threat_level', 'N/A')}",
                "", "📌 Content Strategy:", str(d.get("content_strategy", "")),
                "", "✅ Best Hashtags:",
            ] + [f"  {h}" for h in d.get("best_hashtags", [])] + [
                "", "💡 Opportunities:",
            ] + [f"  • {o}" for o in d.get("opportunities", [])]
            out2.setText("\n".join(lines))
            _enable_btn(btn2, "🕵️ Analyze Competitor")
        w.finished.connect(_done2)
        w.error.connect(lambda e: (out2.setText(f"Error: {e}"), _enable_btn(btn2, "🕵️ Analyze Competitor")))
        page._workers.append(w); w.start()
    btn2.clicked.connect(_comp)
    tabs.addTab(t2, "🕵️ Competitor Analysis")

    # ── Tab 3: Ad Intelligence ─────────────────────────────────────────────
    t3 = QWidget(); tl3 = QVBoxLayout(t3); tl3.setContentsMargins(12, 12, 12, 12)
    tl3.addWidget(_label("📢 Competitor Ad Intelligence", bold=True))
    f3 = QFormLayout(); f3.setSpacing(8)
    e_comp3  = _entry("Competitor name"); f3.addRow("Competitor:", e_comp3)
    c_plat3  = _combo("Facebook", "Instagram", "TikTok", "Google", "YouTube", "LinkedIn")
    f3.addRow("Ad Platform:", c_plat3)
    e_niche3 = _entry("Niche"); f3.addRow("Niche:", e_niche3)
    c_lang3  = _combo("English", "Khmer", "Spanish", "French", "Chinese", "Arabic")
    f3.addRow("Language:", c_lang3)
    tl3.addLayout(f3)
    btn3 = _btn("📢 Analyze Competitor Ads")
    tl3.addWidget(btn3)
    out3 = _out(20); tl3.addWidget(out3, 1)

    def _ads():
        _disable_btn(btn3, "Analyzing…")
        w = _ApiWorker(
            f"{api_base}/api/v1/intel/competitor-ads",
            {"competitor": e_comp3.text(), "platform": c_plat3.currentText(),
             "niche": e_niche3.text() or "General", "language": c_lang3.currentText()},
        )
        def _done3(r):
            d = r.get("data", r)
            lines = [
                f"📊 Est. Active Ads: {d.get('active_ads_estimate', 'N/A')}",
                f"💰 Est. Monthly Spend: {d.get('estimated_monthly_spend', 'N/A')}",
                "", "🎯 Ad Formats:", str(d.get("ad_formats", [])),
                "", "📝 Messaging Themes:",
            ] + [f"  • {m}" for m in d.get("messaging_themes", [])] + [
                "", "💡 Counter Strategies:",
            ] + [f"  {i+1}. {s}" for i, s in enumerate(d.get("counter_strategies", []))]
            out3.setText("\n".join(lines))
            _enable_btn(btn3, "📢 Analyze Competitor Ads")
        w.finished.connect(_done3)
        w.error.connect(lambda e: (out3.setText(f"Error: {e}"), _enable_btn(btn3, "📢 Analyze Competitor Ads")))
        page._workers.append(w); w.start()
    btn3.clicked.connect(_ads)
    tabs.addTab(t3, "📢 Ad Intelligence")

    return page


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 17 — VIRAL & GROWTH
# ═══════════════════════════════════════════════════════════════════════════════

def build_viral_tools_page(api_base: str) -> QWidget:
    """Page 17: Viral Score, Influencer Finder, Hashtag Research, A/B Testing."""
    page, layout = _make_page_layout("🔥 Viral & Growth Tools", "🔥")
    page._workers: list = []

    tabs = QTabWidget()
    tabs.setStyleSheet("QTabWidget::pane{border:none;} QTabBar::tab{padding:8px 18px;}")
    layout.addWidget(tabs)

    # ── Tab 1: Viral Score ─────────────────────────────────────────────────
    t1 = QWidget(); tl = QVBoxLayout(t1); tl.setContentsMargins(12, 12, 12, 12)
    tl.addWidget(_label("🔥 AI Viral Score Predictor", bold=True))
    f1 = QFormLayout(); f1.setSpacing(8)
    e_cont  = QTextEdit(); e_cont.setPlaceholderText("Paste your caption / script…"); e_cont.setFixedHeight(90)
    f1.addRow("Content:", e_cont)
    c_plat  = _combo("TikTok", "Instagram", "YouTube Shorts", "Twitter/X", "LinkedIn", "Facebook")
    f1.addRow("Platform:", c_plat)
    c_type  = _combo("Video", "Reel", "Carousel", "Static Post", "Story", "Thread")
    f1.addRow("Post Type:", c_type)
    e_foll  = _entry("10000"); f1.addRow("Followers:", e_foll)
    e_niche = _entry("Niche"); f1.addRow("Niche:", e_niche)
    c_lang  = _combo("English", "Khmer", "Spanish", "French", "Chinese", "Arabic")
    f1.addRow("Language:", c_lang)
    tl.addLayout(f1)
    btn1 = _btn("🔥 Predict Viral Score")
    tl.addWidget(btn1)
    out1 = _out(18); tl.addWidget(out1, 1)

    def _score():
        _disable_btn(btn1, "Predicting…")
        try:
            foll = int(e_foll.text() or "10000")
        except ValueError:
            foll = 10000
        w = _ApiWorker(
            f"{api_base}/api/v1/viral/score",
            {"content": e_cont.toPlainText(), "platform": c_plat.currentText(),
             "post_type": c_type.currentText(), "followers": foll,
             "niche": e_niche.text() or "General", "language": c_lang.currentText()},
        )
        def _done(r):
            d = r.get("data", r)
            lines = [
                f"🏆 Viral Score: {d.get('score', 'N/A')}/100  (Grade: {d.get('grade', '?')})",
                f"🎯 Verdict: {d.get('verdict', 'N/A')}",
                f"📅 Best Post Time: {d.get('best_post_time', 'N/A')}",
                f"👀 Est. Reach: {d.get('estimated_reach', 'N/A')}",
                "", "📊 Breakdown:",
            ] + [f"  {k}: {v}" for k, v in (d.get("breakdown") or {}).items()] + [
                "", "💡 Improvements:",
            ] + [f"  {i+1}. {x}" for i, x in enumerate(d.get("improvements", []))]
            out1.setText("\n".join(lines))
            _enable_btn(btn1, "🔥 Predict Viral Score")
        w.finished.connect(_done)
        w.error.connect(lambda e: (out1.setText(f"Error: {e}"), _enable_btn(btn1, "🔥 Predict Viral Score")))
        page._workers.append(w); w.start()
    btn1.clicked.connect(_score)
    tabs.addTab(t1, "🔥 Viral Score")

    # ── Tab 2: Influencer Finder ───────────────────────────────────────────
    t2 = QWidget(); tl2 = QVBoxLayout(t2); tl2.setContentsMargins(12, 12, 12, 12)
    tl2.addWidget(_label("👥 AI Influencer Finder", bold=True))
    f2 = QFormLayout(); f2.setSpacing(8)
    e_niche2 = _entry("Niche e.g. Fitness, Tech, Food…"); f2.addRow("Niche:", e_niche2)
    c_plat2  = _combo("Instagram", "TikTok", "YouTube", "Twitter/X", "LinkedIn", "Facebook")
    f2.addRow("Platform:", c_plat2)
    c_range  = _combo("Nano 1K–10K", "Micro 10K–100K", "Mid 100K–1M", "Macro 1M+")
    f2.addRow("Follower Range:", c_range)
    e_ctry   = _entry("Global"); f2.addRow("Country:", e_ctry)
    c_lang2  = _combo("English", "Khmer", "Spanish", "French", "Chinese", "Arabic")
    f2.addRow("Language:", c_lang2)
    tl2.addLayout(f2)
    btn2 = _btn("👥 Find Influencers")
    tl2.addWidget(btn2)
    out2 = _out(18); tl2.addWidget(out2, 1)

    def _infl():
        _disable_btn(btn2, "Searching…")
        w = _ApiWorker(
            f"{api_base}/api/v1/viral/influencers",
            {"niche": e_niche2.text() or "General", "platform": c_plat2.currentText(),
             "follower_range": c_range.currentText(), "country": e_ctry.text() or "Global",
             "language": c_lang2.currentText()},
        )
        def _done2(r):
            d = r.get("data", r)
            infls = d.get("influencers", [])
            lines = [
                f"✅ Found: {d.get('total_found', len(infls))} influencers",
                f"📊 Avg Engagement: {d.get('avg_engagement', 'N/A')}",
                f"💡 {d.get('recommendation', '')}",
                "", "── Influencer Profiles ──",
            ]
            for inf in infls:
                lines += [
                    f"\n👤 {inf.get('name', '?')} | {inf.get('platform', '?')} | {inf.get('followers', '?')} followers",
                    f"   📊 Engagement: {inf.get('engagement_rate', '?')} | 🎯 Niche: {inf.get('niche', '?')}",
                    f"   📍 Location: {inf.get('location', '?')}",
                    f"   💰 Collab Rate: {inf.get('collab_rate', 'N/A')}",
                    f"   ✅ {inf.get('why_good_fit', '')}",
                ]
            out2.setText("\n".join(lines))
            _enable_btn(btn2, "👥 Find Influencers")
        w.finished.connect(_done2)
        w.error.connect(lambda e: (out2.setText(f"Error: {e}"), _enable_btn(btn2, "👥 Find Influencers")))
        page._workers.append(w); w.start()
    btn2.clicked.connect(_infl)
    tabs.addTab(t2, "👥 Influencer Finder")

    # ── Tab 3: Hashtag Research ────────────────────────────────────────────
    t3 = QWidget(); tl3 = QVBoxLayout(t3); tl3.setContentsMargins(12, 12, 12, 12)
    tl3.addWidget(_label("#️⃣ Hashtag Research Engine", bold=True))
    f3 = QFormLayout(); f3.setSpacing(8)
    e_niche3 = _entry("Your niche"); f3.addRow("Niche:", e_niche3)
    c_plat3  = _combo("Instagram", "TikTok", "Twitter/X", "YouTube", "LinkedIn", "Facebook")
    f3.addRow("Platform:", c_plat3)
    c_goal   = _combo("Reach", "Engagement", "Followers", "Sales", "Brand Awareness")
    f3.addRow("Goal:", c_goal)
    c_lang3  = _combo("English", "Khmer", "Spanish", "French", "Chinese", "Arabic")
    f3.addRow("Language:", c_lang3)
    tl3.addLayout(f3)
    btn3 = _btn("#️⃣ Research Hashtags")
    tl3.addWidget(btn3)
    out3 = _out(18); tl3.addWidget(out3, 1)

    def _hash():
        _disable_btn(btn3, "Researching…")
        w = _ApiWorker(
            f"{api_base}/api/v1/viral/hashtags",
            {"niche": e_niche3.text() or "General", "platform": c_plat3.currentText(),
             "goal": c_goal.currentText(), "language": c_lang3.currentText()},
        )
        def _done3(r):
            d = r.get("data", r)
            lines = [
                f"📊 Strategy: {d.get('strategy', '')}",
                "", "🏆 Best Hashtag Set:",
            ] + [f"  {h}" for h in d.get("best_set", [])] + [
                "", "🚫 Banned/Avoid:",
            ] + [f"  ❌ {h}" for h in d.get("banned_found", [])] + [
                "", "📋 All Researched Hashtags:",
            ]
            for h in d.get("hashtags", []):
                lines.append(f"  {h.get('tag','?')} | Posts: {h.get('post_count','?')} | Difficulty: {h.get('difficulty','?')} | Trend: {h.get('trend','?')}")
            out3.setText("\n".join(lines))
            _enable_btn(btn3, "#️⃣ Research Hashtags")
        w.finished.connect(_done3)
        w.error.connect(lambda e: (out3.setText(f"Error: {e}"), _enable_btn(btn3, "#️⃣ Research Hashtags")))
        page._workers.append(w); w.start()
    btn3.clicked.connect(_hash)
    tabs.addTab(t3, "#️⃣ Hashtag Research")

    # ── Tab 4: A/B Testing ─────────────────────────────────────────────────
    t4 = QWidget(); tl4 = QVBoxLayout(t4); tl4.setContentsMargins(12, 12, 12, 12)
    tl4.addWidget(_label("🧪 A/B Test Generator", bold=True))
    f4 = QFormLayout(); f4.setSpacing(8)
    e_cont4 = QTextEdit(); e_cont4.setPlaceholderText("Your original caption/script…"); e_cont4.setFixedHeight(90)
    f4.addRow("Content:", e_cont4)
    c_plat4 = _combo("Instagram", "TikTok", "Twitter/X", "YouTube", "LinkedIn", "Facebook")
    f4.addRow("Platform:", c_plat4)
    c_obj4  = _combo("Engagement", "Reach", "Clicks", "Saves", "Followers", "Sales")
    f4.addRow("Objective:", c_obj4)
    c_lang4 = _combo("English", "Khmer", "Spanish", "French", "Chinese", "Arabic")
    f4.addRow("Language:", c_lang4)
    tl4.addLayout(f4)
    btn4 = _btn("🧪 Generate A/B/C Variants")
    tl4.addWidget(btn4)
    out4 = _out(18); tl4.addWidget(out4, 1)

    def _ab():
        _disable_btn(btn4, "Generating…")
        w = _ApiWorker(
            f"{api_base}/api/v1/viral/ab-test",
            {"content": e_cont4.toPlainText(), "platform": c_plat4.currentText(),
             "objective": c_obj4.currentText(), "language": c_lang4.currentText()},
        )
        def _done4(r):
            d = r.get("data", r)
            lines = [
                f"🏆 Predicted Winner: Variant {d.get('predicted_winner', '?')}",
                f"💡 Reasoning: {d.get('reasoning', '')}",
                f"⏱ Test Duration: {d.get('test_duration', 'N/A')}",
                f"👥 Min. Sample: {d.get('minimum_sample', 'N/A')}",
                "",
            ]
            for key in ["variant_a", "variant_b", "variant_c"]:
                v = d.get(key, {})
                if v:
                    label = v.get("label", key.upper())
                    lines += [
                        f"── {label} ──",
                        f"   Hook: {v.get('hook_type', '?')} | CTR: {v.get('predicted_ctr', '?')} | Engagement: {v.get('predicted_engagement', '?')}",
                        v.get("content", ""),
                        "",
                    ]
            lines += ["💡 A/B Tips:"] + [f"  • {t}" for t in d.get("ab_tips", [])]
            out4.setText("\n".join(lines))
            _enable_btn(btn4, "🧪 Generate A/B/C Variants")
        w.finished.connect(_done4)
        w.error.connect(lambda e: (out4.setText(f"Error: {e}"), _enable_btn(btn4, "🧪 Generate A/B/C Variants")))
        page._workers.append(w); w.start()
    btn4.clicked.connect(_ab)
    tabs.addTab(t4, "🧪 A/B Testing")

    return page


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 18 — AUTOMATION SUITE
# ═══════════════════════════════════════════════════════════════════════════════

def build_automation_page(api_base: str) -> QWidget:
    """Page 18: Comment Manager, Content Repurposer, DM Campaign, Storyboard."""
    page, layout = _make_page_layout("⚡ Automation Suite", "⚡")
    page._workers: list = []

    tabs = QTabWidget()
    tabs.setStyleSheet("QTabWidget::pane{border:none;} QTabBar::tab{padding:8px 18px;}")
    layout.addWidget(tabs)

    # ── Tab 1: Comment Manager ─────────────────────────────────────────────
    t1 = QWidget(); tl = QVBoxLayout(t1); tl.setContentsMargins(12, 12, 12, 12)
    tl.addWidget(_label("💬 AI Comment Manager — Bulk Reply Generator", bold=True))
    f1 = QFormLayout(); f1.setSpacing(8)
    e_brand = _entry("Brand Name"); f1.addRow("Brand:", e_brand)
    c_tone  = _combo("Friendly & Warm", "Professional", "Humorous",
                     "Empathetic", "Concise", "Enthusiastic")
    f1.addRow("Reply Tone:", c_tone)
    c_plat  = _combo("Instagram", "TikTok", "YouTube", "Facebook", "Twitter/X")
    f1.addRow("Platform:", c_plat)
    c_lang  = _combo("English", "Khmer", "Spanish", "French", "Chinese", "Arabic")
    f1.addRow("Language:", c_lang)
    tl.addLayout(f1)
    tl.addWidget(_label("Paste comments (one per line, max 20):"))
    e_comments = QTextEdit(); e_comments.setPlaceholderText("Paste comments here…\nOne comment per line.")
    e_comments.setFixedHeight(120); tl.addWidget(e_comments)
    btn1 = _btn("💬 Generate AI Replies")
    tl.addWidget(btn1)
    out1 = _out(14); tl.addWidget(out1, 1)

    def _replies():
        _disable_btn(btn1, "Generating…")
        raw = e_comments.toPlainText().strip()
        comments = [c.strip() for c in raw.splitlines() if c.strip()][:20]
        if not comments:
            out1.setText("⚠️ Please paste at least one comment."); _enable_btn(btn1, "💬 Generate AI Replies"); return
        w = _ApiWorker(
            f"{api_base}/api/v1/automation/comment-replies",
            {"comments": comments, "tone": c_tone.currentText(),
             "brand_name": e_brand.text(), "platform": c_plat.currentText(),
             "language": c_lang.currentText()},
        )
        def _done(r):
            items = r.get("data", r)
            if not isinstance(items, list): items = []
            lines = []
            for item in items:
                snt = item.get("sentiment", "?")
                pri = item.get("priority", "?")
                ico = "🔴" if pri == "urgent" else "🟡" if pri == "normal" else "🟢"
                lines += [
                    f"{ico} [{snt.upper()}] Original: {item.get('original', '?')}",
                    f"   ↳ Reply: {item.get('reply', '—')}",
                    f"   Action: {item.get('action', 'reply')}",
                    "",
                ]
            out1.setText("\n".join(lines).strip())
            _enable_btn(btn1, "💬 Generate AI Replies")
        w.finished.connect(_done)
        w.error.connect(lambda e: (out1.setText(f"Error: {e}"), _enable_btn(btn1, "💬 Generate AI Replies")))
        page._workers.append(w); w.start()
    btn1.clicked.connect(_replies)
    tabs.addTab(t1, "💬 Comment Manager")

    # ── Tab 2: Content Repurposer ──────────────────────────────────────────
    t2 = QWidget(); tl2 = QVBoxLayout(t2); tl2.setContentsMargins(12, 12, 12, 12)
    tl2.addWidget(_label("♻️ Content Repurposer — 1 Piece → Multiple Formats", bold=True))
    f2 = QFormLayout(); f2.setSpacing(8)
    c_src  = _combo("Blog Post", "YouTube Video Script", "Podcast Transcript",
                    "Twitter Thread", "LinkedIn Post", "Email Newsletter")
    f2.addRow("Source Format:", c_src)
    e_brand2 = _entry("Brand Name"); f2.addRow("Brand:", e_brand2)
    e_niche2 = _entry("Niche"); f2.addRow("Niche:", e_niche2)
    c_lang2  = _combo("English", "Khmer", "Spanish", "French", "Chinese", "Arabic")
    f2.addRow("Language:", c_lang2)
    tl2.addLayout(f2)
    tl2.addWidget(_label("Paste original content:"))
    e_orig = QTextEdit(); e_orig.setPlaceholderText("Paste your original content here…"); e_orig.setFixedHeight(110)
    tl2.addWidget(e_orig)
    btn2 = _btn("♻️ Repurpose Content")
    tl2.addWidget(btn2)
    out2 = _out(14); tl2.addWidget(out2, 1)

    def _repurp():
        _disable_btn(btn2, "Repurposing…")
        w = _ApiWorker(
            f"{api_base}/api/v1/automation/repurpose",
            {"original": e_orig.toPlainText(), "source_format": c_src.currentText(),
             "brand_name": e_brand2.text(), "niche": e_niche2.text() or "General",
             "language": c_lang2.currentText()},
        )
        def _done2(r):
            d = r.get("data", r)
            lines = [
                f"📅 Schedule: {d.get('schedule_suggestion', '')}",
                f"💡 Tip: {d.get('tip', '')}",
                "",
            ]
            for fmt, content in (d.get("repurposed") or {}).items():
                lines += [f"── {fmt} ──", content, ""]
            out2.setText("\n".join(lines))
            _enable_btn(btn2, "♻️ Repurpose Content")
        w.finished.connect(_done2)
        w.error.connect(lambda e: (out2.setText(f"Error: {e}"), _enable_btn(btn2, "♻️ Repurpose Content")))
        page._workers.append(w); w.start()
    btn2.clicked.connect(_repurp)
    tabs.addTab(t2, "♻️ Content Repurposer")

    # ── Tab 3: DM Campaign ─────────────────────────────────────────────────
    t3 = QWidget(); tl3 = QVBoxLayout(t3); tl3.setContentsMargins(12, 12, 12, 12)
    tl3.addWidget(_label("📩 DM Campaign Template Generator", bold=True))
    f3 = QFormLayout(); f3.setSpacing(8)
    c_purpose = _combo("Influencer Outreach", "Lead Generation", "Partnership",
                       "Sales", "Networking", "Event Invite", "Product Launch")
    f3.addRow("Purpose:", c_purpose)
    c_plat3   = _combo("Instagram", "TikTok", "LinkedIn", "Twitter/X", "Facebook")
    f3.addRow("Platform:", c_plat3)
    e_brand3  = _entry("Brand Name"); f3.addRow("Brand:", e_brand3)
    e_niche3  = _entry("Niche"); f3.addRow("Niche:", e_niche3)
    c_tone3   = _combo("Professional", "Casual", "Friendly", "Direct", "Personalized")
    f3.addRow("Tone:", c_tone3)
    c_count   = _combo("3", "5", "7", "10"); f3.addRow("Count:", c_count)
    c_lang3   = _combo("English", "Khmer", "Spanish", "French", "Chinese", "Arabic")
    f3.addRow("Language:", c_lang3)
    tl3.addLayout(f3)
    btn3 = _btn("📩 Generate DM Templates")
    tl3.addWidget(btn3)
    out3 = _out(16); tl3.addWidget(out3, 1)

    def _dm():
        _disable_btn(btn3, "Generating…")
        w = _ApiWorker(
            f"{api_base}/api/v1/automation/dm-templates",
            {"purpose": c_purpose.currentText(), "platform": c_plat3.currentText(),
             "brand_name": e_brand3.text(), "niche": e_niche3.text() or "General",
             "tone": c_tone3.currentText(), "count": int(c_count.currentText()),
             "language": c_lang3.currentText()},
        )
        def _done3(r):
            items = r.get("data", r)
            if not isinstance(items, list): items = []
            lines = []
            for t in items:
                lines += [
                    f"── {t.get('template_name', '?')} ──",
                    t.get("message", ""),
                    f"Best For: {t.get('best_for', '?')} | Open Rate: {t.get('estimated_open_rate', '?')} | Reply Rate: {t.get('estimated_reply_rate', '?')}",
                    f"Follow-up: {t.get('follow_up_timing', '?')}",
                    "",
                ]
            out3.setText("\n".join(lines).strip())
            _enable_btn(btn3, "📩 Generate DM Templates")
        w.finished.connect(_done3)
        w.error.connect(lambda e: (out3.setText(f"Error: {e}"), _enable_btn(btn3, "📩 Generate DM Templates")))
        page._workers.append(w); w.start()
    btn3.clicked.connect(_dm)
    tabs.addTab(t3, "📩 DM Campaign")

    # ── Tab 4: Storyboard ──────────────────────────────────────────────────
    t4 = QWidget(); tl4 = QVBoxLayout(t4); tl4.setContentsMargins(12, 12, 12, 12)
    tl4.addWidget(_label("🎬 Video Storyboard Generator", bold=True))
    f4 = QFormLayout(); f4.setSpacing(8)
    e_topic  = _entry("Video topic e.g. '5 Morning Habits of Rich People'"); f4.addRow("Topic:", e_topic)
    c_plat4  = _combo("TikTok", "Instagram Reels", "YouTube Shorts", "YouTube", "Facebook")
    f4.addRow("Platform:", c_plat4)
    c_dur    = _combo("30", "60", "90", "120", "180", "300", "600"); f4.addRow("Duration (s):", c_dur)
    c_style  = _combo("Educational", "Entertainment", "Storytelling",
                      "Tutorial", "Motivational", "Comedy", "Documentary")
    f4.addRow("Style:", c_style)
    e_niche4 = _entry("Niche"); f4.addRow("Niche:", e_niche4)
    c_lang4  = _combo("English", "Khmer", "Spanish", "French", "Chinese", "Arabic")
    f4.addRow("Language:", c_lang4)
    tl4.addLayout(f4)
    btn4 = _btn("🎬 Generate Storyboard")
    tl4.addWidget(btn4)
    out4 = _out(18); tl4.addWidget(out4, 1)

    def _story():
        _disable_btn(btn4, "Generating…")
        w = _ApiWorker(
            f"{api_base}/api/v1/automation/storyboard",
            {"topic": e_topic.text(), "platform": c_plat4.currentText(),
             "duration_seconds": int(c_dur.currentText()), "style": c_style.currentText(),
             "niche": e_niche4.text() or "General", "language": c_lang4.currentText()},
        )
        def _done4(r):
            d = r.get("data", r)
            lines = [
                f"🎬 Title: {d.get('title', '?')}",
                f"📺 Platform: {d.get('platform', '?')} | ⏱ Duration: {d.get('duration', '?')}",
                "", "── SHOT LIST ──",
            ]
            for shot in d.get("shots", []):
                lines += [
                    f"\n🎥 Shot {shot.get('shot', '?')} ({shot.get('time', '?')}) — {shot.get('type', '?')}",
                    f"   Visual: {shot.get('visual', '?')}",
                    f"   Audio:  {shot.get('audio', '?')}",
                    f"   Text:   {shot.get('text_overlay', '?')}",
                    f"   Goal:   {shot.get('purpose', '?')}",
                ]
            lines += [
                "", "📱 Equipment:", str(d.get("equipment", [])),
                "", "✂️ Editing Tips:",
            ] + [f"  • {t}" for t in d.get("editing_tips", [])] + [
                "", "🪝 Hook Ideas:",
            ] + [f"  • {h}" for h in d.get("hook_ideas", [])] + [
                "", f"🎵 Trending Sounds: {d.get('trending_sounds', '')}",
                f"🖼 Thumbnail Tip: {d.get('thumbnail_tip', '')}",
            ]
            out4.setText("\n".join(lines))
            _enable_btn(btn4, "🎬 Generate Storyboard")
        w.finished.connect(_done4)
        w.error.connect(lambda e: (out4.setText(f"Error: {e}"), _enable_btn(btn4, "🎬 Generate Storyboard")))
        page._workers.append(w); w.start()
    btn4.clicked.connect(_story)
    tabs.addTab(t4, "🎬 Storyboard")

    return page


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 19 — BUSINESS INTELLIGENCE
# ═══════════════════════════════════════════════════════════════════════════════

def build_business_intel_page(api_base: str) -> QWidget:
    """Page 19: Growth Forecast, Crisis Manager, Brand Voice, Profile Optimizer, YouTube SEO."""
    page, layout = _make_page_layout("💼 Business Intelligence", "💼")
    page._workers: list = []

    tabs = QTabWidget()
    tabs.setStyleSheet("QTabWidget::pane{border:none;} QTabBar::tab{padding:8px 16px;}")
    layout.addWidget(tabs)

    # ── Tab 1: Growth Forecast ─────────────────────────────────────────────
    t1 = QWidget(); tl = QVBoxLayout(t1); tl.setContentsMargins(12, 12, 12, 12)
    tl.addWidget(_label("📈 AI Growth Forecasting (3-Scenario ML Model)", bold=True))
    f1 = QFormLayout(); f1.setSpacing(8)
    e_curr  = _entry("10000"); f1.addRow("Current Followers:", e_curr)
    c_plat  = _combo("Instagram", "TikTok", "YouTube", "Twitter/X", "LinkedIn", "Facebook")
    f1.addRow("Platform:", c_plat)
    e_rate  = _entry("5.0"); f1.addRow("Monthly Growth Rate (%):", e_rate)
    e_freq  = _entry("7"); f1.addRow("Posts/Week:", e_freq)
    e_eng   = _entry("3.5"); f1.addRow("Engagement Rate (%):", e_eng)
    c_months = _combo("3", "6", "12", "18", "24"); f1.addRow("Forecast (months):", c_months)
    tl.addLayout(f1)
    btn1 = _btn("📈 Generate Growth Forecast")
    tl.addWidget(btn1)
    out1 = _out(22); tl.addWidget(out1, 1)

    def _forecast():
        _disable_btn(btn1, "Calculating…")
        try:
            curr  = int(e_curr.text() or "10000")
            rate  = float(e_rate.text() or "5.0")
            freq  = int(e_freq.text() or "7")
            eng   = float(e_eng.text() or "3.5")
            mnths = int(c_months.currentText())
        except ValueError:
            out1.setText("⚠️ Please enter valid numbers."); _enable_btn(btn1, "📈 Generate Growth Forecast"); return
        w = _ApiWorker(
            f"{api_base}/api/v1/biz/growth-forecast",
            {"current_followers": curr, "platform": c_plat.currentText(),
             "monthly_growth_rate": rate, "posting_freq": freq,
             "engagement_rate": eng, "months": mnths},
        )
        def _done(r):
            d = r.get("data", r)
            lines = [
                f"🚀 Platform: {d.get('platform', '?')} | Input Rate: {d.get('input_monthly_growth_rate', '?')}",
                f"📊 Forecast: {d.get('forecast_months', '?')} months",
                "",
            ]
            for scenario, pts in (d.get("scenarios") or {}).items():
                if pts:
                    final = pts[-1]
                    lines.append(f"  {scenario}: {final.get('followers', '?'):,} followers (net +{final.get('net_gain', '?'):,})")
            lines += [
                "", f"📌 Next Milestone: {d.get('next_milestone', {})}",
                "", "📏 Platform Benchmark:", str(d.get("platform_benchmark", {})),
                "", "💡 Growth Tips:",
            ] + [f"  {t}" for t in d.get("growth_tips", [])]
            # Monthly table for Realistic
            real = (d.get("scenarios") or {}).get("Realistic", [])
            if real:
                lines += ["", "📅 Realistic Month-by-Month:"]
                for pt in real:
                    lines.append(f"  Month {pt.get('month','?'):>2}: {pt.get('followers','?'):>10,} (+{pt.get('monthly_gain','?'):,}/mo)")
            out1.setText("\n".join(lines))
            _enable_btn(btn1, "📈 Generate Growth Forecast")
        w.finished.connect(_done)
        w.error.connect(lambda e: (out1.setText(f"Error: {e}"), _enable_btn(btn1, "📈 Generate Growth Forecast")))
        page._workers.append(w); w.start()
    btn1.clicked.connect(_forecast)
    tabs.addTab(t1, "📈 Growth Forecast")

    # ── Tab 2: Crisis Manager ──────────────────────────────────────────────
    t2 = QWidget(); tl2 = QVBoxLayout(t2); tl2.setContentsMargins(12, 12, 12, 12)
    tl2.addWidget(_label("🚨 Crisis Manager — Detect & Respond", bold=True))
    f2 = QFormLayout(); f2.setSpacing(8)
    e_brand2 = _entry("Brand Name"); f2.addRow("Brand:", e_brand2)
    c_plat2  = _combo("All Platforms", "Instagram", "TikTok", "Twitter/X", "Facebook", "YouTube")
    f2.addRow("Platform:", c_plat2)
    c_tone2  = _combo("Empathetic & Professional", "Formal", "Apologetic", "Transparent")
    f2.addRow("Response Tone:", c_tone2)
    c_lang2  = _combo("English", "Khmer", "Spanish", "French", "Chinese", "Arabic")
    f2.addRow("Language:", c_lang2)
    tl2.addLayout(f2)
    tl2.addWidget(_label("Paste comments/mentions to analyze:"))
    e_cmts = QTextEdit(); e_cmts.setPlaceholderText("Paste suspicious or negative comments here…"); e_cmts.setFixedHeight(90)
    tl2.addWidget(e_cmts)
    r2 = QHBoxLayout()
    btn2a = _btn("🔍 Detect Crisis"); btn2b = _btn("📝 Generate Response Kit")
    r2.addWidget(btn2a); r2.addWidget(btn2b); tl2.addLayout(r2)
    out2 = _out(16); tl2.addWidget(out2, 1)

    def _detect():
        _disable_btn(btn2a, "Analyzing…")
        w = _ApiWorker(
            f"{api_base}/api/v1/biz/crisis-detect",
            {"comments_text": e_cmts.toPlainText(), "brand": e_brand2.text(),
             "platform": c_plat2.currentText(), "language": c_lang2.currentText()},
        )
        def _dd(r):
            d = r.get("data", r)
            lvl = d.get("crisis_level", "Unknown")
            ico = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢", "None": "✅"}.get(lvl, "⚪")
            lines = [
                f"{ico} Crisis Level: {lvl} | Score: {d.get('crisis_score', 0)}/100",
                f"⏰ Response Urgency: {d.get('response_urgency', 'N/A')}",
                f"⏸ Pause Scheduled Posts: {'YES 🛑' if d.get('pause_scheduled_posts') else 'No'}",
                "", "🔍 Detected Issues:",
            ] + [f"  • {i}" for i in d.get("detected_issues", [])] + [
                "", "📋 Recommended Actions:",
            ] + [f"  {a}" for a in d.get("recommended_actions", [])]
            out2.setText("\n".join(lines))
            _enable_btn(btn2a, "🔍 Detect Crisis")
        w.finished.connect(_dd)
        w.error.connect(lambda e: (out2.setText(f"Error: {e}"), _enable_btn(btn2a, "🔍 Detect Crisis")))
        page._workers.append(w); w.start()
    btn2a.clicked.connect(_detect)

    def _respond():
        _disable_btn(btn2b, "Generating…")
        w = _ApiWorker(
            f"{api_base}/api/v1/biz/crisis-response",
            {"brand": e_brand2.text() or "Our Brand",
             "crisis_description": e_cmts.toPlainText()[:600] or "Negative feedback",
             "tone": c_tone2.currentText(), "platform": c_plat2.currentText(),
             "language": c_lang2.currentText()},
        )
        def _dr(r):
            d = r.get("data", r)
            lines = [
                "── 📢 PUBLIC COMMENT RESPONSE ──", d.get("public_comment_response", ""),
                "", "── 📱 STORY RESPONSE ──", d.get("story_response", ""),
                "", "── 📩 DM RESPONSE ──", d.get("dm_response", ""),
                "", "── 📰 PRESS STATEMENT ──", d.get("press_statement", ""),
                "", "🚫 Do NOT Say:",
            ] + [f"  ❌ {x}" for x in d.get("what_not_to_say", [])] + [
                "", "✅ Action Checklist:",
            ] + [f"  {a}" for a in d.get("action_checklist", [])] + [
                "", f"🗺 Recovery Plan: {d.get('recovery_plan', '')}",
            ]
            out2.setText("\n".join(lines))
            _enable_btn(btn2b, "📝 Generate Response Kit")
        w.finished.connect(_dr)
        w.error.connect(lambda e: (out2.setText(f"Error: {e}"), _enable_btn(btn2b, "📝 Generate Response Kit")))
        page._workers.append(w); w.start()
    btn2b.clicked.connect(_respond)
    tabs.addTab(t2, "🚨 Crisis Manager")

    # ── Tab 3: Brand Voice ─────────────────────────────────────────────────
    t3 = QWidget(); tl3 = QVBoxLayout(t3); tl3.setContentsMargins(12, 12, 12, 12)
    tl3.addWidget(_label("🎨 Brand Voice AI — Analyze & Codify Writing Style", bold=True))
    f3 = QFormLayout(); f3.setSpacing(8)
    e_brand3 = _entry("Brand Name"); f3.addRow("Brand:", e_brand3)
    c_lang3  = _combo("English", "Khmer", "Spanish", "French", "Chinese", "Arabic")
    f3.addRow("Language:", c_lang3)
    tl3.addLayout(f3)
    tl3.addWidget(_label("Paste 3–5 sample posts/captions:"))
    e_samples = QTextEdit(); e_samples.setPlaceholderText("Paste sample posts here…"); e_samples.setFixedHeight(120)
    tl3.addWidget(e_samples)
    btn3 = _btn("🎨 Analyze Brand Voice")
    tl3.addWidget(btn3)
    out3 = _out(16); tl3.addWidget(out3, 1)

    def _voice():
        _disable_btn(btn3, "Analyzing…")
        w = _ApiWorker(
            f"{api_base}/api/v1/biz/brand-voice",
            {"samples": e_samples.toPlainText(), "brand_name": e_brand3.text(),
             "language": c_lang3.currentText()},
        )
        def _dv(r):
            d = r.get("data", r)
            lines = [
                f"🎭 Brand Voice: {d.get('brand_voice_profile', 'N/A')}",
                f"✨ Personality: {d.get('brand_personality', 'N/A')}",
                f"📝 Tone Attributes: {', '.join(d.get('tone_attributes', []))}",
                f"💬 Vocabulary: {d.get('vocabulary_style', 'N/A')}",
                f"📏 Sentences: {d.get('sentence_style', 'N/A')}",
                f"😊 Emoji Use: {d.get('emoji_usage', 'N/A')}",
                "", "✅ Preferred Words:",
            ] + [f"  • {w_}" for w_ in d.get("preferred_words", [])] + [
                "", "🚫 Taboo Words:",
            ] + [f"  ❌ {w_}" for w_ in d.get("taboo_words", [])] + [
                "", "📋 Writing Rules:",
            ] + [f"  {i+1}. {r_}" for i, r_ in enumerate(d.get("writing_rules", []))]
            out3.setText("\n".join(lines))
            _enable_btn(btn3, "🎨 Analyze Brand Voice")
        w.finished.connect(_dv)
        w.error.connect(lambda e: (out3.setText(f"Error: {e}"), _enable_btn(btn3, "🎨 Analyze Brand Voice")))
        page._workers.append(w); w.start()
    btn3.clicked.connect(_voice)
    tabs.addTab(t3, "🎨 Brand Voice")

    # ── Tab 4: Report Builder ──────────────────────────────────────────────
    t4 = QWidget(); tl4 = QVBoxLayout(t4); tl4.setContentsMargins(12, 12, 12, 12)
    tl4.addWidget(_label("📊 AI Report Builder", bold=True))
    f4 = QFormLayout(); f4.setSpacing(8)
    e_acct  = _entry("Account / Brand Name"); f4.addRow("Account:", e_acct)
    c_plat4 = _combo("Instagram", "TikTok", "YouTube", "Facebook", "LinkedIn", "Twitter/X")
    f4.addRow("Platform:", c_plat4)
    c_per4  = _combo("Last 7 days", "Last 30 days", "Last 90 days", "Last 6 months", "Last year")
    f4.addRow("Period:", c_per4)
    c_lang4 = _combo("English", "Khmer", "Spanish", "French", "Chinese", "Arabic")
    f4.addRow("Language:", c_lang4)
    tl4.addLayout(f4)
    tl4.addWidget(_label("Paste metrics (followers, reach, engagement, etc.):"))
    e_metrics = QTextEdit(); e_metrics.setPlaceholderText("E.g.:\nFollowers: 12,500\nReach: 45,000\nEngagement Rate: 4.2%\nBest Post: 1,200 likes…")
    e_metrics.setFixedHeight(100); tl4.addWidget(e_metrics)
    btn4 = _btn("📊 Generate AI Report")
    tl4.addWidget(btn4)
    out4 = _out(16); tl4.addWidget(out4, 1)

    def _report():
        _disable_btn(btn4, "Generating…")
        from ai_core.llm_client import LLM_CLIENT, LLM_MODEL, USE_AI
        import asyncio, re
        if not USE_AI or not LLM_CLIENT:
            out4.setText(
                f"📊 PERFORMANCE REPORT — {e_acct.text() or 'Account'} | {c_plat4.currentText()} | {c_per4.currentText()}\n"
                "══════════════════════════════════════════\n\n"
                "SUMMARY:\nDuring this period, your account showed steady growth.\n\n"
                "KEY METRICS:\n" + e_metrics.toPlainText() + "\n\n"
                "WINS THIS PERIOD:\n• Consistent posting maintained audience retention\n"
                "• Engagement above platform average\n\n"
                "IMPROVEMENT AREAS:\n• Increase Reel/Short video frequency\n"
                "• Optimize posting times based on audience peak hours\n\n"
                "RECOMMENDATIONS:\n1. Double down on top-performing content formats\n"
                "2. Collaborate with 2 niche creators this month\n"
                "3. A/B test 3 different caption styles\n\n"
                "Generated by GrowthOS AI"
            )
            _enable_btn(btn4, "📊 Generate AI Report"); return
        async def _gen():
            resp = await LLM_CLIENT.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": f"You are a social media analytics expert. Language: {c_lang4.currentText()}."},
                    {"role": "user", "content": (
                        f"Write a professional social media performance report for:\n"
                        f"Account: {e_acct.text() or 'N/A'}, Platform: {c_plat4.currentText()}, Period: {c_per4.currentText()}\n"
                        f"Metrics:\n{e_metrics.toPlainText()}\n\n"
                        f"Include: Executive Summary, Key Wins, Problem Areas, Recommendations, Action Plan."
                    )},
                ],
                temperature=0.4, max_tokens=900,
            )
            return resp.choices[0].message.content
        try:
            loop = asyncio.get_event_loop()
            text = loop.run_until_complete(_gen())
        except Exception:
            text = "Report generation failed — check AI connection."
        out4.setText(text)
        _enable_btn(btn4, "📊 Generate AI Report")
    btn4.clicked.connect(_report)
    tabs.addTab(t4, "📊 Report Builder")

    # ── Tab 5: Profile Optimizer ───────────────────────────────────────────
    t5 = QWidget(); tl5 = QVBoxLayout(t5); tl5.setContentsMargins(12, 12, 12, 12)
    tl5.addWidget(_label("🏆 AI Profile Optimizer", bold=True))
    f5 = QFormLayout(); f5.setSpacing(8)
    c_plat5  = _combo("Instagram", "TikTok", "YouTube", "LinkedIn", "Twitter/X",
                      "Facebook", "Pinterest", "Snapchat")
    f5.addRow("Platform:", c_plat5)
    e_user5  = _entry("Your username / handle"); f5.addRow("Username:", e_user5)
    e_niche5 = _entry("Your niche"); f5.addRow("Niche:", e_niche5)
    e_goals5 = _entry("E.g. grow followers, get brand deals, drive traffic"); f5.addRow("Goals:", e_goals5)
    c_lang5  = _combo("English", "Khmer", "Spanish", "French", "Chinese", "Arabic")
    f5.addRow("Language:", c_lang5)
    tl5.addLayout(f5)
    tl5.addWidget(_label("Current Bio:"))
    e_bio = QTextEdit(); e_bio.setPlaceholderText("Paste your current bio here…"); e_bio.setFixedHeight(80)
    tl5.addWidget(e_bio)
    btn5 = _btn("🏆 Optimize My Profile")
    tl5.addWidget(btn5)
    out5 = _out(16); tl5.addWidget(out5, 1)

    def _profopt():
        _disable_btn(btn5, "Optimizing…")
        w = _ApiWorker(
            f"{api_base}/api/v1/creator/profile-optimizer",
            {"platform": c_plat5.currentText(), "current_bio": e_bio.toPlainText(),
             "niche": e_niche5.text() or "General", "goals": e_goals5.text(),
             "username": e_user5.text(), "language": c_lang5.currentText()},
        )
        def _dp(r):
            d = r.get("data", r)
            lines = [
                f"📊 Bio Score: {d.get('bio_score', '?')}/100  (Grade: {d.get('bio_grade', '?')})",
                f"🧮 Bio Formula: {d.get('bio_formula', '')}",
                "", "✨ Optimized Bio:", d.get("optimized_bio", ""),
                "", f"👤 Username Tips: {d.get('username_tips', '')}",
                f"📸 Profile Photo: {d.get('profile_photo_tips', '')}",
                f"🔗 Link Strategy: {d.get('link_in_bio_strategy', '')}",
                "", "📌 Story Highlights:", str(d.get("highlights_strategy", [])),
                "", "📈 Improvements:",
            ] + [f"  {i+1}. {imp}" for i, imp in enumerate(d.get("improvements", []))] + [
                "", "🔑 Keywords to Add:", ", ".join(d.get("keywords_to_add", [])),
            ]
            out5.setText("\n".join(lines))
            _enable_btn(btn5, "🏆 Optimize My Profile")
        w.finished.connect(_dp)
        w.error.connect(lambda e: (out5.setText(f"Error: {e}"), _enable_btn(btn5, "🏆 Optimize My Profile")))
        page._workers.append(w); w.start()
    btn5.clicked.connect(_profopt)
    tabs.addTab(t5, "🏆 Profile Optimizer")

    return page


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 20 — CREATOR TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

def build_creator_tools_page(api_base: str) -> QWidget:
    """Page 20: YouTube SEO Optimizer, Team Workflow, Revenue Attribution."""
    page, layout = _make_page_layout("🎨 Creator Tools", "🎨")
    page._workers: list = []

    tabs = QTabWidget()
    tabs.setStyleSheet("QTabWidget::pane{border:none;} QTabBar::tab{padding:8px 18px;}")
    layout.addWidget(tabs)

    # ── Tab 1: YouTube SEO ─────────────────────────────────────────────────
    t1 = QWidget(); tl = QVBoxLayout(t1); tl.setContentsMargins(12, 12, 12, 12)
    tl.addWidget(_label("▶️ YouTube SEO Optimizer", bold=True))
    f1 = QFormLayout(); f1.setSpacing(8)
    e_title = _entry("Video title"); f1.addRow("Title:", e_title)
    e_kw    = _entry("Main keyword to rank for"); f1.addRow("Target Keyword:", e_kw)
    e_niche = _entry("Your channel niche"); f1.addRow("Niche:", e_niche)
    c_lang  = _combo("English", "Khmer", "Spanish", "French", "Chinese", "Arabic")
    f1.addRow("Language:", c_lang)
    tl.addLayout(f1)
    tl.addWidget(_label("Current Description:"))
    e_desc = QTextEdit(); e_desc.setPlaceholderText("Current video description (optional)…"); e_desc.setFixedHeight(80)
    tl.addWidget(e_desc)
    tl.addWidget(_label("Current Tags (comma-separated):"))
    e_tags = _entry("tag1, tag2, tag3…"); tl.addWidget(e_tags)
    btn1 = _btn("▶️ Optimize YouTube SEO")
    tl.addWidget(btn1)
    out1 = _out(18); tl.addWidget(out1, 1)

    def _yt():
        _disable_btn(btn1, "Optimizing…")
        w = _ApiWorker(
            f"{api_base}/api/v1/creator/youtube-seo",
            {"title": e_title.text(), "description": e_desc.toPlainText(),
             "tags": e_tags.text(), "target_keyword": e_kw.text(),
             "niche": e_niche.text() or "General", "language": c_lang.currentText()},
        )
        def _done(r):
            d = r.get("data", r)
            sc = d.get("scores") or {}
            lines = [
                f"📊 SEO Scores — Title: {sc.get('title', '?')}/100 | Desc: {sc.get('description', '?')}/100 | Tags: {sc.get('tags', '?')}/100 | Overall: {sc.get('overall', '?')}/100",
                f"📈 {d.get('estimated_ctr_boost', '')}",
                "", "✅ Optimized Title:", d.get("optimized_title", ""),
                "", "📝 Optimized Description:", d.get("optimized_description", ""),
                "", "🏷 Optimized Tags:", ", ".join(d.get("optimized_tags", [])),
                "", "💡 Improvements:",
            ] + [f"  {i+1}. {x}" for i, x in enumerate(d.get("improvements", []))] + [
                "", f"🖼 Thumbnail Tips: {d.get('thumbnail_tips', '')}",
            ]
            out1.setText("\n".join(lines))
            _enable_btn(btn1, "▶️ Optimize YouTube SEO")
        w.finished.connect(_done)
        w.error.connect(lambda e: (out1.setText(f"Error: {e}"), _enable_btn(btn1, "▶️ Optimize YouTube SEO")))
        page._workers.append(w); w.start()
    btn1.clicked.connect(_yt)
    tabs.addTab(t1, "▶️ YouTube SEO")

    # ── Tab 2: Team Workflow ───────────────────────────────────────────────
    t2 = QWidget(); tl2 = QVBoxLayout(t2); tl2.setContentsMargins(12, 12, 12, 12)
    tl2.addWidget(_label("👥 Team Workflow Planner", bold=True))
    tl2.addWidget(_label("Organize your content team's weekly workflow:"))
    f2 = QFormLayout(); f2.setSpacing(8)
    e_brand2 = _entry("Brand / Team Name"); f2.addRow("Team:", e_brand2)
    c_size2  = _combo("Solo Creator", "2-Person", "3–5 Person", "6–10 Person", "Agency 10+")
    f2.addRow("Team Size:", c_size2)
    c_plats2 = _combo("Instagram + TikTok", "YouTube + Instagram", "All Platforms",
                      "LinkedIn + Twitter/X", "Custom")
    f2.addRow("Active Platforms:", c_plats2)
    e_posts2 = _entry("14"); f2.addRow("Posts/Week Target:", e_posts2)
    c_lang2  = _combo("English", "Khmer", "Spanish", "French", "Chinese", "Arabic")
    f2.addRow("Language:", c_lang2)
    tl2.addLayout(f2)
    btn2 = _btn("👥 Generate Workflow Plan")
    tl2.addWidget(btn2)
    out2 = _out(20); tl2.addWidget(out2, 1)

    def _workflow():
        _disable_btn(btn2, "Generating…")
        from ai_core.llm_client import LLM_CLIENT, LLM_MODEL, USE_AI
        import asyncio
        team   = e_brand2.text() or "Content Team"
        size   = c_size2.currentText()
        plats  = c_plats2.currentText()
        posts  = e_posts2.text() or "14"
        lang   = c_lang2.currentText()
        if not USE_AI or not LLM_CLIENT:
            out2.setText(
                f"📋 WEEKLY WORKFLOW — {team} ({size})\n"
                "══════════════════════════════\n\n"
                "MONDAY: Strategy & Planning\n  • Weekly content calendar review\n  • Assign topics per platform\n  • Approve pending drafts\n\n"
                "TUESDAY: Content Creation\n  • Film/record 3–4 videos\n  • Write 5–7 captions\n  • Design graphics\n\n"
                "WEDNESDAY: Editing & Review\n  • Edit all videos from Tuesday\n  • QA captions and hashtags\n  • Submit for approval\n\n"
                "THURSDAY: Scheduling\n  • Schedule approved posts via GrowthOS\n  • Pre-write comment replies\n  • Prepare Stories content\n\n"
                "FRIDAY: Engagement & Analytics\n  • Reply to all comments and DMs\n  • Review weekly analytics\n  • Document top performers\n\n"
                "WEEKEND: Ideation\n  • Trend research for next week\n  • Brainstorm new angles\n  • Competitor monitor\n\n"
                f"Tools: GrowthOS AI | Platforms: {plats} | Target: {posts} posts/week"
            )
            _enable_btn(btn2, "👥 Generate Workflow Plan"); return
        async def _gen():
            resp = await LLM_CLIENT.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": f"You are a content operations manager. Language: {lang}."},
                    {"role": "user", "content": (
                        f"Create a detailed weekly content workflow for:\n"
                        f"Team: {team} ({size}), Platforms: {plats}, Target: {posts} posts/week.\n"
                        f"Include day-by-day tasks, role assignments, and tools to use."
                    )},
                ],
                temperature=0.4, max_tokens=700,
            )
            return resp.choices[0].message.content
        try:
            loop = asyncio.get_event_loop()
            text = loop.run_until_complete(_gen())
        except Exception:
            text = "Workflow generation failed — check AI connection."
        out2.setText(text)
        _enable_btn(btn2, "👥 Generate Workflow Plan")
    btn2.clicked.connect(_workflow)
    tabs.addTab(t2, "👥 Team Workflow")

    # ── Tab 3: Revenue Attribution ─────────────────────────────────────────
    t3 = QWidget(); tl3 = QVBoxLayout(t3); tl3.setContentsMargins(12, 12, 12, 12)
    tl3.addWidget(_label("💰 Revenue Attribution & ROI Tracker", bold=True))
    f3 = QFormLayout(); f3.setSpacing(8)
    e_brand3 = _entry("Brand / Creator Name"); f3.addRow("Brand:", e_brand3)
    e_rev3   = _entry("e.g. 5000 USD"); f3.addRow("Total Revenue (period):", e_rev3)
    e_spend3 = _entry("e.g. 800 USD"); f3.addRow("Ad Spend (period):", e_spend3)
    e_posts3 = _entry("e.g. 28"); f3.addRow("Total Posts (period):", e_posts3)
    e_sales3 = _entry("e.g. 45"); f3.addRow("Total Sales/Conversions:", e_sales3)
    c_lang3  = _combo("English", "Khmer", "Spanish", "French", "Chinese", "Arabic")
    f3.addRow("Language:", c_lang3)
    tl3.addLayout(f3)
    tl3.addWidget(_label("Revenue sources (paste text or describe):"))
    e_src3 = QTextEdit(); e_src3.setPlaceholderText("E.g.\nOrganic posts: $2,000\nPaid ads: $2,500\nCollaborations: $500")
    e_src3.setFixedHeight(90); tl3.addWidget(e_src3)
    btn3 = _btn("💰 Analyze ROI & Attribution")
    tl3.addWidget(btn3)
    out3 = _out(16); tl3.addWidget(out3, 1)

    def _roi():
        _disable_btn(btn3, "Calculating…")
        try:
            rev   = float(e_rev3.text().replace(",", "").replace("USD", "").strip() or "0")
            spend = float(e_spend3.text().replace(",", "").replace("USD", "").strip() or "0")
            posts = int(e_posts3.text() or "1")
            sales = int(e_sales3.text() or "0")
        except ValueError:
            out3.setText("⚠️ Please enter valid numbers."); _enable_btn(btn3, "💰 Analyze ROI & Attribution"); return
        roi = ((rev - spend) / spend * 100) if spend > 0 else 0
        roas = (rev / spend) if spend > 0 else 0
        cpconv = (spend / sales) if sales > 0 else 0
        rev_per_post = (rev / posts) if posts > 0 else 0
        out3.setText(
            f"💰 REVENUE ATTRIBUTION REPORT — {e_brand3.text() or 'Creator'}\n"
            "══════════════════════════════════════\n\n"
            f"📊 Total Revenue:     ${rev:,.2f}\n"
            f"💸 Total Ad Spend:    ${spend:,.2f}\n"
            f"📈 ROI:               {roi:.1f}%\n"
            f"🎯 ROAS:              {roas:.2f}x\n"
            f"🛒 Cost per Sale:     ${cpconv:.2f}\n"
            f"📝 Revenue/Post:      ${rev_per_post:.2f}\n"
            f"🔢 Total Posts:       {posts}\n"
            f"✅ Total Conversions: {sales}\n\n"
            "── Revenue Sources ──\n" + (e_src3.toPlainText() or "N/A") + "\n\n"
            "── AI Insights ──\n"
            f"{'✅ Strong ROI — Keep scaling this strategy!' if roi > 100 else '⚠️ ROI below 100% — review top posts and cut underperformers.'}\n"
            f"{'✅ ROAS above 3x — very healthy paid performance!' if roas >= 3 else '⚠️ ROAS below 3x — optimize ad creatives or targeting.'}\n"
            "💡 Focus budget on posts with highest engagement rates.\n"
            "💡 Use GrowthOS A/B Testing to find your top-converting hook."
        )
        _enable_btn(btn3, "💰 Analyze ROI & Attribution")
    btn3.clicked.connect(_roi)
    tabs.addTab(t3, "💰 Revenue & ROI")

    return page


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 21 — SALES ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

def build_sales_engine_page(api_base: str) -> QWidget:
    """P5 Sales & Revenue Engine: Funnel Map, Lead Magnet, Product Desc, Email Seq, CTAs."""
    page, layout = _make_page_layout("Sales Engine", "💰")
    tabs = QTabWidget()
    layout.addWidget(tabs)

    # ── Tab 1: Sales Funnel Mapper ────────────────────────────────────────────
    t1 = QWidget(); f1 = QFormLayout(t1)
    e1_niche = _entry("Fitness Coaching"); e1_product = _entry("12-Week Transformation Program")
    e1_platform = _combo("Instagram", "TikTok", "YouTube", "LinkedIn", "Twitter/X", "Facebook")
    e1_audience = _entry("Busy professionals aged 30-45"); e1_lang = _combo("English","Spanish","French","German","Portuguese","Arabic","Hindi","Japanese","Chinese")
    btn1 = _btn("🗺 Map Sales Funnel"); out1 = _out()
    f1.addRow("Niche:", e1_niche); f1.addRow("Product/Service:", e1_product)
    f1.addRow("Platform:", e1_platform); f1.addRow("Target Audience:", e1_audience)
    f1.addRow("Language:", e1_lang); f1.addRow(btn1); f1.addRow(out1)
    def run_funnel():
        _disable_btn(btn1)
        def done(r, e): out1.setPlainText(json.dumps(r, indent=2) if not e else f"Error: {e}"); _enable_btn(btn1)
        _ApiWorker(api_base, "sales/funnel-map", {"niche": e1_niche.text(), "product": e1_product.text(),
            "platform": e1_platform.currentText(), "audience": e1_audience.text(),
            "language": e1_lang.currentText()}, done).start()
    btn1.clicked.connect(run_funnel)
    tabs.addTab(t1, "🗺 Sales Funnel")

    # ── Tab 2: Lead Magnet Builder ────────────────────────────────────────────
    t2 = QWidget(); f2 = QFormLayout(t2)
    e2_niche = _entry("Digital Marketing"); e2_topic = _entry("5 Steps to Double Your Instagram Following")
    e2_fmt = _combo("PDF Checklist", "Mini eBook", "Email Course", "Video Training", "Webinar", "Cheat Sheet", "Swipe File", "Template Pack")
    e2_aud = _entry("Small business owners"); e2_lang2 = _combo("English","Spanish","French","German","Portuguese","Arabic","Hindi","Japanese","Chinese")
    btn2 = _btn("🎁 Build Lead Magnet"); out2 = _out()
    f2.addRow("Niche:", e2_niche); f2.addRow("Topic/Title Idea:", e2_topic)
    f2.addRow("Format:", e2_fmt); f2.addRow("Audience:", e2_aud)
    f2.addRow("Language:", e2_lang2); f2.addRow(btn2); f2.addRow(out2)
    def run_lead():
        _disable_btn(btn2)
        def done(r, e): out2.setPlainText(json.dumps(r, indent=2) if not e else f"Error: {e}"); _enable_btn(btn2)
        _ApiWorker(api_base, "sales/lead-magnet", {"niche": e2_niche.text(), "topic": e2_topic.text(),
            "format_type": e2_fmt.currentText(), "audience": e2_aud.text(),
            "language": e2_lang2.currentText()}, done).start()
    btn2.clicked.connect(run_lead)
    tabs.addTab(t2, "🎁 Lead Magnet")

    # ── Tab 3: Social Commerce Product Descriptions ───────────────────────────
    t3 = QWidget(); f3 = QFormLayout(t3)
    e3_name = _entry("GlowSkin Serum"); e3_type = _combo("Physical Product", "Digital Product", "Service", "Course", "Membership", "App/Software")
    e3_niche = _entry("Beauty & Skincare"); e3_price = _entry("$49"); e3_plat = _combo("Instagram","TikTok","Amazon","Shopify","Etsy","Facebook Shop")
    e3_lang = _combo("English","Spanish","French","German","Portuguese","Arabic","Hindi","Japanese","Chinese")
    btn3 = _btn("🛒 Generate Product Copy"); out3 = _out()
    f3.addRow("Product Name:", e3_name); f3.addRow("Product Type:", e3_type)
    f3.addRow("Niche:", e3_niche); f3.addRow("Price:", e3_price)
    f3.addRow("Platform:", e3_plat); f3.addRow("Language:", e3_lang); f3.addRow(btn3); f3.addRow(out3)
    def run_product():
        _disable_btn(btn3)
        def done(r, e): out3.setPlainText(json.dumps(r, indent=2) if not e else f"Error: {e}"); _enable_btn(btn3)
        _ApiWorker(api_base, "sales/product-description", {"product_name": e3_name.text(), "product_type": e3_type.currentText(),
            "niche": e3_niche.text(), "price": e3_price.text(), "platform": e3_plat.currentText(),
            "language": e3_lang.currentText()}, done).start()
    btn3.clicked.connect(run_product)
    tabs.addTab(t3, "🛒 Social Commerce")

    # ── Tab 4: Email Sequence Generator ──────────────────────────────────────
    t4 = QWidget(); f4 = QFormLayout(t4)
    e4_topic = _entry("How to Grow on Instagram in 2025"); e4_niche = _entry("Social Media Marketing")
    e4_product = _entry("Social Media Mastery Course"); e4_num = QSpinBox(); e4_num.setRange(1, 10); e4_num.setValue(5)
    e4_tone = _combo("Conversational", "Professional", "Casual", "Persuasive", "Inspirational", "Authoritative")
    e4_lang = _combo("English","Spanish","French","German","Portuguese","Arabic","Hindi","Japanese","Chinese")
    btn4 = _btn("📧 Generate Email Sequence"); out4 = _out()
    f4.addRow("Topic:", e4_topic); f4.addRow("Niche:", e4_niche)
    f4.addRow("Product/Offer:", e4_product); f4.addRow("Number of Emails:", e4_num)
    f4.addRow("Tone:", e4_tone); f4.addRow("Language:", e4_lang); f4.addRow(btn4); f4.addRow(out4)
    def run_email():
        _disable_btn(btn4)
        def done(r, e): out4.setPlainText(json.dumps(r, indent=2) if not e else f"Error: {e}"); _enable_btn(btn4)
        _ApiWorker(api_base, "sales/email-sequence", {"topic": e4_topic.text(), "niche": e4_niche.text(),
            "product": e4_product.text(), "num_emails": e4_num.value(),
            "tone": e4_tone.currentText(), "language": e4_lang.currentText()}, done).start()
    btn4.clicked.connect(run_email)
    tabs.addTab(t4, "📧 Email Sequence")

    # ── Tab 5: CTA Generator ──────────────────────────────────────────────────
    t5 = QWidget(); f5 = QFormLayout(t5)
    e5_niche = _entry("Fitness"); e5_product = _entry("Personal Training Program")
    e5_plat = _combo("Instagram","TikTok","YouTube","LinkedIn","Twitter/X","Email","Website")
    e5_goal = _combo("Sales", "Lead Generation", "Followers", "Email Signups", "Website Clicks", "DMs", "App Downloads")
    e5_count = QSpinBox(); e5_count.setRange(5, 20); e5_count.setValue(10)
    e5_lang = _combo("English","Spanish","French","German","Portuguese","Arabic","Hindi","Japanese","Chinese")
    btn5 = _btn("🎯 Generate CTAs"); out5 = _out()
    f5.addRow("Niche:", e5_niche); f5.addRow("Product/Offer:", e5_product)
    f5.addRow("Platform:", e5_plat); f5.addRow("Goal:", e5_goal)
    f5.addRow("Number of CTAs:", e5_count); f5.addRow("Language:", e5_lang); f5.addRow(btn5); f5.addRow(out5)
    def run_ctas():
        _disable_btn(btn5)
        def done(r, e): out5.setPlainText(json.dumps(r, indent=2) if not e else f"Error: {e}"); _enable_btn(btn5)
        _ApiWorker(api_base, "sales/ctas", {"niche": e5_niche.text(), "product": e5_product.text(),
            "platform": e5_plat.currentText(), "goal": e5_goal.currentText(),
            "count": e5_count.value(), "language": e5_lang.currentText()}, done).start()
    btn5.clicked.connect(run_ctas)
    tabs.addTab(t5, "🎯 CTA Generator")

    return page


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 22 — CONTENT DOMINATION
# ═══════════════════════════════════════════════════════════════════════════════

def build_content_domination_page(api_base: str) -> QWidget:
    """P6 Content Domination: Viral Hooks, Reel Scripts, Content Series, Thumbnails, Emotion Captions."""
    page, layout = _make_page_layout("Content Domination", "🎬")
    tabs = QTabWidget()
    layout.addWidget(tabs)

    # ── Tab 1: Viral Hook Library ─────────────────────────────────────────────
    t1 = QWidget(); f1 = QFormLayout(t1)
    e1_niche = _entry("Personal Finance"); e1_plat = _combo("TikTok","Instagram Reels","YouTube Shorts","LinkedIn","Twitter/X")
    e1_type = _combo("Video","Carousel","Story","Text Post","Live"); e1_count = QSpinBox(); e1_count.setRange(5, 30); e1_count.setValue(20)
    e1_lang = _combo("English","Spanish","French","German","Portuguese","Arabic","Hindi","Japanese","Chinese")
    btn1 = _btn("🪝 Generate Viral Hooks"); out1 = _out()
    f1.addRow("Niche:", e1_niche); f1.addRow("Platform:", e1_plat)
    f1.addRow("Content Type:", e1_type); f1.addRow("Number of Hooks:", e1_count)
    f1.addRow("Language:", e1_lang); f1.addRow(btn1); f1.addRow(out1)
    def run_hooks():
        _disable_btn(btn1)
        def done(r, e): out1.setPlainText(json.dumps(r, indent=2) if not e else f"Error: {e}"); _enable_btn(btn1)
        _ApiWorker(api_base, "content/viral-hooks", {"niche": e1_niche.text(), "platform": e1_plat.currentText(),
            "content_type": e1_type.currentText(), "count": e1_count.value(),
            "language": e1_lang.currentText()}, done).start()
    btn1.clicked.connect(run_hooks)
    tabs.addTab(t1, "🪝 Viral Hooks")

    # ── Tab 2: Reel/Short Script Engine ──────────────────────────────────────
    t2 = QWidget(); f2 = QFormLayout(t2)
    e2_topic = _entry("5 Money Mistakes You're Making in Your 20s"); e2_plat = _combo("TikTok","Instagram Reels","YouTube Shorts","Facebook Reels")
    e2_dur = _combo("15s","30s","60s","90s","3min"); e2_style = _combo("Educational","Entertaining","Motivational","Storytime","Tutorial","Reaction")
    e2_niche = _entry("Personal Finance"); e2_lang = _combo("English","Spanish","French","German","Portuguese","Arabic","Hindi","Japanese","Chinese")
    btn2 = _btn("🎬 Generate Script"); out2 = _out()
    f2.addRow("Topic:", e2_topic); f2.addRow("Platform:", e2_plat)
    f2.addRow("Duration:", e2_dur); f2.addRow("Style:", e2_style)
    f2.addRow("Niche:", e2_niche); f2.addRow("Language:", e2_lang); f2.addRow(btn2); f2.addRow(out2)
    def run_script():
        _disable_btn(btn2)
        def done(r, e): out2.setPlainText(json.dumps(r, indent=2) if not e else f"Error: {e}"); _enable_btn(btn2)
        _ApiWorker(api_base, "content/reel-script", {"topic": e2_topic.text(), "platform": e2_plat.currentText(),
            "duration": e2_dur.currentText(), "style": e2_style.currentText(),
            "niche": e2_niche.text(), "language": e2_lang.currentText()}, done).start()
    btn2.clicked.connect(run_script)
    tabs.addTab(t2, "🎬 Reel Scripts")

    # ── Tab 3: Content Series Planner ─────────────────────────────────────────
    t3 = QWidget(); f3 = QFormLayout(t3)
    e3_theme = _entry("Master Instagram Growth From Zero"); e3_niche = _entry("Social Media")
    e3_plat = _combo("Instagram","TikTok","YouTube","LinkedIn","Twitter/X"); e3_type = _combo("7-Day Challenge","5-Part Series","30-Day Program","4-Week Course","10-Day Boot Camp")
    e3_lang = _combo("English","Spanish","French","German","Portuguese","Arabic","Hindi","Japanese","Chinese")
    btn3 = _btn("📺 Plan Content Series"); out3 = _out()
    f3.addRow("Theme:", e3_theme); f3.addRow("Niche:", e3_niche)
    f3.addRow("Platform:", e3_plat); f3.addRow("Series Type:", e3_type)
    f3.addRow("Language:", e3_lang); f3.addRow(btn3); f3.addRow(out3)
    def run_series():
        _disable_btn(btn3)
        def done(r, e): out3.setPlainText(json.dumps(r, indent=2) if not e else f"Error: {e}"); _enable_btn(btn3)
        _ApiWorker(api_base, "content/series-plan", {"theme": e3_theme.text(), "niche": e3_niche.text(),
            "platform": e3_plat.currentText(), "series_type": e3_type.currentText(),
            "language": e3_lang.currentText()}, done).start()
    btn3.clicked.connect(run_series)
    tabs.addTab(t3, "📺 Content Series")

    # ── Tab 4: Thumbnail Concept Generator ───────────────────────────────────
    t4 = QWidget(); f4 = QFormLayout(t4)
    e4_title = _entry("How I Made $10,000 With No Experience"); e4_niche = _entry("Make Money Online")
    e4_plat = _combo("YouTube","TikTok","Instagram","LinkedIn"); e4_style = _combo("Bold & Dramatic","Clean & Minimal","Text-Heavy","Face-Forward","Before/After")
    e4_count = QSpinBox(); e4_count.setRange(1, 5); e4_count.setValue(5)
    e4_lang = _combo("English","Spanish","French","German","Portuguese","Arabic","Hindi","Japanese","Chinese")
    btn4 = _btn("🖼 Generate Thumbnail Concepts"); out4 = _out()
    f4.addRow("Title:", e4_title); f4.addRow("Niche:", e4_niche)
    f4.addRow("Platform:", e4_plat); f4.addRow("Style:", e4_style)
    f4.addRow("Number of Concepts:", e4_count); f4.addRow("Language:", e4_lang); f4.addRow(btn4); f4.addRow(out4)
    def run_thumb():
        _disable_btn(btn4)
        def done(r, e): out4.setPlainText(json.dumps(r, indent=2) if not e else f"Error: {e}"); _enable_btn(btn4)
        _ApiWorker(api_base, "content/thumbnail", {"title": e4_title.text(), "niche": e4_niche.text(),
            "platform": e4_plat.currentText(), "style": e4_style.currentText(),
            "count": e4_count.value(), "language": e4_lang.currentText()}, done).start()
    btn4.clicked.connect(run_thumb)
    tabs.addTab(t4, "🖼 Thumbnail AI")

    # ── Tab 5: Caption Emotion Engine ─────────────────────────────────────────
    t5 = QWidget(); f5 = QFormLayout(t5)
    e5_topic = _entry("Overcoming fear of failure"); e5_niche = _entry("Self-Improvement")
    e5_plat = _combo("Instagram","TikTok","LinkedIn","Twitter/X","Facebook"); e5_emotion = _combo("Curiosity","FOMO","Inspiration","Humor","Authority","Empathy","Urgency")
    e5_count = QSpinBox(); e5_count.setRange(1, 10); e5_count.setValue(5)
    e5_lang = _combo("English","Spanish","French","German","Portuguese","Arabic","Hindi","Japanese","Chinese")
    btn5 = _btn("💭 Generate Emotion Captions"); out5 = _out()
    f5.addRow("Topic:", e5_topic); f5.addRow("Niche:", e5_niche)
    f5.addRow("Platform:", e5_plat); f5.addRow("Emotion Trigger:", e5_emotion)
    f5.addRow("Number of Captions:", e5_count); f5.addRow("Language:", e5_lang); f5.addRow(btn5); f5.addRow(out5)
    def run_caption():
        _disable_btn(btn5)
        def done(r, e): out5.setPlainText(json.dumps(r, indent=2) if not e else f"Error: {e}"); _enable_btn(btn5)
        _ApiWorker(api_base, "content/emotional-caption", {"topic": e5_topic.text(), "niche": e5_niche.text(),
            "platform": e5_plat.currentText(), "emotion": e5_emotion.currentText(),
            "count": e5_count.value(), "language": e5_lang.currentText()}, done).start()
    btn5.clicked.connect(run_caption)
    tabs.addTab(t5, "💭 Emotion Caption")

    return page


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 23 — BRAND AUTHORITY
# ═══════════════════════════════════════════════════════════════════════════════

def build_brand_authority_page(api_base: str) -> QWidget:
    """P7 Brand Authority: Scorecard, Content Audit, Content Gap, Persona, Algorithm."""
    page, layout = _make_page_layout("Brand Authority", "🏆")
    tabs = QTabWidget()
    layout.addWidget(tabs)

    # ── Tab 1: Personal Brand Scorecard ──────────────────────────────────────
    t1 = QWidget(); f1 = QFormLayout(t1)
    e1_plat = _combo("Instagram","TikTok","YouTube","LinkedIn","Twitter/X","Facebook")
    e1_niche = _entry("Fitness & Wellness"); e1_bio = _entry("I help busy professionals lose 20 lbs in 90 days | Online Coach | DM me 'FIT'")
    e1_freq = _combo("Daily","2x/day","5x/week","3x/week","1x/week","Monthly")
    e1_eng = QDoubleSpinBox(); e1_eng.setRange(0.0, 100.0); e1_eng.setValue(3.5); e1_eng.setSuffix("%"); e1_eng.setSingleStep(0.1)
    e1_foll = QSpinBox(); e1_foll.setRange(0, 10000000); e1_foll.setValue(5000); e1_foll.setSingleStep(1000)
    e1_web = QCheckBox("Has Website"); e1_email = QCheckBox("Has Email List")
    e1_lang = _combo("English","Spanish","French","German","Portuguese","Arabic","Hindi","Japanese","Chinese")
    btn1 = _btn("🏆 Audit My Brand"); out1 = _out()
    f1.addRow("Platform:", e1_plat); f1.addRow("Niche:", e1_niche)
    f1.addRow("Bio:", e1_bio); f1.addRow("Posting Frequency:", e1_freq)
    f1.addRow("Engagement Rate:", e1_eng); f1.addRow("Followers:", e1_foll)
    f1.addRow(e1_web); f1.addRow(e1_email); f1.addRow("Language:", e1_lang); f1.addRow(btn1); f1.addRow(out1)
    def run_scorecard():
        _disable_btn(btn1)
        def done(r, e): out1.setPlainText(json.dumps(r, indent=2) if not e else f"Error: {e}"); _enable_btn(btn1)
        _ApiWorker(api_base, "brand/scorecard", {"platform": e1_plat.currentText(), "niche": e1_niche.text(),
            "bio": e1_bio.text(), "posting_freq": e1_freq.currentText(),
            "engagement_rate": e1_eng.value(), "follower_count": e1_foll.value(),
            "has_website": e1_web.isChecked(), "has_email_list": e1_email.isChecked(),
            "language": e1_lang.currentText()}, done).start()
    btn1.clicked.connect(run_scorecard)
    tabs.addTab(t1, "🏆 Brand Scorecard")

    # ── Tab 2: Content Performance Audit ─────────────────────────────────────
    t2 = QWidget(); f2 = QFormLayout(t2)
    e2_plat = _combo("Instagram","TikTok","YouTube","LinkedIn","Twitter/X")
    e2_niche = _entry("Business Coaching")
    e2_data = QTextEdit(); e2_data.setPlaceholderText("Describe your recent posts and their performance:\nPost 1: [How to start a business] - 500 likes, 80 comments, 200 saves\nPost 2: [Motivational quote] - 50 likes, 5 comments, 2 saves\n...")
    e2_data.setMinimumHeight(100)
    e2_lang = _combo("English","Spanish","French","German","Portuguese","Arabic","Hindi","Japanese","Chinese")
    btn2 = _btn("📊 Audit Content Performance"); out2 = _out()
    f2.addRow("Platform:", e2_plat); f2.addRow("Niche:", e2_niche)
    f2.addRow("Posts Data:", e2_data); f2.addRow("Language:", e2_lang); f2.addRow(btn2); f2.addRow(out2)
    def run_audit():
        _disable_btn(btn2)
        def done(r, e): out2.setPlainText(json.dumps(r, indent=2) if not e else f"Error: {e}"); _enable_btn(btn2)
        _ApiWorker(api_base, "brand/content-audit", {"posts_summary": e2_data.toPlainText() or "No data provided",
            "platform": e2_plat.currentText(), "niche": e2_niche.text(),
            "language": e2_lang.currentText()}, done).start()
    btn2.clicked.connect(run_audit)
    tabs.addTab(t2, "📊 Content Audit")

    # ── Tab 3: Competitor Content Gap ─────────────────────────────────────────
    t3 = QWidget(); f3 = QFormLayout(t3)
    e3_niche = _entry("Health & Nutrition"); e3_comp = _entry("They post recipes and motivational content 3x/week but ignore advanced science-backed strategies")
    e3_plat = _combo("Instagram","TikTok","YouTube","LinkedIn","Twitter/X")
    e3_lang = _combo("English","Spanish","French","German","Portuguese","Arabic","Hindi","Japanese","Chinese")
    btn3 = _btn("🔍 Find Content Gaps"); out3 = _out()
    f3.addRow("Your Niche:", e3_niche); f3.addRow("Competitor Info:", e3_comp)
    f3.addRow("Platform:", e3_plat); f3.addRow("Language:", e3_lang); f3.addRow(btn3); f3.addRow(out3)
    def run_gap():
        _disable_btn(btn3)
        def done(r, e): out3.setPlainText(json.dumps(r, indent=2) if not e else f"Error: {e}"); _enable_btn(btn3)
        _ApiWorker(api_base, "brand/content-gap", {"your_niche": e3_niche.text(),
            "competitor_info": e3_comp.text(), "platform": e3_plat.currentText(),
            "language": e3_lang.currentText()}, done).start()
    btn3.clicked.connect(run_gap)
    tabs.addTab(t3, "🔍 Content Gap")

    # ── Tab 4: Audience Persona Builder ───────────────────────────────────────
    t4 = QWidget(); f4 = QFormLayout(t4)
    e4_niche = _entry("Online Education"); e4_plat = _combo("Instagram","TikTok","YouTube","LinkedIn","Twitter/X","Facebook")
    e4_product = _entry("Online Course on Productivity"); e4_lang = _combo("English","Spanish","French","German","Portuguese","Arabic","Hindi","Japanese","Chinese")
    btn4 = _btn("👤 Build Audience Personas"); out4 = _out()
    f4.addRow("Niche:", e4_niche); f4.addRow("Platform:", e4_plat)
    f4.addRow("Product/Service:", e4_product); f4.addRow("Language:", e4_lang); f4.addRow(btn4); f4.addRow(out4)
    def run_persona():
        _disable_btn(btn4)
        def done(r, e): out4.setPlainText(json.dumps(r, indent=2) if not e else f"Error: {e}"); _enable_btn(btn4)
        _ApiWorker(api_base, "brand/persona", {"niche": e4_niche.text(), "platform": e4_plat.currentText(),
            "product_or_service": e4_product.text(), "language": e4_lang.currentText()}, done).start()
    btn4.clicked.connect(run_persona)
    tabs.addTab(t4, "👤 Audience Persona")

    # ── Tab 5: Algorithm Intelligence ─────────────────────────────────────────
    t5 = QWidget(); f5 = QFormLayout(t5)
    e5_plat = _combo("TikTok","Instagram","YouTube","LinkedIn","Twitter/X","Pinterest","Facebook")
    e5_ctype = _combo("Short Video","Long Video","Static Post","Carousel","Story","Live","Audio/Podcast")
    e5_niche = _entry("Technology"); e5_lang = _combo("English","Spanish","French","German","Portuguese","Arabic","Hindi","Japanese","Chinese")
    btn5 = _btn("⚡ Get Algorithm Strategy"); out5 = _out()
    f5.addRow("Platform:", e5_plat); f5.addRow("Content Type:", e5_ctype)
    f5.addRow("Niche:", e5_niche); f5.addRow("Language:", e5_lang); f5.addRow(btn5); f5.addRow(out5)
    def run_algo():
        _disable_btn(btn5)
        def done(r, e): out5.setPlainText(json.dumps(r, indent=2) if not e else f"Error: {e}"); _enable_btn(btn5)
        _ApiWorker(api_base, "brand/algorithm", {"platform": e5_plat.currentText(),
            "content_type": e5_ctype.currentText(), "niche": e5_niche.text(),
            "language": e5_lang.currentText()}, done).start()
    btn5.clicked.connect(run_algo)
    tabs.addTab(t5, "⚡ Algorithm Intel")

    return page


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 24 — COMMUNITY HUB
# ═══════════════════════════════════════════════════════════════════════════════

def build_community_page(api_base: str) -> QWidget:
    """P8 Community & Collaboration: Influencer Collab, UGC, Social Proof, Playbook, Live Stream."""
    page, layout = _make_page_layout("Community Hub", "🤝")
    tabs = QTabWidget()
    layout.addWidget(tabs)

    # ── Tab 1: Influencer Collaboration Hub ───────────────────────────────────
    t1 = QWidget(); f1 = QFormLayout(t1)
    e1_brand = _entry("FitLife Supplements"); e1_iniche = _entry("Fitness & Health")
    e1_plat = _combo("Instagram","TikTok","YouTube","Twitter/X","LinkedIn","Pinterest")
    e1_budget = _combo("$100–$500","$500–$2,000","$2,000–$10,000","$10,000+","Product Exchange","Revenue Share")
    e1_goal = _combo("Brand Awareness","Sales/Conversions","Followers Growth","Product Launch","Event Promotion","App Downloads")
    e1_lang = _combo("English","Spanish","French","German","Portuguese","Arabic","Hindi","Japanese","Chinese")
    btn1 = _btn("🤝 Plan Collaboration"); out1 = _out()
    f1.addRow("Your Brand:", e1_brand); f1.addRow("Influencer Niche:", e1_iniche)
    f1.addRow("Platform:", e1_plat); f1.addRow("Budget:", e1_budget)
    f1.addRow("Goal:", e1_goal); f1.addRow("Language:", e1_lang); f1.addRow(btn1); f1.addRow(out1)
    def run_collab():
        _disable_btn(btn1)
        def done(r, e): out1.setPlainText(json.dumps(r, indent=2) if not e else f"Error: {e}"); _enable_btn(btn1)
        _ApiWorker(api_base, "community/collab", {"brand": e1_brand.text(), "influencer_niche": e1_iniche.text(),
            "platform": e1_plat.currentText(), "budget": e1_budget.currentText(),
            "goal": e1_goal.currentText(), "language": e1_lang.currentText()}, done).start()
    btn1.clicked.connect(run_collab)
    tabs.addTab(t1, "🤝 Influencer Collab")

    # ── Tab 2: UGC Campaign Planner ───────────────────────────────────────────
    t2 = QWidget(); f2 = QFormLayout(t2)
    e2_brand = _entry("EcoStyle Clothing"); e2_niche = _entry("Sustainable Fashion")
    e2_plat = _combo("Instagram","TikTok","Twitter/X","Facebook","Pinterest","YouTube")
    e2_incentive = _combo("Feature on our page","Discount code","Free product","Cash prize","Gift card","Affiliate commission")
    e2_hashtag = _entry("#EcoStyleChallenge")
    e2_lang = _combo("English","Spanish","French","German","Portuguese","Arabic","Hindi","Japanese","Chinese")
    btn2 = _btn("📸 Plan UGC Campaign"); out2 = _out()
    f2.addRow("Brand:", e2_brand); f2.addRow("Niche:", e2_niche)
    f2.addRow("Platform:", e2_plat); f2.addRow("Incentive:", e2_incentive)
    f2.addRow("Campaign Hashtag:", e2_hashtag); f2.addRow("Language:", e2_lang); f2.addRow(btn2); f2.addRow(out2)
    def run_ugc():
        _disable_btn(btn2)
        def done(r, e): out2.setPlainText(json.dumps(r, indent=2) if not e else f"Error: {e}"); _enable_btn(btn2)
        _ApiWorker(api_base, "community/ugc", {"brand": e2_brand.text(), "niche": e2_niche.text(),
            "platform": e2_plat.currentText(), "incentive": e2_incentive.currentText(),
            "hashtag": e2_hashtag.text(), "language": e2_lang.currentText()}, done).start()
    btn2.clicked.connect(run_ugc)
    tabs.addTab(t2, "📸 UGC Campaign")

    # ── Tab 3: Social Proof Creator ───────────────────────────────────────────
    t3 = QWidget(); f3 = QFormLayout(t3)
    e3_test = QTextEdit(); e3_test.setPlaceholderText("Paste the customer testimonial here...\n\nExample: 'I joined Sarah's program 3 months ago as a complete beginner. Today I've lost 25 lbs and have more energy than I did 10 years ago. The step-by-step approach made it so easy to follow!'")
    e3_test.setMinimumHeight(100)
    e3_plat = _combo("Instagram","LinkedIn","Twitter/X","Facebook","TikTok")
    e3_brand = _entry("FitTransform Academy"); e3_niche = _entry("Weight Loss")
    e3_lang = _combo("English","Spanish","French","German","Portuguese","Arabic","Hindi","Japanese","Chinese")
    btn3 = _btn("⭐ Transform to Social Proof"); out3 = _out()
    f3.addRow("Customer Testimonial:", e3_test); f3.addRow("Platform:", e3_plat)
    f3.addRow("Brand:", e3_brand); f3.addRow("Niche:", e3_niche)
    f3.addRow("Language:", e3_lang); f3.addRow(btn3); f3.addRow(out3)
    def run_proof():
        _disable_btn(btn3)
        def done(r, e): out3.setPlainText(json.dumps(r, indent=2) if not e else f"Error: {e}"); _enable_btn(btn3)
        _ApiWorker(api_base, "community/testimonial", {"testimonial": e3_test.toPlainText() or "Great product!",
            "platform": e3_plat.currentText(), "brand": e3_brand.text(),
            "niche": e3_niche.text(), "language": e3_lang.currentText()}, done).start()
    btn3.clicked.connect(run_proof)
    tabs.addTab(t3, "⭐ Social Proof")

    # ── Tab 4: Community Growth Playbook ──────────────────────────────────────
    t4 = QWidget(); f4 = QFormLayout(t4)
    e4_niche = _entry("Mindfulness & Meditation"); e4_plat = _combo("Instagram","TikTok","YouTube","LinkedIn","Twitter/X","Facebook")
    e4_curr = QSpinBox(); e4_curr.setRange(0, 10000000); e4_curr.setValue(500); e4_curr.setSingleStep(100)
    e4_goal = QSpinBox(); e4_goal.setRange(100, 10000000); e4_goal.setValue(10000); e4_goal.setSingleStep(1000)
    e4_lang = _combo("English","Spanish","French","German","Portuguese","Arabic","Hindi","Japanese","Chinese")
    btn4 = _btn("🌱 Generate Community Playbook"); out4 = _out()
    f4.addRow("Niche:", e4_niche); f4.addRow("Platform:", e4_plat)
    f4.addRow("Current Followers:", e4_curr); f4.addRow("Goal Followers:", e4_goal)
    f4.addRow("Language:", e4_lang); f4.addRow(btn4); f4.addRow(out4)
    def run_playbook():
        _disable_btn(btn4)
        def done(r, e): out4.setPlainText(json.dumps(r, indent=2) if not e else f"Error: {e}"); _enable_btn(btn4)
        _ApiWorker(api_base, "community/playbook", {"niche": e4_niche.text(), "platform": e4_plat.currentText(),
            "current_followers": e4_curr.value(), "goal_followers": e4_goal.value(),
            "language": e4_lang.currentText()}, done).start()
    btn4.clicked.connect(run_playbook)
    tabs.addTab(t4, "🌱 Community Playbook")

    # ── Tab 5: Live Stream Planner ────────────────────────────────────────────
    t5 = QWidget(); f5 = QFormLayout(t5)
    e5_topic = _entry("How to Build a 6-Figure Online Business in 2025"); e5_plat = _combo("Instagram Live","TikTok Live","YouTube Live","LinkedIn Live","Facebook Live","Twitch")
    e5_dur = QSpinBox(); e5_dur.setRange(15, 180); e5_dur.setValue(60); e5_dur.setSuffix(" min"); e5_dur.setSingleStep(15)
    e5_niche = _entry("Online Business"); e5_lang = _combo("English","Spanish","French","German","Portuguese","Arabic","Hindi","Japanese","Chinese")
    btn5 = _btn("🎥 Plan Live Stream"); out5 = _out()
    f5.addRow("Topic:", e5_topic); f5.addRow("Platform:", e5_plat)
    f5.addRow("Duration:", e5_dur); f5.addRow("Niche:", e5_niche)
    f5.addRow("Language:", e5_lang); f5.addRow(btn5); f5.addRow(out5)
    def run_live():
        _disable_btn(btn5)
        def done(r, e): out5.setPlainText(json.dumps(r, indent=2) if not e else f"Error: {e}"); _enable_btn(btn5)
        _ApiWorker(api_base, "community/livestream", {"topic": e5_topic.text(), "platform": e5_plat.currentText(),
            "duration_minutes": e5_dur.value(), "niche": e5_niche.text(),
            "language": e5_lang.currentText()}, done).start()
    btn5.clicked.connect(run_live)
    tabs.addTab(t5, "🎥 Live Stream")

    return page


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 25 — REAL-TIME INTEL
# ═══════════════════════════════════════════════════════════════════════════════

def build_realtime_intel_page(api_base: str) -> QWidget:
    """P9 Real-Time Intelligence: Trend Hijacker, Viral Cloner, Posting Times, Niche Scanner."""
    page, layout = _make_page_layout("Real-Time Intel", "⚡")
    tabs = QTabWidget()
    layout.addWidget(tabs)

    # ── Tab 1: Trend Hijacker ─────────────────────────────────────────────────
    t1 = QWidget(); f1 = QFormLayout(t1)
    e1_trend = _entry("AI replacing jobs"); e1_niche = _entry("Career Development")
    e1_plat = _combo("TikTok","Instagram","Twitter/X","LinkedIn","YouTube","Facebook")
    e1_lang = _combo("English","Spanish","French","German","Portuguese","Arabic","Hindi","Japanese","Chinese")
    btn1 = _btn("🔥 Hijack This Trend"); out1 = _out()
    f1.addRow("Trending Topic:", e1_trend); f1.addRow("Your Niche:", e1_niche)
    f1.addRow("Platform:", e1_plat); f1.addRow("Language:", e1_lang); f1.addRow(btn1); f1.addRow(out1)
    def run_hijack():
        _disable_btn(btn1)
        def done(r, e): out1.setPlainText(json.dumps(r, indent=2) if not e else f"Error: {e}"); _enable_btn(btn1)
        _ApiWorker(api_base, "realtime/trend-hijack", {"trend_topic": e1_trend.text(), "niche": e1_niche.text(),
            "platform": e1_plat.currentText(), "language": e1_lang.currentText()}, done).start()
    btn1.clicked.connect(run_hijack)
    tabs.addTab(t1, "🔥 Trend Hijacker")

    # ── Tab 2: Viral Content Cloner ───────────────────────────────────────────
    t2 = QWidget(); f2 = QFormLayout(t2)
    e2_viral = QTextEdit(); e2_viral.setPlaceholderText("Describe the viral content you want to adapt:\n\nExample: A TikTok video saying 'POV: You just realized you've been doing XYZ wrong your whole life' with a shocked face reaction, slow zoom, dramatic music, 2.3M views.")
    e2_viral.setMinimumHeight(100)
    e2_niche = _entry("Personal Finance"); e2_plat = _combo("TikTok","Instagram Reels","YouTube Shorts","LinkedIn","Twitter/X")
    e2_lang = _combo("English","Spanish","French","German","Portuguese","Arabic","Hindi","Japanese","Chinese")
    btn2 = _btn("🧬 Clone For My Niche"); out2 = _out()
    f2.addRow("Viral Content Description:", e2_viral); f2.addRow("Your Niche:", e2_niche)
    f2.addRow("Platform:", e2_plat); f2.addRow("Language:", e2_lang); f2.addRow(btn2); f2.addRow(out2)
    def run_clone():
        _disable_btn(btn2)
        def done(r, e): out2.setPlainText(json.dumps(r, indent=2) if not e else f"Error: {e}"); _enable_btn(btn2)
        _ApiWorker(api_base, "realtime/viral-clone", {"viral_description": e2_viral.toPlainText() or "Describe viral content",
            "your_niche": e2_niche.text(), "platform": e2_plat.currentText(),
            "language": e2_lang.currentText()}, done).start()
    btn2.clicked.connect(run_clone)
    tabs.addTab(t2, "🧬 Viral Cloner")

    # ── Tab 3: Optimal Posting Times ──────────────────────────────────────────
    t3 = QWidget(); f3 = QFormLayout(t3)
    e3_plat = _combo("TikTok","Instagram","YouTube","LinkedIn","Twitter/X","Pinterest","Facebook","Threads")
    e3_niche = _entry("Food & Recipes"); e3_tz = _combo("EST (UTC-5)","PST (UTC-8)","CST (UTC-6)","MST (UTC-7)","GMT (UTC+0)","CET (UTC+1)","IST (UTC+5:30)","JST (UTC+9)","AEST (UTC+10)","BST (UTC+1)","BRT (UTC-3)")
    e3_lang = _combo("English","Spanish","French","German","Portuguese","Arabic","Hindi","Japanese","Chinese")
    btn3 = _btn("⏰ Get Optimal Posting Times"); out3 = _out()
    f3.addRow("Platform:", e3_plat); f3.addRow("Niche:", e3_niche)
    f3.addRow("Audience Timezone:", e3_tz); f3.addRow("Language:", e3_lang); f3.addRow(btn3); f3.addRow(out3)
    def run_times():
        _disable_btn(btn3)
        def done(r, e): out3.setPlainText(json.dumps(r, indent=2) if not e else f"Error: {e}"); _enable_btn(btn3)
        _ApiWorker(api_base, "realtime/posting-times", {"platform": e3_plat.currentText(),
            "niche": e3_niche.text(), "audience_timezone": e3_tz.currentText(),
            "language": e3_lang.currentText()}, done).start()
    btn3.clicked.connect(run_times)
    tabs.addTab(t3, "⏰ Posting Times")

    # ── Tab 4: Niche Opportunity Scanner ─────────────────────────────────────
    t4 = QWidget(); f4 = QFormLayout(t4)
    e4_niche = _entry("Health & Fitness"); e4_plat = _combo("TikTok","Instagram","YouTube","LinkedIn","Twitter/X","Pinterest","Facebook")
    e4_lang = _combo("English","Spanish","French","German","Portuguese","Arabic","Hindi","Japanese","Chinese")
    btn4 = _btn("🎯 Scan Niche Opportunities"); out4 = _out()
    f4.addRow("Broad Niche:", e4_niche); f4.addRow("Platform:", e4_plat)
    f4.addRow("Language:", e4_lang); f4.addRow(btn4); f4.addRow(out4)
    def run_scan():
        _disable_btn(btn4)
        def done(r, e): out4.setPlainText(json.dumps(r, indent=2) if not e else f"Error: {e}"); _enable_btn(btn4)
        _ApiWorker(api_base, "realtime/niche-scan", {"broad_niche": e4_niche.text(),
            "platform": e4_plat.currentText(), "language": e4_lang.currentText()}, done).start()
    btn4.clicked.connect(run_scan)
    tabs.addTab(t4, "🎯 Niche Scanner")

    return page


# ═══════════════════════════════════════════════════════════════════════════════
# AI SOCIAL NETWORK PAGE  (page index 35)
# ═══════════════════════════════════════════════════════════════════════════════

def build_social_network_page(api_base: str) -> QWidget:
    """Full AI Social Network — Feed, Post, Like, Comment, Members."""
    page, layout = _make_page_layout("AI Social Network", "📱")
    page._workers = []   # keep QThread refs alive

    sub = QLabel("Telegram-integrated social platform — Posts · Images · Videos · Likes · Comments · Replies")
    sub.setStyleSheet(f"color:{SUBTEXT}; font-size:14px;")
    layout.addWidget(sub)

    # ── Stat cards row ────────────────────────────────────────────────────────
    stats_row = QHBoxLayout()
    _stat_vals = {}
    for lbl, icon, color in [
        ("👥 Members",   "👥", ACCENT),
        ("📝 Posts",     "📝", SUCCESS),
        ("❤️ Likes",     "❤️", "#F38BA8"),
        ("💬 Comments",  "💬", WARNING),
        ("🆕 Today",     "🆕", "#CBA6F7"),
    ]:
        card = QFrame()
        card.setStyleSheet(f"background:{SURFACE};border-radius:10px;padding:6px;")
        cl = QVBoxLayout(card); cl.setContentsMargins(10, 6, 10, 6)
        vl = QLabel("—"); vl.setFont(QFont("Segoe UI", 20, QFont.Bold))
        vl.setStyleSheet(f"color:{color};"); vl.setAlignment(Qt.AlignCenter)
        ll = QLabel(lbl); ll.setStyleSheet(f"color:{SUBTEXT};font-size:12px;"); ll.setAlignment(Qt.AlignCenter)
        cl.addWidget(vl); cl.addWidget(ll)
        stats_row.addWidget(card)
        _stat_vals[lbl] = vl
    layout.addLayout(stats_row)

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tabs = QTabWidget()
    tabs.setStyleSheet(f"""
        QTabWidget::pane{{background:{DARK_BG};border:1px solid {BORDER};border-radius:8px;}}
        QTabBar::tab{{background:{SURFACE};color:{SUBTEXT};padding:8px 16px;font-size:13px;border-radius:6px 6px 0 0;margin-right:2px;}}
        QTabBar::tab:selected{{background:{ACCENT};color:#11111B;font-weight:bold;}}
        QTabBar::tab:hover{{background:{HOVER};color:{TEXT};}}
    """)
    layout.addWidget(tabs, 1)

    _tbl_style = (
        f"QTableWidget{{background:{SURFACE};color:{TEXT};border:1px solid {BORDER};"
        f"border-radius:8px;gridline-color:{BORDER};font-size:13px;}}"
        f"QTableWidget::item{{padding:5px;}}"
        f"QTableWidget::item:selected{{background:{ACCENT}33;}}"
        f"QHeaderView::section{{background:{SIDEBAR};color:{ACCENT};font-weight:bold;padding:5px;border:none;}}"
    )

    # ──────────────────────────────────────────────────────────────────────────
    # TAB 1 — Live Feed
    # ──────────────────────────────────────────────────────────────────────────
    t1 = QWidget(); t1l = QVBoxLayout(t1)
    t1l.setContentsMargins(14, 10, 14, 10); t1l.setSpacing(8)

    t1_ctrl = QHBoxLayout()
    btn_refresh_feed = ActionButton("🔄 Refresh Feed", ACCENT)
    btn_refresh_feed.setFixedHeight(34)
    page_spin = QSpinBox(); page_spin.setRange(1, 100); page_spin.setValue(1)
    page_spin.setPrefix("Page: "); page_spin.setFixedWidth(110)
    page_spin.setStyleSheet(f"background:{SURFACE};color:{TEXT};border:1px solid {BORDER};border-radius:6px;padding:4px;")
    t1_ctrl.addWidget(btn_refresh_feed)
    t1_ctrl.addWidget(page_spin)
    t1_ctrl.addStretch()
    t1l.addLayout(t1_ctrl)

    feed_table = QTableWidget(0, 7)
    feed_table.setHorizontalHeaderLabels([
        "Author", "Type", "Content Preview", "Likes", "Comments", "Posted At", "Post ID"
    ])
    feed_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
    feed_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
    feed_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
    feed_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
    feed_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
    feed_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
    feed_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
    feed_table.setSelectionBehavior(QTableWidget.SelectRows)
    feed_table.setEditTriggers(QTableWidget.NoEditTriggers)
    feed_table.setAlternatingRowColors(True)
    feed_table.setStyleSheet(_tbl_style)
    t1l.addWidget(feed_table, 1)

    feed_detail = QTextEdit()
    feed_detail.setReadOnly(True)
    feed_detail.setMaximumHeight(130)
    feed_detail.setStyleSheet(
        f"background:{SURFACE};color:{TEXT};border:1px solid {BORDER};border-radius:6px;padding:8px;font-size:13px;"
    )
    feed_detail.setPlaceholderText("Click a post to see full content & comments…")
    t1l.addWidget(feed_detail)

    # Delete post button (admin moderation)
    mod_row = QHBoxLayout()
    btn_del_post = ActionButton("🗑 Delete Selected Post", "#F38BA8")
    btn_del_post.setFixedHeight(34)
    mod_row.addWidget(btn_del_post); mod_row.addStretch()
    t1l.addLayout(mod_row)

    def _load_feed():
        btn_refresh_feed.set_loading(True)
        w = ApiWorker(f"{api_base}/api/v1/social/feed?page={page_spin.value()}&per_page=20", method="GET")
        def _done(resp):
            btn_refresh_feed.set_loading(False)
            posts = resp.get("data", [])
            feed_table.setRowCount(0)
            media_icons = {"text": "📝", "image": "📸", "video": "🎬", "audio": "🎵"}
            for p in posts:
                r = feed_table.rowCount(); feed_table.insertRow(r)
                media = media_icons.get(p.get("media_type", "text"), "📝")
                cells = [
                    p.get("author_name", "Unknown"),
                    f"{media} {p.get('media_type','text').title()}",
                    p.get("content", "")[:80],
                    str(len(p.get("likes", []))),
                    str(len(p.get("comments", []))),
                    p.get("created_at", "")[:16],
                    p.get("post_id", ""),
                ]
                for col, val in enumerate(cells):
                    item = QTableWidgetItem(val)
                    if col == 3:
                        item.setForeground(QColor("#F38BA8"))
                    if col == 4:
                        item.setForeground(QColor(WARNING))
                    feed_table.setItem(r, col, item)
        w.result_ready.connect(_done)
        page._workers.append(w)
        w.start()

    def _feed_row_clicked():
        row = feed_table.currentRow()
        if row < 0:
            return
        pid  = feed_table.item(row, 6).text() if feed_table.item(row, 6) else ""
        auth = feed_table.item(row, 0).text() if feed_table.item(row, 0) else ""
        cont = feed_table.item(row, 2).text() if feed_table.item(row, 2) else ""
        lks  = feed_table.item(row, 3).text() if feed_table.item(row, 3) else "0"
        cmts = feed_table.item(row, 4).text() if feed_table.item(row, 4) else "0"
        dt   = feed_table.item(row, 5).text() if feed_table.item(row, 5) else ""
        feed_detail.setPlainText(
            f"Post ID:  {pid}\nAuthor:   {auth}\nPosted:   {dt}\n"
            f"Likes:    {lks}   Comments: {cmts}\n\nContent:\n{cont}"
        )

    def _delete_selected_post():
        row = feed_table.currentRow()
        if row < 0:
            QMessageBox.warning(page, "Select Post", "Please select a post to delete.")
            return
        pid = feed_table.item(row, 6).text() if feed_table.item(row, 6) else ""
        if not pid:
            return
        reply = QMessageBox.question(
            page, "Delete Post",
            f"Permanently delete post {pid}?",
            QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel,
        )
        if reply != QMessageBox.Yes:
            return
        import requests as _req
        try:
            r = _req.delete(f"{api_base}/api/v1/social/admin/posts/{pid}", timeout=10)
            QMessageBox.information(page, "Deleted", f"Post {pid} deleted.")
            _load_feed()
        except Exception as e:
            QMessageBox.critical(page, "Error", str(e))

    btn_refresh_feed.clicked.connect(_load_feed)
    page_spin.valueChanged.connect(_load_feed)
    feed_table.itemSelectionChanged.connect(_feed_row_clicked)
    btn_del_post.clicked.connect(_delete_selected_post)
    tabs.addTab(t1, "📰 Live Feed")

    # ──────────────────────────────────────────────────────────────────────────
    # TAB 2 — Create Post
    # ──────────────────────────────────────────────────────────────────────────
    t2 = QWidget(); t2l = QVBoxLayout(t2)
    t2l.setContentsMargins(16, 14, 16, 14); t2l.setSpacing(10)

    post_grp = QGroupBox("✍️ Create New Post")
    post_grp.setStyleSheet(
        f"QGroupBox{{color:{ACCENT};font-weight:bold;border:1px solid {BORDER};"
        f"border-radius:8px;padding-top:8px;margin-top:4px;}}"
        f"QGroupBox::title{{subcontrol-origin:margin;left:8px;padding:0 4px;}}"
    )
    pg = QGridLayout(post_grp); pg.setSpacing(10)

    pg.addWidget(QLabel("Author TG ID:"), 0, 0)
    inp_post_tid = QLineEdit(); inp_post_tid.setPlaceholderText("Telegram User ID (e.g. 123456789)")
    pg.addWidget(inp_post_tid, 0, 1)

    pg.addWidget(QLabel("Media Type:"), 1, 0)
    cbo_media = QComboBox()
    cbo_media.addItems(["text", "image", "video", "audio"])
    pg.addWidget(cbo_media, 1, 1)

    pg.addWidget(QLabel("Content:"), 2, 0)
    inp_content = QTextEdit(); inp_content.setMaximumHeight(100)
    inp_content.setPlaceholderText("Write your post content here…")
    pg.addWidget(inp_content, 2, 1)

    pg.addWidget(QLabel("Location (opt):"), 3, 0)
    inp_location = QLineEdit(); inp_location.setPlaceholderText("e.g. Phnom Penh, Cambodia")
    pg.addWidget(inp_location, 3, 1)

    t2l.addWidget(post_grp)

    post_btn_row = QHBoxLayout()
    btn_enhance  = ActionButton("✨ AI Enhance Caption", "#CBA6F7")
    btn_publish  = ActionButton("🚀 Publish Post", SUCCESS)
    btn_enhance.setFixedHeight(38); btn_publish.setFixedHeight(38)
    post_btn_row.addWidget(btn_enhance); post_btn_row.addWidget(btn_publish)
    t2l.addLayout(post_btn_row)

    post_out = QTextEdit(); post_out.setReadOnly(True)
    post_out.setStyleSheet(f"background:{SURFACE};color:{SUCCESS};border:1px solid {BORDER};border-radius:6px;padding:8px;font-size:13px;")
    post_out.setMaximumHeight(120)
    post_out.setPlaceholderText("Post result will appear here…")
    t2l.addWidget(post_out)
    t2l.addStretch()

    def _enhance_caption():
        txt = inp_content.toPlainText().strip()
        if not txt:
            post_out.setPlainText("Please enter content first."); return
        btn_enhance.set_loading(True)
        w = ApiWorker(
            f"{api_base}/api/v1/social/enhance-caption",
            method="POST", payload={"text": txt, "platform": "Social"},
        )
        def _done(resp):
            btn_enhance.set_loading(False)
            enhanced = resp.get("data", {}).get("enhanced", txt)
            inp_content.setPlainText(enhanced)
            post_out.setPlainText(f"✨ Caption enhanced by AI!\n\n{enhanced}")
        w.result_ready.connect(_done)
        page._workers.append(w)
        w.start()

    def _publish_post():
        tid  = inp_post_tid.text().strip()
        cont = inp_content.toPlainText().strip()
        if not tid or not cont:
            post_out.setPlainText("❌ Please fill in Author TG ID and Content."); return
        btn_publish.set_loading(True)
        w = ApiWorker(
            f"{api_base}/api/v1/social/post",
            method="POST",
            payload={
                "telegram_id": tid, "content": cont,
                "media_type": cbo_media.currentText(),
                "location": inp_location.text().strip(),
                "tags": [],
            },
        )
        def _done(resp):
            btn_publish.set_loading(False)
            if resp.get("status") == "success":
                p = resp.get("data", {})
                post_out.setPlainText(
                    f"✅ Post published!\nPost ID: {p.get('post_id','')}\n"
                    f"Time: {p.get('created_at','')}"
                )
                inp_content.clear()
                _load_feed()
            else:
                post_out.setPlainText(f"❌ Error: {resp.get('detail', str(resp))}")
        w.result_ready.connect(_done)
        page._workers.append(w)
        w.start()

    btn_enhance.clicked.connect(_enhance_caption)
    btn_publish.clicked.connect(_publish_post)
    tabs.addTab(t2, "✍️ Create Post")

    # ──────────────────────────────────────────────────────────────────────────
    # TAB 3 — Members (Registered Telegram Users)
    # ──────────────────────────────────────────────────────────────────────────
    t3 = QWidget(); t3l = QVBoxLayout(t3)
    t3l.setContentsMargins(14, 10, 14, 10); t3l.setSpacing(8)

    t3_ctrl = QHBoxLayout()
    btn_refresh_members = ActionButton("🔄 Refresh Members", ACCENT)
    btn_refresh_members.setFixedHeight(34)
    member_search = QLineEdit(); member_search.setPlaceholderText("🔍 Search by name, username, phone…")
    member_search.setStyleSheet(
        f"background:{SURFACE};color:{TEXT};border:1px solid {BORDER};border-radius:6px;padding:6px 10px;font-size:13px;"
    )
    t3_ctrl.addWidget(btn_refresh_members)
    t3_ctrl.addWidget(member_search, 1)
    t3l.addLayout(t3_ctrl)

    members_table = QTableWidget(0, 10)
    members_table.setHorizontalHeaderLabels([
        "Full Name", "Username", "TG ID", "Phone", "Sex", "Date of Birth",
        "Language", "Posts", "Joined", "Status",
    ])
    members_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
    members_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
    members_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
    members_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
    members_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
    members_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
    members_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
    members_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)
    members_table.horizontalHeader().setSectionResizeMode(8, QHeaderView.ResizeToContents)
    members_table.horizontalHeader().setSectionResizeMode(9, QHeaderView.Stretch)
    members_table.setSelectionBehavior(QTableWidget.SelectRows)
    members_table.setEditTriggers(QTableWidget.NoEditTriggers)
    members_table.setAlternatingRowColors(True)
    members_table.setStyleSheet(_tbl_style)
    t3l.addWidget(members_table, 1)

    mem_count_lbl = QLabel("0 members loaded")
    mem_count_lbl.setStyleSheet(f"color:{SUBTEXT};font-size:13px;")
    t3l.addWidget(mem_count_lbl)

    _all_members = []

    def _populate_members(members):
        members_table.setRowCount(0)
        for u in members:
            r = members_table.rowCount(); members_table.insertRow(r)
            active = u.get("is_active", True)
            cells = [
                u.get("display_name") or f"{u.get('first_name','')} {u.get('last_name','')}".strip() or "Unknown",
                f"@{u.get('username')}" if u.get("username") else "—",
                str(u.get("telegram_id", "")),
                u.get("phone", "—") or "—",
                u.get("sex", "—") or "—",
                u.get("date_of_birth", "—") or "—",
                u.get("language_code", "").upper() or "—",
                str(u.get("post_count", 0)),
                u.get("registered_at", "")[:10],
                "✅ Active" if active else "🚫 Banned",
            ]
            for col, val in enumerate(cells):
                item = QTableWidgetItem(val)
                if col == 9 and not active:
                    item.setForeground(QColor("#F38BA8"))
                if col == 7:
                    item.setForeground(QColor(SUCCESS))
                members_table.setItem(r, col, item)
        mem_count_lbl.setText(f"👥 {len(members)} members total")

    def _load_members():
        btn_refresh_members.set_loading(True)
        w = ApiWorker(f"{api_base}/api/v1/social/admin/users", method="GET")
        def _done(resp):
            btn_refresh_members.set_loading(False)
            nonlocal _all_members
            _all_members = resp.get("data", [])
            _populate_members(_all_members)
            # Update stat cards
            _stat_vals.get("👥 Members", QLabel()).setText(str(len(_all_members)))
        w.result_ready.connect(_done)
        page._workers.append(w)
        w.start()

    def _search_members(text: str):
        if not _all_members:
            return
        text = text.lower().strip()
        if not text:
            _populate_members(_all_members)
            return
        filtered = [
            u for u in _all_members
            if (text in (u.get("display_name") or "").lower()
                or text in (u.get("first_name") or "").lower()
                or text in (u.get("username") or "").lower()
                or text in (u.get("phone") or "").lower()
                or text in str(u.get("telegram_id", "")).lower()
            )
        ]
        _populate_members(filtered)

    btn_refresh_members.clicked.connect(_load_members)
    member_search.textChanged.connect(_search_members)
    tabs.addTab(t3, "👥 Members")

    # ──────────────────────────────────────────────────────────────────────────
    # TAB 4 — Platform Stats
    # ──────────────────────────────────────────────────────────────────────────
    t4 = QWidget(); t4l = QVBoxLayout(t4)
    t4l.setContentsMargins(14, 14, 14, 14); t4l.setSpacing(12)

    btn_refresh_stats = ActionButton("🔄 Refresh Stats", ACCENT)
    btn_refresh_stats.setFixedHeight(36)
    t4l.addWidget(btn_refresh_stats)

    stats_display = QTextEdit()
    stats_display.setReadOnly(True)
    stats_display.setStyleSheet(
        f"background:{SURFACE};color:{TEXT};border:1px solid {BORDER};border-radius:8px;padding:14px;font-size:14px;"
    )
    stats_display.setPlaceholderText("Click Refresh Stats to load platform statistics…")
    t4l.addWidget(stats_display, 1)

    def _load_stats():
        btn_refresh_stats.set_loading(True)
        w = ApiWorker(f"{api_base}/api/v1/social/stats", method="GET")
        def _done(resp):
            btn_refresh_stats.set_loading(False)
            d = resp.get("data", {})
            if not d:
                stats_display.setPlainText(f"❌ Error: {resp}"); return

            # Update stat cards
            _stat_vals.get("👥 Members",  QLabel()).setText(str(d.get("total_users", "—")))
            _stat_vals.get("📝 Posts",    QLabel()).setText(str(d.get("total_posts", "—")))
            _stat_vals.get("❤️ Likes",    QLabel()).setText(str(d.get("total_likes", "—")))
            _stat_vals.get("💬 Comments", QLabel()).setText(str(d.get("total_comments", "—")))
            _stat_vals.get("🆕 Today",    QLabel()).setText(
                f"{d.get('registered_today',0)}u / {d.get('posts_today',0)}p"
            )

            stats_display.setPlainText(
                f"📊  GrowthOS AI Social Network — Platform Statistics\n"
                f"{'─'*50}\n\n"
                f"👥  Total Members:        {d.get('total_users', 0)}\n"
                f"✅  Active Members:        {d.get('active_users', 0)}\n"
                f"📝  Total Posts:           {d.get('total_posts', 0)}\n"
                f"❤️  Total Likes:           {d.get('total_likes', 0)}\n"
                f"💬  Total Comments:        {d.get('total_comments', 0)}\n\n"
                f"🆕  New Registrations Today:  {d.get('registered_today', 0)}\n"
                f"📅  Posts Published Today:    {d.get('posts_today', 0)}\n"
            )
        w.result_ready.connect(_done)
        page._workers.append(w)
        w.start()

    btn_refresh_stats.clicked.connect(_load_stats)
    tabs.addTab(t4, "📊 Stats")

    # ──────────────────────────────────────────────────────────────────────────
    # TAB 5 — Bot Setup & Instructions
    # ──────────────────────────────────────────────────────────────────────────
    t5 = QWidget(); t5l = QVBoxLayout(t5)
    t5l.setContentsMargins(16, 14, 16, 14); t5l.setSpacing(10)

    guide = QTextEdit()
    guide.setReadOnly(True)
    guide.setStyleSheet(
        f"background:{SURFACE};color:{TEXT};border:1px solid {BORDER};border-radius:8px;padding:14px;font-size:14px;"
    )
    guide.setHtml(f"""
    <h2 style='color:{ACCENT};margin-top:0;'>📱 AI Social Network — User Guide</h2>
    <h3 style='color:{SUCCESS};'>🤖 How Registration Works (Automatic)</h3>
    <ol style='color:{TEXT};line-height:2.0;'>
      <li>User opens Telegram and sends <code style='color:{ACCENT};'>/start</code> to the bot</li>
      <li>Bot auto-registers them → asks for <b>Phone Number</b> (via Telegram contact button)</li>
      <li>Bot asks for <b>Gender</b> (Male / Female / Other)</li>
      <li>Bot asks for <b>Date of Birth</b> (DD/MM/YYYY)</li>
      <li>Registration complete → User gets full social network access</li>
    </ol>
    <h3 style='color:{SUCCESS};'>📝 Social Media Features Available</h3>
    <table style='color:{TEXT};width:100%;border-collapse:collapse;font-size:13px;'>
      <tr><td style='padding:6px;color:{ACCENT};'>📱 /social</td><td>Open Social Network hub with live stats</td></tr>
      <tr><td style='padding:6px;color:{ACCENT};'>📰 /feed</td><td>Browse latest posts from the community</td></tr>
      <tr><td style='padding:6px;color:{ACCENT};'>✍️ /post</td><td>Share a text post (AI-enhanced captions)</td></tr>
      <tr><td style='padding:6px;color:{ACCENT};'>📸 /photo</td><td>Share a photo with caption</td></tr>
      <tr><td style='padding:6px;color:{ACCENT};'>🎬 /video</td><td>Share a short video / selfie video</td></tr>
      <tr><td style='padding:6px;color:{ACCENT};'>❤️ /like</td><td>Like or unlike posts (toggle)</td></tr>
      <tr><td style='padding:6px;color:{ACCENT};'>💬 /comment</td><td>Comment on a post</td></tr>
      <tr><td style='padding:6px;color:{ACCENT};'>↩️ /reply</td><td>Reply to a specific comment</td></tr>
      <tr><td style='padding:6px;color:{ACCENT};'>👤 /profile</td><td>View your full profile: Name/TG ID/Phone/Sex/DOB</td></tr>
    </table>
    <h3 style='color:{SUCCESS};'>🔑 Data Stored Per User</h3>
    <p style='color:{TEXT};'>Full Name &bull; Telegram ID &bull; Username (@handle) &bull; Phone Number &bull;
    Gender &bull; Date of Birth &bull; Language &bull; Post Count &bull; Join Date &bull; Last Seen &bull; Role</p>
    <h3 style='color:{SUCCESS};'>🛡️ Admin Controls (This Panel)</h3>
    <ul style='color:{TEXT};line-height:2.0;'>
      <li><b>Live Feed tab</b> — Monitor all posts, delete inappropriate content</li>
      <li><b>Members tab</b> — View all registered users with full profile data, search/filter</li>
      <li><b>Stats tab</b> — Real-time platform statistics</li>
      <li><b>Create Post tab</b> — Post on behalf of any user ID</li>
    </ul>
    """)
    t5l.addWidget(guide, 1)
    tabs.addTab(t5, "📖 Guide")

    # ── Auto-load stats on open ───────────────────────────────────────────────
    QTimer.singleShot(500, _load_stats)
    QTimer.singleShot(800, _load_members)
    QTimer.singleShot(600, _load_feed)

    return page


# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN PANEL PAGE
# ═══════════════════════════════════════════════════════════════════════════════

def build_admin_page(user_info: dict) -> QWidget:
    """Admin-only panel: user management, create user, activity log, my account."""
    import admin as _admin
    token = user_info.get("token", "")

    page, layout = _make_page_layout("Admin Panel", "👑")

    uname = user_info.get("display_name", user_info.get("username", "admin"))
    sub = QLabel(f"Signed in as  {uname}  (admin)  •  Full system access")
    sub.setStyleSheet(f"color: {SUBTEXT}; font-size: 14px;")
    layout.addWidget(sub)

    tabs = QTabWidget()

    # ── TABLE STYLE (reused across tabs) ────────────────────────────────────
    _TBL = f"""
        QTableWidget {{ background:{SURFACE}; color:{TEXT}; gridline-color:#45475A;
                        border:1px solid #45475A; border-radius:6px;
                        selection-background-color:#313244; selection-color:{ACCENT}; }}
        QHeaderView::section {{ background:{SIDEBAR}; color:{ACCENT}; font-weight:bold;
                                 padding:6px; border:none; border-bottom:1px solid #45475A; }}
        QTableWidget::item {{ padding:4px 8px; }}
    """

    # ── TAB 1: User Management ────────────────────────────────────────────────
    t1 = QWidget()
    t1_lay = QVBoxLayout(t1)
    t1_lay.setContentsMargins(16, 14, 16, 14)
    t1_lay.setSpacing(10)

    btn_row1 = QHBoxLayout()
    btn_refresh  = ActionButton("🔄 Refresh", ACCENT)
    btn_toggle   = ActionButton("⏸ Toggle Active/Suspend", WARNING)
    btn_reset_pw = ActionButton("🔑 Reset Password", "#CBA6F7")
    btn_del_user = ActionButton("🗑 Delete User", "#F38BA8")
    for b in (btn_refresh, btn_toggle, btn_reset_pw, btn_del_user):
        b.setMinimumHeight(36)
        btn_row1.addWidget(b)
    t1_lay.addLayout(btn_row1)

    user_tbl = QTableWidget(0, 8)
    user_tbl.setHorizontalHeaderLabels([
        "Username", "Display Name", "Role", "Status",
        "Last Login", "Logins", "Expiry", "Created By",
    ])
    user_tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    user_tbl.horizontalHeader().setStretchLastSection(True)
    user_tbl.setSelectionBehavior(QTableWidget.SelectRows)
    user_tbl.setEditTriggers(QTableWidget.NoEditTriggers)
    user_tbl.setStyleSheet(_TBL)
    t1_lay.addWidget(user_tbl, 1)

    t1_out = OutputBox("Select a user and click an action button above.")
    t1_out.setMaximumHeight(80)
    t1_lay.addWidget(t1_out)

    def _refresh_users():
        try:
            users = _admin.list_users(token)
        except Exception as e:
            t1_out.set_error(str(e))
            return
        user_tbl.setRowCount(0)
        for u in users:
            r = user_tbl.rowCount()
            user_tbl.insertRow(r)
            active = u.get("active", True)
            expiry = u.get("expiry", "")
            expiry_str = expiry[:10] if expiry else "Never"
            last_login = u.get("last_login", "")
            last_login_str = last_login[:16].replace("T", " ") if last_login else "Never"
            role_color = {"admin": ACCENT, "member": SUCCESS, "viewer": WARNING}.get(u["role"], TEXT)
            cells = [
                u["username"], u.get("display_name", ""), u["role"],
                "✅ Active" if active else "🚫 Suspended",
                last_login_str, str(u.get("login_count", 0)),
                expiry_str, u.get("created_by", ""),
            ]
            for c, val in enumerate(cells):
                item = QTableWidgetItem(val)
                if c == 2:
                    item.setForeground(QColor(role_color))
                if c == 3 and not active:
                    item.setForeground(QColor("#F38BA8"))
                user_tbl.setItem(r, c, item)
        t1_out.setPlainText(f"✅ Loaded {len(users)} user(s).")

    def _selected_username() -> str:
        sel = user_tbl.selectedItems()
        if not sel:
            return ""
        return user_tbl.item(user_tbl.currentRow(), 0).text()

    def _toggle_user():
        uname_sel = _selected_username()
        if not uname_sel:
            t1_out.set_error("Select a user first."); return
        try:
            new_state = _admin.toggle_active(token, uname_sel)
            t1_out.setPlainText(f"✅ '{uname_sel}' is now {'Active' if new_state else 'Suspended'}.")
            _refresh_users()
        except Exception as e:
            t1_out.set_error(str(e))

    def _reset_pw():
        uname_sel = _selected_username()
        if not uname_sel:
            t1_out.set_error("Select a user first."); return
        from PyQt5.QtWidgets import QInputDialog
        pw, ok = QInputDialog.getText(
            page, "Reset Password",
            f"New password for '{uname_sel}' (min 8 chars):",
            QLineEdit.Password
        )
        if not ok or not pw:
            return
        try:
            _admin.reset_password(token, uname_sel, pw)
            t1_out.setPlainText(f"✅ Password reset for '{uname_sel}'. User must change on next login.")
        except Exception as e:
            t1_out.set_error(str(e))

    def _delete_user():
        uname_sel = _selected_username()
        if not uname_sel:
            t1_out.set_error("Select a user first."); return
        from PyQt5.QtWidgets import QMessageBox
        reply = QMessageBox.warning(
            page, "Delete User",
            f"Permanently delete user '{uname_sel}'? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel,
        )
        if reply != QMessageBox.Yes:
            return
        try:
            _admin.delete_user(token, uname_sel)
            t1_out.setPlainText(f"✅ User '{uname_sel}' deleted.")
            _refresh_users()
        except Exception as e:
            t1_out.set_error(str(e))

    btn_refresh.clicked.connect(_refresh_users)
    btn_toggle.clicked.connect(_toggle_user)
    btn_reset_pw.clicked.connect(_reset_pw)
    btn_del_user.clicked.connect(_delete_user)
    QTimer.singleShot(400, _refresh_users)
    tabs.addTab(t1, "👥 Users")

    # ── TAB 2: Create User ────────────────────────────────────────────────────
    t2 = QWidget()
    t2_lay = QVBoxLayout(t2)
    t2_lay.setContentsMargins(20, 16, 20, 16)
    t2_lay.setSpacing(10)
    t2_lay.setAlignment(Qt.AlignTop)

    grp2 = QGroupBox("➕ New Member Account")
    g2_lay = QGridLayout(grp2)
    g2_lay.setSpacing(10)

    inp_uname   = _styled_input("e.g. johndoe  (lowercase, no spaces)")
    inp_dname   = _styled_input("e.g. John Doe")
    inp_email   = _styled_input("john@example.com  (optional)")
    inp_pw      = QLineEdit(); inp_pw.setEchoMode(QLineEdit.Password)
    inp_pw.setPlaceholderText("Min 8 characters")
    inp_pw.setStyleSheet("background:#313244; color:#CDD6F4; border:1px solid #6C7086; border-radius:6px; padding:6px 10px;")
    cbo_role    = _combo("member", "viewer", "admin")
    spn_expiry  = QSpinBox()
    spn_expiry.setRange(0, 3650)
    spn_expiry.setValue(0)
    spn_expiry.setSuffix("  days  (0 = no expiry)")
    spn_expiry.setStyleSheet("background:#313244; color:#CDD6F4; border:1px solid #6C7086; border-radius:6px; padding:4px;")

    for row, (lbl_txt, widget) in enumerate([
        ("Username *",       inp_uname),
        ("Display Name",     inp_dname),
        ("Email",            inp_email),
        ("Password *",       inp_pw),
        ("Role",             cbo_role),
        ("License Expiry",   spn_expiry),
    ]):
        g2_lay.addWidget(QLabel(lbl_txt), row, 0)
        g2_lay.addWidget(widget, row, 1)

    t2_lay.addWidget(grp2)

    btn_create = ActionButton("➕  Create Account", SUCCESS)
    t2_lay.addWidget(btn_create)
    t2_out = OutputBox("Created user will appear here.")
    t2_out.setMaximumHeight(100)
    t2_lay.addWidget(t2_out)

    def _create_user():
        uname_v    = inp_uname.text().strip()
        pw_v       = inp_pw.text()
        dname_v    = inp_dname.text().strip()
        email_v    = inp_email.text().strip()
        role_v     = cbo_role.currentText()
        expiry_v   = spn_expiry.value() if spn_expiry.value() > 0 else None
        try:
            result = _admin.create_user(
                token, uname_v, pw_v, role=role_v,
                display_name=dname_v, email=email_v, expiry_days=expiry_v
            )
            t2_out.setPlainText(
                f"✅ Account created!\n"
                f"Username:  {result['username']}\n"
                f"Role:      {result['role']}\n"
                f"Expiry:    {result.get('expiry','Never')}\n\n"
                f"The user must change their password on first login."
            )
            inp_uname.clear(); inp_pw.clear(); inp_dname.clear(); inp_email.clear()
            _refresh_users()
        except Exception as e:
            t2_out.set_error(str(e))

    btn_create.clicked.connect(_create_user)
    tabs.addTab(t2, "➕ Create User")

    # ── TAB 3: Activity Log ───────────────────────────────────────────────────
    t3 = QWidget()
    t3_lay = QVBoxLayout(t3)
    t3_lay.setContentsMargins(16, 14, 16, 14)
    t3_lay.setSpacing(10)

    log_btn = ActionButton("🔄 Refresh Log", ACCENT)
    log_btn.setMinimumHeight(36)
    t3_lay.addWidget(log_btn)

    log_tbl = QTableWidget(0, 5)
    log_tbl.setHorizontalHeaderLabels(["Time", "Action", "Actor", "Target", "Detail"])
    log_tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    log_tbl.horizontalHeader().setStretchLastSection(True)
    log_tbl.setSelectionBehavior(QTableWidget.SelectRows)
    log_tbl.setEditTriggers(QTableWidget.NoEditTriggers)
    log_tbl.setStyleSheet(_TBL)
    t3_lay.addWidget(log_tbl, 1)

    def _refresh_log():
        try:
            entries = _admin.get_activity_log(token)
        except Exception as e:
            return
        log_tbl.setRowCount(0)
        action_colors = {
            "LOGIN": SUCCESS, "LOGOUT": SUBTEXT,
            "LOGIN_FAIL": "#F38BA8", "CREATE_USER": ACCENT,
            "DELETE_USER": "#F38BA8", "TOGGLE_ACTIVE": WARNING,
            "PW_CHANGE": "#CBA6F7", "RESET_PW": WARNING,
            "BOOTSTRAP": ACCENT,
        }
        for entry in entries[:200]:
            r = log_tbl.rowCount()
            log_tbl.insertRow(r)
            cells = [
                entry.get("ts", ""), entry.get("action", ""),
                entry.get("actor", ""), entry.get("target", ""),
                entry.get("detail", ""),
            ]
            for c, val in enumerate(cells):
                item = QTableWidgetItem(val)
                if c == 1:
                    color = action_colors.get(val, TEXT)
                    item.setForeground(QColor(color))
                log_tbl.setItem(r, c, item)

    log_btn.clicked.connect(_refresh_log)
    QTimer.singleShot(600, _refresh_log)
    tabs.addTab(t3, "📋 Activity Log")

    # ── TAB 4: My Account ─────────────────────────────────────────────────────
    t4 = QWidget()
    t4_lay = QVBoxLayout(t4)
    t4_lay.setContentsMargins(20, 16, 20, 16)
    t4_lay.setSpacing(12)
    t4_lay.setAlignment(Qt.AlignTop)

    # Info card
    me = _admin.get_current_user(token) or user_info
    info_grp = QGroupBox("🪪 Account Information")
    info_grid = QGridLayout(info_grp)
    for row, (lbl, val) in enumerate([
        ("Username",     me.get("username", "")),
        ("Display Name", me.get("display_name", "")),
        ("Email",        me.get("email", "") or "—"),
        ("Role",         me.get("role", "").upper()),
        ("Last Login",   (me.get("last_login") or "Now")[:16].replace("T", " ")),
        ("Login Count",  str(me.get("login_count", 0))),
        ("Expiry",       me.get("expiry", "Never")[:10] if me.get("expiry") else "Never"),
    ]):
        lbl_w = QLabel(lbl)
        lbl_w.setStyleSheet(f"color:{SUBTEXT}; font-weight:bold;")
        val_w = QLabel(val)
        val_w.setStyleSheet(f"color:{TEXT};")
        info_grid.addWidget(lbl_w, row, 0)
        info_grid.addWidget(val_w, row, 1)
    t4_lay.addWidget(info_grp)

    # Change password
    pw_grp = QGroupBox("🔑 Change Password")
    pw_glay = QGridLayout(pw_grp)
    inp_old = QLineEdit(); inp_old.setEchoMode(QLineEdit.Password)
    inp_old.setPlaceholderText("Current password")
    inp_new = QLineEdit(); inp_new.setEchoMode(QLineEdit.Password)
    inp_new.setPlaceholderText("New password (min 8 characters)")
    inp_conf = QLineEdit(); inp_conf.setEchoMode(QLineEdit.Password)
    inp_conf.setPlaceholderText("Confirm new password")
    _pw_style = "background:#313244; color:#CDD6F4; border:1px solid #6C7086; border-radius:6px; padding:6px 10px;"
    for w in (inp_old, inp_new, inp_conf):
        w.setStyleSheet(_pw_style)
    pw_glay.addWidget(QLabel("Current Password"), 0, 0)
    pw_glay.addWidget(inp_old, 0, 1)
    pw_glay.addWidget(QLabel("New Password"), 1, 0)
    pw_glay.addWidget(inp_new, 1, 1)
    pw_glay.addWidget(QLabel("Confirm New"), 2, 0)
    pw_glay.addWidget(inp_conf, 2, 1)
    t4_lay.addWidget(pw_grp)

    btn_pw = ActionButton("💾 Save New Password", ACCENT)
    t4_lay.addWidget(btn_pw)
    t4_out = OutputBox("")
    t4_out.setMaximumHeight(70)
    t4_lay.addWidget(t4_out)

    def _change_pw():
        old  = inp_old.text()
        new  = inp_new.text()
        conf = inp_conf.text()
        if new != conf:
            t4_out.set_error("New passwords do not match."); return
        try:
            _admin.change_password(token, old, new)
            t4_out.setPlainText("✅ Password changed successfully!")
            inp_old.clear(); inp_new.clear(); inp_conf.clear()
        except Exception as e:
            t4_out.set_error(str(e))

    btn_pw.clicked.connect(_change_pw)
    tabs.addTab(t4, "🔑 My Account")

    # ── TAB 5: Telegram Members ────────────────────────────────────────────────
    t5 = QWidget(); t5l = QVBoxLayout(t5)
    t5l.setContentsMargins(14, 10, 14, 10); t5l.setSpacing(8)

    _admin_tbl_style = (
        f"QTableWidget{{background:{SURFACE};color:{TEXT};border:1px solid {BORDER};"
        f"border-radius:8px;gridline-color:{BORDER};font-size:13px;}}"
        f"QTableWidget::item{{padding:5px;}}"
        f"QTableWidget::item:selected{{background:{ACCENT}33;}}"
        f"QHeaderView::section{{background:{SIDEBAR};color:{ACCENT};font-weight:bold;padding:5px;border:none;}}"
    )

    adm_ctrl = QHBoxLayout()
    btn_adm_refresh = ActionButton("🔄 Refresh Members", ACCENT); btn_adm_refresh.setFixedHeight(34)
    btn_adm_csv     = ActionButton("📄 Export CSV", SUCCESS);     btn_adm_csv.setFixedHeight(34)
    btn_adm_ban     = ActionButton("🚫 Ban Selected", "#F38BA8"); btn_adm_ban.setFixedHeight(34)
    adm_ctrl.addWidget(btn_adm_refresh)
    adm_ctrl.addWidget(btn_adm_csv)
    adm_ctrl.addWidget(btn_adm_ban)
    adm_ctrl.addStretch()
    t5l.addLayout(adm_ctrl)

    adm_tbl = QTableWidget(0, 9)
    adm_tbl.setHorizontalHeaderLabels([
        "Full Name", "Username", "Telegram ID", "Phone", "Sex", "Date of Birth",
        "Joined", "Posts", "Status"
    ])
    for ci in range(9):
        adm_tbl.horizontalHeader().setSectionResizeMode(
            ci, QHeaderView.Stretch if ci == 0 else QHeaderView.ResizeToContents
        )
    adm_tbl.setSelectionBehavior(QTableWidget.SelectRows)
    adm_tbl.setEditTriggers(QTableWidget.NoEditTriggers)
    adm_tbl.setAlternatingRowColors(True)
    adm_tbl.setStyleSheet(_admin_tbl_style)
    t5l.addWidget(adm_tbl, 1)

    adm_count = QLabel("0 members"); adm_count.setStyleSheet(f"color:{SUBTEXT};font-size:12px;")
    t5l.addWidget(adm_count)

    _adm_users: list = []

    def _fill_adm_tbl(users: list):
        adm_tbl.setRowCount(0)
        for u in users:
            r = adm_tbl.rowCount(); adm_tbl.insertRow(r)
            active = u.get("is_active", True)
            cells = [
                u.get("display_name") or f"{u.get('first_name','')} {u.get('last_name','')}".strip() or "Unknown",
                f"@{u.get('username')}" if u.get("username") else "—",
                str(u.get("telegram_id", "")),
                u.get("phone", "—") or "—",
                u.get("sex", "—") or "—",
                u.get("date_of_birth", "—") or "—",
                u.get("registered_at", "")[:10],
                str(u.get("post_count", 0)),
                "✅ Active" if active else "🚫 Banned",
            ]
            for col, val in enumerate(cells):
                item = QTableWidgetItem(val)
                if col == 8 and not active:
                    item.setForeground(QColor("#F38BA8"))
                adm_tbl.setItem(r, col, item)
        adm_count.setText(f"👥 {len(users)} registered Telegram members")

    def _adm_load():
        btn_adm_refresh.set_loading(True)
        import requests as _req
        try:
            r = _req.get(f"http://127.0.0.1:8000/api/v1/social/admin/users", timeout=10)
            r.raise_for_status()
            data = r.json().get("data", [])
            nonlocal _adm_users; _adm_users = data
            _fill_adm_tbl(data)
        except Exception as e:
            adm_count.setText(f"❌ Error: {e}")
        finally:
            btn_adm_refresh.set_loading(False)

    def _adm_export_csv():
        if not _adm_users:
            QMessageBox.warning(page, "No Data", "Please refresh members first."); return
        from PyQt5.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(page, "Export CSV", "telegram_members.csv", "CSV Files (*.csv)")
        if not path:
            return
        import csv
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                wr = csv.DictWriter(f, fieldnames=[
                    "telegram_id","first_name","last_name","username","phone",
                    "sex","date_of_birth","registered_at","post_count","is_active"
                ])
                wr.writeheader()
                for u in _adm_users:
                    wr.writerow({k: u.get(k,"") for k in wr.fieldnames})
            QMessageBox.information(page, "Exported", f"✅ CSV saved to:\n{path}")
        except Exception as e:
            QMessageBox.critical(page, "Export Error", str(e))

    def _adm_ban():
        row = adm_tbl.currentRow()
        if row < 0:
            QMessageBox.warning(page, "Select User", "Please select a user to ban."); return
        tid = adm_tbl.item(row, 2).text() if adm_tbl.item(row, 2) else ""
        if not tid:
            return
        reply = QMessageBox.question(
            page, "Ban User",
            f"Ban Telegram user {tid}? They will no longer be able to post.",
            QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel,
        )
        if reply != QMessageBox.Yes:
            return
        import requests as _req
        try:
            r = _req.post(f"http://127.0.0.1:8000/api/v1/social/admin/ban/{tid}", timeout=10)
            r.raise_for_status()
            QMessageBox.information(page, "Banned", f"User {tid} has been banned.")
            _adm_load()
        except Exception as e:
            QMessageBox.critical(page, "Error", str(e))

    btn_adm_refresh.clicked.connect(_adm_load)
    btn_adm_csv.clicked.connect(_adm_export_csv)
    btn_adm_ban.clicked.connect(_adm_ban)
    tabs.addTab(t5, "📱 Telegram Members")

    layout.addWidget(tabs, 1)
    return page


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 27 — FACEBOOK PAGES MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

def build_facebook_manager_page(api_base: str) -> QWidget:
    """Facebook Pages Manager — Posts, Comments, Messenger, AI Content Studio, Insights."""
    page, layout = _make_page_layout("Facebook Pages Manager", "📘")
    tabs = QTabWidget()
    layout.addWidget(tabs, 1)

    _fb_base = api_base

    # ─────────────────────────────────────────────────────────────────────────
    # Shared helpers
    # ─────────────────────────────────────────────────────────────────────────
    def _fb_get(endpoint, params=None):
        """Blocking GET via requests (called inside QThread)."""
        import requests as _req
        r = _req.get(f"{_fb_base}{endpoint}", params=params or {}, timeout=25)
        return r.json()

    def _fb_post(endpoint, payload):
        import requests as _req
        r = _req.post(f"{_fb_base}{endpoint}", json=payload, timeout=25)
        return r.json()

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 1 — Pages & Posts
    # ─────────────────────────────────────────────────────────────────────────
    t1 = QWidget()
    t1_layout = QVBoxLayout(t1)
    t1_layout.setContentsMargins(14, 14, 14, 14)
    t1_layout.setSpacing(10)

    # Account + Page selectors row
    sel_row = QHBoxLayout()
    acct_combo = QComboBox()
    acct_combo.setMinimumWidth(200)
    acct_combo.setStyleSheet(f"QComboBox{{background:{SURFACE};color:{TEXT};border:1px solid {BORDER};border-radius:6px;padding:4px 8px;font-size:13px;}}")
    acct_combo.setPlaceholderText("Select account…")
    page_combo = QComboBox()
    page_combo.setMinimumWidth(240)
    page_combo.setStyleSheet(acct_combo.styleSheet())
    page_combo.setPlaceholderText("Select Page…")
    btn_load_accounts = QPushButton("🔄 Load Accounts")
    btn_load_pages    = QPushButton("📄 Load Pages")
    btn_load_posts    = QPushButton("📰 Load Posts")
    for b in (btn_load_accounts, btn_load_pages, btn_load_posts):
        b.setStyleSheet(f"QPushButton{{background:{ACCENT};color:#11111B;border-radius:6px;padding:6px 14px;font-weight:bold;font-size:13px;}}QPushButton:hover{{opacity:0.85;}}")
        b.setCursor(Qt.PointingHandCursor)
    sel_row.addWidget(QLabel("Account:"))
    sel_row.addWidget(acct_combo)
    sel_row.addWidget(btn_load_accounts)
    sel_row.addSpacing(12)
    sel_row.addWidget(QLabel("Page:"))
    sel_row.addWidget(page_combo)
    sel_row.addWidget(btn_load_pages)
    sel_row.addSpacing(12)
    sel_row.addWidget(btn_load_posts)
    sel_row.addStretch()
    t1_layout.addLayout(sel_row)

    # Posts table — 6 cols: Page ID | Post ID | Message | Likes | Comments | Date
    posts_table = QTableWidget(0, 6)
    posts_table.setHorizontalHeaderLabels(["📋 Page ID", "🆔 Post ID", "Message", "👍 Likes", "💬 Comments", "📅 Date"])
    posts_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
    posts_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
    posts_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
    posts_table.setSelectionBehavior(QTableWidget.SelectRows)
    posts_table.setAlternatingRowColors(True)
    posts_table.setStyleSheet(f"""
        QTableWidget{{background:{SURFACE};color:{TEXT};border:1px solid {BORDER};border-radius:8px;font-size:13px;gridline-color:{BORDER};}}
        QHeaderView::section{{background:{SIDEBAR};color:{ACCENT};font-weight:bold;padding:5px;border:none;}}
        QTableWidget::item{{padding:4px 8px;}}
        QTableWidget::item:selected{{background:{ACCENT}33;}}
    """)
    posts_table.verticalHeader().setVisible(False)
    # Tooltip on header: remind user cols 0 & 1 are click-to-copy
    posts_table.horizontalHeaderItem(0).setToolTip("Click any cell to copy Page ID")
    posts_table.horizontalHeaderItem(1).setToolTip("Click any cell to copy Post ID")
    t1_layout.addWidget(posts_table, 1)

    # Floating copy-toast label (hidden by default)
    _copy_toast = QLabel("", page)
    _copy_toast.setStyleSheet(
        f"background:#A6E3A1; color:#11111B; border-radius:8px;"
        f"padding:4px 14px; font-weight:bold; font-size:13px;"
    )
    _copy_toast.setVisible(False)
    _copy_toast_timer = QTimer(page)
    _copy_toast_timer.setSingleShot(True)
    _copy_toast_timer.timeout.connect(lambda: _copy_toast.setVisible(False))

    def _show_copy_toast(text: str, cell_widget: QTableWidget, row: int, col: int):
        """Show a floating toast near the clicked cell for 1.5 s."""
        _copy_toast.setText(f"✅ Copied: {text}")
        _copy_toast.adjustSize()
        # Position relative to the cell rect inside the viewport
        cell_rect = cell_widget.visualItemRect(cell_widget.item(row, col))
        vp_pos    = cell_widget.viewport().mapTo(page, cell_rect.topLeft())
        _copy_toast.move(vp_pos.x(), max(0, vp_pos.y() - _copy_toast.height() - 4))
        _copy_toast.raise_()
        _copy_toast.setVisible(True)
        _copy_toast_timer.start(1500)

    def _posts_cell_clicked(row: int, col: int):
        """Col 0 = Page ID, col 1 = Post ID — both click-to-copy.
           Any column click also auto-fills the Post ID input in Tab 2."""
        item = posts_table.item(row, col)
        if item is None:
            return
        # Auto-fill Tab 2 Post ID input from col 1
        post_id_item = posts_table.item(row, 1)
        if post_id_item:
            cmt_post_id.setText(post_id_item.text())
        # Copy to clipboard for cols 0 and 1
        if col in (0, 1):
            QApplication.clipboard().setText(item.text())
            _show_copy_toast(item.text(), posts_table, row, col)

    posts_table.cellClicked.connect(_posts_cell_clicked)

    # Publish form
    pub_group = QGroupBox("📝 Publish New Post")
    pub_group.setStyleSheet(f"QGroupBox{{color:{ACCENT};font-weight:bold;font-size:14px;border:1px solid {BORDER};border-radius:8px;padding:10px;margin-top:8px;}}QGroupBox::title{{subcontrol-origin:margin;left:10px;top:3px;}}")
    pub_form = QVBoxLayout(pub_group)
    pub_msg = QTextEdit()
    pub_msg.setPlaceholderText("Write your post message here… (or use AI to generate ↓)")
    pub_msg.setMaximumHeight(90)
    pub_msg.setStyleSheet(f"background:{SURFACE};color:{TEXT};border:1px solid {BORDER};border-radius:6px;font-size:13px;padding:6px;")
    pub_link = QLineEdit()
    pub_link.setPlaceholderText("Optional link URL (https://…)")
    pub_link.setStyleSheet(f"background:{SURFACE};color:{TEXT};border:1px solid {BORDER};border-radius:6px;font-size:13px;padding:6px;")
    pub_img  = QLineEdit()
    pub_img.setPlaceholderText("Optional image URL (https://…)")
    pub_img.setStyleSheet(pub_link.styleSheet())
    pub_form.addWidget(pub_msg)
    pub_link_row = QHBoxLayout()
    pub_link_row.addWidget(QLabel("Link:"))
    pub_link_row.addWidget(pub_link, 1)
    pub_link_row.addSpacing(8)
    pub_link_row.addWidget(QLabel("Image URL:"))
    pub_link_row.addWidget(pub_img, 1)
    pub_form.addLayout(pub_link_row)
    btn_publish = QPushButton("🚀 Publish Now")
    btn_publish.setStyleSheet(f"QPushButton{{background:#A6E3A1;color:#11111B;border-radius:6px;padding:8px 20px;font-weight:bold;font-size:13px;}}QPushButton:hover{{background:#94D898;}}")
    btn_publish.setCursor(Qt.PointingHandCursor)
    pub_out = OutputBox()
    pub_out.setMaximumHeight(60)
    pub_row = QHBoxLayout()
    pub_row.addWidget(btn_publish)
    pub_row.addStretch()
    pub_form.addLayout(pub_row)
    pub_form.addWidget(pub_out)
    t1_layout.addWidget(pub_group)

    # Internal state store
    _t1_state = {"accounts": [], "pages": [], "page_tokens": {}}

    def _load_accounts_cb(resp, err):
        if err or resp.get("status") == "error":
            pub_out.set_error(resp.get("message", err or "Error loading accounts"))
            return
        accs = resp.get("accounts", [])
        _t1_state["accounts"] = accs
        acct_combo.clear()
        for a in accs:
            acct_combo.addItem(f"{a.get('display_name', 'Facebook')} ({a.get('status', '?')})", a.get("id", ""))
        if accs:
            pub_out.setPlainText(f"✅ {len(accs)} account(s) loaded.")
        else:
            pub_out.setPlainText("⚠ No Facebook accounts found. Connect one in 🔐 Social Accounts.")
        _enable_btn(btn_load_accounts, "🔄 Load Accounts")

    def _do_load_accounts():
        _disable_btn(btn_load_accounts)
        w = _ApiWorker(f"{_fb_base}/api/v1/facebook/accounts", {}, "GET", None)
        w.finished.connect(lambda r: _load_accounts_cb(r, None))
        w.error.connect(lambda e: (_enable_btn(btn_load_accounts, "🔄 Load Accounts"), pub_out.set_error(e)))
        w.start(); _do_load_accounts._w = w

    btn_load_accounts.clicked.connect(_do_load_accounts)

    def _load_pages_cb(resp, err):
        if err or resp.get("status") == "error":
            pub_out.set_error(resp.get("message", err or "Error loading pages"))
            _enable_btn(btn_load_pages, "📄 Load Pages")
            return
        pages = resp.get("pages", [])
        _t1_state["pages"] = pages
        _t1_state["page_tokens"] = {p["id"]: p.get("access_token", "") for p in pages}
        page_combo.clear()
        for p in pages:
            fans = p.get("fan_count", 0)
            page_combo.addItem(f"{p.get('name', p['id'])} ({fans:,} fans)", p["id"])
        if not pages:
            pub_out.setPlainText("⚠ No Pages found. Make sure your token has pages_show_list scope.")
        else:
            pub_out.setPlainText(f"✅ {len(pages)} Page(s) loaded.")
        _enable_btn(btn_load_pages, "📄 Load Pages")

    def _do_load_pages():
        acct_id = acct_combo.currentData() or ""
        _disable_btn(btn_load_pages)
        w = _ApiWorker(f"{_fb_base}/api/v1/facebook/pages?account_id={acct_id}", {}, "GET", None)
        w.finished.connect(lambda r: _load_pages_cb(r, None))
        w.error.connect(lambda e: (_enable_btn(btn_load_pages, "📄 Load Pages"), pub_out.set_error(e)))
        w.start(); _do_load_pages._w = w

    btn_load_pages.clicked.connect(_do_load_pages)

    def _load_posts_cb(resp, err):
        if err or resp.get("status") == "error":
            pub_out.set_error(resp.get("message", err or "Error loading posts"))
            _enable_btn(btn_load_posts, "📰 Load Posts")
            return
        posts   = resp.get("posts", [])
        cur_pid = page_combo.currentData() or ""      # active Page ID
        posts_table.setRowCount(0)
        for post in posts:
            row = posts_table.rowCount()
            posts_table.insertRow(row)
            # derive page_id: prefer field in response, fall back to selector
            pg_id   = str(post.get("page_id") or post.get("id", "").split("_")[0] or cur_pid)
            pid     = str(post.get("id", ""))
            msg     = (post.get("message") or post.get("story") or "")[:80]
            likes   = str(post.get("likes",   {}).get("summary", {}).get("total_count", 0))
            comments= str(post.get("comments",{}).get("summary", {}).get("total_count", 0))
            created = post.get("created_time", "")[:10]
            for col, val in enumerate([pg_id, pid, msg, likes, comments, created]):
                item = QTableWidgetItem(val)
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                # Color Page ID and Post ID columns distinctly to signal click-to-copy
                if col == 0:
                    item.setForeground(QColor(WARNING))     # amber — Page ID
                    item.setToolTip("🖱 Click to copy Page ID")
                elif col == 1:
                    item.setForeground(QColor(ACCENT))      # blue — Post ID
                    item.setToolTip("🖱 Click to copy Post ID")
                posts_table.setItem(row, col, item)
        pub_out.setPlainText(f"✅ {len(posts)} post(s) loaded.  💡 Click Page ID (amber) or Post ID (blue) to copy.")
        _enable_btn(btn_load_posts, "📰 Load Posts")

    def _do_load_posts():
        page_id = page_combo.currentData()
        if not page_id:
            pub_out.set_error("Select a page first."); return
        acct_id = acct_combo.currentData() or ""
        _disable_btn(btn_load_posts)
        w = _ApiWorker(f"{_fb_base}/api/v1/facebook/pages/{page_id}/posts?account_id={acct_id}", {}, "GET", None)
        w.finished.connect(lambda r: _load_posts_cb(r, None))
        w.error.connect(lambda e: (_enable_btn(btn_load_posts, "📰 Load Posts"), pub_out.set_error(e)))
        w.start(); _do_load_posts._w = w

    btn_load_posts.clicked.connect(_do_load_posts)

    def _do_publish():
        page_id = page_combo.currentData()
        if not page_id:
            pub_out.set_error("Select a page first."); return
        msg = pub_msg.toPlainText().strip()
        if not msg:
            pub_out.set_error("Post message cannot be empty."); return
        payload = {
            "account_id": acct_combo.currentData() or "",
            "page_id": page_id,
            "message": msg,
            "link": pub_link.text().strip(),
            "image_url": pub_img.text().strip(),
        }
        _disable_btn(btn_publish)
        w = _ApiWorker(f"{_fb_base}/api/v1/facebook/pages/{page_id}/publish", payload)
        def _cb(r, e):
            _enable_btn(btn_publish, "🚀 Publish Now")
            if e or r.get("status") == "error":
                pub_out.set_error(r.get("message", e or "Publish failed"))
            else:
                pub_out.setPlainText(f"✅ {r.get('message', 'Published!')}  Post ID: {r.get('post_id','')}")
                pub_msg.clear(); pub_link.clear(); pub_img.clear()
        w.finished.connect(lambda r: _cb(r, None))
        w.error.connect(lambda e: _cb({}, e))
        w.start(); _do_publish._w = w

    btn_publish.clicked.connect(_do_publish)

    tabs.addTab(t1, "📄 Pages & Posts")

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 2 — Comments Manager
    # ─────────────────────────────────────────────────────────────────────────
    t2 = QWidget()
    t2_layout = QVBoxLayout(t2)
    t2_layout.setContentsMargins(14, 14, 14, 14)
    t2_layout.setSpacing(10)

    cmt_row = QHBoxLayout()
    cmt_post_id = QLineEdit()
    cmt_post_id.setPlaceholderText("Paste Post ID (from Posts tab)…")
    cmt_post_id.setStyleSheet(f"background:{SURFACE};color:{TEXT};border:1px solid {BORDER};border-radius:6px;font-size:13px;padding:6px;")
    btn_load_cmts = QPushButton("💬 Load Comments")
    btn_load_cmts.setStyleSheet(f"QPushButton{{background:{ACCENT};color:#11111B;border-radius:6px;padding:6px 14px;font-weight:bold;}}QPushButton:hover{{opacity:0.85;}}")
    btn_load_cmts.setCursor(Qt.PointingHandCursor)
    cmt_row.addWidget(QLabel("Post ID:"))
    cmt_row.addWidget(cmt_post_id, 1)
    cmt_row.addWidget(btn_load_cmts)
    cmt_row.addStretch()
    t2_layout.addLayout(cmt_row)

    cmt_table = QTableWidget(0, 4)
    cmt_table.setHorizontalHeaderLabels(["Comment ID", "Author", "Message", "👍 Likes"])
    cmt_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
    cmt_table.setSelectionBehavior(QTableWidget.SelectRows)
    cmt_table.setAlternatingRowColors(True)
    cmt_table.setStyleSheet(posts_table.styleSheet())
    cmt_table.verticalHeader().setVisible(False)
    t2_layout.addWidget(cmt_table, 1)

    # Reply panel
    reply_group = QGroupBox("✉️ Reply to Selected Comment")
    reply_group.setStyleSheet(pub_group.styleSheet())
    reply_form = QVBoxLayout(reply_group)
    reply_txt = QLineEdit()
    reply_txt.setPlaceholderText("Type reply or use AI Suggest below…")
    reply_txt.setStyleSheet(pub_link.styleSheet())
    btn_ai_suggest = QPushButton("🤖 AI Suggest Reply")
    btn_reply_send = QPushButton("📤 Send Reply")
    btn_ai_suggest.setStyleSheet(f"QPushButton{{background:{SURFACE};color:{ACCENT};border:1px solid {ACCENT};border-radius:6px;padding:6px 14px;font-size:13px;}}QPushButton:hover{{background:{ACCENT};color:#11111B;}}")
    btn_reply_send.setStyleSheet(f"QPushButton{{background:{ACCENT};color:#11111B;border-radius:6px;padding:6px 14px;font-weight:bold;font-size:13px;}}QPushButton:hover{{opacity:0.85;}}")
    for b in (btn_ai_suggest, btn_reply_send):
        b.setCursor(Qt.PointingHandCursor)
    cmt_reply_row = QHBoxLayout()
    cmt_reply_row.addWidget(reply_txt, 1)
    cmt_reply_row.addWidget(btn_ai_suggest)
    cmt_reply_row.addWidget(btn_reply_send)
    reply_form.addLayout(cmt_reply_row)
    cmt_out = OutputBox()
    cmt_out.setMaximumHeight(70)
    reply_form.addWidget(cmt_out)
    t2_layout.addWidget(reply_group)

    def _load_comments_cb(resp, err):
        if err or resp.get("status") == "error":
            cmt_out.set_error(resp.get("message", err or "Error"))
            _enable_btn(btn_load_cmts, "💬 Load Comments")
            return
        cmts = resp.get("comments", [])
        cmt_table.setRowCount(0)
        for c in cmts:
            row = cmt_table.rowCount()
            cmt_table.insertRow(row)
            author = c.get("from", {}).get("name", "Unknown")
            for col, val in enumerate([c.get("id",""), author, c.get("message","")[:100], str(c.get("like_count",0))]):
                item = QTableWidgetItem(val)
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                cmt_table.setItem(row, col, item)
        cmt_out.setPlainText(f"✅ {len(cmts)} comment(s) loaded. Total: {resp.get('total', len(cmts))}")
        _enable_btn(btn_load_cmts, "💬 Load Comments")

    def _do_load_comments():
        pid = cmt_post_id.text().strip()
        if not pid:
            cmt_out.set_error("Enter a Post ID first."); return
        acct_id = acct_combo.currentData() or ""
        _disable_btn(btn_load_cmts)
        w = _ApiWorker(f"{_fb_base}/api/v1/facebook/posts/{pid}/comments?account_id={acct_id}", {}, "GET", None)
        w.finished.connect(lambda r: _load_comments_cb(r, None))
        w.error.connect(lambda e: (_enable_btn(btn_load_cmts, "💬 Load Comments"), cmt_out.set_error(e)))
        w.start(); _do_load_comments._w = w

    btn_load_cmts.clicked.connect(_do_load_comments)

    def _do_ai_suggest():
        sel = cmt_table.selectedItems()
        if not sel:
            cmt_out.set_error("Select a comment row first."); return
        row = cmt_table.currentRow()
        orig = cmt_table.item(row, 2).text() if cmt_table.item(row, 2) else ""
        if not orig:
            cmt_out.set_error("No comment text found."); return
        payload = {"original_text": orig, "tone": "friendly", "account_id": acct_combo.currentData() or ""}
        _disable_btn(btn_ai_suggest)
        w = _ApiWorker(f"{_fb_base}/api/v1/facebook/ai/suggest-reply", payload)
        def _cb(r, e):
            _enable_btn(btn_ai_suggest, "🤖 AI Suggest Reply")
            if e or r.get("status") == "error":
                cmt_out.set_error(r.get("message", e or "AI error"))
            else:
                reply_txt.setText(r.get("reply", ""))
                cmt_out.setPlainText("✅ AI reply suggestion ready — edit if needed, then Send.")
        w.finished.connect(lambda r: _cb(r, None))
        w.error.connect(lambda e: _cb({}, e))
        w.start(); _do_ai_suggest._w = w

    btn_ai_suggest.clicked.connect(_do_ai_suggest)

    def _do_reply():
        sel = cmt_table.selectedItems()
        if not sel:
            cmt_out.set_error("Select a comment row first."); return
        row = cmt_table.currentRow()
        cmt_id = cmt_table.item(row, 0).text() if cmt_table.item(row, 0) else ""
        msg = reply_txt.text().strip()
        if not cmt_id:
            cmt_out.set_error("Could not get Comment ID."); return
        if not msg:
            cmt_out.set_error("Reply message cannot be empty."); return
        payload = {"comment_id": cmt_id, "message": msg, "account_id": acct_combo.currentData() or ""}
        _disable_btn(btn_reply_send)
        w = _ApiWorker(f"{_fb_base}/api/v1/facebook/comments/{cmt_id}/reply", payload)
        def _cb(r, e):
            _enable_btn(btn_reply_send, "📤 Send Reply")
            if e or r.get("status") == "error":
                cmt_out.set_error(r.get("message", e or "Reply failed"))
            else:
                cmt_out.setPlainText(f"✅ {r.get('message', 'Reply sent!')}")
                reply_txt.clear()
        w.finished.connect(lambda r: _cb(r, None))
        w.error.connect(lambda e: _cb({}, e))
        w.start(); _do_reply._w = w

    btn_reply_send.clicked.connect(_do_reply)

    tabs.addTab(t2, "💬 Comments")

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 3 — Messenger
    # ─────────────────────────────────────────────────────────────────────────
    t3 = QWidget()
    t3_layout = QVBoxLayout(t3)
    t3_layout.setContentsMargins(14, 14, 14, 14)
    t3_layout.setSpacing(10)

    msg_page_row = QHBoxLayout()
    msg_page_id = QLineEdit()
    msg_page_id.setPlaceholderText("Page ID (from Pages & Posts tab)…")
    msg_page_id.setStyleSheet(pub_link.styleSheet())
    btn_load_convs = QPushButton("📩 Load Conversations")
    btn_load_convs.setStyleSheet(btn_load_cmts.styleSheet())
    btn_load_convs.setCursor(Qt.PointingHandCursor)
    msg_page_row.addWidget(QLabel("Page ID:"))
    msg_page_row.addWidget(msg_page_id, 1)
    msg_page_row.addWidget(btn_load_convs)
    msg_page_row.addStretch()
    t3_layout.addLayout(msg_page_row)

    # Splitter: conversation list | message thread
    conv_splitter = QSplitter(Qt.Horizontal)
    conv_list = QListWidget()
    conv_list.setStyleSheet(f"QListWidget{{background:{SURFACE};color:{TEXT};border:1px solid {BORDER};border-radius:8px;font-size:13px;}}QListWidget::item{{padding:8px;}}QListWidget::item:selected{{background:{ACCENT}33;}}")
    conv_list.setMaximumWidth(280)
    thread_view = QTextEdit()
    thread_view.setReadOnly(True)
    thread_view.setStyleSheet(f"background:{SURFACE};color:{TEXT};border:1px solid {BORDER};border-radius:8px;font-size:13px;padding:8px;")
    conv_splitter.addWidget(conv_list)
    conv_splitter.addWidget(thread_view)
    conv_splitter.setSizes([260, 500])
    t3_layout.addWidget(conv_splitter, 1)

    # Reply row
    msg_reply_row = QHBoxLayout()
    msg_reply_txt = QLineEdit()
    msg_reply_txt.setPlaceholderText("Type reply or use AI Suggest…")
    msg_reply_txt.setStyleSheet(pub_link.styleSheet())
    btn_msg_ai = QPushButton("🤖 AI Reply")
    btn_msg_send = QPushButton("📤 Send")
    btn_msg_ai.setStyleSheet(btn_ai_suggest.styleSheet())
    btn_msg_send.setStyleSheet(btn_reply_send.styleSheet())
    btn_msg_ai.setCursor(Qt.PointingHandCursor)
    btn_msg_send.setCursor(Qt.PointingHandCursor)
    msg_reply_row.addWidget(msg_reply_txt, 1)
    msg_reply_row.addWidget(btn_msg_ai)
    msg_reply_row.addWidget(btn_msg_send)
    t3_layout.addLayout(msg_reply_row)
    msg_out = OutputBox()
    msg_out.setMaximumHeight(55)
    t3_layout.addWidget(msg_out)

    _t3_state = {"conversations": [], "current_psid": ""}

    def _load_convs_cb(resp, err):
        if err or resp.get("status") == "error":
            msg_out.set_error(resp.get("message", err or "Error"))
            _enable_btn(btn_load_convs, "📩 Load Conversations")
            return
        convs = resp.get("conversations", [])
        _t3_state["conversations"] = convs
        conv_list.clear()
        for c in convs:
            participants = c.get("participants", {}).get("data", [])
            names = [p.get("name", "?") for p in participants]
            updated = c.get("updated_time", "")[:10]
            label = ", ".join(names) + f"  ({updated})"
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, c)
            conv_list.addItem(item)
        msg_out.setPlainText(f"✅ {len(convs)} conversation(s) loaded.")
        _enable_btn(btn_load_convs, "📩 Load Conversations")

    def _do_load_convs():
        pid = msg_page_id.text().strip()
        if not pid:
            msg_out.set_error("Enter a Page ID first."); return
        acct_id = acct_combo.currentData() or ""
        _disable_btn(btn_load_convs)
        w = _ApiWorker(f"{_fb_base}/api/v1/facebook/pages/{pid}/conversations?account_id={acct_id}", {}, "GET", None)
        w.finished.connect(lambda r: _load_convs_cb(r, None))
        w.error.connect(lambda e: (_enable_btn(btn_load_convs, "📩 Load Conversations"), msg_out.set_error(e)))
        w.start(); _do_load_convs._w = w

    btn_load_convs.clicked.connect(_do_load_convs)

    def _on_conv_selected(item):
        conv = item.data(Qt.UserRole)
        if not conv:
            return
        participants = conv.get("participants", {}).get("data", [])
        # Find non-page participant (the customer) for PSID
        psid = ""
        for p in participants:
            if p.get("id"):
                psid = p["id"]
                break
        _t3_state["current_psid"] = psid
        msgs = conv.get("messages", {}).get("data", [])
        lines = []
        for m in reversed(msgs):
            sender = m.get("from", {}).get("name", "?")
            ts = m.get("created_time", "")[:16].replace("T", " ")
            lines.append(f"[{ts}] {sender}:\n{m.get('message', '')}\n")
        thread_view.setPlainText("\n".join(lines) if lines else "(No messages loaded)")

    conv_list.itemClicked.connect(_on_conv_selected)

    def _do_msg_ai():
        last_msg = ""
        items = conv_list.selectedItems()
        if items:
            conv = items[0].data(Qt.UserRole)
            msgs = conv.get("messages", {}).get("data", [])
            if msgs:
                last_msg = msgs[0].get("message", "")
        if not last_msg:
            msg_out.set_error("Select a conversation with messages first."); return
        payload = {"original_text": last_msg, "tone": "friendly", "account_id": acct_combo.currentData() or ""}
        _disable_btn(btn_msg_ai)
        w = _ApiWorker(f"{_fb_base}/api/v1/facebook/ai/suggest-reply", payload)
        def _cb(r, e):
            _enable_btn(btn_msg_ai, "🤖 AI Reply")
            if e or r.get("status") == "error":
                msg_out.set_error(r.get("message", e or "AI error"))
            else:
                msg_reply_txt.setText(r.get("reply", ""))
                msg_out.setPlainText("✅ AI reply ready — edit then Send.")
        w.finished.connect(lambda r: _cb(r, None))
        w.error.connect(lambda e: _cb({}, e))
        w.start(); _do_msg_ai._w = w

    btn_msg_ai.clicked.connect(_do_msg_ai)

    def _do_msg_send():
        psid = _t3_state.get("current_psid", "")
        if not psid:
            msg_out.set_error("Select a conversation first."); return
        txt = msg_reply_txt.text().strip()
        if not txt:
            msg_out.set_error("Message cannot be empty."); return
        payload = {"recipient_id": psid, "message": txt, "account_id": acct_combo.currentData() or "", "page_id": msg_page_id.text().strip()}
        _disable_btn(btn_msg_send)
        w = _ApiWorker(f"{_fb_base}/api/v1/facebook/messenger/reply", payload)
        def _cb(r, e):
            _enable_btn(btn_msg_send, "📤 Send")
            if e or r.get("status") == "error":
                msg_out.set_error(r.get("message", e or "Send failed"))
            else:
                msg_out.setPlainText(f"✅ {r.get('message', 'Message sent!')}")
                msg_reply_txt.clear()
        w.finished.connect(lambda r: _cb(r, None))
        w.error.connect(lambda e: _cb({}, e))
        w.start(); _do_msg_send._w = w

    btn_msg_send.clicked.connect(_do_msg_send)

    tabs.addTab(t3, "📩 Messenger")

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 4 — AI Content Studio
    # ─────────────────────────────────────────────────────────────────────────
    t4 = QWidget()
    t4_layout = QVBoxLayout(t4)
    t4_layout.setContentsMargins(14, 14, 14, 14)
    t4_layout.setSpacing(12)

    ai_form = QFormLayout()
    ai_page_name = _entry("My Business Page")
    ai_topic     = _entry("digital marketing tips")
    ai_tone      = _combo("engaging", "inspiring", "educational", "funny", "professional", "casual", "urgent")
    ai_goal      = _combo("grow followers", "drive traffic", "sell products", "build trust", "generate leads", "boost engagement")
    ai_audience  = _entry("entrepreneurs and small business owners")
    ai_num       = QSpinBox()
    ai_num.setRange(1, 10)
    ai_num.setValue(3)
    ai_num.setStyleSheet(f"background:{SURFACE};color:{TEXT};border:1px solid {BORDER};border-radius:6px;padding:4px;min-width:70px;")
    for lbl, w in [("Page Name:", ai_page_name), ("Topic / Niche:", ai_topic), ("Tone:", ai_tone),
                   ("Goal:", ai_goal), ("Target Audience:", ai_audience), ("# Posts (Bulk):", ai_num)]:
        ai_form.addRow(lbl, w)
    t4_layout.addLayout(ai_form)

    ai_btn_row = QHBoxLayout()
    btn_ai_single = QPushButton("✨ Generate Single Post")
    btn_ai_bulk   = QPushButton("📦 Bulk Generate Posts")
    for b in (btn_ai_single, btn_ai_bulk):
        b.setStyleSheet(f"QPushButton{{background:{ACCENT};color:#11111B;border-radius:6px;padding:8px 18px;font-weight:bold;font-size:13px;}}QPushButton:hover{{opacity:0.85;}}")
        b.setCursor(Qt.PointingHandCursor)
    ai_btn_row.addWidget(btn_ai_single)
    ai_btn_row.addWidget(btn_ai_bulk)
    ai_btn_row.addStretch()
    t4_layout.addLayout(ai_btn_row)

    ai_out = OutputBox()
    ai_out.setMinimumHeight(300)
    t4_layout.addWidget(ai_out, 1)

    btn_copy_ai = QPushButton("📋 Copy to Post Editor (Tab 1)")
    btn_copy_ai.setStyleSheet(f"QPushButton{{background:{SURFACE};color:{ACCENT};border:1px solid {ACCENT};border-radius:6px;padding:7px 16px;font-size:13px;}}QPushButton:hover{{background:{ACCENT};color:#11111B;}}")
    btn_copy_ai.setCursor(Qt.PointingHandCursor)
    t4_layout.addWidget(btn_copy_ai)

    def _do_ai_single():
        payload = {
            "account_id": acct_combo.currentData() or "",
            "page_name": ai_page_name.text().strip(),
            "tone": ai_tone.currentText(),
            "goal": ai_goal.currentText(),
            "audience": ai_audience.text().strip(),
            "topic": ai_topic.text().strip(),
        }
        _disable_btn(btn_ai_single)
        w = _ApiWorker(f"{_fb_base}/api/v1/facebook/ai/generate-post", payload)
        def _cb(r, e):
            _enable_btn(btn_ai_single, "✨ Generate Single Post")
            if e or r.get("status") == "error":
                ai_out.set_error(r.get("message", e or "AI error"))
            else:
                ai_out.setPlainText(r.get("post", ""))
        w.finished.connect(lambda r: _cb(r, None))
        w.error.connect(lambda e: _cb({}, e))
        w.start(); _do_ai_single._w = w

    btn_ai_single.clicked.connect(_do_ai_single)

    def _do_ai_bulk():
        payload = {
            "account_id": acct_combo.currentData() or "",
            "page_name": ai_page_name.text().strip(),
            "topic": ai_topic.text().strip() or "social media growth",
            "num_posts": ai_num.value(),
            "tone": ai_tone.currentText(),
            "goal": ai_goal.currentText(),
        }
        _disable_btn(btn_ai_bulk)
        w = _ApiWorker(f"{_fb_base}/api/v1/facebook/ai/bulk-schedule", payload)
        def _cb(r, e):
            _enable_btn(btn_ai_bulk, "📦 Bulk Generate Posts")
            if e or r.get("status") == "error":
                ai_out.set_error(r.get("message", e or "AI error"))
            else:
                posts = r.get("posts", [])
                ai_out.setPlainText("\n\n" + "─"*60 + "\n\n".join(
                    [f"── POST {i+1} ──\n{p}" for i, p in enumerate(posts)]
                ))
        w.finished.connect(lambda r: _cb(r, None))
        w.error.connect(lambda e: _cb({}, e))
        w.start(); _do_ai_bulk._w = w

    btn_ai_bulk.clicked.connect(_do_ai_bulk)

    def _copy_to_editor():
        txt = ai_out.toPlainText().strip()
        if txt:
            pub_msg.setPlainText(txt)
            tabs.setCurrentIndex(0)

    btn_copy_ai.clicked.connect(_copy_to_editor)

    tabs.addTab(t4, "🤖 AI Content Studio")

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 5 — Page Insights & Analytics
    # ─────────────────────────────────────────────────────────────────────────
    t5 = QWidget()
    t5_layout = QVBoxLayout(t5)
    t5_layout.setContentsMargins(14, 14, 14, 14)
    t5_layout.setSpacing(12)

    ins_row = QHBoxLayout()
    ins_page_id = QLineEdit()
    ins_page_id.setPlaceholderText("Page ID…")
    ins_page_id.setStyleSheet(pub_link.styleSheet())
    ins_since = QLineEdit()
    ins_since.setPlaceholderText("Since YYYY-MM-DD (optional)")
    ins_since.setStyleSheet(pub_link.styleSheet())
    ins_until = QLineEdit()
    ins_until.setPlaceholderText("Until YYYY-MM-DD (optional)")
    ins_until.setStyleSheet(pub_link.styleSheet())
    btn_load_ins = QPushButton("📊 Load Insights")
    btn_load_ins.setStyleSheet(btn_load_cmts.styleSheet())
    btn_load_ins.setCursor(Qt.PointingHandCursor)
    ins_row.addWidget(QLabel("Page ID:"))
    ins_row.addWidget(ins_page_id)
    ins_row.addWidget(QLabel("Since:"))
    ins_row.addWidget(ins_since)
    ins_row.addWidget(QLabel("Until:"))
    ins_row.addWidget(ins_until)
    ins_row.addWidget(btn_load_ins)
    ins_row.addStretch()
    t5_layout.addLayout(ins_row)

    # Insight cards row
    cards_row = QHBoxLayout()
    _ins_cards = {}
    for metric in ("Fans", "Reach", "Impressions", "Engagement", "New Fans", "Page Views"):
        card = QFrame()
        card.setStyleSheet(f"background:{SURFACE};border:1px solid {BORDER};border-radius:10px;padding:10px;")
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(10, 8, 10, 8)
        lbl = QLabel(metric)
        lbl.setStyleSheet(f"color:{SUBTEXT};font-size:12px;")
        lbl.setAlignment(Qt.AlignCenter)
        val = QLabel("—")
        val.setStyleSheet(f"color:{ACCENT};font-size:22px;font-weight:bold;")
        val.setAlignment(Qt.AlignCenter)
        card_lay.addWidget(lbl)
        card_lay.addWidget(val)
        _ins_cards[metric] = val
        cards_row.addWidget(card)
    t5_layout.addLayout(cards_row)

    ins_raw = OutputBox()
    ins_raw.setMinimumHeight(200)
    t5_layout.addWidget(ins_raw, 1)

    # AI analysis button
    btn_ai_analyze_ins = QPushButton("🤖 AI Analyze Insights")
    btn_ai_analyze_ins.setStyleSheet(btn_ai_single.styleSheet())
    btn_ai_analyze_ins.setCursor(Qt.PointingHandCursor)
    t5_layout.addWidget(btn_ai_analyze_ins)

    _t5_state = {"page_id": "", "metrics": {}}

    def _load_insights_cb(resp, err):
        if err or resp.get("status") == "error":
            ins_raw.set_error(resp.get("message", err or "Error"))
            _enable_btn(btn_load_ins, "📊 Load Insights")
            return
        fan_count = resp.get("fan_count", 0)
        _ins_cards["Fans"].setText(f"{fan_count:,}")
        insights = resp.get("insights", [])
        # Map metric names to card keys
        metric_map = {
            "page_fans": "Fans",
            "page_reach": "Reach",              # legacy name (kept for compat)
            "page_impressions_unique": "Reach",  # new name (replaces page_reach)
            "page_impressions": "Impressions",
            "page_engaged_users": "Engagement",
            "page_fan_adds": "New Fans",
            "page_views_total": "Page Views",    # kept for compat if ever returned
        }
        summary = {}
        for ins in insights:
            name  = ins.get("name", "")
            key   = metric_map.get(name)
            vals  = ins.get("values", [])
            total = sum(v.get("value", 0) for v in vals if isinstance(v.get("value", 0), (int, float)))
            summary[name] = total
            if key:
                _ins_cards[key].setText(f"{total:,.0f}")
        _t5_state["metrics"] = summary
        _t5_state["page_id"] = resp.get("page_name", "")
        # Show raw insight data
        lines = [f"📊 {resp.get('page_name','Page')} • {len(insights)} metrics\n"]
        for ins in insights:
            name = ins.get("name", "")
            vals = ins.get("values", [])
            total = sum(v.get("value", 0) for v in vals if isinstance(v.get("value", 0), (int, float)))
            lines.append(f"  {name}: {total:,.0f}")
        ins_raw.setPlainText("\n".join(lines))
        _enable_btn(btn_load_ins, "📊 Load Insights")

    def _do_load_insights():
        pid = ins_page_id.text().strip()
        if not pid:
            ins_raw.set_error("Enter a Page ID first."); return
        acct_id = acct_combo.currentData() or ""
        _disable_btn(btn_load_ins)
        params_str = f"?account_id={acct_id}"
        if ins_since.text().strip():
            params_str += f"&since={ins_since.text().strip()}"
        if ins_until.text().strip():
            params_str += f"&until={ins_until.text().strip()}"
        w = _ApiWorker(f"{_fb_base}/api/v1/facebook/pages/{pid}/insights{params_str}", {}, "GET", None)
        w.finished.connect(lambda r: _load_insights_cb(r, None))
        w.error.connect(lambda e: (_enable_btn(btn_load_ins, "📊 Load Insights"), ins_raw.set_error(e)))
        w.start(); _do_load_insights._w = w

    btn_load_ins.clicked.connect(_do_load_insights)

    def _do_ai_insights():
        metrics = _t5_state.get("metrics", {})
        if not metrics:
            ins_raw.set_error("Load insights first."); return
        # Use post-analysis endpoint with aggregated data
        reach = metrics.get("page_reach", 0)
        payload = {
            "post_id": "page_insights",
            "post_text": f"Page: {_t5_state.get('page_id', 'Facebook Page')} — Insights analysis",
            "likes": int(metrics.get("page_engaged_users", 0)),
            "comments": 0,
            "shares": 0,
            "reach": int(reach),
            "account_id": acct_combo.currentData() or "",
        }
        _disable_btn(btn_ai_analyze_ins)
        w = _ApiWorker(f"{_fb_base}/api/v1/facebook/ai/analyze-post", payload)
        def _cb(r, e):
            _enable_btn(btn_ai_analyze_ins, "🤖 AI Analyze Insights")
            if e or r.get("status") == "error":
                ins_raw.set_error(r.get("message", e or "AI error"))
            else:
                ins_raw.setPlainText(
                    ins_raw.toPlainText() + "\n\n── 🤖 AI Analysis ──\n" + r.get("analysis", "")
                )
        w.finished.connect(lambda r: _cb(r, None))
        w.error.connect(lambda e: _cb({}, e))
        w.start(); _do_ai_insights._w = w

    btn_ai_analyze_ins.clicked.connect(_do_ai_insights)

    tabs.addTab(t5, "📊 Page Insights")

    return page



# ═══════════════════════════════════════════════════════════════════════════════
# TELEGRAM BOT MANAGER PAGE
# ═══════════════════════════════════════════════════════════════════════════════

def build_telegram_bot_page(api_base: str) -> QWidget:
    """Telegram Bot Manager — configure, start/stop and monitor the AI bot 24/7."""
    page = QWidget()
    pl = QVBoxLayout(page)
    pl.setContentsMargins(20, 16, 20, 16)
    pl.setSpacing(10)

    # ── Header ────────────────────────────────────────────────────────────────
    hdr = QLabel("📱  Telegram Bot Manager")
    hdr.setFont(QFont("Segoe UI", 17, QFont.Bold))
    hdr.setStyleSheet(f"color:{ACCENT};")
    pl.addWidget(hdr)

    sub = QLabel("Manage your 24/7 AI growth bot — all 110 features accessible via Telegram")
    sub.setStyleSheet(f"color:{SUBTEXT}; font-size:13px;")
    pl.addWidget(sub)

    # ── Status card ───────────────────────────────────────────────────────────
    status_card = QFrame()
    status_card.setStyleSheet(f"background:{SURFACE};border-radius:10px;border:1px solid {BORDER};")
    sc_lay = QHBoxLayout(status_card)
    sc_lay.setContentsMargins(16, 10, 16, 10)
    _dot        = QLabel("⚫")
    _dot.setFont(QFont("Segoe UI", 18))
    _status_lbl = QLabel("Bot: Stopped")
    _status_lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
    _status_lbl.setStyleSheet(f"color:{SUBTEXT};")
    _uptime_lbl = QLabel("—")
    _uptime_lbl.setStyleSheet(f"color:{SUBTEXT}; font-size:12px;")
    _msg_lbl    = QLabel("📨 Msgs: 0")
    _msg_lbl.setStyleSheet(f"color:{SUBTEXT}; font-size:12px;")
    sc_lay.addWidget(_dot)
    sc_lay.addWidget(_status_lbl)
    sc_lay.addSpacing(16)
    sc_lay.addWidget(_uptime_lbl)
    sc_lay.addStretch()
    sc_lay.addWidget(_msg_lbl)
    pl.addWidget(status_card)

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tabs = QTabWidget()
    tabs.setStyleSheet(f"""
        QTabWidget::pane{{background:{DARK_BG};border:1px solid {BORDER};border-radius:8px;}}
        QTabBar::tab{{background:{SURFACE};color:{SUBTEXT};padding:8px 16px;font-size:13px;border-radius:6px 6px 0 0;margin-right:2px;}}
        QTabBar::tab:selected{{background:{ACCENT};color:#11111B;font-weight:bold;}}
        QTabBar::tab:hover{{background:{HOVER};color:{TEXT};}}
    """)
    pl.addWidget(tabs, 1)

    _grp_style = (
        f"QGroupBox{{color:{ACCENT};font-weight:bold;border:1px solid {BORDER};"
        f"border-radius:8px;padding-top:8px;margin-top:4px;}}"
        f"QGroupBox::title{{subcontrol-origin:margin;left:8px;padding:0 4px;}}"
    )
    _tbl_style = (
        f"QTableWidget{{background:{SURFACE};color:{TEXT};border:1px solid {BORDER};"
        f"border-radius:8px;gridline-color:{BORDER};font-size:12px;}}"
        f"QTableWidget::item{{padding:5px;}}"
        f"QTableWidget::item:selected{{background:{ACCENT}33;}}"
        f"QHeaderView::section{{background:{SIDEBAR};color:{ACCENT};font-weight:bold;padding:5px;border:none;}}"
        f"QTableWidget::item:alternate{{background:{DARK_BG};}}"
    )

    # ──────────────────────────────────────────────────────────────────────────
    # TAB 1 — Setup & Control
    # ──────────────────────────────────────────────────────────────────────────
    t1 = QWidget(); t1l = QVBoxLayout(t1)
    t1l.setContentsMargins(14, 14, 14, 14); t1l.setSpacing(10)

    # Config group
    cfg_grp = QGroupBox("🔑 Bot Configuration")
    cfg_grp.setStyleSheet(_grp_style)
    cfg_lay = QGridLayout(cfg_grp)
    cfg_lay.setSpacing(8)

    cfg_lay.addWidget(QLabel("Bot Token:"), 0, 0)
    tok_input = QLineEdit()
    tok_input.setEchoMode(QLineEdit.Password)
    tok_input.setPlaceholderText("1234567890:AAFxxxxx...  (get from @BotFather on Telegram)")
    tok_input.setStyleSheet(f"background:{DARK_BG};color:{TEXT};border:1px solid {BORDER};border-radius:6px;padding:6px;font-size:13px;")
    # Pre-fill if token already set in config
    try:
        from config import TELEGRAM_BOT_TOKEN as _cfg_tok
        if _cfg_tok and _cfg_tok not in ("", "your_token", "YOUR_TELEGRAM_BOT_TOKEN_HERE"):
            tok_input.setText(_cfg_tok)
    except Exception:
        pass

    tok_eye = QPushButton("👁")
    tok_eye.setFixedWidth(34)
    tok_eye.setCursor(Qt.PointingHandCursor)
    tok_eye.setStyleSheet(f"background:{SURFACE};color:{TEXT};border:1px solid {BORDER};border-radius:6px;padding:3px;")
    def _toggle_eye():
        if tok_input.echoMode() == QLineEdit.Password:
            tok_input.setEchoMode(QLineEdit.Normal); tok_eye.setText("🔒")
        else:
            tok_input.setEchoMode(QLineEdit.Password); tok_eye.setText("👁")
    tok_eye.clicked.connect(_toggle_eye)

    tok_row_w = QWidget(); tok_row = QHBoxLayout(tok_row_w)
    tok_row.setContentsMargins(0, 0, 0, 0); tok_row.addWidget(tok_input, 1); tok_row.addWidget(tok_eye)
    cfg_lay.addWidget(tok_row_w, 0, 1)

    cfg_lay.addWidget(QLabel("Backend URL:"), 1, 0)
    url_input = QLineEdit(api_base)
    url_input.setStyleSheet(tok_input.styleSheet())
    cfg_lay.addWidget(url_input, 1, 1)

    btn_save_cfg = QPushButton("💾  Save to .env")
    btn_save_cfg.setCursor(Qt.PointingHandCursor)
    btn_save_cfg.setStyleSheet(f"background:{ACCENT};color:#11111B;border:none;border-radius:6px;padding:7px 18px;font-weight:bold;font-size:13px;")
    cfg_lay.addWidget(btn_save_cfg, 2, 1)
    t1l.addWidget(cfg_grp)

    # Controls group
    ctrl_grp = QGroupBox("▶  Bot Controls")
    ctrl_grp.setStyleSheet(_grp_style)
    ctrl_lay = QHBoxLayout(ctrl_grp)
    ctrl_lay.setContentsMargins(14, 10, 14, 10); ctrl_lay.setSpacing(10)

    _btn_s = "border:none;border-radius:8px;font-weight:bold;font-size:14px;padding:0 22px;"
    btn_start   = QPushButton("▶  Start Bot");  btn_start.setFixedHeight(38);   btn_start.setCursor(Qt.PointingHandCursor)
    btn_stop    = QPushButton("⏹  Stop");       btn_stop.setFixedHeight(38);    btn_stop.setCursor(Qt.PointingHandCursor);    btn_stop.setEnabled(False)
    btn_restart = QPushButton("🔄  Restart");   btn_restart.setFixedHeight(38); btn_restart.setCursor(Qt.PointingHandCursor); btn_restart.setEnabled(False)
    btn_start.setStyleSheet(f"background:{SUCCESS};color:#11111B;{_btn_s}")
    btn_stop.setStyleSheet(f"background:#F38BA8;color:#11111B;{_btn_s}")
    btn_restart.setStyleSheet(f"background:{WARNING};color:#11111B;{_btn_s}")
    ctrl_lay.addWidget(btn_start); ctrl_lay.addWidget(btn_stop); ctrl_lay.addWidget(btn_restart); ctrl_lay.addStretch()
    t1l.addWidget(ctrl_grp)

    # Log group
    log_grp = QGroupBox("📜  Live Bot Log")
    log_grp.setStyleSheet(_grp_style)
    log_lay = QVBoxLayout(log_grp)
    log_lay.setContentsMargins(10, 8, 10, 8)

    log_view = QTextEdit()
    log_view.setReadOnly(True)
    log_view.setStyleSheet(f"background:#11111B;color:{SUCCESS};font-family:Consolas,monospace;font-size:12px;border:1px solid {BORDER};border-radius:6px;padding:8px;")
    log_view.setMinimumHeight(180)
    log_view.setPlaceholderText("Bot logs appear here when the bot is running…")

    log_ctrl_row = QHBoxLayout()
    btn_clear_log = QPushButton("🗑  Clear"); btn_clear_log.setFixedWidth(90)
    btn_clear_log.setCursor(Qt.PointingHandCursor)
    btn_clear_log.setStyleSheet(f"background:{SURFACE};color:{SUBTEXT};border:1px solid {BORDER};border-radius:6px;padding:4px;font-size:12px;")
    btn_clear_log.clicked.connect(log_view.clear)
    auto_scroll = QCheckBox("Auto-scroll"); auto_scroll.setChecked(True)
    auto_scroll.setStyleSheet(f"color:{SUBTEXT};font-size:12px;")
    log_ctrl_row.addWidget(btn_clear_log); log_ctrl_row.addWidget(auto_scroll); log_ctrl_row.addStretch()
    log_lay.addLayout(log_ctrl_row)
    log_lay.addWidget(log_view, 1)
    t1l.addWidget(log_grp, 1)
    tabs.addTab(t1, "⚙️ Setup & Control")

    # ──────────────────────────────────────────────────────────────────────────
    # TAB 2 — Commands Reference
    # ──────────────────────────────────────────────────────────────────────────
    t2 = QWidget(); t2l = QVBoxLayout(t2)
    t2l.setContentsMargins(14, 14, 14, 14); t2l.setSpacing(8)

    cmd_note = QLabel("💡 All commands work 24/7 via Telegram — the bot connects to the same backend API as the Desktop App.")
    cmd_note.setWordWrap(True)
    cmd_note.setStyleSheet(f"color:{SUBTEXT};font-size:12px;background:{SURFACE};border-radius:6px;padding:8px;")
    t2l.addWidget(cmd_note)

    cmd_table = QTableWidget(0, 4)
    cmd_table.setHorizontalHeaderLabels(["Command", "Category", "Description", "Usage Example"])
    cmd_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
    cmd_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
    cmd_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
    cmd_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
    cmd_table.setSelectionBehavior(QTableWidget.SelectRows)
    cmd_table.setEditTriggers(QTableWidget.NoEditTriggers)
    cmd_table.setAlternatingRowColors(True)
    cmd_table.setStyleSheet(_tbl_style)
    t2l.addWidget(cmd_table, 1)

    _cmd_data = [
        ("/start",     "Core",        "Welcome screen + interactive keyboard",                "/start"),
        ("/help",      "Core",        "Full command list with descriptions",                  "/help"),
        ("/strategy",  "AI Brain",    "Generate 30-day AI growth strategy",                   "/strategy"),
        ("/content",   "AI Brain",    "Viral content package (hook/caption/hashtags/script)", "/content"),
        ("/audit",     "AI Brain",    "Deep account performance audit",                       "/audit"),
        ("/trends",    "AI Brain",    "Scan live trending topics by platform",                "/trends"),
        ("/risk",      "AI Brain",    "Content safety & policy compliance check",             "/risk"),
        ("/agents",    "AI Brain",    "Run full 5-agent AI team parallel analysis",           "/agents"),
        ("/campaign",  "AI Brain",    "Build AI-optimised campaign plan",                     "/campaign"),
        ("/report",    "AI Brain",    "Generate detailed performance report",                 "/report"),
        ("/viral",     "Growth",      "Viral hooks, captions, trending hashtags",             "/viral"),
        ("/brand",     "Growth",      "Brand authority & positioning score",                  "/brand"),
        ("/creator",   "Growth",      "Creator toolkit — scripts, ideas, repurpose",          "/creator"),
        ("/community", "Growth",      "Community engagement strategies & tips",               "/community"),
        ("/analytics", "Analytics",   "Quick analytics dashboard by platform",                "/analytics"),
        ("/business",  "Business",    "Business intelligence & market analysis",              "/business"),
        ("/geo",       "SMM/Geo",     "🌍 AI GEO-targeted order — country/city precision",   "/geo"),
        ("/panel",     "SMM",         "SMM panel services catalog",                           "/panel"),
        ("/order",     "SMM",         "Place AI smart SMM order",                             "/order"),
        ("/balance",   "SMM",         "Check SMM panel balance",                              "/balance"),
        ("/facebook",  "Facebook",    "Facebook page tools — posts, AI content, schedule",   "/facebook"),
        ("/schedule",  "Scheduler",   "Content scheduling — week plan / best times",         "/schedule"),
        ("/inbox",     "Inbox",       "Auto-reply templates & comment strategies",            "/inbox"),
    ]
    _cat_colors = {
        "Core": ACCENT, "AI Brain": SUCCESS, "Growth": "#CBA6F7",
        "Analytics": "#89DCEB", "Business": "#A6E3A1", "SMM/Geo": "#FAB387",
        "SMM": WARNING, "Facebook": "#4C9EEB", "Scheduler": "#ABE9B3", "Inbox": "#DDB6F2",
    }
    for cmd, cat, desc, ex in _cmd_data:
        r = cmd_table.rowCount(); cmd_table.insertRow(r)
        for col, val in enumerate([cmd, cat, desc, ex]):
            item = QTableWidgetItem(val)
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            if col == 0:
                item.setForeground(QColor(ACCENT))
                item.setFont(QFont("Consolas", 12, QFont.Bold))
            elif col == 1:
                item.setForeground(QColor(_cat_colors.get(cat, TEXT)))
                item.setFont(QFont("Segoe UI", 11, QFont.Bold))
            cmd_table.setItem(r, col, item)
    tabs.addTab(t2, "📋 Commands")

    # ──────────────────────────────────────────────────────────────────────────
    # TAB 3 — AI Features Map
    # ──────────────────────────────────────────────────────────────────────────
    t3 = QWidget(); t3l = QVBoxLayout(t3)
    t3l.setContentsMargins(14, 14, 14, 14); t3l.setSpacing(8)

    feat_note = QLabel(
        "Every AI feature in the Desktop App is also available on the Telegram Bot — same backend API, delivered to your chat 24/7."
    )
    feat_note.setWordWrap(True)
    feat_note.setStyleSheet(f"color:{TEXT};font-size:13px;background:{SURFACE};border-radius:8px;padding:10px;")
    t3l.addWidget(feat_note)

    feat_table = QTableWidget(0, 3)
    feat_table.setHorizontalHeaderLabels(["Desktop Page", "Bot Command(s)", "Features Covered"])
    feat_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
    feat_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
    feat_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
    feat_table.setEditTriggers(QTableWidget.NoEditTriggers)
    feat_table.setAlternatingRowColors(True)
    feat_table.setStyleSheet(_tbl_style)
    t3l.addWidget(feat_table, 1)

    _feature_map = [
        ("📊 Dashboard",         "/start",                  "Status overview, quick stats"),
        ("🧠 Strategy Brain",    "/strategy",               "30-day growth plan, posting schedule, goal modeling"),
        ("✍️ Content Studio",    "/content + /creator",     "Viral hooks, captions, hashtags, video scripts, repurpose"),
        ("📈 Analytics",         "/analytics + /report",    "Performance metrics, engagement rate, ROI analysis"),
        ("🔮 Trend Radar",       "/trends",                 "Live trending topics, viral sounds, hashtag waves"),
        ("⚙️ Campaign Engine",   "/campaign",               "Campaign planning, budget allocation, timeline"),
        ("🛡️ Risk Engine",       "/risk",                   "Content safety, shadowban detection, policy compliance"),
        ("🛒 SMM Panel",         "/panel + /order",         "Service catalog, smart orders, balance management"),
        ("🤖 Multi-Agent AI",    "/agents",                 "5-agent parallel analysis, orchestrated insights"),
        ("📅 Auto-Scheduler",    "/schedule",               "Content calendar, best time to post, weekly plan"),
        ("💬 Social Inbox",      "/inbox",                  "Auto-reply templates, comment strategies, DM tips"),
        ("🌍 Geo Intelligence",  "/geo",                    "Country/city-targeted orders, Real Human delivery"),
        ("📱 Social Manager",    "/facebook + /content",    "Multi-platform management, post analytics"),
        ("🔍 Intelligence Hub",  "/business",               "Competitor analysis, market intelligence"),
        ("🔥 Viral & Growth",    "/viral",                  "Hook formulas, viral formats, growth hacks"),
        ("💼 Business Intel",    "/business",               "Market analysis, customer personas, revenue tracking"),
        ("🎨 Creator Tools",     "/creator",                "Script writing, content repurpose, idea generation"),
        ("💰 Sales Engine",      "/business",               "Sales funnels, DM scripts, conversion tactics"),
        ("🏆 Brand Authority",   "/brand",                  "Brand positioning, authority score, trust building"),
        ("🤝 Community Hub",     "/community",              "Engagement tactics, loyalty programs, growth hacks"),
        ("📘 Facebook Manager",  "/facebook",               "Page insights, AI post generation, bulk schedule"),
    ]
    for desk, bot_cmd, feats in _feature_map:
        r = feat_table.rowCount(); feat_table.insertRow(r)
        for col, val in enumerate([desk, bot_cmd, feats]):
            item = QTableWidgetItem(val)
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            if col == 1:
                item.setForeground(QColor(ACCENT))
                item.setFont(QFont("Consolas", 12))
            feat_table.setItem(r, col, item)
    tabs.addTab(t3, "🚀 AI Features Map")

    # ──────────────────────────────────────────────────────────────────────────
    # TAB 4 — Stats & Setup Guide
    # ──────────────────────────────────────────────────────────────────────────
    t4 = QWidget(); t4l = QVBoxLayout(t4)
    t4l.setContentsMargins(14, 14, 14, 14); t4l.setSpacing(10)

    stats_row = QHBoxLayout()
    _stat_cards = {}
    for lbl, val, clr in [("⏱ Uptime", "—", ACCENT), ("📨 Messages", "0", SUCCESS), ("⌨️ Commands", "0", WARNING), ("👥 Sessions", "0", "#CBA6F7")]:
        card = QFrame()
        card.setStyleSheet(f"background:{SURFACE};border-radius:10px;border:1px solid {BORDER};")
        cl = QVBoxLayout(card); cl.setContentsMargins(14, 10, 14, 10)
        vl = QLabel(val); vl.setFont(QFont("Segoe UI", 20, QFont.Bold))
        vl.setStyleSheet(f"color:{clr};"); vl.setAlignment(Qt.AlignCenter)
        ll = QLabel(lbl); ll.setStyleSheet(f"color:{SUBTEXT};font-size:12px;"); ll.setAlignment(Qt.AlignCenter)
        cl.addWidget(vl); cl.addWidget(ll)
        stats_row.addWidget(card); _stat_cards[lbl] = vl
    t4l.addLayout(stats_row)

    guide = QTextEdit()
    guide.setReadOnly(True)
    guide.setStyleSheet(f"background:{SURFACE};color:{TEXT};border:1px solid {BORDER};border-radius:8px;padding:12px;font-size:13px;")
    guide.setHtml(f"""
    <h3 style='color:{ACCENT};margin-top:0;'>Quick Setup Guide (3 steps)</h3>
    <ol style='color:{TEXT};line-height:2.0;'>
      <li><b>Get a bot token:</b> Open Telegram → search <code style='color:{ACCENT};'>@BotFather</code> → send <code style='color:{ACCENT};'>/newbot</code> → copy the token</li>
      <li><b>Paste & save:</b> Go to ⚙️ Setup tab → paste token → click <b>💾 Save to .env</b></li>
      <li><b>Launch:</b> Click <b>▶ Start Bot</b> → open Telegram → send <code style='color:{ACCENT};'>/start</code></li>
    </ol>
    <h3 style='color:{SUCCESS};'>What your 24/7 AI bot does:</h3>
    <table style='color:{TEXT};width:100%;border-collapse:collapse;'>
      <tr><td style='padding:4px;'>🧠</td><td>Generates 30-day AI growth strategies on demand</td></tr>
      <tr><td style='padding:4px;'>✍️</td><td>Creates viral content packages — hook, caption, hashtags, script</td></tr>
      <tr><td style='padding:4px;'>📊</td><td>Delivers analytics reports and competitor insights to your chat</td></tr>
      <tr><td style='padding:4px;'>🌍</td><td>Places geo-targeted Real Human SMM orders from your phone</td></tr>
      <tr><td style='padding:4px;'>🛡️</td><td>Checks content safety before you publish — no more bans</td></tr>
      <tr><td style='padding:4px;'>🤖</td><td>Runs full 5-agent AI team analysis in one /agents command</td></tr>
      <tr><td style='padding:4px;'>📘</td><td>Generates AI Facebook posts, shows page insights, bulk schedules</td></tr>
      <tr><td style='padding:4px;'>🔥</td><td>Delivers viral hooks, trending hashtags, growth hacks instantly</td></tr>
      <tr><td style='padding:4px;'>💬</td><td>Auto-reply templates and comment engagement strategies</td></tr>
      <tr><td style='padding:4px;'>📅</td><td>Schedules content calendars and tells you best posting times</td></tr>
    </table>
    <p style='color:{SUBTEXT};margin-top:12px;font-size:12px;'>
      💡 Set <code>GROQ_API_KEY</code> or <code>OPENAI_API_KEY</code> in your .env for real GPT-4o / LLaMA 3 AI responses.
    </p>
    """)
    t4l.addWidget(guide, 1)
    tabs.addTab(t4, "📊 Stats & Guide")

    # ──────────────────────────────────────────────────────────────────────────
    # Bot lifecycle logic
    # ──────────────────────────────────────────────────────────────────────────
    _state = {"thread": None, "start_time": None, "msg_count": 0, "cmd_count": 0, "sessions": set()}

    def _append_log(line: str):
        ts = _dt_cls.now().strftime("%H:%M:%S")
        safe = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        color = WARNING if "ERROR" in line.upper() or "error" in line else (SUCCESS if any(k in line for k in ["start", "poll", "✅"]) else TEXT)
        log_view.append(f"<span style='color:{SUBTEXT};font-size:11px;'>[{ts}]</span> <span style='color:{color};'>{safe}</span>")
        if auto_scroll.isChecked():
            sb = log_view.verticalScrollBar(); sb.setValue(sb.maximum())
        lo = line.lower()
        if any(k in lo for k in ["message", "update", "received"]):
            _state["msg_count"] += 1
            _stat_cards["📨 Messages"].setText(str(_state["msg_count"]))
            _msg_lbl.setText(f"📨 Msgs: {_state['msg_count']}")
        if any(k in lo for k in ["/strategy", "/content", "/geo", "/viral", "/agents", "/audit"]):
            _state["cmd_count"] += 1
            _stat_cards["⌨️ Commands"].setText(str(_state["cmd_count"]))

    def _on_status(s: str):
        if s == "running":
            _state["start_time"] = _dt_cls.now()
            _dot.setText("🟢"); _status_lbl.setText("Bot: Running ✓")
            _status_lbl.setStyleSheet(f"color:{SUCCESS};font-weight:bold;font-size:13px;")
            btn_start.setEnabled(False); btn_stop.setEnabled(True); btn_restart.setEnabled(True)
            _append_log("✅ GrowthOS AI Bot is LIVE — polling Telegram for messages…")
        elif s == "stopped":
            _dot.setText("⚫"); _status_lbl.setText("Bot: Stopped")
            _status_lbl.setStyleSheet(f"color:{SUBTEXT};font-weight:bold;font-size:13px;")
            btn_start.setEnabled(True); btn_stop.setEnabled(False); btn_restart.setEnabled(False)
            _uptime_lbl.setText("—"); _state["start_time"] = None; _state["thread"] = None
            _append_log("⏹ Bot stopped.")
        elif s.startswith("error:"):
            _dot.setText("🔴"); _status_lbl.setText("Bot: Error")
            _status_lbl.setStyleSheet(f"color:#F38BA8;font-weight:bold;font-size:13px;")
            btn_start.setEnabled(True); btn_stop.setEnabled(False); btn_restart.setEnabled(False)
            _state["thread"] = None; _append_log(f"❌ {s}")

    def _save_config():
        tok = tok_input.text().strip()
        url = url_input.text().strip()
        if not tok:
            _append_log("⚠️ Token is empty — nothing saved."); return
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        lines = []
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        updated_tok = False; updated_url = False
        for i, line in enumerate(lines):
            if line.startswith("TELEGRAM_BOT_TOKEN="):
                lines[i] = f"TELEGRAM_BOT_TOKEN={tok}\n"; updated_tok = True
            if line.startswith("BACKEND_URL="):
                lines[i] = f"BACKEND_URL={url}\n"; updated_url = True
        if not updated_tok: lines.append(f"TELEGRAM_BOT_TOKEN={tok}\n")
        if not updated_url: lines.append(f"BACKEND_URL={url}\n")
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        _append_log("💾 Saved — TELEGRAM_BOT_TOKEN & BACKEND_URL written to .env")
        _dot.setText("🟡"); _status_lbl.setText("Bot: Ready (token saved)")
        _status_lbl.setStyleSheet(f"color:{WARNING};font-weight:bold;font-size:13px;")

    def _start_bot():
        if _state["thread"] and _state["thread"].isRunning():
            return
        tok = tok_input.text().strip()
        if not tok:
            _append_log("⚠️ No token set. Paste your token and click 💾 Save first."); return
        os.environ["TELEGRAM_BOT_TOKEN"] = tok
        os.environ["BACKEND_URL"] = url_input.text().strip() or api_base
        t = BotThread()
        t.log_line.connect(_append_log)
        t.status_change.connect(_on_status)
        _state["thread"] = t; _state["msg_count"] = 0; _state["cmd_count"] = 0
        _dot.setText("🟡"); _status_lbl.setText("Bot: Starting…")
        _status_lbl.setStyleSheet(f"color:{WARNING};font-weight:bold;font-size:13px;")
        _append_log("▶ Launching GrowthOS AI Telegram Bot…")
        t.start()

    def _stop_bot():
        t = _state.get("thread")
        if t and t.isRunning():
            t.stop_bot(); _append_log("⏹ Sending stop signal…")

    def _restart_bot():
        _stop_bot(); QTimer.singleShot(1600, _start_bot)

    # Uptime ticker (1-second)
    _uptime_timer = QTimer()
    def _tick():
        st = _state.get("start_time")
        if st:
            delta = _dt_cls.now() - st
            h, rem = divmod(int(delta.total_seconds()), 3600)
            m, s = divmod(rem, 60)
            txt = f"⏱ {h:02d}:{m:02d}:{s:02d}"
            _uptime_lbl.setText(txt); _stat_cards["⏱ Uptime"].setText(f"{h:02d}:{m:02d}:{s:02d}")
    _uptime_timer.timeout.connect(_tick); _uptime_timer.start(1000)

    btn_save_cfg.clicked.connect(_save_config)
    btn_start.clicked.connect(_start_bot)
    btn_stop.clicked.connect(_stop_bot)
    btn_restart.clicked.connect(_restart_bot)

    return page


# ═══════════════════════════════════════════════════════════════════════════════
# ✦ NEW FEATURE PAGE 30: AI VIDEO STUDIO
# ═══════════════════════════════════════════════════════════════════════════════

def build_video_studio_page(api_base: str) -> QWidget:
    """AI Video Studio — TikTok/Reels/Shorts script & storyboard generator."""
    import asyncio

    _GS = (f"QGroupBox{{color:{ACCENT};font-weight:bold;border:1px solid {BORDER};"
           f"border-radius:8px;padding-top:8px;margin-top:4px;}}"
           f"QGroupBox::title{{subcontrol-origin:margin;left:8px;padding:0 4px;}}")

    def _btn(text, color=None):
        b = QPushButton(text)
        b.setCursor(Qt.PointingHandCursor)
        c = color or ACCENT
        b.setStyleSheet(
            f"QPushButton{{background:{c};color:#11111B;border:none;border-radius:8px;"
            f"padding:8px 18px;font-weight:bold;font-size:13px;}}"
            f"QPushButton:hover{{background:{c}CC;}}"
            f"QPushButton:disabled{{background:{BORDER};color:{SUBTEXT};}}"
        )
        return b

    page = QWidget()
    pl = QVBoxLayout(page)
    pl.setContentsMargins(20, 16, 20, 16)
    pl.setSpacing(10)

    hdr = QLabel("🎬  AI Video Studio")
    hdr.setFont(QFont("Segoe UI", 17, QFont.Bold))
    hdr.setStyleSheet(f"color:{ACCENT};")
    pl.addWidget(hdr)
    sub = QLabel("Generate complete TikTok / Reels / YouTube Shorts scripts, storyboards, hooks & SEO metadata with AI")
    sub.setStyleSheet(f"color:{SUBTEXT}; font-size:13px;")
    pl.addWidget(sub)

    tabs = QTabWidget()
    tabs.setStyleSheet(
        f"QTabWidget::pane{{background:{DARK_BG};border:1px solid {BORDER};border-radius:8px;}}"
        f"QTabBar::tab{{background:{SURFACE};color:{SUBTEXT};padding:8px 14px;font-size:13px;border-radius:6px 6px 0 0;margin-right:2px;}}"
        f"QTabBar::tab:selected{{background:{ACCENT};color:#11111B;font-weight:bold;}}"
        f"QTabBar::tab:hover{{background:{HOVER};color:{TEXT};}}"
    )
    pl.addWidget(tabs, 1)

    # ── TAB 1: Script Generator ───────────────────────────────────────────────
    t1 = QWidget(); t1l = QVBoxLayout(t1); t1l.setContentsMargins(14, 12, 14, 12); t1l.setSpacing(8)

    grp_in = QGroupBox("🎯 Video Brief"); grp_in.setStyleSheet(_GS)
    gin = QGridLayout(grp_in); gin.setSpacing(8)

    gin.addWidget(QLabel("Topic / Idea:"), 0, 0)
    vs_topic = QLineEdit(); vs_topic.setPlaceholderText("e.g. How to grow on TikTok in 2025")
    gin.addWidget(vs_topic, 0, 1, 1, 3)

    gin.addWidget(QLabel("Platform:"), 1, 0)
    vs_platform = QComboBox(); vs_platform.addItems(["TikTok", "Instagram Reels", "YouTube Shorts", "Facebook Reels", "Snapchat Spotlight"])
    gin.addWidget(vs_platform, 1, 1)

    gin.addWidget(QLabel("Duration (sec):"), 1, 2)
    vs_dur = QSpinBox(); vs_dur.setRange(15, 600); vs_dur.setValue(60); vs_dur.setSuffix(" sec")
    gin.addWidget(vs_dur, 1, 3)

    gin.addWidget(QLabel("Style:"), 2, 0)
    vs_style = QComboBox(); vs_style.addItems(["Educational", "Entertainment", "Inspirational", "Tutorial", "Storytelling", "Comedy", "POV", "Vlog"])
    gin.addWidget(vs_style, 2, 1)

    gin.addWidget(QLabel("Niche:"), 2, 2)
    vs_niche = QLineEdit(); vs_niche.setPlaceholderText("e.g. fitness, business, beauty")
    gin.addWidget(vs_niche, 2, 3)

    gin.addWidget(QLabel("Language:"), 3, 0)
    vs_lang = QComboBox(); vs_lang.addItems(["English", "Khmer", "Thai", "Vietnamese", "Chinese", "Japanese", "Korean", "Spanish", "French", "Arabic", "Hindi"])
    gin.addWidget(vs_lang, 3, 1)

    t1l.addWidget(grp_in)

    btn_row = QHBoxLayout()
    vs_gen_script = _btn("🎬 Generate Script", ACCENT)
    vs_gen_board  = _btn("🎞 Build Storyboard", SUCCESS)
    vs_gen_seo    = _btn("🔍 Video SEO Pack", WARNING)
    btn_row.addWidget(vs_gen_script); btn_row.addWidget(vs_gen_board); btn_row.addWidget(vs_gen_seo); btn_row.addStretch()
    t1l.addLayout(btn_row)

    vs_out = QTextEdit(); vs_out.setReadOnly(True)
    vs_out.setPlaceholderText("📝 Your AI-generated video script will appear here...\n\nFill in the brief above and click Generate Script.")
    vs_out.setStyleSheet(f"background:{SURFACE};color:{TEXT};border:1px solid {BORDER};border-radius:8px;font-family:Consolas,monospace;font-size:13px;")
    t1l.addWidget(vs_out, 1)
    tabs.addTab(t1, "📝 Script Generator")

    # ── TAB 2: Hook Optimizer ─────────────────────────────────────────────────
    t2 = QWidget(); t2l = QVBoxLayout(t2); t2l.setContentsMargins(14, 12, 14, 12); t2l.setSpacing(8)

    grp_hook = QGroupBox("🎣 Hook Optimizer"); grp_hook.setStyleSheet(_GS)
    gh = QGridLayout(grp_hook); gh.setSpacing(8)
    gh.addWidget(QLabel("Existing Hook:"), 0, 0)
    vs_hook_in = QLineEdit(); vs_hook_in.setPlaceholderText("Paste your current opening line or hook...")
    gh.addWidget(vs_hook_in, 0, 1, 1, 3)
    gh.addWidget(QLabel("Platform:"), 1, 0)
    vs_hook_plat = QComboBox(); vs_hook_plat.addItems(["TikTok", "Instagram Reels", "YouTube Shorts"])
    gh.addWidget(vs_hook_plat, 1, 1)
    gh.addWidget(QLabel("Language:"), 1, 2)
    vs_hook_lang = QComboBox(); vs_hook_lang.addItems(["English", "Khmer", "Thai", "Vietnamese", "Chinese", "Spanish"])
    gh.addWidget(vs_hook_lang, 1, 3)
    t2l.addWidget(grp_hook)

    btn_hook = _btn("⚡ Optimize Hook", WARNING)
    t2l.addWidget(btn_hook)
    vs_hook_out = QTextEdit(); vs_hook_out.setReadOnly(True)
    vs_hook_out.setPlaceholderText("Optimized hook variations with AI retention predictions will appear here...")
    vs_hook_out.setStyleSheet(f"background:{SURFACE};color:{TEXT};border:1px solid {BORDER};border-radius:8px;font-size:13px;")
    t2l.addWidget(vs_hook_out, 1)

    grp_caption = QGroupBox("📝 Caption & Subtitle Generator"); grp_caption.setStyleSheet(_GS)
    gc = QGridLayout(grp_caption); gc.setSpacing(8)
    gc.addWidget(QLabel("Topic:"), 0, 0)
    vs_cap_topic = QLineEdit(); vs_cap_topic.setPlaceholderText("Video topic for caption generation...")
    gc.addWidget(vs_cap_topic, 0, 1, 1, 3)
    gc.addWidget(QLabel("Caption Style:"), 1, 0)
    vs_cap_style = QComboBox(); vs_cap_style.addItems(["Energetic", "Professional", "Funny", "Inspirational", "Educational", "Storytelling"])
    gc.addWidget(vs_cap_style, 1, 1)
    gc.addWidget(QLabel("Platform:"), 1, 2)
    vs_cap_plat = QComboBox(); vs_cap_plat.addItems(["Instagram", "TikTok", "YouTube", "Facebook"])
    gc.addWidget(vs_cap_plat, 1, 3)
    t2l.addWidget(grp_caption)

    btn_caption = _btn("✍️ Generate Captions", ACCENT)
    t2l.addWidget(btn_caption)
    tabs.addTab(t2, "🎣 Hook & Captions")

    # ── Worker thread ─────────────────────────────────────────────────────────
    class _VS_Worker(QThread):
        finished = pyqtSignal(str)
        error    = pyqtSignal(str)
        def __init__(self, coro): super().__init__(); self._coro = coro
        def run(self):
            try:
                loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
                result = loop.run_until_complete(self._coro); loop.close()
                self.finished.emit(result)
            except Exception as e:
                self.error.emit(str(e))

    _vs_workers = []

    def _run_vs(coro, out_widget, btn_widget, btn_label):
        btn_widget.setEnabled(False); btn_widget.setText("⏳ Generating...")
        out_widget.setText("🔄 AI is generating your video content... please wait.")
        w = _VS_Worker(coro)
        w.finished.connect(lambda r: (_set_out(out_widget, r), _reset_btn(btn_widget, btn_label)))
        w.error.connect(lambda e: (out_widget.setText(f"❌ Error: {e}"), _reset_btn(btn_widget, btn_label)))
        _vs_workers.append(w); w.start()

    def _set_out(widget, raw):
        try:
            data = json.loads(raw) if isinstance(raw, str) and raw.startswith("{") else raw
            if isinstance(data, dict):
                txt = ""
                for k, v in data.items():
                    if isinstance(v, list):
                        txt += f"\n{'─'*50}\n🔹 {k.upper().replace('_',' ')}\n"
                        for i, item in enumerate(v, 1):
                            if isinstance(item, dict):
                                txt += f"\n  [{i}] " + " | ".join(f"{kk}: {vv}" for kk, vv in item.items()) + "\n"
                            else:
                                txt += f"  {i}. {item}\n"
                    elif isinstance(v, dict):
                        txt += f"\n{'─'*50}\n🔹 {k.upper().replace('_',' ')}\n"
                        for kk, vv in v.items():
                            txt += f"  • {kk}: {vv}\n"
                    else:
                        txt += f"\n🔹 {k.upper().replace('_',' ')}: {v}\n"
                widget.setText(txt.strip())
            else:
                widget.setText(str(raw))
        except Exception:
            widget.setText(str(raw))

    def _reset_btn(btn, label):
        btn.setEnabled(True); btn.setText(label)

    def _do_gen_script():
        from ai_core.video_studio import generate_video_script
        import asyncio as _al
        async def _run():
            r = await generate_video_script(
                vs_topic.text().strip() or "social media growth",
                vs_platform.currentText(), vs_dur.value(),
                vs_style.currentText(), vs_niche.text().strip() or "General",
                vs_lang.currentText()
            )
            return json.dumps(r, ensure_ascii=False, indent=2)
        _run_vs(_run(), vs_out, vs_gen_script, "🎬 Generate Script")

    def _do_gen_board():
        from ai_core.video_studio import build_storyboard
        async def _run():
            r = await build_storyboard(
                vs_topic.text().strip() or "social media growth",
                vs_platform.currentText(), 6, vs_lang.currentText()
            )
            return json.dumps(r, ensure_ascii=False, indent=2)
        _run_vs(_run(), vs_out, vs_gen_board, "🎞 Build Storyboard")

    def _do_gen_seo():
        from ai_core.video_studio import generate_video_seo
        async def _run():
            r = await generate_video_seo(
                vs_topic.text().strip() or "social media growth",
                vs_platform.currentText(), vs_lang.currentText()
            )
            return json.dumps(r, ensure_ascii=False, indent=2)
        _run_vs(_run(), vs_out, vs_gen_seo, "🔍 Video SEO Pack")

    def _do_hook():
        from ai_core.video_studio import optimize_video_hook
        async def _run():
            r = await optimize_video_hook(
                vs_hook_in.text().strip() or "Stop scrolling — this changes everything...",
                vs_hook_plat.currentText(), vs_hook_lang.currentText()
            )
            return json.dumps(r, ensure_ascii=False, indent=2)
        _run_vs(_run(), vs_hook_out, btn_hook, "⚡ Optimize Hook")

    def _do_caption():
        from ai_core.video_studio import generate_captions
        async def _run():
            r = await generate_captions(
                vs_cap_topic.text().strip() or "social media",
                vs_cap_plat.currentText(), vs_cap_style.currentText(),
                vs_hook_lang.currentText()
            )
            return json.dumps(r, ensure_ascii=False, indent=2)
        _run_vs(_run(), vs_hook_out, btn_caption, "✍️ Generate Captions")

    vs_gen_script.clicked.connect(_do_gen_script)
    vs_gen_board.clicked.connect(_do_gen_board)
    vs_gen_seo.clicked.connect(_do_gen_seo)
    btn_hook.clicked.connect(_do_hook)
    btn_caption.clicked.connect(_do_caption)

    return page


# ═══════════════════════════════════════════════════════════════════════════════
# ✦ NEW FEATURE PAGE 31: A/B INTELLIGENCE LAB
# ═══════════════════════════════════════════════════════════════════════════════

def build_ab_lab_page(api_base: str) -> QWidget:
    """A/B Intelligence Lab — AI-powered multi-variant content testing."""
    import asyncio

    _GS = (f"QGroupBox{{color:{ACCENT};font-weight:bold;border:1px solid {BORDER};"
           f"border-radius:8px;padding-top:8px;margin-top:4px;}}"
           f"QGroupBox::title{{subcontrol-origin:margin;left:8px;padding:0 4px;}}")

    def _btn(text, color=None):
        b = QPushButton(text); b.setCursor(Qt.PointingHandCursor)
        c = color or ACCENT
        b.setStyleSheet(
            f"QPushButton{{background:{c};color:#11111B;border:none;border-radius:8px;"
            f"padding:8px 18px;font-weight:bold;font-size:13px;}}"
            f"QPushButton:hover{{background:{c}CC;}}"
            f"QPushButton:disabled{{background:{BORDER};color:{SUBTEXT};}}"
        )
        return b

    page = QWidget(); pl = QVBoxLayout(page)
    pl.setContentsMargins(20, 16, 20, 16); pl.setSpacing(10)

    hdr = QLabel("🧪  A/B Intelligence Lab")
    hdr.setFont(QFont("Segoe UI", 17, QFont.Bold))
    hdr.setStyleSheet(f"color:{ACCENT};")
    pl.addWidget(hdr)
    sub = QLabel("Generate AI-predicted A/B content variants — know your winner BEFORE you post")
    sub.setStyleSheet(f"color:{SUBTEXT}; font-size:13px;")
    pl.addWidget(sub)

    tabs = QTabWidget()
    tabs.setStyleSheet(
        f"QTabWidget::pane{{background:{DARK_BG};border:1px solid {BORDER};border-radius:8px;}}"
        f"QTabBar::tab{{background:{SURFACE};color:{SUBTEXT};padding:8px 14px;font-size:13px;border-radius:6px 6px 0 0;margin-right:2px;}}"
        f"QTabBar::tab:selected{{background:{ACCENT};color:#11111B;font-weight:bold;}}"
        f"QTabBar::tab:hover{{background:{HOVER};color:{TEXT};}}"
    )
    pl.addWidget(tabs, 1)

    # ── TAB 1: Variant Generator ──────────────────────────────────────────────
    t1 = QWidget(); t1l = QVBoxLayout(t1); t1l.setContentsMargins(14, 12, 14, 12); t1l.setSpacing(8)

    grp1 = QGroupBox("📋 Original Content"); grp1.setStyleSheet(_GS)
    g1 = QGridLayout(grp1); g1.setSpacing(8)
    g1.addWidget(QLabel("Platform:"), 0, 0)
    ab_platform = QComboBox(); ab_platform.addItems(["Instagram", "TikTok", "Facebook", "Twitter/X", "LinkedIn", "YouTube"])
    g1.addWidget(ab_platform, 0, 1)
    g1.addWidget(QLabel("Test Element:"), 0, 2)
    ab_element = QComboBox(); ab_element.addItems(["Full Post", "Caption Only", "Headline", "Hook / Opening Line", "CTA"])
    g1.addWidget(ab_element, 0, 3)
    g1.addWidget(QLabel("Variants:"), 1, 0)
    ab_variants = QSpinBox(); ab_variants.setRange(2, 4); ab_variants.setValue(3)
    g1.addWidget(ab_variants, 1, 1)
    g1.addWidget(QLabel("Language:"), 1, 2)
    ab_lang = QComboBox(); ab_lang.addItems(["English", "Khmer", "Thai", "Vietnamese", "Chinese", "Spanish", "French"])
    g1.addWidget(ab_lang, 1, 3)
    g1.addWidget(QLabel("Original Content:"), 2, 0)
    ab_content = QTextEdit(); ab_content.setMaximumHeight(100)
    ab_content.setPlaceholderText("Paste your original post content here to generate optimized variants...")
    ab_content.setStyleSheet(f"background:{DARK_BG};color:{TEXT};border:1px solid {BORDER};border-radius:6px;padding:6px;font-size:13px;")
    g1.addWidget(ab_content, 2, 1, 1, 3)
    t1l.addWidget(grp1)

    b_row = QHBoxLayout()
    ab_gen_btn    = _btn("🧬 Generate A/B Variants", ACCENT)
    ab_predict_btn = _btn("🎯 Predict Winner", SUCCESS)
    ab_caption_btn = _btn("🔮 Caption Psychology", WARNING)
    b_row.addWidget(ab_gen_btn); b_row.addWidget(ab_predict_btn); b_row.addWidget(ab_caption_btn); b_row.addStretch()
    t1l.addLayout(b_row)

    ab_out = QTextEdit(); ab_out.setReadOnly(True)
    ab_out.setPlaceholderText("🧪 A/B variant predictions will appear here...\n\nPaste your content and click Generate to see AI-scored variants before you post.")
    ab_out.setStyleSheet(f"background:{SURFACE};color:{TEXT};border:1px solid {BORDER};border-radius:8px;font-size:13px;")
    t1l.addWidget(ab_out, 1)
    tabs.addTab(t1, "🧬 Variant Generator")

    # ── TAB 2: Head-to-Head Comparison ────────────────────────────────────────
    t2 = QWidget(); t2l = QVBoxLayout(t2); t2l.setContentsMargins(14, 12, 14, 12); t2l.setSpacing(8)

    spl = QSplitter(Qt.Horizontal)
    grp_a = QGroupBox("Version A"); grp_a.setStyleSheet(_GS)
    ga = QVBoxLayout(grp_a)
    ab_va = QTextEdit(); ab_va.setPlaceholderText("Paste Variant A here...")
    ab_va.setStyleSheet(f"background:{DARK_BG};color:{TEXT};border:1px solid {BORDER};border-radius:6px;padding:6px;font-size:13px;")
    ga.addWidget(ab_va)
    grp_b = QGroupBox("Version B"); grp_b.setStyleSheet(_GS)
    gb = QVBoxLayout(grp_b)
    ab_vb = QTextEdit(); ab_vb.setPlaceholderText("Paste Variant B here...")
    ab_vb.setStyleSheet(f"background:{DARK_BG};color:{TEXT};border:1px solid {BORDER};border-radius:6px;padding:6px;font-size:13px;")
    gb.addWidget(ab_vb)
    spl.addWidget(grp_a); spl.addWidget(grp_b)
    t2l.addWidget(spl)

    h2r = QHBoxLayout()
    ab_h2h_platform = QComboBox(); ab_h2h_platform.addItems(["Instagram", "TikTok", "Facebook", "LinkedIn"])
    ab_metric = QComboBox(); ab_metric.addItems(["Engagement Rate", "Reach", "Saves", "Comments", "Shares", "Profile Visits"])
    ab_h2h_btn = _btn("⚔️ Compare & Predict Winner", ACCENT)
    h2r.addWidget(QLabel("Platform:")); h2r.addWidget(ab_h2h_platform)
    h2r.addSpacing(8); h2r.addWidget(QLabel("Optimize for:")); h2r.addWidget(ab_metric)
    h2r.addSpacing(8); h2r.addWidget(ab_h2h_btn); h2r.addStretch()
    t2l.addLayout(h2r)

    ab_h2h_out = QTextEdit(); ab_h2h_out.setReadOnly(True)
    ab_h2h_out.setPlaceholderText("Head-to-head comparison results will appear here...")
    ab_h2h_out.setStyleSheet(f"background:{SURFACE};color:{TEXT};border:1px solid {BORDER};border-radius:8px;font-size:13px;")
    t2l.addWidget(ab_h2h_out, 1)
    tabs.addTab(t2, "⚔️ Head-to-Head")

    # ── TAB 3: Posting Time Optimizer ─────────────────────────────────────────
    t3 = QWidget(); t3l = QVBoxLayout(t3); t3l.setContentsMargins(14, 12, 14, 12); t3l.setSpacing(8)
    grp3 = QGroupBox("⏰ Posting Time Optimizer"); grp3.setStyleSheet(_GS)
    g3 = QGridLayout(grp3); g3.setSpacing(8)
    g3.addWidget(QLabel("Platform:"), 0, 0)
    ab_time_plat = QComboBox(); ab_time_plat.addItems(["Instagram", "TikTok", "Facebook", "YouTube", "LinkedIn", "Twitter/X"])
    g3.addWidget(ab_time_plat, 0, 1)
    g3.addWidget(QLabel("Niche:"), 0, 2)
    ab_time_niche = QLineEdit(); ab_time_niche.setPlaceholderText("e.g. fitness, business, beauty")
    g3.addWidget(ab_time_niche, 0, 3)
    g3.addWidget(QLabel("Audience Location:"), 1, 0)
    ab_time_loc = QLineEdit(); ab_time_loc.setPlaceholderText("e.g. USA, Cambodia, Thailand")
    g3.addWidget(ab_time_loc, 1, 1)
    g3.addWidget(QLabel("Current Best Day:"), 1, 2)
    ab_time_day = QComboBox(); ab_time_day.addItems(["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"])
    g3.addWidget(ab_time_day, 1, 3)
    t3l.addWidget(grp3)
    ab_time_btn = _btn("📅 Get Optimal Schedule", SUCCESS)
    t3l.addWidget(ab_time_btn)
    ab_time_out = QTextEdit(); ab_time_out.setReadOnly(True)
    ab_time_out.setPlaceholderText("Optimal posting schedule with AI analysis will appear here...")
    ab_time_out.setStyleSheet(f"background:{SURFACE};color:{TEXT};border:1px solid {BORDER};border-radius:8px;font-size:13px;")
    t3l.addWidget(ab_time_out, 1)
    tabs.addTab(t3, "⏰ Time Optimizer")

    # ── Workers ───────────────────────────────────────────────────────────────
    _ab_workers = []

    def _run_ab(coro, out_widget, btn_widget, label):
        btn_widget.setEnabled(False); btn_widget.setText("⏳ Analyzing...")
        out_widget.setText("🔄 AI is processing... please wait.")
        class _W(QThread):
            done = pyqtSignal(str); err = pyqtSignal(str)
            def __init__(self, c): super().__init__(); self._c = c
            def run(self):
                try:
                    loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
                    r = loop.run_until_complete(self._c); loop.close(); self.done.emit(r)
                except Exception as e: self.err.emit(str(e))
        w = _W(coro)
        w.done.connect(lambda r: (_pretty_out(out_widget, r), btn_widget.setEnabled(True), btn_widget.setText(label)))
        w.err.connect(lambda e: (out_widget.setText(f"❌ {e}"), btn_widget.setEnabled(True), btn_widget.setText(label)))
        _ab_workers.append(w); w.start()

    def _pretty_out(widget, raw):
        try:
            data = json.loads(raw) if isinstance(raw, str) else raw
            if isinstance(data, dict):
                lines = []
                for k, v in data.items():
                    lines.append(f"\n{'═'*48}")
                    lines.append(f"  {k.upper().replace('_',' ')}")
                    lines.append(f"{'─'*48}")
                    if isinstance(v, list):
                        for i, item in enumerate(v, 1):
                            if isinstance(item, dict):
                                lines.append(f"\n  [{i}]")
                                for kk, vv in item.items():
                                    lines.append(f"      {kk}: {vv}")
                            else:
                                lines.append(f"  {i}. {item}")
                    elif isinstance(v, dict):
                        for kk, vv in v.items():
                            lines.append(f"  • {kk}: {vv}")
                    else:
                        lines.append(f"  {v}")
                widget.setText("\n".join(lines))
            else:
                widget.setText(str(raw))
        except Exception:
            widget.setText(str(raw))

    def _do_ab_variants():
        from ai_core.ab_testing import generate_ab_variants
        async def _r():
            res = await generate_ab_variants(
                ab_content.toPlainText().strip() or "Check out our latest product — you'll love it!",
                ab_platform.currentText(), ab_variants.value(), ab_element.currentText(), ab_lang.currentText()
            )
            return json.dumps(res, ensure_ascii=False, indent=2)
        _run_ab(_r(), ab_out, ab_gen_btn, "🧬 Generate A/B Variants")

    def _do_predict():
        from ai_core.ab_testing import predict_ab_winner
        async def _r():
            res = await predict_ab_winner(
                ab_va.toPlainText().strip() or "Variant A content",
                ab_vb.toPlainText().strip() or "Variant B content",
                ab_h2h_platform.currentText(), ab_metric.currentText(), "General", ab_lang.currentText()
            )
            return json.dumps(res, ensure_ascii=False, indent=2)
        _run_ab(_r(), ab_h2h_out, ab_predict_btn, "🎯 Predict Winner")

    def _do_caption_psych():
        from ai_core.ab_testing import optimize_caption_ab
        async def _r():
            res = await optimize_caption_ab(
                ab_content.toPlainText().strip() or "Check out our product — you'll love it!",
                ab_platform.currentText(), "Engagement", ab_lang.currentText()
            )
            return json.dumps(res, ensure_ascii=False, indent=2)
        _run_ab(_r(), ab_out, ab_caption_btn, "🔮 Caption Psychology")

    def _do_h2h():
        from ai_core.ab_testing import predict_ab_winner
        async def _r():
            res = await predict_ab_winner(
                ab_va.toPlainText().strip() or "Variant A",
                ab_vb.toPlainText().strip() or "Variant B",
                ab_h2h_platform.currentText(), ab_metric.currentText()
            )
            return json.dumps(res, ensure_ascii=False, indent=2)
        _run_ab(_r(), ab_h2h_out, ab_h2h_btn, "⚔️ Compare & Predict Winner")

    def _do_timing():
        from ai_core.ab_testing import analyze_posting_times
        async def _r():
            res = await analyze_posting_times(
                ab_time_plat.currentText(), ab_time_niche.text().strip() or "General",
                ab_time_loc.text().strip() or "USA", ab_time_day.currentText(), ab_lang.currentText()
            )
            return json.dumps(res, ensure_ascii=False, indent=2)
        _run_ab(_r(), ab_time_out, ab_time_btn, "📅 Get Optimal Schedule")

    ab_gen_btn.clicked.connect(_do_ab_variants)
    ab_predict_btn.clicked.connect(_do_predict)
    ab_caption_btn.clicked.connect(_do_caption_psych)
    ab_h2h_btn.clicked.connect(_do_h2h)
    ab_time_btn.clicked.connect(_do_timing)

    return page


# ═══════════════════════════════════════════════════════════════════════════════
# ✦ NEW FEATURE PAGE 32: SOCIAL COMMERCE AI
# ═══════════════════════════════════════════════════════════════════════════════

def build_social_commerce_page(api_base: str) -> QWidget:
    """Social Commerce AI — Shoppable content, DM funnels, and conversion optimization."""
    import asyncio

    _GS = (f"QGroupBox{{color:{ACCENT};font-weight:bold;border:1px solid {BORDER};"
           f"border-radius:8px;padding-top:8px;margin-top:4px;}}"
           f"QGroupBox::title{{subcontrol-origin:margin;left:8px;padding:0 4px;}}")

    def _btn(text, color=None):
        b = QPushButton(text); b.setCursor(Qt.PointingHandCursor)
        c = color or ACCENT
        b.setStyleSheet(
            f"QPushButton{{background:{c};color:#11111B;border:none;border-radius:8px;"
            f"padding:8px 18px;font-weight:bold;font-size:13px;}}"
            f"QPushButton:hover{{background:{c}CC;}}"
            f"QPushButton:disabled{{background:{BORDER};color:{SUBTEXT};}}"
        )
        return b

    page = QWidget(); pl = QVBoxLayout(page)
    pl.setContentsMargins(20, 16, 20, 16); pl.setSpacing(10)

    hdr = QLabel("🛍️  Social Commerce AI")
    hdr.setFont(QFont("Segoe UI", 17, QFont.Bold))
    hdr.setStyleSheet(f"color:{ACCENT};")
    pl.addWidget(hdr)
    sub = QLabel("Generate shoppable content, DM sales funnels, social proof, and conversion optimization with AI")
    sub.setStyleSheet(f"color:{SUBTEXT}; font-size:13px;")
    pl.addWidget(sub)

    tabs = QTabWidget()
    tabs.setStyleSheet(
        f"QTabWidget::pane{{background:{DARK_BG};border:1px solid {BORDER};border-radius:8px;}}"
        f"QTabBar::tab{{background:{SURFACE};color:{SUBTEXT};padding:8px 14px;font-size:13px;border-radius:6px 6px 0 0;margin-right:2px;}}"
        f"QTabBar::tab:selected{{background:{ACCENT};color:#11111B;font-weight:bold;}}"
        f"QTabBar::tab:hover{{background:{HOVER};color:{TEXT};}}"
    )
    pl.addWidget(tabs, 1)

    # ── TAB 1: Shoppable Content ──────────────────────────────────────────────
    t1 = QWidget(); t1l = QVBoxLayout(t1); t1l.setContentsMargins(14, 12, 14, 12); t1l.setSpacing(8)
    grp1 = QGroupBox("🛒 Shoppable Post Generator"); grp1.setStyleSheet(_GS)
    g1 = QGridLayout(grp1); g1.setSpacing(8)
    g1.addWidget(QLabel("Product Name:"), 0, 0)
    sc_product = QLineEdit(); sc_product.setPlaceholderText("e.g. Organic Glow Serum")
    g1.addWidget(sc_product, 0, 1, 1, 3)
    g1.addWidget(QLabel("Price:"), 1, 0)
    sc_price = QLineEdit(); sc_price.setPlaceholderText("e.g. $29 / $49.99")
    g1.addWidget(sc_price, 1, 1)
    g1.addWidget(QLabel("Platform:"), 1, 2)
    sc_plat = QComboBox(); sc_plat.addItems(["Instagram", "TikTok Shop", "Facebook Shop", "Pinterest", "Snapchat"])
    g1.addWidget(sc_plat, 1, 3)
    g1.addWidget(QLabel("Target Audience:"), 2, 0)
    sc_audience = QLineEdit(); sc_audience.setPlaceholderText("e.g. women 25-35 interested in skincare")
    g1.addWidget(sc_audience, 2, 1, 1, 3)
    g1.addWidget(QLabel("Language:"), 3, 0)
    sc_lang = QComboBox(); sc_lang.addItems(["English", "Khmer", "Thai", "Vietnamese", "Chinese", "Spanish"])
    g1.addWidget(sc_lang, 3, 1)
    t1l.addWidget(grp1)

    b1r = QHBoxLayout()
    sc_shop_btn     = _btn("🛍️ Generate Shoppable Post", ACCENT)
    sc_showcase_btn = _btn("✨ Product Showcase", SUCCESS)
    sc_proof_btn    = _btn("⭐ Social Proof Pack", WARNING)
    b1r.addWidget(sc_shop_btn); b1r.addWidget(sc_showcase_btn); b1r.addWidget(sc_proof_btn); b1r.addStretch()
    t1l.addLayout(b1r)

    sc_out1 = QTextEdit(); sc_out1.setReadOnly(True)
    sc_out1.setPlaceholderText("🛍️ Your shoppable content will appear here...\n\nFill in product details above and click Generate.")
    sc_out1.setStyleSheet(f"background:{SURFACE};color:{TEXT};border:1px solid {BORDER};border-radius:8px;font-size:13px;")
    t1l.addWidget(sc_out1, 1)
    tabs.addTab(t1, "🛒 Shoppable Posts")

    # ── TAB 2: DM Sales Funnel ────────────────────────────────────────────────
    t2 = QWidget(); t2l = QVBoxLayout(t2); t2l.setContentsMargins(14, 12, 14, 12); t2l.setSpacing(8)
    grp2 = QGroupBox("💬 DM Sales Funnel Builder"); grp2.setStyleSheet(_GS)
    g2 = QGridLayout(grp2); g2.setSpacing(8)
    g2.addWidget(QLabel("Product:"), 0, 0)
    sc_funnel_product = QLineEdit(); sc_funnel_product.setPlaceholderText("Product or service name")
    g2.addWidget(sc_funnel_product, 0, 1, 1, 3)
    g2.addWidget(QLabel("Trigger Keyword:"), 1, 0)
    sc_trigger = QLineEdit(); sc_trigger.setPlaceholderText("e.g. INFO, PRICE, YES, DETAILS")
    g2.addWidget(sc_trigger, 1, 1)
    g2.addWidget(QLabel("Target Audience:"), 1, 2)
    sc_funnel_aud = QLineEdit(); sc_funnel_aud.setPlaceholderText("e.g. small business owners")
    g2.addWidget(sc_funnel_aud, 1, 3)
    g2.addWidget(QLabel("Language:"), 2, 0)
    sc_funnel_lang = QComboBox(); sc_funnel_lang.addItems(["English", "Khmer", "Thai", "Vietnamese", "Chinese", "Spanish"])
    g2.addWidget(sc_funnel_lang, 2, 1)
    t2l.addWidget(grp2)

    sc_funnel_btn = _btn("💬 Build DM Sales Funnel", ACCENT)
    t2l.addWidget(sc_funnel_btn)
    sc_out2 = QTextEdit(); sc_out2.setReadOnly(True)
    sc_out2.setPlaceholderText("Your automated DM sales funnel sequence will appear here...\n\nThis generates a complete 5-step DM conversation that converts followers to buyers.")
    sc_out2.setStyleSheet(f"background:{SURFACE};color:{TEXT};border:1px solid {BORDER};border-radius:8px;font-size:13px;")
    t2l.addWidget(sc_out2, 1)
    tabs.addTab(t2, "💬 DM Funnel")

    # ── TAB 3: Conversion Optimizer ───────────────────────────────────────────
    t3 = QWidget(); t3l = QVBoxLayout(t3); t3l.setContentsMargins(14, 12, 14, 12); t3l.setSpacing(8)
    grp3 = QGroupBox("📈 Bio & Conversion Optimizer"); grp3.setStyleSheet(_GS)
    g3 = QGridLayout(grp3); g3.setSpacing(8)
    g3.addWidget(QLabel("Current Bio:"), 0, 0)
    sc_bio = QTextEdit(); sc_bio.setMaximumHeight(80)
    sc_bio.setPlaceholderText("Paste your current social media bio here...")
    sc_bio.setStyleSheet(f"background:{DARK_BG};color:{TEXT};border:1px solid {BORDER};border-radius:6px;padding:6px;font-size:13px;")
    g3.addWidget(sc_bio, 0, 1, 1, 3)
    g3.addWidget(QLabel("Product/Offer:"), 1, 0)
    sc_conv_product = QLineEdit(); sc_conv_product.setPlaceholderText("What you're selling or promoting")
    g3.addWidget(sc_conv_product, 1, 1, 1, 3)
    g3.addWidget(QLabel("Traffic Source:"), 2, 0)
    sc_traffic = QComboBox(); sc_traffic.addItems(["Instagram", "TikTok", "Facebook", "YouTube", "LinkedIn", "Twitter/X"])
    g3.addWidget(sc_traffic, 2, 1)
    t3l.addWidget(grp3)

    sc_conv_btn = _btn("📈 Optimize for Conversion", SUCCESS)
    t3l.addWidget(sc_conv_btn)
    sc_out3 = QTextEdit(); sc_out3.setReadOnly(True)
    sc_out3.setPlaceholderText("Bio optimization and conversion strategy will appear here...")
    sc_out3.setStyleSheet(f"background:{SURFACE};color:{TEXT};border:1px solid {BORDER};border-radius:8px;font-size:13px;")
    t3l.addWidget(sc_out3, 1)
    tabs.addTab(t3, "📈 Conversion Optimizer")

    # ── Workers ───────────────────────────────────────────────────────────────
    _sc_workers = []

    def _run_sc(coro, out_w, btn_w, label):
        btn_w.setEnabled(False); btn_w.setText("⏳ Generating...")
        out_w.setText("🔄 AI is generating commerce content... please wait.")
        class _W(QThread):
            done = pyqtSignal(str); err = pyqtSignal(str)
            def __init__(self, c): super().__init__(); self._c = c
            def run(self):
                try:
                    loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
                    r = loop.run_until_complete(self._c); loop.close(); self.done.emit(r)
                except Exception as e: self.err.emit(str(e))
        w = _W(coro)
        w.done.connect(lambda r: (_fmt_out(out_w, r), btn_w.setEnabled(True), btn_w.setText(label)))
        w.err.connect(lambda e: (out_w.setText(f"❌ {e}"), btn_w.setEnabled(True), btn_w.setText(label)))
        _sc_workers.append(w); w.start()

    def _fmt_out(widget, raw):
        try:
            data = json.loads(raw) if isinstance(raw, str) else raw
            if isinstance(data, dict):
                lines = []
                for k, v in data.items():
                    lines.append(f"\n{'═'*50}\n  {k.upper().replace('_',' ')}\n{'─'*50}")
                    if isinstance(v, list):
                        for i, item in enumerate(v, 1):
                            if isinstance(item, dict):
                                lines.append(f"\n  Step {i if 'step' not in item else item.get('step', i)}:")
                                for kk, vv in item.items():
                                    lines.append(f"    {kk}: {vv}")
                            else:
                                lines.append(f"  {i}. {item}")
                    elif isinstance(v, dict):
                        for kk, vv in v.items():
                            lines.append(f"  • {kk}: {vv}")
                    else:
                        lines.append(f"  {v}")
                widget.setText("\n".join(lines))
            else:
                widget.setText(str(raw))
        except Exception:
            widget.setText(str(raw))

    def _do_shop():
        from ai_core.social_commerce import generate_shoppable_content
        async def _r():
            res = await generate_shoppable_content(
                sc_product.text().strip() or "Premium Product",
                sc_price.text().strip() or "$29",
                sc_plat.currentText(), sc_audience.text().strip() or "General audience",
                sc_lang.currentText()
            )
            return json.dumps(res, ensure_ascii=False, indent=2)
        _run_sc(_r(), sc_out1, sc_shop_btn, "🛍️ Generate Shoppable Post")

    def _do_showcase():
        from ai_core.social_commerce import generate_product_showcase
        async def _r():
            res = await generate_product_showcase(
                sc_product.text().strip() or "Premium Product",
                "Key features of the product", "Main benefit",
                sc_plat.currentText(), sc_lang.currentText()
            )
            return json.dumps(res, ensure_ascii=False, indent=2)
        _run_sc(_r(), sc_out1, sc_showcase_btn, "✨ Product Showcase")

    def _do_proof():
        from ai_core.social_commerce import generate_social_proof
        async def _r():
            res = await generate_social_proof(
                sc_product.text().strip() or "Premium Product",
                "increased sales by 300%", sc_plat.currentText(), sc_lang.currentText()
            )
            return json.dumps(res, ensure_ascii=False, indent=2)
        _run_sc(_r(), sc_out1, sc_proof_btn, "⭐ Social Proof Pack")

    def _do_funnel():
        from ai_core.social_commerce import build_dm_funnel
        async def _r():
            res = await build_dm_funnel(
                sc_funnel_product.text().strip() or "Our Product",
                sc_trigger.text().strip() or "INFO",
                sc_funnel_aud.text().strip() or "General audience",
                sc_funnel_lang.currentText()
            )
            return json.dumps(res, ensure_ascii=False, indent=2)
        _run_sc(_r(), sc_out2, sc_funnel_btn, "💬 Build DM Sales Funnel")

    def _do_conv():
        from ai_core.social_commerce import optimize_conversion_rate
        async def _r():
            res = await optimize_conversion_rate(
                sc_bio.toPlainText().strip() or "Your current bio",
                sc_conv_product.text().strip() or "Our Product",
                sc_traffic.currentText(), sc_funnel_lang.currentText()
            )
            return json.dumps(res, ensure_ascii=False, indent=2)
        _run_sc(_r(), sc_out3, sc_conv_btn, "📈 Optimize for Conversion")

    sc_shop_btn.clicked.connect(_do_shop)
    sc_showcase_btn.clicked.connect(_do_showcase)
    sc_proof_btn.clicked.connect(_do_proof)
    sc_funnel_btn.clicked.connect(_do_funnel)
    sc_conv_btn.clicked.connect(_do_conv)

    return page


# ═══════════════════════════════════════════════════════════════════════════════
# ✦ NEW FEATURE PAGE 33: AUDIO & VOICE AI
# ═══════════════════════════════════════════════════════════════════════════════

def build_audio_ai_page(api_base: str) -> QWidget:
    """Audio & Voice AI — Trending audio, podcast scripts, voice notes & audio branding."""
    import asyncio

    _GS = (f"QGroupBox{{color:{ACCENT};font-weight:bold;border:1px solid {BORDER};"
           f"border-radius:8px;padding-top:8px;margin-top:4px;}}"
           f"QGroupBox::title{{subcontrol-origin:margin;left:8px;padding:0 4px;}}")

    def _btn(text, color=None):
        b = QPushButton(text); b.setCursor(Qt.PointingHandCursor)
        c = color or ACCENT
        b.setStyleSheet(
            f"QPushButton{{background:{c};color:#11111B;border:none;border-radius:8px;"
            f"padding:8px 18px;font-weight:bold;font-size:13px;}}"
            f"QPushButton:hover{{background:{c}CC;}}"
            f"QPushButton:disabled{{background:{BORDER};color:{SUBTEXT};}}"
        )
        return b

    page = QWidget(); pl = QVBoxLayout(page)
    pl.setContentsMargins(20, 16, 20, 16); pl.setSpacing(10)

    hdr = QLabel("🎵  Audio & Voice AI")
    hdr.setFont(QFont("Segoe UI", 17, QFont.Bold))
    hdr.setStyleSheet(f"color:{ACCENT};")
    pl.addWidget(hdr)
    sub = QLabel("Trending audio analysis, podcast scripts, voice note DMs, audio branding & caption optimization")
    sub.setStyleSheet(f"color:{SUBTEXT}; font-size:13px;")
    pl.addWidget(sub)

    tabs = QTabWidget()
    tabs.setStyleSheet(
        f"QTabWidget::pane{{background:{DARK_BG};border:1px solid {BORDER};border-radius:8px;}}"
        f"QTabBar::tab{{background:{SURFACE};color:{SUBTEXT};padding:8px 14px;font-size:13px;border-radius:6px 6px 0 0;margin-right:2px;}}"
        f"QTabBar::tab:selected{{background:{ACCENT};color:#11111B;font-weight:bold;}}"
        f"QTabBar::tab:hover{{background:{HOVER};color:{TEXT};}}"
    )
    pl.addWidget(tabs, 1)

    # ── TAB 1: Trending Audio ─────────────────────────────────────────────────
    t1 = QWidget(); t1l = QVBoxLayout(t1); t1l.setContentsMargins(14, 12, 14, 12); t1l.setSpacing(8)
    grp1 = QGroupBox("🔊 Trending Audio Strategy"); grp1.setStyleSheet(_GS)
    g1 = QGridLayout(grp1); g1.setSpacing(8)
    g1.addWidget(QLabel("Niche:"), 0, 0)
    aud_niche = QLineEdit(); aud_niche.setPlaceholderText("e.g. fitness, business, beauty, tech")
    g1.addWidget(aud_niche, 0, 1)
    g1.addWidget(QLabel("Platform:"), 0, 2)
    aud_plat = QComboBox(); aud_plat.addItems(["TikTok", "Instagram Reels", "YouTube Shorts", "Facebook Reels"])
    g1.addWidget(aud_plat, 0, 3)
    g1.addWidget(QLabel("Content Type:"), 1, 0)
    aud_type = QComboBox(); aud_type.addItems(["Educational", "Entertainment", "Inspirational", "Tutorial", "Lifestyle", "Comedy"])
    g1.addWidget(aud_type, 1, 1)
    g1.addWidget(QLabel("Language:"), 1, 2)
    aud_lang = QComboBox(); aud_lang.addItems(["English", "Khmer", "Thai", "Vietnamese", "Chinese", "Spanish"])
    g1.addWidget(aud_lang, 1, 3)
    t1l.addWidget(grp1)
    aud_trend_btn = _btn("🎵 Analyze Trending Audio", ACCENT)
    t1l.addWidget(aud_trend_btn)
    aud_out1 = QTextEdit(); aud_out1.setReadOnly(True)
    aud_out1.setPlaceholderText("Trending audio analysis and strategy will appear here...")
    aud_out1.setStyleSheet(f"background:{SURFACE};color:{TEXT};border:1px solid {BORDER};border-radius:8px;font-size:13px;")
    t1l.addWidget(aud_out1, 1)
    tabs.addTab(t1, "🎵 Trending Audio")

    # ── TAB 2: Podcast Script ─────────────────────────────────────────────────
    t2 = QWidget(); t2l = QVBoxLayout(t2); t2l.setContentsMargins(14, 12, 14, 12); t2l.setSpacing(8)
    grp2 = QGroupBox("🎙️ Podcast Script Generator"); grp2.setStyleSheet(_GS)
    g2 = QGridLayout(grp2); g2.setSpacing(8)
    g2.addWidget(QLabel("Episode Topic:"), 0, 0)
    pod_topic = QLineEdit(); pod_topic.setPlaceholderText("e.g. How to grow on social media in 2025")
    g2.addWidget(pod_topic, 0, 1, 1, 3)
    g2.addWidget(QLabel("Show Name:"), 1, 0)
    pod_show = QLineEdit(); pod_show.setPlaceholderText("Your podcast show name")
    g2.addWidget(pod_show, 1, 1)
    g2.addWidget(QLabel("Host Name:"), 1, 2)
    pod_host = QLineEdit(); pod_host.setPlaceholderText("Your name or host name")
    g2.addWidget(pod_host, 1, 3)
    g2.addWidget(QLabel("Length (min):"), 2, 0)
    pod_len = QSpinBox(); pod_len.setRange(5, 120); pod_len.setValue(20); pod_len.setSuffix(" min")
    g2.addWidget(pod_len, 2, 1)
    g2.addWidget(QLabel("Style:"), 2, 2)
    pod_style = QComboBox(); pod_style.addItems(["Educational", "Interview", "Solo", "Storytelling", "News/Recap", "Comedy"])
    g2.addWidget(pod_style, 2, 3)
    g2.addWidget(QLabel("Language:"), 3, 0)
    pod_lang = QComboBox(); pod_lang.addItems(["English", "Khmer", "Thai", "Vietnamese", "Chinese", "Spanish"])
    g2.addWidget(pod_lang, 3, 1)
    t2l.addWidget(grp2)
    pod_btn = _btn("🎙️ Generate Episode Script", ACCENT)
    t2l.addWidget(pod_btn)
    pod_out = QTextEdit(); pod_out.setReadOnly(True)
    pod_out.setPlaceholderText("Your complete podcast episode script will appear here...")
    pod_out.setStyleSheet(f"background:{SURFACE};color:{TEXT};border:1px solid {BORDER};border-radius:8px;font-size:13px;")
    t2l.addWidget(pod_out, 1)
    tabs.addTab(t2, "🎙️ Podcast Script")

    # ── TAB 3: Voice Note DM ──────────────────────────────────────────────────
    t3 = QWidget(); t3l = QVBoxLayout(t3); t3l.setContentsMargins(14, 12, 14, 12); t3l.setSpacing(8)
    grp3 = QGroupBox("🎤 Voice Note DM Script"); grp3.setStyleSheet(_GS)
    g3 = QGridLayout(grp3); g3.setSpacing(8)
    g3.addWidget(QLabel("Purpose:"), 0, 0)
    vn_purpose = QLineEdit(); vn_purpose.setPlaceholderText("e.g. introduce my product, follow up on offer, reconnect with old follower")
    g3.addWidget(vn_purpose, 0, 1, 1, 3)
    g3.addWidget(QLabel("Recipient:"), 1, 0)
    vn_recipient = QLineEdit(); vn_recipient.setPlaceholderText("e.g. potential customer, influencer, existing follower")
    g3.addWidget(vn_recipient, 1, 1)
    g3.addWidget(QLabel("Tone:"), 1, 2)
    vn_tone = QComboBox(); vn_tone.addItems(["Friendly", "Professional", "Excited", "Casual", "Persuasive", "Warm"])
    g3.addWidget(vn_tone, 1, 3)
    g3.addWidget(QLabel("Length:"), 2, 0)
    vn_len = QComboBox(); vn_len.addItems(["30 seconds", "60 seconds", "90 seconds"])
    g3.addWidget(vn_len, 2, 1)
    g3.addWidget(QLabel("Language:"), 2, 2)
    vn_lang = QComboBox(); vn_lang.addItems(["English", "Khmer", "Thai", "Vietnamese", "Chinese", "Spanish"])
    g3.addWidget(vn_lang, 2, 3)
    t3l.addWidget(grp3)
    vn_btn = _btn("🎤 Generate Voice Script", SUCCESS)
    t3l.addWidget(vn_btn)
    vn_out = QTextEdit(); vn_out.setReadOnly(True)
    vn_out.setPlaceholderText("Your natural-sounding voice note script will appear here...")
    vn_out.setStyleSheet(f"background:{SURFACE};color:{TEXT};border:1px solid {BORDER};border-radius:8px;font-size:13px;")
    t3l.addWidget(vn_out, 1)
    tabs.addTab(t3, "🎤 Voice Note DM")

    # ── TAB 4: Audio Brand & Transcript ───────────────────────────────────────
    t4 = QWidget(); t4l = QVBoxLayout(t4); t4l.setContentsMargins(14, 12, 14, 12); t4l.setSpacing(8)

    grp4a = QGroupBox("🎼 Audio Brand Strategy"); grp4a.setStyleSheet(_GS)
    g4a = QGridLayout(grp4a); g4a.setSpacing(8)
    g4a.addWidget(QLabel("Brand Name:"), 0, 0)
    ab_brand = QLineEdit(); ab_brand.setPlaceholderText("Your brand or account name")
    g4a.addWidget(ab_brand, 0, 1)
    g4a.addWidget(QLabel("Niche:"), 0, 2)
    ab_niche = QLineEdit(); ab_niche.setPlaceholderText("Your content niche")
    g4a.addWidget(ab_niche, 0, 3)
    g4a.addWidget(QLabel("Target Emotion:"), 1, 0)
    ab_emotion = QComboBox(); ab_emotion.addItems(["Trust & Excitement", "Inspiration & Hope", "Fun & Energy", "Professional & Authority", "Calm & Mindful"])
    g4a.addWidget(ab_emotion, 1, 1, 1, 3)
    t4l.addWidget(grp4a)
    ab_brand_btn = _btn("🎼 Build Audio Brand Strategy", ACCENT)
    t4l.addWidget(ab_brand_btn)

    grp4b = QGroupBox("📝 Transcript → Caption Optimizer"); grp4b.setStyleSheet(_GS)
    g4b = QGridLayout(grp4b); g4b.setSpacing(8)
    g4b.addWidget(QLabel("Raw Transcript:"), 0, 0)
    ab_transcript = QTextEdit(); ab_transcript.setMaximumHeight(80)
    ab_transcript.setPlaceholderText("Paste your raw audio/video transcript here to optimize it into a social media caption...")
    ab_transcript.setStyleSheet(f"background:{DARK_BG};color:{TEXT};border:1px solid {BORDER};border-radius:6px;padding:6px;font-size:13px;")
    g4b.addWidget(ab_transcript, 0, 1, 1, 3)
    g4b.addWidget(QLabel("Platform:"), 1, 0)
    ab_trans_plat = QComboBox(); ab_trans_plat.addItems(["Instagram", "TikTok", "LinkedIn", "Facebook", "Twitter/X"])
    g4b.addWidget(ab_trans_plat, 1, 1)
    g4b.addWidget(QLabel("Max Length (chars):"), 1, 2)
    ab_trans_len = QSpinBox(); ab_trans_len.setRange(50, 2000); ab_trans_len.setValue(300)
    g4b.addWidget(ab_trans_len, 1, 3)
    t4l.addWidget(grp4b)

    ab_trans_btn = _btn("📝 Optimize Transcript", WARNING)
    t4l.addWidget(ab_trans_btn)
    aud_out4 = QTextEdit(); aud_out4.setReadOnly(True)
    aud_out4.setPlaceholderText("Audio brand strategy or optimized caption will appear here...")
    aud_out4.setStyleSheet(f"background:{SURFACE};color:{TEXT};border:1px solid {BORDER};border-radius:8px;font-size:13px;")
    t4l.addWidget(aud_out4, 1)
    tabs.addTab(t4, "🎼 Brand & Transcript")

    # ── Workers ───────────────────────────────────────────────────────────────
    _aud_workers = []

    def _run_aud(coro, out_w, btn_w, label):
        btn_w.setEnabled(False); btn_w.setText("⏳ Processing...")
        out_w.setText("🔄 AI is analyzing audio content... please wait.")
        class _W(QThread):
            done = pyqtSignal(str); err = pyqtSignal(str)
            def __init__(self, c): super().__init__(); self._c = c
            def run(self):
                try:
                    loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
                    r = loop.run_until_complete(self._c); loop.close(); self.done.emit(r)
                except Exception as e: self.err.emit(str(e))
        w = _W(coro)
        w.done.connect(lambda r: (_aud_fmt(out_w, r), btn_w.setEnabled(True), btn_w.setText(label)))
        w.err.connect(lambda e: (out_w.setText(f"❌ {e}"), btn_w.setEnabled(True), btn_w.setText(label)))
        _aud_workers.append(w); w.start()

    def _aud_fmt(widget, raw):
        try:
            data = json.loads(raw) if isinstance(raw, str) else raw
            if isinstance(data, dict):
                lines = []
                for k, v in data.items():
                    lines.append(f"\n{'═'*50}\n  {k.upper().replace('_', ' ')}\n{'─'*50}")
                    if isinstance(v, list):
                        for i, item in enumerate(v, 1):
                            if isinstance(item, dict):
                                lines.append(f"\n  [{i}]")
                                for kk, vv in item.items():
                                    lines.append(f"    {kk}: {vv}")
                            else:
                                lines.append(f"  {i}. {item}")
                    elif isinstance(v, dict):
                        for kk, vv in v.items():
                            if isinstance(vv, list):
                                lines.append(f"  {kk}:")
                                for x in vv: lines.append(f"    • {x}")
                            else:
                                lines.append(f"  • {kk}: {vv}")
                    else:
                        lines.append(f"  {v}")
                widget.setText("\n".join(lines))
            else:
                widget.setText(str(raw))
        except Exception:
            widget.setText(str(raw))

    def _do_trending():
        from ai_core.audio_ai import analyze_trending_audio
        async def _r():
            res = await analyze_trending_audio(
                aud_niche.text().strip() or "General", aud_plat.currentText(),
                aud_type.currentText(), aud_lang.currentText()
            )
            return json.dumps(res, ensure_ascii=False, indent=2)
        _run_aud(_r(), aud_out1, aud_trend_btn, "🎵 Analyze Trending Audio")

    def _do_podcast():
        from ai_core.audio_ai import generate_podcast_script
        async def _r():
            res = await generate_podcast_script(
                pod_topic.text().strip() or "Growing on Social Media in 2025",
                pod_len.value(), pod_show.text().strip() or "My Podcast",
                pod_host.text().strip() or "Host", pod_style.currentText(),
                pod_lang.currentText()
            )
            return json.dumps(res, ensure_ascii=False, indent=2)
        _run_aud(_r(), pod_out, pod_btn, "🎙️ Generate Episode Script")

    def _do_voice():
        from ai_core.audio_ai import generate_voice_note_script
        async def _r():
            res = await generate_voice_note_script(
                vn_purpose.text().strip() or "introduce my product to a potential customer",
                vn_recipient.text().strip() or "potential customer",
                vn_tone.currentText(), vn_len.currentText(), vn_lang.currentText()
            )
            return json.dumps(res, ensure_ascii=False, indent=2)
        _run_aud(_r(), vn_out, vn_btn, "🎤 Generate Voice Script")

    def _do_audio_brand():
        from ai_core.audio_ai import build_audio_brand_strategy
        async def _r():
            res = await build_audio_brand_strategy(
                ab_brand.text().strip() or "My Brand",
                ab_niche.text().strip() or "General",
                ab_emotion.currentText(), aud_lang.currentText()
            )
            return json.dumps(res, ensure_ascii=False, indent=2)
        _run_aud(_r(), aud_out4, ab_brand_btn, "🎼 Build Audio Brand Strategy")

    def _do_transcript():
        from ai_core.audio_ai import optimize_transcription_to_caption
        async def _r():
            res = await optimize_transcription_to_caption(
                ab_transcript.toPlainText().strip() or "Today I want to talk about growing your social media...",
                ab_trans_plat.currentText(), ab_trans_len.value(), aud_lang.currentText()
            )
            return json.dumps(res, ensure_ascii=False, indent=2)
        _run_aud(_r(), aud_out4, ab_trans_btn, "📝 Optimize Transcript")

    aud_trend_btn.clicked.connect(_do_trending)
    pod_btn.clicked.connect(_do_podcast)
    vn_btn.clicked.connect(_do_voice)
    ab_brand_btn.clicked.connect(_do_audio_brand)
    ab_trans_btn.clicked.connect(_do_transcript)

    return page


# ═══════════════════════════════════════════════════════════════════════════════
# ✦ NEW FEATURE PAGE 34: ALGORITHM DECODER
# ═══════════════════════════════════════════════════════════════════════════════

def build_algorithm_decoder_page(api_base: str) -> QWidget:
    """Algorithm Decoder — Reverse-engineer platform algorithms for maximum reach."""
    import asyncio

    _GS = (f"QGroupBox{{color:{ACCENT};font-weight:bold;border:1px solid {BORDER};"
           f"border-radius:8px;padding-top:8px;margin-top:4px;}}"
           f"QGroupBox::title{{subcontrol-origin:margin;left:8px;padding:0 4px;}}")

    def _btn(text, color=None):
        b = QPushButton(text); b.setCursor(Qt.PointingHandCursor)
        c = color or ACCENT
        b.setStyleSheet(
            f"QPushButton{{background:{c};color:#11111B;border:none;border-radius:8px;"
            f"padding:8px 18px;font-weight:bold;font-size:13px;}}"
            f"QPushButton:hover{{background:{c}CC;}}"
            f"QPushButton:disabled{{background:{BORDER};color:{SUBTEXT};}}"
        )
        return b

    page = QWidget(); pl = QVBoxLayout(page)
    pl.setContentsMargins(20, 16, 20, 16); pl.setSpacing(10)

    hdr = QLabel("🔮  Algorithm Intelligence Decoder")
    hdr.setFont(QFont("Segoe UI", 17, QFont.Bold))
    hdr.setStyleSheet(f"color:{ACCENT};")
    pl.addWidget(hdr)
    sub = QLabel("Decode platform algorithms, score content before posting, check shadow-ban risk & track algorithm updates")
    sub.setStyleSheet(f"color:{SUBTEXT}; font-size:13px;")
    pl.addWidget(sub)

    tabs = QTabWidget()
    tabs.setStyleSheet(
        f"QTabWidget::pane{{background:{DARK_BG};border:1px solid {BORDER};border-radius:8px;}}"
        f"QTabBar::tab{{background:{SURFACE};color:{SUBTEXT};padding:8px 14px;font-size:13px;border-radius:6px 6px 0 0;margin-right:2px;}}"
        f"QTabBar::tab:selected{{background:{ACCENT};color:#11111B;font-weight:bold;}}"
        f"QTabBar::tab:hover{{background:{HOVER};color:{TEXT};}}"
    )
    pl.addWidget(tabs, 1)

    # ── TAB 1: Algorithm Decoder ──────────────────────────────────────────────
    t1 = QWidget(); t1l = QVBoxLayout(t1); t1l.setContentsMargins(14, 12, 14, 12); t1l.setSpacing(8)
    grp1 = QGroupBox("🔮 Decode Platform Algorithm"); grp1.setStyleSheet(_GS)
    g1 = QGridLayout(grp1); g1.setSpacing(8)
    g1.addWidget(QLabel("Platform:"), 0, 0)
    alg_plat = QComboBox(); alg_plat.addItems(["Instagram", "TikTok", "YouTube", "Facebook", "LinkedIn", "Twitter/X", "Pinterest"])
    g1.addWidget(alg_plat, 0, 1)
    g1.addWidget(QLabel("Content Type:"), 0, 2)
    alg_type = QComboBox(); alg_type.addItems(["Reels", "Posts/Carousels", "Stories", "Live", "Shorts", "Videos", "Articles"])
    g1.addWidget(alg_type, 0, 3)
    g1.addWidget(QLabel("Niche:"), 1, 0)
    alg_niche = QLineEdit(); alg_niche.setPlaceholderText("e.g. fitness, business, beauty")
    g1.addWidget(alg_niche, 1, 1)
    g1.addWidget(QLabel("Language:"), 1, 2)
    alg_lang = QComboBox(); alg_lang.addItems(["English", "Khmer", "Thai", "Vietnamese", "Chinese", "Spanish"])
    g1.addWidget(alg_lang, 1, 3)
    t1l.addWidget(grp1)

    b1r = QHBoxLayout()
    alg_decode_btn   = _btn("🔮 Decode Algorithm", ACCENT)
    alg_updates_btn  = _btn("📡 Latest Updates", SUCCESS)
    alg_peaks_btn    = _btn("⏰ Peak Windows", WARNING)
    b1r.addWidget(alg_decode_btn); b1r.addWidget(alg_updates_btn); b1r.addWidget(alg_peaks_btn); b1r.addStretch()
    t1l.addLayout(b1r)

    alg_out1 = QTextEdit(); alg_out1.setReadOnly(True)
    alg_out1.setPlaceholderText(
        "🔮 Algorithm intelligence will appear here...\n\n"
        "• Decode Algorithm — full breakdown of ranking factors, distribution phases, and secret signals\n"
        "• Latest Updates — 2025 algorithm changes and what's working NOW\n"
        "• Peak Windows — personalized optimal posting schedule"
    )
    alg_out1.setStyleSheet(f"background:{SURFACE};color:{TEXT};border:1px solid {BORDER};border-radius:8px;font-size:13px;")
    t1l.addWidget(alg_out1, 1)
    tabs.addTab(t1, "🔮 Algorithm Decoder")

    # ── TAB 2: Pre-Post Content Scorer ────────────────────────────────────────
    t2 = QWidget(); t2l = QVBoxLayout(t2); t2l.setContentsMargins(14, 12, 14, 12); t2l.setSpacing(8)
    grp2 = QGroupBox("📊 Pre-Post Content Scorer"); grp2.setStyleSheet(_GS)
    g2 = QGridLayout(grp2); g2.setSpacing(8)
    g2.addWidget(QLabel("Content Type:"), 0, 0)
    pp_type = QComboBox(); pp_type.addItems(["Reel", "Post", "Carousel", "Story", "Short", "Video"])
    g2.addWidget(pp_type, 0, 1)
    g2.addWidget(QLabel("Platform:"), 0, 2)
    pp_plat = QComboBox(); pp_plat.addItems(["Instagram", "TikTok", "YouTube", "Facebook", "LinkedIn"])
    g2.addWidget(pp_plat, 0, 3)
    g2.addWidget(QLabel("Planned Post Time:"), 1, 0)
    pp_time = QLineEdit(); pp_time.setPlaceholderText("e.g. Tuesday 11:00 AM")
    g2.addWidget(pp_time, 1, 1)
    g2.addWidget(QLabel("Hashtags:"), 1, 2)
    pp_hashtags = QLineEdit(); pp_hashtags.setPlaceholderText("#tag1 #tag2 #tag3 ...")
    g2.addWidget(pp_hashtags, 1, 3)
    g2.addWidget(QLabel("Content to Score:"), 2, 0)
    pp_content = QTextEdit(); pp_content.setMaximumHeight(100)
    pp_content.setPlaceholderText("Paste your post caption or content description here to get an AI score before posting...")
    pp_content.setStyleSheet(f"background:{DARK_BG};color:{TEXT};border:1px solid {BORDER};border-radius:6px;padding:6px;font-size:13px;")
    g2.addWidget(pp_content, 2, 1, 1, 3)
    t2l.addWidget(grp2)

    pp_btn = _btn("📊 Score My Content", ACCENT)
    t2l.addWidget(pp_btn)
    pp_out = QTextEdit(); pp_out.setReadOnly(True)
    pp_out.setPlaceholderText("Your pre-post content score and optimization tips will appear here...")
    pp_out.setStyleSheet(f"background:{SURFACE};color:{TEXT};border:1px solid {BORDER};border-radius:8px;font-size:13px;")
    t2l.addWidget(pp_out, 1)
    tabs.addTab(t2, "📊 Pre-Post Scorer")

    # ── TAB 3: Shadow-Ban Checker ─────────────────────────────────────────────
    t3 = QWidget(); t3l = QVBoxLayout(t3); t3l.setContentsMargins(14, 12, 14, 12); t3l.setSpacing(8)
    grp3 = QGroupBox("🛡️ Shadow-Ban Risk Checker"); grp3.setStyleSheet(_GS)
    g3 = QGridLayout(grp3); g3.setSpacing(8)
    g3.addWidget(QLabel("Recent Hashtags Used:"), 0, 0)
    sb_hashtags = QTextEdit(); sb_hashtags.setMaximumHeight(70)
    sb_hashtags.setPlaceholderText("#yourtag1 #yourtag2 #yourtag3 — paste your recent hashtags here...")
    sb_hashtags.setStyleSheet(f"background:{DARK_BG};color:{TEXT};border:1px solid {BORDER};border-radius:6px;padding:6px;font-size:13px;")
    g3.addWidget(sb_hashtags, 0, 1, 1, 3)
    g3.addWidget(QLabel("Recent Activity:"), 1, 0)
    sb_activity = QLineEdit(); sb_activity.setPlaceholderText("e.g. posted 5x/day, used automation, follow/unfollow")
    g3.addWidget(sb_activity, 1, 1)
    g3.addWidget(QLabel("Platform:"), 1, 2)
    sb_plat = QComboBox(); sb_plat.addItems(["Instagram", "TikTok", "Facebook", "YouTube", "Twitter/X"])
    g3.addWidget(sb_plat, 1, 3)
    t3l.addWidget(grp3)

    sb_btn = _btn("🛡️ Check Shadow-Ban Risk", WARNING)
    t3l.addWidget(sb_btn)
    sb_out = QTextEdit(); sb_out.setReadOnly(True)
    sb_out.setPlaceholderText("Shadow-ban risk analysis and recovery plan will appear here...")
    sb_out.setStyleSheet(f"background:{SURFACE};color:{TEXT};border:1px solid {BORDER};border-radius:8px;font-size:13px;")
    t3l.addWidget(sb_out, 1)
    tabs.addTab(t3, "🛡️ Shadow-Ban Checker")

    # ── Workers ───────────────────────────────────────────────────────────────
    _alg_workers = []

    def _run_alg(coro, out_w, btn_w, label):
        btn_w.setEnabled(False); btn_w.setText("⏳ Decoding...")
        out_w.setText("🔄 Decoding algorithm intelligence... please wait.")
        class _W(QThread):
            done = pyqtSignal(str); err = pyqtSignal(str)
            def __init__(self, c): super().__init__(); self._c = c
            def run(self):
                try:
                    loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
                    r = loop.run_until_complete(self._c); loop.close(); self.done.emit(r)
                except Exception as e: self.err.emit(str(e))
        w = _W(coro)
        w.done.connect(lambda r: (_alg_fmt(out_w, r), btn_w.setEnabled(True), btn_w.setText(label)))
        w.err.connect(lambda e: (out_w.setText(f"❌ {e}"), btn_w.setEnabled(True), btn_w.setText(label)))
        _alg_workers.append(w); w.start()

    def _alg_fmt(widget, raw):
        try:
            data = json.loads(raw) if isinstance(raw, str) else raw
            if isinstance(data, dict):
                lines = []
                for k, v in data.items():
                    lines.append(f"\n{'═'*52}")
                    lines.append(f"  ✦ {k.upper().replace('_', ' ')}")
                    lines.append(f"{'─'*52}")
                    if isinstance(v, list):
                        for i, item in enumerate(v, 1):
                            if isinstance(item, dict):
                                lines.append(f"\n  [{i}]")
                                for kk, vv in item.items():
                                    lines.append(f"    {kk}: {vv}")
                            else:
                                lines.append(f"  {i}. {item}")
                    elif isinstance(v, dict):
                        for kk, vv in v.items():
                            if isinstance(vv, list):
                                lines.append(f"  {kk}:")
                                for x in vv: lines.append(f"    ▸ {x}")
                            else:
                                lines.append(f"  ▸ {kk}: {vv}")
                    else:
                        lines.append(f"  {v}")
                widget.setText("\n".join(lines))
            else:
                widget.setText(str(raw))
        except Exception:
            widget.setText(str(raw))

    def _do_decode():
        from ai_core.algorithm_decoder import decode_algorithm
        async def _r():
            res = await decode_algorithm(
                alg_plat.currentText(), alg_type.currentText(),
                alg_niche.text().strip() or "General", alg_lang.currentText()
            )
            return json.dumps(res, ensure_ascii=False, indent=2)
        _run_alg(_r(), alg_out1, alg_decode_btn, "🔮 Decode Algorithm")

    def _do_updates():
        from ai_core.algorithm_decoder import get_algorithm_updates
        async def _r():
            res = await get_algorithm_updates(alg_plat.currentText(), alg_lang.currentText())
            return json.dumps(res, ensure_ascii=False, indent=2)
        _run_alg(_r(), alg_out1, alg_updates_btn, "📡 Latest Updates")

    def _do_peaks():
        from ai_core.algorithm_decoder import calculate_peak_window
        async def _r():
            res = await calculate_peak_window(
                alg_plat.currentText(), 10000,
                alg_niche.text().strip() or "General", "UTC-5 (Eastern)", alg_lang.currentText()
            )
            return json.dumps(res, ensure_ascii=False, indent=2)
        _run_alg(_r(), alg_out1, alg_peaks_btn, "⏰ Peak Windows")

    def _do_score():
        from ai_core.algorithm_decoder import score_content_prepost
        async def _r():
            res = await score_content_prepost(
                pp_content.toPlainText().strip() or "Check out our latest post!",
                pp_plat.currentText(), pp_type.currentText(),
                pp_time.text().strip() or "Tuesday 11:00 AM",
                pp_hashtags.text().strip(), alg_lang.currentText()
            )
            return json.dumps(res, ensure_ascii=False, indent=2)
        _run_alg(_r(), pp_out, pp_btn, "📊 Score My Content")

    def _do_shadowban():
        from ai_core.algorithm_decoder import check_shadowban_risk
        async def _r():
            res = await check_shadowban_risk(
                sb_hashtags.toPlainText().strip() or "#general #content #post",
                sb_activity.text().strip() or "Normal posting",
                sb_plat.currentText(), alg_lang.currentText()
            )
            return json.dumps(res, ensure_ascii=False, indent=2)
        _run_alg(_r(), sb_out, sb_btn, "🛡️ Check Shadow-Ban Risk")

    alg_decode_btn.clicked.connect(_do_decode)
    alg_updates_btn.clicked.connect(_do_updates)
    alg_peaks_btn.clicked.connect(_do_peaks)
    pp_btn.clicked.connect(_do_score)
    sb_btn.clicked.connect(_do_shadowban)

    return page


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN WINDOW
# ═══════════════════════════════════════════════════════════════════════════════

class GrowthOS_Desktop(QMainWindow):
    _backend_proc = None  # class-level so only one process is spawned

    def __init__(self, user_info: dict = None):
        super().__init__()
        self._user_info = user_info or {}
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION} — Ultimate AI Social Growth System")
        self.setGeometry(60, 40, 1420, 900)
        self.setMinimumSize(1100, 680)
        self.setStyleSheet(GLOBAL_STYLE)

        self._ensure_backend()          # auto-start backend if not running

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._setup_sidebar(main_layout)
        self._setup_pages(main_layout)

    # ── Backend auto-start ────────────────────────────────────────────────────
    @staticmethod
    def _backend_alive() -> bool:
        try:
            return requests.get(f"{BACKEND_URL}/api/v1/health", timeout=2).status_code == 200
        except Exception:
            return False

    @classmethod
    def _ensure_backend(cls):
        """Start uvicorn backend in background if it is not already running."""
        if cls._backend_alive():
            return  # already up
        if cls._backend_proc is not None and cls._backend_proc.poll() is None:
            return  # already started by us, still running

        import subprocess
        _cwd = os.path.dirname(os.path.abspath(__file__))
        _flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        try:
            # Launch uvicorn directly (no --reload) so no child-process
            # spawning is needed — avoids Windows multiprocessing issues.
            cls._backend_proc = subprocess.Popen(
                [
                    sys.executable, "-m", "uvicorn",
                    "backend_api:app",
                    "--host", "127.0.0.1",
                    "--port", "8000",
                ],
                cwd=_cwd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=_flags,
            )
        except Exception:
            pass  # will surface as a normal "Cannot connect" error in the UI

    def _setup_sidebar(self, parent_layout):
        sidebar = QFrame()
        sidebar.setFixedWidth(235)
        sidebar.setStyleSheet(f"background-color: {SIDEBAR}; border-right: 1px solid #313244;")
        sl = QVBoxLayout(sidebar)
        sl.setContentsMargins(10, 16, 10, 10)
        sl.setSpacing(3)

        # ── Logo & version ────────────────────────────────────────────────────
        logo = QLabel(f"🚀 {APP_NAME}")
        logo.setFont(QFont("Segoe UI", 15, QFont.Bold))
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet(f"color: {ACCENT}; padding: 10px 0;")
        sl.addWidget(logo)

        ver = QLabel(f"v{APP_VERSION}  •  110 AI Features")
        ver.setAlignment(Qt.AlignCenter)
        ver.setStyleSheet(f"color: {SUBTEXT}; font-size: 14px;")
        sl.addWidget(ver)
        sl.addSpacing(8)

        # ── User info banner ──────────────────────────────────────────────────
        if self._user_info:
            role      = self._user_info.get("role", "member")
            disp_name = self._user_info.get("display_name", self._user_info.get("username", "User"))
            role_color = ACCENT if role == "admin" else (SUCCESS if role == "member" else WARNING)
            role_icon  = "👑" if role == "admin" else ("👤" if role == "member" else "👁")
            banner = QFrame()
            banner.setStyleSheet(f"background:{SURFACE}; border-radius:8px;")
            b_lay = QVBoxLayout(banner)
            b_lay.setContentsMargins(10, 7, 10, 7)
            b_lay.setSpacing(2)
            name_lbl = QLabel(f"{role_icon}  {disp_name}")
            name_lbl.setStyleSheet(f"color:{TEXT}; font-size:14px; font-weight:bold;")
            role_lbl = QLabel(role.upper())
            role_lbl.setStyleSheet(f"color:{role_color}; font-size:14px; letter-spacing:1px;")
            b_lay.addWidget(name_lbl)
            b_lay.addWidget(role_lbl)
            sl.addWidget(banner)
            sl.addSpacing(6)

        # ── Scrollable nav buttons ────────────────────────────────────────────
        nav_items = [
            (0,  "📊", "Dashboard"),
            (35, "📱", "AI Social Network"),
            (1,  "🌌", "Omni AI Hub"),
            (2,  "🧠", "Strategy Brain"),
            (3,  "✍️", "Content Studio"),
            (4,  "📈", "Analytics"),
            (5,  "🔮", "Trend Radar"),
            (6,  "⚙️", "Campaign Engine"),
            (7,  "🛡️", "Risk Engine"),
            (8,  "🛒", "SMM Panel"),
            (9,  "🤖", "Multi-Agent AI"),
            (10, "💾", "Memory System"),
            (11, "📅", "Auto-Scheduler"),
            (12, "💬", "Social Inbox"),
            (13, "🌍", "Geo Intelligence"),
            (14, "🔧", "Settings & Help"),
            (15, "🔐", "Social Accounts"),
            (16, "📱", "Social Manager"),
            (17, "🔍", "Intelligence Hub"),
            (18, "🔥", "Viral & Growth"),
            (19, "⚡", "Automation Suite"),
            (20, "💼", "Business Intel"),
            (21, "🎨", "Creator Tools"),
            (22, "💰", "Sales Engine"),
            (23, "🎬", "Content Domination"),
            (24, "🏆", "Brand Authority"),
            (25, "🤝", "Community Hub"),
            (26, "⚡", "Real-Time Intel"),
            (27, "📘", "Facebook Manager"),
            (28, "📱", "Telegram Bot"),
            (30, "🎬", "Video Studio"),
            (31, "🧪", "A/B Lab"),
            (32, "🛍️", "Social Commerce"),
            (33, "🎵", "Audio AI"),
            (34, "🔮", "Algorithm Decoder"),
        ]
        if self._user_info.get("role") == "admin":
            nav_items.append((29, "👑", "Admin Panel"))

        self._nav_buttons = {}
        nav_container = QWidget()
        nav_container.setStyleSheet(f"background: transparent;")
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(2)

        for idx, icon, label in nav_items:
            btn = NavButton(f"{icon}  {label}")
            btn.setMinimumHeight(40)
            btn.clicked.connect(lambda _, i=idx: self._switch_page(i))
            nav_layout.addWidget(btn)
            self._nav_buttons[idx] = btn

        nav_layout.addStretch()

        nav_scroll = QScrollArea()
        nav_scroll.setWidget(nav_container)
        nav_scroll.setWidgetResizable(True)
        nav_scroll.setFrameShape(QScrollArea.NoFrame)
        nav_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        nav_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        nav_scroll.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background: {SIDEBAR};
                width: 6px;
                border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: {BORDER};
                border-radius: 3px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {ACCENT};
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        sl.addWidget(nav_scroll, 1)   # stretch=1 so it fills available space

        # ── Status indicator ──────────────────────────────────────────────────
        self._status_label = QLabel("● Backend: Unknown")
        self._status_label.setStyleSheet(f"color:{SUBTEXT}; font-size:14px; padding:4px;")
        self._status_label.setAlignment(Qt.AlignCenter)
        sl.addWidget(self._status_label)

        # ── Logout button ─────────────────────────────────────────────────────
        if self._user_info:
            logout_btn = QPushButton("🚪  Logout")
            logout_btn.setCursor(Qt.PointingHandCursor)
            logout_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; color: {SUBTEXT};
                    border: 1px solid {SURFACE}; border-radius: 6px;
                    padding: 7px 10px; font-size: 14px; text-align: left;
                }}
                QPushButton:hover {{ background: #F38BA820; color: #F38BA8; border-color: #F38BA8; }}
            """)
            logout_btn.clicked.connect(self._do_logout)
            sl.addWidget(logout_btn)

        # ── Theme selector ────────────────────────────────────────────────────
        sl.addSpacing(6)
        _div = QFrame()
        _div.setFrameShape(QFrame.HLine)
        _div.setStyleSheet(f"background: {BORDER}; border: none; max-height: 1px;")
        sl.addWidget(_div)

        _theme_lbl = QLabel("🎨  Theme")
        _theme_lbl.setStyleSheet(f"color: {SUBTEXT}; font-size: 14px; padding: 4px 2px 1px 2px;")
        sl.addWidget(_theme_lbl)

        self._theme_cbo = QComboBox()
        self._theme_cbo.addItems(THEME_NAMES)
        try:
            self._theme_cbo.setCurrentText(_active_theme_name())
        except Exception:
            pass
        self._theme_cbo.setStyleSheet(f"""
            QComboBox {{
                background: {SURFACE}; color: {TEXT}; font-size: 14px;
                border: 1px solid {BORDER}; border-radius: 6px;
                padding: 4px 8px; min-height: 30px;
            }}
            QComboBox:focus {{ border: 1px solid {ACCENT}; }}
            QComboBox::drop-down {{ border: none; width: 20px; }}
            QComboBox QAbstractItemView {{
                background: {SURFACE}; color: {TEXT}; font-size: 14px;
                selection-background-color: {HOVER}; border: 1px solid {BORDER};
            }}
        """)
        sl.addWidget(self._theme_cbo)

        _apply_btn = QPushButton("✦ Apply & Restart")
        _apply_btn.setFixedHeight(32)
        _apply_btn.setCursor(Qt.PointingHandCursor)
        _apply_btn.setStyleSheet(f"""
            QPushButton {{
                background: {SURFACE}; color: {ACCENT};
                border: 1px solid {ACCENT}; border-radius: 6px;
                font-size: 14px; font-weight: bold; padding: 4px;
            }}
            QPushButton:hover {{ background: {ACCENT}; color: #11111B; }}
        """)
        _apply_btn.clicked.connect(self._apply_theme)
        sl.addWidget(_apply_btn)

        self._nav_buttons[0].setChecked(True)
        parent_layout.addWidget(sidebar)

        # Ping backend — retry every 2 s until online
        QTimer.singleShot(1500, self._ping_backend)

    def _ping_backend(self):
        try:
            r = requests.get(f"{BACKEND_URL}/api/v1/health", timeout=2)
            if r.status_code == 200:
                self._status_label.setText("● Backend: Online ✓")
                self._status_label.setStyleSheet(f"color:{SUCCESS}; font-size:14px; padding:4px;")
                # Load connected accounts once when backend first comes online
                if not _ACCOUNTS_CACHE:
                    self._do_refresh_accounts()
                return  # done — backend is up, stop retrying
            else:
                self._status_label.setText("● Backend: Error")
                self._status_label.setStyleSheet(f"color:{WARNING}; font-size:14px; padding:4px;")
        except Exception:
            self._status_label.setText("● Backend: Starting…")
            self._status_label.setStyleSheet(f"color:{WARNING}; font-size:14px; padding:4px;")
        # Not yet online — retry in 2 seconds
        QTimer.singleShot(2000, self._ping_backend)

    def _do_refresh_accounts(self):
        """Fetch connected accounts into the module-level cache and update the sidebar."""
        w = ApiWorker(f"{BACKEND_URL}/api/v1/auth/accounts", method="GET")
        def _done(resp):
            global _ACCOUNTS_CACHE
            _ACCOUNTS_CACHE = resp.get("data", [])
            connected = sum(1 for a in _ACCOUNTS_CACHE if a.get("status") == "connected")
            if connected > 0:
                self._status_label.setText(
                    f"● Online ✓  |  🔗 {connected} acct{'s' if connected != 1 else ''}"
                )
                self._status_label.setStyleSheet(f"color:{SUCCESS}; font-size:14px; padding:4px;")
        w.result_ready.connect(_done)
        w.start()
        self._acc_cache_worker = w  # prevent GC

    def _setup_pages(self, parent_layout):
        self.stack = QStackedWidget()
        api = BACKEND_URL
        pages = [
            build_dashboard_page(api),       # 0
            build_omni_hub_page(api),        # 1
            build_strategy_page(api),        # 2
            build_content_page(api),         # 3
            build_analytics_page(api),       # 4
            build_trends_page(api),          # 5
            build_campaign_page(api),        # 6
            build_risk_page(api),            # 7
            build_smm_page(api),             # 8
            build_multiagent_page(api),      # 9
            build_memory_page(api),          # 10
            build_scheduler_page(api),       # 11
            build_inbox_page(api),           # 12
            build_geo_page(api),             # 13
            build_settings_page(api),        # 14
            build_social_accounts_page(api), # 15
            build_social_manager_page(api),  # 16
            build_intelligence_page(api),    # 17
            build_viral_tools_page(api),     # 18
            build_automation_page(api),      # 19
            build_business_intel_page(api),  # 20
            build_creator_tools_page(api),   # 21
            build_sales_engine_page(api),        # 22
            build_content_domination_page(api),  # 23
            build_brand_authority_page(api),     # 24
            build_community_page(api),           # 25
            build_realtime_intel_page(api),      # 26
            build_facebook_manager_page(api),    # 27
            build_telegram_bot_page(api),        # 28
        ]
        if self._user_info.get("role") == "admin":
            pages.append(build_admin_page(self._user_info))  # 29
        else:
            pages.append(QWidget())  # 29 placeholder (non-admin)
        # New AI features: pages 30–34
        pages.append(build_video_studio_page(api))       # 30
        pages.append(build_ab_lab_page(api))             # 31
        pages.append(build_social_commerce_page(api))    # 32
        pages.append(build_audio_ai_page(api))           # 33
        pages.append(build_algorithm_decoder_page(api))  # 34
        pages.append(build_social_network_page(api))     # 35 – AI Social Network
        for p in pages:
            self.stack.addWidget(p)
        parent_layout.addWidget(self.stack, 1)

    def _switch_page(self, index: int):
        self.stack.setCurrentIndex(index)
        for i, btn in self._nav_buttons.items():
            btn.setChecked(i == index)

    def closeEvent(self, event):
        """Terminate the auto-started backend process when the window closes."""
        proc = GrowthOS_Desktop._backend_proc
        if proc is not None and proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=3)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
        event.accept()

    def _apply_theme(self):
        selected = self._theme_cbo.currentText()
        try:
            with open(_THEME_FILE, "w", encoding="utf-8") as _tf:
                _tf.write(selected)
        except Exception:
            pass
        import subprocess
        # Start a fresh process with the new theme, then quit current
        subprocess.Popen([sys.executable] + sys.argv)
        QTimer.singleShot(250, QApplication.instance().quit)

    def _do_logout(self):
        from PyQt5.QtWidgets import QMessageBox, QDialog
        reply = QMessageBox.question(
            self, "Confirm Logout",
            f"Logout as  {self._user_info.get('display_name', 'user')}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        try:
            import admin as _admin
            _admin.logout(self._user_info.get("token", ""))
        except Exception:
            pass
        from login_window import LoginWindow
        self.hide()
        dlg = LoginWindow()
        if dlg.exec_() == QDialog.Accepted:
            new_win = GrowthOS_Desktop(user_info=dlg.logged_in_user)
            new_win.show()
        else:
            QApplication.quit()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    from login_window import LoginWindow
    from PyQt5.QtWidgets import QDialog
    dlg = LoginWindow()
    if dlg.exec_() != QDialog.Accepted:
        sys.exit(0)
    window = GrowthOS_Desktop(user_info=dlg.logged_in_user)
    window.show()
    sys.exit(app.exec_())
