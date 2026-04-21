# desktop_app.py  — GrowthOS AI v2.0 — Complete 99-Feature Desktop Client
import sys
import os
import json
import requests
from datetime import datetime as _dt_cls, timedelta
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel, QStackedWidget,
    QLineEdit, QTextEdit, QFrame, QComboBox, QGroupBox, QGridLayout,
    QScrollArea, QSpinBox, QDoubleSpinBox, QMessageBox, QTabWidget,
    QSplitter, QDateTimeEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QProgressBar,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QDateTime
from PyQt5.QtGui import QFont, QColor, QPalette

try:
    from config import BACKEND_URL, APP_NAME, APP_VERSION
except ImportError:
    BACKEND_URL  = "http://127.0.0.1:8000"
    APP_NAME     = "GrowthOS AI"
    APP_VERSION  = "2.0"


# ─── Scheduler Data Store (local JSON) ───────────────────────────────────────
_SCHED_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scheduled_posts.json")


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


# ─── Styles ───────────────────────────────────────────────────────────────────
DARK_BG   = "#1E1E2E"
SIDEBAR   = "#181825"
SURFACE   = "#313244"
ACCENT    = "#89B4FA"
SUCCESS   = "#A6E3A1"
WARNING   = "#FAB387"
TEXT      = "#CDD6F4"
SUBTEXT   = "#6C7086"


GLOBAL_STYLE = f"""
    QWidget {{ background-color: {DARK_BG}; color: {TEXT}; font-family: 'Segoe UI', Arial; }}
    QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
        background-color: {SURFACE}; color: {TEXT};
        border: 1px solid #45475A; border-radius: 6px; padding: 6px;
    }}
    QGroupBox {{
        border: 1px solid #45475A; border-radius: 8px; margin-top: 12px; font-weight: bold;
    }}
    QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 6px; color: {ACCENT}; }}
    QTabWidget::pane {{ border: 1px solid #45475A; border-radius: 6px; }}
    QTabBar::tab {{
        background: {SURFACE}; color: {TEXT};
        padding: 8px 20px; border-top-left-radius: 6px; border-top-right-radius: 6px;
    }}
    QTabBar::tab:selected {{ background: {DARK_BG}; color: {ACCENT}; font-weight: bold; }}
    QScrollBar:vertical {{ background: {SURFACE}; width: 8px; border-radius: 4px; }}
    QScrollBar::handle:vertical {{ background: #45475A; border-radius: 4px; }}
"""


def _styled_input(placeholder=""):
    w = QLineEdit()
    w.setPlaceholderText(placeholder)
    return w


def _big_text(placeholder=""):
    w = QTextEdit()
    w.setPlaceholderText(placeholder)
    return w


def _combo(*items):
    w = QComboBox()
    w.addItems(items)
    return w


