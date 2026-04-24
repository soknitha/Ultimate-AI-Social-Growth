"""
GrowthOS AI v2.0 — Login Window
================================
PyQt5 login screen that gates access to the main application.

Features:
  • Dark Catppuccin Mocha theme (matches main app exactly)
  • Username / password with show-toggle
  • Remember username (saved in .remember_user)
  • Forced first-login password change dialog
  • Live error / success status messages
  • User count stats bar
  • Drag-to-move frameless window
"""

import os
import sys

from PyQt5.QtWidgets import (
    QApplication, QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox, QFrame,
    QGraphicsDropShadowEffect,
)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont, QColor

try:
    from config import APP_NAME, APP_VERSION
except ImportError:
    APP_NAME    = "GrowthOS AI"
    APP_VERSION = "2.0"

import admin

# ── Theme (mirrors desktop_app.py constants) ──────────────────────────────────
DARK_BG  = "#1E1E2E"
SIDEBAR  = "#181825"
SURFACE  = "#313244"
ACCENT   = "#89B4FA"
SUCCESS  = "#A6E3A1"
WARNING  = "#FAB387"
ERROR    = "#F38BA8"
TEXT     = "#CDD6F4"
SUBTEXT  = "#6C7086"

_REMEMBER_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".remember_user")

# ── Shared input style ────────────────────────────────────────────────────────
_INPUT_STYLE = f"""
    QLineEdit {{
        background: {SURFACE};
        color: {TEXT};
        border: 1px solid {SUBTEXT};
        border-radius: 8px;
        padding: 0 12px;
        font-size: 13px;
    }}
    QLineEdit:focus {{ border: 1px solid {ACCENT}; }}
"""

_BTN_ACCENT = f"""
    QPushButton {{
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 {ACCENT}, stop:1 #74c7ec);
        color: #1E1E2E;
        border: none;
        border-radius: 10px;
        font-size: 14px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 #b4cdf8, stop:1 #89dceb);
    }}
    QPushButton:pressed {{ background: {ACCENT}; }}
    QPushButton:disabled {{ background: {SURFACE}; color: {SUBTEXT}; }}
"""


# ═══════════════════════════════════════════════════════════════════════════════
# Change Password Dialog  (shown on force_pw_change = True)
# ═══════════════════════════════════════════════════════════════════════════════