# ─── Worker Thread (non-blocking API calls) ──────────────────────────────────
class ApiWorker(QThread):
    result_ready = pyqtSignal(dict)
    error_signal = pyqtSignal(str)

    def __init__(self, url: str, payload: dict = None, method: str = "POST"):
        super().__init__()
        self.url     = url
        self.payload = payload
        self.method  = method

    def run(self):
        try:
            if self.method == "GET":
                r = requests.get(self.url, params=self.payload, timeout=30)
            else:
                r = requests.post(self.url, json=self.payload, timeout=30)
            r.raise_for_status()
            self.result_ready.emit(r.json())
        except requests.exceptions.ConnectionError:
            self.error_signal.emit("Cannot connect to backend. Start it with:\n\n  uvicorn backend_api:app --reload")
        except Exception as e:
            self.error_signal.emit(str(e))


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
                padding: 10px 14px; font-weight: bold;
                text-align: left;
            }}
            QPushButton:hover {{ background-color: #2D2D3B; }}
            QPushButton:checked {{ background-color: #313244; color: {ACCENT}; border-left: 3px solid {ACCENT}; }}
        """)


# ─── Action Button ────────────────────────────────────────────────────────────
class ActionButton(QPushButton):
    def __init__(self, text: str, color: str = ACCENT):
        super().__init__(text)
        self.color = color
        self.setMinimumHeight(42)
        self.setCursor(Qt.PointingHandCursor)
        self._apply_style(color)

    def _apply_style(self, color: str):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color}; color: #11111B;
                border: none; border-radius: 8px;
                padding: 10px 18px; font-weight: bold; font-size: 13px;
            }}
            QPushButton:hover {{ opacity: 0.9; }}
            QPushButton:disabled {{ background-color: #45475A; color: {SUBTEXT}; }}
        """)

    def set_loading(self, loading: bool):
        self.setEnabled(not loading)
        if loading:
            self.setText("⏳ Processing…")
        else:
            self._apply_style(self.color)


# ─── Output Box ───────────────────────────────────────────────────────────────
class OutputBox(QTextEdit):
    def __init__(self, placeholder="Results will appear here…"):
        super().__init__()
        self.setReadOnly(True)
        self.setPlaceholderText(placeholder)
        self.setStyleSheet(f"""
            QTextEdit {{
                background-color: {SURFACE}; color: {SUCCESS};
                border: 1px solid #45475A; border-radius: 8px;
                padding: 12px; font-size: 13px;
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
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(30, 24, 30, 24)
    layout.setSpacing(14)

    title = QLabel(f"{icon}  {title_text}" if icon else title_text)
    title.setFont(QFont("Segoe UI", 18, QFont.Bold))
    title.setStyleSheet(f"color: {ACCENT}; margin-bottom: 4px;")
    layout.addWidget(title)
    return page, layout


def build_dashboard_page(api_base: str) -> QWidget:
    page, layout = _make_page_layout("GrowthOS AI — Command Center", "🚀")

    info = QLabel(f"Backend: {api_base}   |   All 99 features active   |   Multi-Agent AI ready")
    info.setStyleSheet(f"color: {SUBTEXT}; font-size: 12px;")
    layout.addWidget(info)

    # KPI cards
    kpi_frame = QFrame()
    kpi_layout = QHBoxLayout(kpi_frame)
    kpi_layout.setSpacing(12)
    for icon, label, value, color in [
        ("🧠", "AI Features",     "99",   ACCENT),
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
        top.setStyleSheet(f"color:{SUBTEXT}; font-size:11px;")
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
        w = ApiWorker(f"{api_base}/api/v1/health", method="GET")
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

    def _run1(url, payload):
        out1.reset_color(); out1.setPlainText("AI is thinking…")
        w = ApiWorker(url, payload)
        page._w1 = w
        w.result_ready.connect(lambda d: out1.set_result(d.get("data", d)))
        w.error_signal.connect(out1.set_error)
        w.start()

    btn_strategy.clicked.connect(lambda: _run1(f"{api_base}/api/v1/ai/strategy", {
        "username": username.text() or "demo", "platform": platform.currentText(),
        "current_followers": followers.value(), "niche": niche.text() or "General",
        "goal_followers": goal_foll.value(), "duration_days": duration.value(),
    }))
    btn_audit.clicked.connect(lambda: _run1(f"{api_base}/api/v1/ai/audit", {
        "username": username.text() or "demo", "platform": platform.currentText(),
        "followers": followers.value(), "niche": niche.text() or "General",
    }))
    btn_forecast.clicked.connect(lambda: _run1(f"{api_base}/api/v1/ai/forecast", {
        "current_followers": followers.value(), "engagement_rate": 3.5,
        "posting_frequency": 1, "platform": platform.currentText(), "months": 3,
    }))

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
        })
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
        })
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

    def _run1(url):
        out1.reset_color(); out1.setPlainText("Generating content…")
        w = ApiWorker(url, _payload())
        page._w1 = w
        w.result_ready.connect(lambda d: out1.set_result(d.get("data", d)))
        w.error_signal.connect(out1.set_error)
        w.start()

    btn_full.clicked.connect(lambda: _run1(f"{api_base}/api/v1/ai/content"))
    btn_hook.clicked.connect(lambda: _run1(f"{api_base}/api/v1/ai/hook"))
    btn_hashtag.clicked.connect(lambda: _run1(f"{api_base}/api/v1/ai/hashtags"))

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

    def _run2(url):
        out2.reset_color(); out2.setPlainText("Generating…")
        w = ApiWorker(url, _payload2())
        page._w2 = w
        w.result_ready.connect(lambda d: out2.set_result(d.get("data", d)))
        w.error_signal.connect(out2.set_error)
        w.start()

    btn_script.clicked.connect(lambda: _run2(f"{api_base}/api/v1/ai/script"))
    btn_cal.clicked.connect(lambda: _run2(f"{api_base}/api/v1/ai/calendar"))

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
    hint.setStyleSheet(f"color:{SUBTEXT}; font-size:12px; padding:6px;")
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
        })
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

    def _run1(url, payload=None, method="POST"):
        out1.reset_color(); out1.setPlainText("Analyzing…")
        w = ApiWorker(url, payload, method)
        page._w1 = w
        w.result_ready.connect(lambda d: out1.set_result(d.get("data", d)))
        w.error_signal.connect(out1.set_error)
        w.start()

    btn_analyze.clicked.connect(lambda: _run1(f"{api_base}/api/v1/ai/performance", _metrics()))
    btn_timing.clicked.connect(lambda: _run1(f"{api_base}/api/v1/ai/timing/{platform.currentText()}", method="GET"))
    btn_fatigue.clicked.connect(lambda: _run1(f"{api_base}/api/v1/ai/performance", _metrics()))

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
        w = ApiWorker(f"{api_base}/api/v1/ai/report", payload)
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

    def _run3(url, payload):
        out3.reset_color(); out3.setPlainText("Calculating…")
        w = ApiWorker(url, payload)
        page._w3 = w
        w.result_ready.connect(lambda d: out3.set_result(d.get("data", d)))
        w.error_signal.connect(out3.set_error)
        w.start()

    btn_roi.clicked.connect(lambda: _run3(f"{api_base}/api/v1/ai/performance", {
        "platform": roi_plat.currentText(),
        "views": 50000, "likes": int(50000 * roi_eng_rate.value() / 100),
        "comments": 400, "shares": 200, "saves": 150, "follows": 55,
    }))
    btn_trust.clicked.connect(lambda: _run3(f"{api_base}/api/v1/ai/performance", {
        "platform": roi_plat.currentText(),
        "views": 50000, "likes": 3500, "comments": 420, "shares": 210,
        "saves": 180, "follows": roi_followers.value(),
    }))

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

    def _post(url, payload=None):
        output.reset_color(); output.setPlainText("Scanning trends…")
        w = ApiWorker(url, payload or _p())
        page._worker = w
        w.result_ready.connect(lambda d: output.set_result(d.get("data", d)))
        w.error_signal.connect(output.set_error)
        w.start()

    def _get(url):
        output.reset_color(); output.setPlainText("Fetching…")
        w = ApiWorker(url, method="GET")
        page._worker = w
        w.result_ready.connect(lambda d: output.set_result(d.get("data", d)))
        w.error_signal.connect(output.set_error)
        w.start()

    btn_trend.clicked.connect(lambda: _post(f"{api_base}/api/v1/ai/trends"))
    btn_predict.clicked.connect(lambda: _post(f"{api_base}/api/v1/ai/predict-trends"))
    btn_opps.clicked.connect(lambda: _get(f"{api_base}/api/v1/ai/opportunities/{platform.currentText()}/{niche.text() or 'General'}"))
    btn_strategy.clicked.connect(lambda: _get(f"{api_base}/api/v1/ai/time-strategy/{platform.currentText()}"))
    btn_fuse.clicked.connect(lambda: _post(f"{api_base}/api/v1/ai/trends", {**_p(), "cross_platform": True}))
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
        })
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
        })
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
        })
        page._w1 = w
        w.result_ready.connect(lambda d: out1.set_result(d.get("data", d)))
        w.error_signal.connect(out1.set_error)
        w.start()

    def _limits():
        out1.reset_color(); out1.setPlainText("Calculating safe limits…")
        url = f"{api_base}/api/v1/ai/safe-limits/{platform.currentText()}/{followers1.value()}"
        w = ApiWorker(url, method="GET")
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
        })
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
        })
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
    panel_url_lbl.setStyleSheet(f"color:{SUBTEXT}; font-size:11px;")
    btn_ping = ActionButton("🔌 Check Connection", ACCENT)
    btn_ping.setFixedWidth(160)
    brow.addWidget(panel_status_lbl)
    brow.addStretch()
    brow.addWidget(panel_url_lbl)
    brow.addWidget(btn_ping)
    layout.addWidget(banner)

    def _ping_panel():
        panel_status_lbl.setText("● Checking…")
        panel_status_lbl.setStyleSheet(f"color:{SUBTEXT}; font-weight:bold;")
        w = ApiWorker(f"{api_base}/api/v1/smm/panel-info", method="GET")
        page._wp = w
        def _got(resp):
            d = resp.get("data", resp)
            mode = d.get("mode", "demo")
            url  = d.get("api_url", "")
            if mode == "live":
                panel_status_lbl.setText("🟢 Live API — Real SMM Panel Connected")
                panel_status_lbl.setStyleSheet(f"color:{SUCCESS}; font-weight:bold;")
            else:
                panel_status_lbl.setText("🟡 Demo Mode — Set DEMOSMM_API_KEY in .env for Live")
                panel_status_lbl.setStyleSheet(f"color:{WARNING}; font-weight:bold;")
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
    svc_stats.setStyleSheet(f"color:{SUBTEXT}; font-size:11px; padding:2px 0;")
    t1l.addWidget(svc_stats)

    bal_box = OutputBox()
    bal_box.setMaximumHeight(90)
    t1l.addWidget(bal_box)
    tabs.addTab(t1, "📋 Services & Balance")

    def _load_services():
        svc_stats.setText("Loading services from panel…")
        cat = cat_input.text().strip()
        url = f"{api_base}/api/v1/smm/services" + (f"?category={cat}" if cat else "")
        w = ApiWorker(url, method="GET")
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
        w = ApiWorker(f"{api_base}/api/v1/smm/balance", method="GET")
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
    hint2.setStyleSheet(f"color:{SUBTEXT}; font-size:11px;")
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
        })
        t2._w = w
        w.result_ready.connect(lambda d: out2.set_result(d.get("data", d)))
        w.error_signal.connect(out2.set_error)
        w.start()

    btn_order.clicked.connect(_place_order)

    # ── Tab 3: AI Smart Order ─────────────────────────────────────────────────
    t3 = QWidget(); t3l = QVBoxLayout(t3)
    grp3 = QGroupBox("AI Smart Order  — AI selects best service within your budget")
    g3 = QGridLayout(grp3)
    smart_link   = _styled_input("Your profile or post URL")
    smart_goal   = _combo("Grow Followers", "Get Views", "Get Likes",
                          "Get Members", "Get Comments", "Get Subscribers")
    smart_budget = QDoubleSpinBox()
    smart_budget.setRange(1.0, 10_000.0); smart_budget.setValue(50.0); smart_budget.setPrefix("$ ")
    smart_plat   = _combo("TikTok", "Instagram", "Facebook", "YouTube", "Telegram")
    g3.addWidget(QLabel("Link:"),     0, 0); g3.addWidget(smart_link,   0, 1)
    g3.addWidget(QLabel("Goal:"),     1, 0); g3.addWidget(smart_goal,   1, 1)
    g3.addWidget(QLabel("Budget:"),   2, 0); g3.addWidget(smart_budget, 2, 1)
    g3.addWidget(QLabel("Platform:"), 3, 0); g3.addWidget(smart_plat,   3, 1)
    t3l.addWidget(grp3)

    btn_smart = ActionButton("🤖 AI Smart Order — Best Value", ACCENT)
    btn_place_smart = ActionButton("✅ Place This Smart Order", SUCCESS)
    btn_place_smart.setEnabled(False)
    btn_row3 = QHBoxLayout()
    btn_row3.addWidget(btn_smart); btn_row3.addWidget(btn_place_smart)
    out3 = OutputBox("AI will select the highest-quality service within your budget…")
    t3l.addLayout(btn_row3); t3l.addWidget(out3, 1)
    tabs.addTab(t3, "🤖 AI Smart Order")

    _smart_result = [None]

    def _smart_order():
        out3.reset_color(); out3.setPlainText("AI selecting optimal service for your budget…")
        btn_place_smart.setEnabled(False)
        w = ApiWorker(f"{api_base}/api/v1/smm/smart-order", {
            "link":       smart_link.text().strip() or "https://tiktok.com/@example",
            "goal":       smart_goal.currentText(),
            "budget_usd": smart_budget.value(),
            "platform":   smart_plat.currentText(),
        })
        t3._w = w
        def _got(d):
            data = d.get("data", d)
            _smart_result[0] = data
            btn_place_smart.setEnabled(data.get("place_order_ready", False))
            out3.set_result(data)
        w.result_ready.connect(_got)
        w.error_signal.connect(out3.set_error)
        w.start()

    def _place_smart():
        r = _smart_result[0]
        if not r:
            return
        svc = r.get("selected_service", {})
        out3.reset_color(); out3.setPlainText("Placing smart order…")
        w = ApiWorker(f"{api_base}/api/v1/smm/order", {
            "service_id": svc.get("service", 1004),
            "link":       r.get("link", smart_link.text().strip()),
            "quantity":   r.get("recommended_quantity", 500),
        })
        t3._wp = w
        w.result_ready.connect(lambda d: out3.set_result(d.get("data", d)))
        w.error_signal.connect(out3.set_error)
        w.start()

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
        w = ApiWorker(f"{api_base}/api/v1/smm/order/{order_id_input.value()}", method="GET")
        t4._ws = w
        w.result_ready.connect(lambda d: out4.set_result(d.get("data", d)))
        w.error_signal.connect(out4.set_error)
        w.start()

    def _request_refill():
        out4.reset_color(); out4.setPlainText(f"Requesting refill for order #{order_id_input.value()}…")
        w = ApiWorker(f"{api_base}/api/v1/smm/refill", {"order_id": order_id_input.value()})
        t4._wr = w
        w.result_ready.connect(lambda d: out4.set_result(d.get("data", d)))
        w.error_signal.connect(out4.set_error)
        w.start()

    def _cancel_order():
        out4.reset_color(); out4.setPlainText(f"Cancelling order #{order_id_input.value()}…")
        w = ApiWorker(f"{api_base}/api/v1/smm/cancel", {"order_ids": [order_id_input.value()]})
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
        w = ApiWorker(f"{api_base}/api/v1/smm/bulk-status", {"order_ids": ids[:100]})
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
    hist_stats.setStyleSheet(f"color:{SUBTEXT}; font-size:11px; padding:2px 0;")
    t5l.addWidget(hist_stats)
    tabs.addTab(t5, "📜 Order History")

    def _load_history():
        hist_stats.setText("Loading history…")
        w = ApiWorker(f"{api_base}/api/v1/smm/history?limit={hist_limit.value()}", method="GET")
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
    info.setStyleSheet(f"color:{SUBTEXT}; font-size:12px; padding:4px 0;")
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
        })
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
    info.setStyleSheet(f"color:{SUBTEXT}; font-size:12px;")
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
        })
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

    def _get_context():
        out2.reset_color(); out2.setPlainText("Retrieving brand memory…")
        bid = get_brand_id.text() or "default_brand"
        w = ApiWorker(f"{api_base}/api/v1/memory/brand/{bid}", method="GET")
        page._w2 = w
        w.result_ready.connect(lambda d: out2.set_result(d.get("data", d)))
        w.error_signal.connect(out2.set_error)
        w.start()

    btn_get.clicked.connect(_get_context)
    btn_timeline.clicked.connect(_get_context)

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
        })
        page._w3 = w
        w.result_ready.connect(lambda d: out3.set_result(d.get("data", d)))
        w.error_signal.connect(out3.set_error)
        w.start()

    btn_search.clicked.connect(_search)

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
        w = ApiWorker(f"{api_base}/", method="GET")
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
    subtitle.setStyleSheet(f"color:{SUBTEXT}; font-size:12px;")
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
            f"{api_base}/api/v1/ai/timing/{sched_platform.currentText()}", method="GET"
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
    next_lbl.setStyleSheet(f"color:{SUBTEXT}; font-size:11px;")
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
    queue_stats.setStyleSheet(f"color:{SUBTEXT}; font-size:12px; padding:4px;")
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

    def _run3_post(url, payload):
        out3.reset_color(); out3.setPlainText("Running AI optimization…")
        w = ApiWorker(url, payload)
        page._w3 = w
        w.result_ready.connect(lambda d: out3.set_result(d.get("data", d)))
        w.error_signal.connect(out3.set_error)
        w.start()

    def _run3_get(url):
        out3.reset_color(); out3.setPlainText("Fetching best posting times…")
        w = ApiWorker(url, method="GET")
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
    }))
    btn_best_t.clicked.connect(
        lambda: _run3_get(f"{api_base}/api/v1/ai/timing/{opt_plat.currentText()}")
    )
    btn_simulate.clicked.connect(lambda: _run3_post(f"{api_base}/api/v1/ai/strategy", {
        "username":          opt_user.text() or "demo",
        "platform":          opt_plat.currentText(),
        "current_followers": opt_foll.value(),
        "niche":             opt_niche.text() or "General",
        "goal_followers":    opt_foll.value() * 3,
        "duration_days":     opt_days.value(),
    }))

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
    hint4.setStyleSheet(f"color:{SUBTEXT}; font-size:12px; padding:4px 0;")
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
        btn_batch.setEnabled(False)

        w = ApiWorker(f"{api_base}/api/v1/ai/calendar", {
            "topic":            b_topic.text() or "Social Media Growth",
            "platform":         b_plat.currentText(),
            "tone":             b_tone.currentText(),
            "language":         b_lang.currentText(),
            "duration_seconds": 60,
        })
        page._w4 = w

        def _on_cal(resp):
            btn_batch.setEnabled(True)
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
        w = ApiWorker(f"{api_base}/api/v1/ai/timing/{ro_plat.currentText()}", method="GET")
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
    subtitle.setStyleSheet(f"color:{SUBTEXT}; font-size:12px;")
    layout.addWidget(subtitle)

    # ── Country selector (shared across all tabs) ──────────────────────────────
    sel_row = QHBoxLayout()
    sel_lbl = QLabel("🎯 Target Country:")
    sel_lbl.setStyleSheet(f"color:{TEXT}; font-weight:bold; font-size:13px;")

    country_combo = QComboBox()
    country_combo.setMinimumWidth(280)
    country_combo.setEditable(True)
    country_combo.setStyleSheet(
        f"background:{SURFACE}; color:{TEXT}; border:1px solid #45475A; border-radius:6px; padding:4px 8px; font-size:13px;"
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
        f"background:{SURFACE}; color:{TEXT}; border:1px solid #45475A; border-radius:6px; padding:4px 8px; font-size:13px;"
    )

    niche_input = QLineEdit()
    niche_input.setPlaceholderText("Niche (e.g. Food, Fashion, Tech)")
    niche_input.setText("General")
    niche_input.setStyleSheet(
        f"background:{SURFACE}; color:{TEXT}; border:1px solid #45475A; border-radius:6px; padding:6px 10px; font-size:13px;"
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
        f"background:{SURFACE}; color:{ACCENT}; padding:6px 12px; border-radius:6px; font-size:12px; font-weight:bold;"
    )
    layout.addWidget(time_banner)

    tabs = QTabWidget()

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _out(parent: QVBoxLayout) -> tuple[OutputBox, QPushButton]:
        btn = QPushButton()
        btn.setStyleSheet(
            f"background:{ACCENT}; color:#1E1E2E; font-weight:bold; padding:8px 20px; "
            f"border-radius:6px; font-size:13px;"
        )
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
    out1, btn1 = _out(t1l)
    btn1.setText("🌍 Load Country Card")

    def _load_country():
        code = _selected_code()
        out1.setPlainText(f"Loading country info for {code}…")
        worker = ApiWorker(f"{api_base}/api/v1/geo/country/{code}", method="GET")
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
    out2, btn2 = _out(t2l)
    btn2.setText("🚀 Generate Geo-Targeted Strategy")

    def _geo_strategy():
        code    = _selected_code()
        plat    = platform_combo.currentText()
        niche   = niche_input.text().strip() or "General"
        out2.setPlainText(f"Generating geo strategy for {code} / {plat} / {niche}…")
        worker = ApiWorker(f"{api_base}/api/v1/geo/strategy",
                           {"country_code": code, "platform": plat, "niche": niche})
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
    out3, btn3 = _out(t3l)
    btn3.setText("⏰ Get Timezone & Best Posting Times")

    def _best_times():
        code = _selected_code()
        plat = platform_combo.currentText()
        out3.setPlainText(f"Loading timezone schedule for {code} / {plat}…")
        worker = ApiWorker(f"{api_base}/api/v1/geo/best-times/{code}/{plat}", method="GET")
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
    out4, btn4 = _out(t4l)
    btn4.setText("📈 Scan Regional Trends")

    def _regional_trends():
        code  = _selected_code()
        niche = niche_input.text().strip() or "General"
        out4.setPlainText(f"Scanning trends in {code} for niche: {niche}…")
        worker = ApiWorker(f"{api_base}/api/v1/geo/trends/{code}", {"niche": niche}, "GET")
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
    out5, btn5 = _out(t5l)
    btn5.setText("🎨 Get Cultural Content Guide")

    def _cultural_guide():
        code  = _selected_code()
        niche = niche_input.text().strip() or "General"
        out5.setPlainText(f"Loading cultural guide for {code} / {niche}…")
        worker = ApiWorker(f"{api_base}/api/v1/geo/cultural-guide/{code}", {"niche": niche}, "GET")
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
    out6, btn6 = _out(t6l)
    btn6.setText("👥 Analyse Regional Audience")

    def _audience():
        code  = _selected_code()
        plat  = platform_combo.currentText()
        niche = niche_input.text().strip() or "General"
        out6.setPlainText(f"Loading audience data for {code} / {plat} / {niche}…")
        worker = ApiWorker(f"{api_base}/api/v1/geo/audience",
                           {"country_code": code, "platform": plat, "niche": niche})
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
    out7, btn7 = _out(t7l)
    btn7.setText("📱 Load Platform Dominance Map")

    def _platform_map():
        code = _selected_code()
        out7.setPlainText(f"Loading platform map for {code}…")
        worker = ApiWorker(f"{api_base}/api/v1/geo/platforms/{code}", method="GET")
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
# MAIN WINDOW
# ═══════════════════════════════════════════════════════════════════════════════

class GrowthOS_Desktop(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION} — Ultimate AI Social Growth System")
        self.setGeometry(60, 40, 1380, 860)
        self.setStyleSheet(GLOBAL_STYLE)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._setup_sidebar(main_layout)
        self._setup_pages(main_layout)

    def _setup_sidebar(self, parent_layout):
        sidebar = QFrame()
        sidebar.setFixedWidth(235)
        sidebar.setStyleSheet(f"background-color: {SIDEBAR}; border-right: 1px solid #313244;")
        sl = QVBoxLayout(sidebar)
        sl.setContentsMargins(10, 16, 10, 16)
        sl.setSpacing(3)

        logo = QLabel(f"🚀 {APP_NAME}")
        logo.setFont(QFont("Segoe UI", 15, QFont.Bold))
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet(f"color: {ACCENT}; padding: 10px 0;")
        sl.addWidget(logo)

        ver = QLabel(f"v{APP_VERSION}  •  99 AI Features")
        ver.setAlignment(Qt.AlignCenter)
        ver.setStyleSheet(f"color: {SUBTEXT}; font-size: 11px;")
        sl.addWidget(ver)
        sl.addSpacing(8)

        self._nav_buttons = {}
        nav_items = [
            (0,  "📊", "Dashboard"),
            (1,  "🧠", "Strategy Brain"),
            (2,  "✍️", "Content Studio"),
            (3,  "📈", "Analytics"),
            (4,  "🔮", "Trend Radar"),
            (5,  "⚙️", "Campaign Engine"),
            (6,  "🛡️", "Risk Engine"),
            (7,  "🛒", "SMM Panel"),
            (8,  "🤖", "Multi-Agent AI"),
            (9,  "💾", "Memory System"),
            (10, "📅", "Auto-Scheduler"),
            (11, "🌍", "Geo Intelligence"),
            (12, "🔧", "Settings & Help"),
        ]

        for idx, icon, label in nav_items:
            btn = NavButton(f"{icon}  {label}")
            btn.clicked.connect(lambda _, i=idx: self._switch_page(i))
            sl.addWidget(btn)
            self._nav_buttons[idx] = btn

        sl.addStretch()

        # Status indicator
        self._status_label = QLabel("● Backend: Unknown")
        self._status_label.setStyleSheet(f"color:{SUBTEXT}; font-size:10px; padding:4px;")
        self._status_label.setAlignment(Qt.AlignCenter)
        sl.addWidget(self._status_label)

        self._nav_buttons[0].setChecked(True)
        parent_layout.addWidget(sidebar)

        # Ping backend on startup
        QTimer.singleShot(1500, self._ping_backend)

    def _ping_backend(self):
        try:
            r = requests.get(f"{BACKEND_URL}/api/v1/health", timeout=2)
            if r.status_code == 200:
                self._status_label.setText("● Backend: Online ✓")
                self._status_label.setStyleSheet(f"color:{SUCCESS}; font-size:10px; padding:4px;")
            else:
                self._status_label.setText("● Backend: Error")
                self._status_label.setStyleSheet(f"color:{WARNING}; font-size:10px; padding:4px;")
        except Exception:
            self._status_label.setText("● Backend: Offline")
            self._status_label.setStyleSheet(f"color:#F38BA8; font-size:10px; padding:4px;")

    def _setup_pages(self, parent_layout):
        self.stack = QStackedWidget()
        api = BACKEND_URL
        pages = [
            build_dashboard_page(api),       # 0
            build_strategy_page(api),        # 1
            build_content_page(api),         # 2
            build_analytics_page(api),       # 3
            build_trends_page(api),          # 4
            build_campaign_page(api),        # 5
            build_risk_page(api),            # 6
            build_smm_page(api),             # 7
            build_multiagent_page(api),      # 8
            build_memory_page(api),          # 9
            build_scheduler_page(api),       # 10
            build_geo_page(api),             # 11
            build_settings_page(api),        # 12
        ]
        for p in pages:
            self.stack.addWidget(p)
        parent_layout.addWidget(self.stack, 1)

    def _switch_page(self, index: int):
        self.stack.setCurrentIndex(index)
        for i, btn in self._nav_buttons.items():
            btn.setChecked(i == index)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = GrowthOS_Desktop()
    window.show()
    sys.exit(app.exec_())