class ChangePasswordDialog(QDialog):
    """Force-change password dialog. Shown when force_pw_change is True."""

    def __init__(self, token: str, parent=None):
        super().__init__(parent)
        self.token = token
        self.setWindowTitle("Set New Password — Required")
        self.setModal(True)
        self.setFixedSize(400, 360)
        self.setStyleSheet(f"""
            QDialog  {{ background: {DARK_BG}; color: {TEXT}; font-family: 'Segoe UI'; }}
            QLabel   {{ color: {TEXT}; }}
        """)
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(32, 28, 32, 28)
        lay.setSpacing(12)

        title = QLabel("🔐  First Login — Set Your Password")
        title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        title.setStyleSheet(f"color: {ACCENT};")
        title.setWordWrap(True)
        lay.addWidget(title)

        note = QLabel(
            "For your security, please set a new password "
            "before accessing the application."
        )
        note.setStyleSheet(f"color: {SUBTEXT}; font-size: 11px;")
        note.setWordWrap(True)
        lay.addWidget(note)

        lay.addSpacing(4)

        for label_text, attr, placeholder in [
            ("Current Password", "_old_pw",  "Enter current password"),
            ("New Password",     "_new_pw",  "Minimum 8 characters"),
            ("Confirm New",      "_conf_pw", "Repeat new password"),
        ]:
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-size: 11px; font-weight: bold;")
            lay.addWidget(lbl)
            inp = QLineEdit()
            inp.setEchoMode(QLineEdit.Password)
            inp.setPlaceholderText(placeholder)
            inp.setFixedHeight(38)
            inp.setStyleSheet(_INPUT_STYLE)
            setattr(self, attr, inp)
            lay.addWidget(inp)

        self._status = QLabel("")
        self._status.setWordWrap(True)
        self._status.setStyleSheet(f"color: {ERROR}; font-size: 11px;")
        lay.addWidget(self._status)

        btn = QPushButton("Set New Password  →")
        btn.setFixedHeight(44)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(_BTN_ACCENT)
        btn.clicked.connect(self._submit)
        lay.addWidget(btn)

    def _submit(self):
        old  = self._old_pw.text()
        new  = self._new_pw.text()
        conf = self._conf_pw.text()
        if new != conf:
            self._status.setText("New passwords do not match.")
            return
        try:
            admin.change_password(self.token, old, new)
            self.accept()
        except Exception as e:
            self._status.setText(str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# Login Window
# ═══════════════════════════════════════════════════════════════════════════════

class LoginWindow(QDialog):
    """
    Frameless, draggable login dialog.
    After successful login, `self.logged_in_user` holds the user info dict.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logged_in_user: dict = {}
        self._drag_pos: QPoint | None = None

        self.setWindowTitle(f"{APP_NAME} — Login")
        self.setFixedSize(440, 540)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self._build()
        self._load_remembered()

    # ── UI construction ───────────────────────────────────────────────────────
    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 20, 20, 20)

        # Card
        card = QFrame()
        card.setObjectName("loginCard")
        card.setStyleSheet(f"""
            QFrame#loginCard {{
                background: {DARK_BG};
                border-radius: 18px;
                border: 1px solid {SURFACE};
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(50)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 140))
        card.setGraphicsEffect(shadow)
        outer.addWidget(card)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(40, 36, 40, 32)
        lay.setSpacing(0)

        # ── Header ────────────────────────────────────────────────────────────
        icon_lbl = QLabel("🚀")
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet("font-size: 46px;")
        lay.addWidget(icon_lbl)

        lay.addSpacing(6)

        title_lbl = QLabel(APP_NAME)
        title_lbl.setAlignment(Qt.AlignCenter)
        title_lbl.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title_lbl.setStyleSheet(f"color: {TEXT}; letter-spacing: 1px;")
        lay.addWidget(title_lbl)

        sub_lbl = QLabel(f"v{APP_VERSION}  •  AI Social Growth Platform")
        sub_lbl.setAlignment(Qt.AlignCenter)
        sub_lbl.setStyleSheet(f"color: {SUBTEXT}; font-size: 11px;")
        lay.addWidget(sub_lbl)

        lay.addSpacing(20)

        # ── Divider ───────────────────────────────────────────────────────────
        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"border: 1px solid {SURFACE};")
        div.setFixedHeight(1)
        lay.addWidget(div)

        lay.addSpacing(18)

        # ── Username ──────────────────────────────────────────────────────────
        user_lbl = QLabel("Username")
        user_lbl.setStyleSheet(f"color: {TEXT}; font-size: 11px; font-weight: bold;")
        lay.addWidget(user_lbl)
        lay.addSpacing(5)

        self._user_inp = QLineEdit()
        self._user_inp.setPlaceholderText("Enter your username")
        self._user_inp.setFixedHeight(44)
        self._user_inp.setStyleSheet(_INPUT_STYLE)
        lay.addWidget(self._user_inp)

        lay.addSpacing(12)

        # ── Password ──────────────────────────────────────────────────────────
        pw_lbl = QLabel("Password")
        pw_lbl.setStyleSheet(f"color: {TEXT}; font-size: 11px; font-weight: bold;")
        lay.addWidget(pw_lbl)
        lay.addSpacing(5)

        pw_row = QHBoxLayout()
        pw_row.setSpacing(6)

        self._pw_inp = QLineEdit()
        self._pw_inp.setEchoMode(QLineEdit.Password)
        self._pw_inp.setPlaceholderText("Enter your password")
        self._pw_inp.setFixedHeight(44)
        self._pw_inp.setStyleSheet(_INPUT_STYLE)
        self._pw_inp.returnPressed.connect(self._do_login)
        pw_row.addWidget(self._pw_inp)

        self._eye_btn = QPushButton("👁")
        self._eye_btn.setFixedSize(44, 44)
        self._eye_btn.setCheckable(True)
        self._eye_btn.setCursor(Qt.PointingHandCursor)
        self._eye_btn.setToolTip("Show / hide password")
        self._eye_btn.setStyleSheet(f"""
            QPushButton {{
                background: {SURFACE}; border: 1px solid {SUBTEXT};
                border-radius: 8px; font-size: 18px;
            }}
            QPushButton:checked {{ background: {ACCENT}; color: #1E1E2E; border-color: {ACCENT}; }}
        """)
        self._eye_btn.toggled.connect(
            lambda on: self._pw_inp.setEchoMode(
                QLineEdit.Normal if on else QLineEdit.Password
            )
        )
        pw_row.addWidget(self._eye_btn)
        lay.addLayout(pw_row)

        lay.addSpacing(10)

        # ── Remember me ───────────────────────────────────────────────────────
        self._remember_cb = QCheckBox("Remember my username")
        self._remember_cb.setStyleSheet(f"color: {SUBTEXT}; font-size: 11px;")
        lay.addWidget(self._remember_cb)

        lay.addSpacing(8)

        # ── Status message ────────────────────────────────────────────────────
        self._status_lbl = QLabel("")
        self._status_lbl.setAlignment(Qt.AlignCenter)
        self._status_lbl.setWordWrap(True)
        self._status_lbl.setFixedHeight(22)
        self._status_lbl.setStyleSheet(f"font-size: 11px; color: {ERROR};")
        lay.addWidget(self._status_lbl)

        lay.addSpacing(8)

        # ── Login button ──────────────────────────────────────────────────────
        self._login_btn = QPushButton("🔓  Sign In")
        self._login_btn.setFixedHeight(48)
        self._login_btn.setCursor(Qt.PointingHandCursor)
        self._login_btn.setStyleSheet(_BTN_ACCENT)
        self._login_btn.clicked.connect(self._do_login)
        lay.addWidget(self._login_btn)

        lay.addSpacing(14)

        # ── Stats bar ─────────────────────────────────────────────────────────
        try:
            s = admin.get_stats()
            stats_txt = (
                f"👥 {s['total']} users  •  "
                f"✅ {s['active']} active  •  "
                f"👑 {s['admins']} admin  •  "
                f"👤 {s['members']} member"
            )
        except Exception:
            stats_txt = "🔐 Secure authentication"
        stats_lbl = QLabel(stats_txt)
        stats_lbl.setAlignment(Qt.AlignCenter)
        stats_lbl.setStyleSheet(f"color: {SUBTEXT}; font-size: 10px;")
        lay.addWidget(stats_lbl)

        # ── Close button (top-right of card) ──────────────────────────────────
        close_btn = QPushButton("✕")
        close_btn.setParent(card)
        close_btn.setFixedSize(30, 30)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {SUBTEXT};
                border: none; font-size: 15px;
            }}
            QPushButton:hover {{ color: {ERROR}; }}
        """)
        close_btn.clicked.connect(self.reject)
        # Position inside the card (top-right corner)
        close_btn.move(card.width() - 40, 10)

    # ── Drag support ──────────────────────────────────────────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos is not None:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    # ── Logic ─────────────────────────────────────────────────────────────────
    def _set_status(self, msg: str, color: str = ERROR):
        self._status_lbl.setText(msg)
        self._status_lbl.setStyleSheet(f"font-size: 11px; color: {color};")

    def _load_remembered(self):
        if os.path.exists(_REMEMBER_FILE):
            try:
                uname = open(_REMEMBER_FILE, "r", encoding="utf-8").read().strip()
                if uname:
                    self._user_inp.setText(uname)
                    self._remember_cb.setChecked(True)
                    self._pw_inp.setFocus()
            except Exception:
                pass

    def _do_login(self):
        username = self._user_inp.text().strip()
        password = self._pw_inp.text()
        if not username or not password:
            self._set_status("Please enter both username and password.")
            return

        self._login_btn.setEnabled(False)
        self._login_btn.setText("⏳  Signing in…")
        self._set_status("")

        try:
            user_info = admin.login(username, password)
        except ValueError as e:
            self._set_status(str(e))
            self._login_btn.setEnabled(True)
            self._login_btn.setText("🔓  Sign In")
            return

        # Persist / clear remember-me
        if self._remember_cb.isChecked():
            try:
                with open(_REMEMBER_FILE, "w", encoding="utf-8") as f:
                    f.write(username)
            except Exception:
                pass
        else:
            try:
                if os.path.exists(_REMEMBER_FILE):
                    os.remove(_REMEMBER_FILE)
            except Exception:
                pass

        # Force password change on first login
        if user_info.get("force_pw_change"):
            dlg = ChangePasswordDialog(user_info["token"], self)
            if dlg.exec_() != QDialog.Accepted:
                self._login_btn.setEnabled(True)
                self._login_btn.setText("🔓  Sign In")
                self._set_status("Password change required before you can continue.", color=WARNING)
                return

        self._set_status(f"Welcome, {user_info['display_name']}! 🎉", color=SUCCESS)
        self.logged_in_user = user_info
        self.accept()


# ── Standalone test ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    dlg = LoginWindow()
    if dlg.exec_() == QDialog.Accepted:
        print("Logged in:", dlg.logged_in_user)
    sys.exit(0)
