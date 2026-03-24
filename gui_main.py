"""
gui_main.py
-----------
Modern PySide6 GUI for the Password Security Toolkit.

Layout:
  ┌─────────────┬───────────────────────────────────────────┐
  │  SIDEBAR    │           MAIN CONTENT PANEL              │
  │  • Dashboard│  Stacked pages switch based on sidebar     │
  │  • Analyzer │  navigation.                               │
  │  • Wordlist │                                            │
  │  • Reports  │                                            │
  │  • Settings │                                            │
  └─────────────┴───────────────────────────────────────────┘
"""

import os
import sys
import logging
from datetime import datetime

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit,
    QProgressBar, QStackedWidget, QScrollArea,
    QFrame, QGridLayout, QFileDialog, QMessageBox,
    QCheckBox, QSizePolicy, QSpacerItem,
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QColor, QPalette, QIcon, QCursor

# ── Backend imports ──────────────────────────────────────────────────────────
from password_analyzer  import analyze_password
from wordlist_generator import generate_wordlist, save_wordlist
from report_generator   import generate_report

logger = logging.getLogger("PasswordToolkit")

# ════════════════════════════════════════════════════════════════════
#  COLOUR PALETTE & STYLESHEET
# ════════════════════════════════════════════════════════════════════

DARK_STYLE = """
QMainWindow, QWidget {
    background-color: #0d1117;
    color: #c9d1d9;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 13px;
}

/* ── Sidebar ─────────────────────────────── */
#sidebar {
    background-color: #010409;
    border-right: 1px solid #21262d;
    min-width: 200px;
    max-width: 200px;
}

#sidebar QLabel#logo {
    color: #58a6ff;
    font-size: 18px;
    font-weight: 700;
    padding: 20px 16px 8px 16px;
    letter-spacing: 1px;
}

#sidebar QLabel#tagline {
    color: #6e7681;
    font-size: 10px;
    padding: 0 16px 20px 16px;
}

/* nav buttons */
#nav_btn {
    background: transparent;
    color: #8b949e;
    border: none;
    border-radius: 8px;
    text-align: left;
    padding: 10px 16px;
    font-size: 13px;
    font-weight: 500;
}
#nav_btn:hover {
    background-color: #161b22;
    color: #c9d1d9;
}
#nav_btn[active="true"] {
    background-color: #1f2937;
    color: #58a6ff;
    border-left: 3px solid #58a6ff;
}

/* ── Cards / Panels ──────────────────────── */
#card {
    background-color: #161b22;
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 16px;
}

#section_title {
    color: #c9d1d9;
    font-size: 15px;
    font-weight: 700;
    padding-bottom: 4px;
}

#page_title {
    color: #e6edf3;
    font-size: 22px;
    font-weight: 700;
}

#subtitle {
    color: #6e7681;
    font-size: 12px;
}

/* ── Input fields ────────────────────────── */
QLineEdit {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 8px;
    color: #c9d1d9;
    padding: 8px 12px;
    font-size: 13px;
}
QLineEdit:focus {
    border: 1px solid #58a6ff;
}
QLineEdit::placeholder {
    color: #484f58;
}

/* ── Buttons ─────────────────────────────── */
#primary_btn {
    background-color: #238636;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 9px 20px;
    font-size: 13px;
    font-weight: 600;
}
#primary_btn:hover  { background-color: #2ea043; }
#primary_btn:pressed{ background-color: #1a7f37; }

#secondary_btn {
    background-color: transparent;
    color: #58a6ff;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 9px 20px;
    font-size: 13px;
    font-weight: 500;
}
#secondary_btn:hover  { border-color: #58a6ff; background-color: #161b22; }
#secondary_btn:pressed{ background-color: #0d1117; }

#danger_btn {
    background-color: transparent;
    color: #f85149;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 9px 20px;
    font-size: 13px;
}
#danger_btn:hover { border-color: #f85149; background-color: #1a0d0e; }

#icon_btn {
    background: transparent;
    border: none;
    color: #6e7681;
    padding: 4px 8px;
    border-radius: 4px;
}
#icon_btn:hover { color: #c9d1d9; background: #21262d; }

/* ── Progress bar ────────────────────────── */
QProgressBar {
    background-color: #21262d;
    border: none;
    border-radius: 6px;
    height: 14px;
    text-align: center;
    font-size: 10px;
    color: #c9d1d9;
}
QProgressBar::chunk { border-radius: 6px; }

/* ── Text area ───────────────────────────── */
QTextEdit {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 8px;
    color: #c9d1d9;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    padding: 8px;
}

/* ── Scroll bars ─────────────────────────── */
QScrollBar:vertical {
    background: #0d1117;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #30363d;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover { background: #484f58; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

/* ── Separator ───────────────────────────── */
QFrame[frameShape="4"], QFrame[frameShape="5"] {
    color: #21262d;
}

/* ── Checkboxes ──────────────────────────── */
QCheckBox { color: #c9d1d9; spacing: 6px; }
QCheckBox::indicator {
    width: 16px; height: 16px;
    border: 1px solid #30363d;
    border-radius: 4px;
    background: #0d1117;
}
QCheckBox::indicator:checked {
    background-color: #238636;
    border-color: #238636;
}
"""

LIGHT_STYLE = """
QMainWindow, QWidget {
    background-color: #f6f8fa;
    color: #1f2328;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 13px;
}
#sidebar {
    background-color: #ffffff;
    border-right: 1px solid #d0d7de;
    min-width: 200px; max-width: 200px;
}
#sidebar QLabel#logo  { color: #0969da; font-size: 18px; font-weight: 700; padding: 20px 16px 8px 16px; }
#sidebar QLabel#tagline{ color: #656d76; font-size: 10px; padding: 0 16px 20px 16px; }
#nav_btn {
    background: transparent; color: #57606a; border: none;
    border-radius: 8px; text-align: left;
    padding: 10px 16px; font-size: 13px; font-weight: 500;
}
#nav_btn:hover { background-color: #f6f8fa; color: #1f2328; }
#nav_btn[active="true"] {
    background-color: #ddf4ff; color: #0969da; border-left: 3px solid #0969da;
}
#card { background-color: #ffffff; border: 1px solid #d0d7de; border-radius: 10px; padding: 16px; }
#section_title { color: #1f2328; font-size: 15px; font-weight: 700; }
#page_title    { color: #1f2328; font-size: 22px; font-weight: 700; }
#subtitle      { color: #656d76; font-size: 12px; }
QLineEdit {
    background: #ffffff; border: 1px solid #d0d7de; border-radius: 8px;
    color: #1f2328; padding: 8px 12px;
}
QLineEdit:focus { border: 1px solid #0969da; }
#primary_btn {
    background-color: #1f883d; color: #fff; border: none;
    border-radius: 8px; padding: 9px 20px; font-weight: 600;
}
#primary_btn:hover { background-color: #2da44e; }
#secondary_btn {
    background: transparent; color: #0969da; border: 1px solid #d0d7de;
    border-radius: 8px; padding: 9px 20px;
}
#secondary_btn:hover { border-color: #0969da; }
#danger_btn {
    background: transparent; color: #cf222e; border: 1px solid #d0d7de;
    border-radius: 8px; padding: 9px 20px;
}
#danger_btn:hover { border-color: #cf222e; }
QProgressBar {
    background: #eaeef2; border: none; border-radius: 6px; height: 14px;
}
QProgressBar::chunk { border-radius: 6px; }
QTextEdit {
    background: #ffffff; border: 1px solid #d0d7de; border-radius: 8px;
    color: #1f2328; font-family: 'Consolas', monospace; font-size: 12px; padding: 8px;
}
QScrollBar:vertical { background: #f6f8fa; width: 8px; }
QScrollBar::handle:vertical { background: #d0d7de; border-radius: 4px; }
QCheckBox { color: #1f2328; }
QCheckBox::indicator { width:16px;height:16px;border:1px solid #d0d7de;border-radius:4px;background:#fff; }
QCheckBox::indicator:checked { background:#1f883d;border-color:#1f883d; }
#icon_btn { background:transparent;border:none;color:#57606a;padding:4px 8px;border-radius:4px; }
#icon_btn:hover { color:#1f2328;background:#eaeef2; }
"""


# ════════════════════════════════════════════════════════════════════
#  HELPER WIDGETS
# ════════════════════════════════════════════════════════════════════

def make_separator():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)
    return line


def card_widget(layout):
    """Wrap a layout inside a styled card frame."""
    frame = QFrame()
    frame.setObjectName("card")
    frame.setLayout(layout)
    return frame


class StatCard(QFrame):
    """Small statistics card with a big number and label."""
    def __init__(self, value: str, label: str, color: str = "#58a6ff"):
        super().__init__()
        self.setObjectName("card")
        lay = QVBoxLayout(self)
        lay.setSpacing(4)

        val_lbl = QLabel(value)
        val_lbl.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: 700;")
        val_lbl.setAlignment(Qt.AlignCenter)

        lbl = QLabel(label)
        lbl.setStyleSheet("color: #6e7681; font-size: 11px;")
        lbl.setAlignment(Qt.AlignCenter)

        lay.addWidget(val_lbl)
        lay.addWidget(lbl)


# ════════════════════════════════════════════════════════════════════
#  PAGE: DASHBOARD
# ════════════════════════════════════════════════════════════════════

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.setSpacing(20)

        # Header
        title = QLabel("🛡  Password Security Toolkit")
        title.setObjectName("page_title")
        sub = QLabel("A professional cybersecurity utility for password analysis & wordlist generation.")
        sub.setObjectName("subtitle")
        outer.addWidget(title)
        outer.addWidget(sub)
        outer.addWidget(make_separator())

        # Stat cards row
        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)
        stats_row.addWidget(StatCard("5", "Modules",    "#58a6ff"))
        stats_row.addWidget(StatCard("∞", "Wordlists",  "#3fb950"))
        stats_row.addWidget(StatCard("0–4","Score Range","#d29922"))
        stats_row.addWidget(StatCard("txt","Export Format","#bc8cff"))
        outer.addLayout(stats_row)

        # Security tips card
        tips_lay = QVBoxLayout()
        tips_lay.setSpacing(8)
        tips_title = QLabel("💡  Quick Security Tips")
        tips_title.setObjectName("section_title")
        tips_lay.addWidget(tips_title)

        tips = [
            ("✅", "Use a password longer than 12 characters."),
            ("✅", "Mix uppercase, lowercase, digits, and symbols."),
            ("✅", "Never reuse passwords across different sites."),
            ("✅", "Use a reputable password manager."),
            ("⚠️", "Avoid using personal info like names or birthdays."),
            ("⚠️", "Dictionary words are cracked in seconds by attackers."),
            ("⚠️", "Passwords with common patterns like '123' are trivially weak."),
        ]
        for icon, tip in tips:
            row = QHBoxLayout()
            row.setSpacing(8)
            icon_lbl = QLabel(icon)
            icon_lbl.setFixedWidth(24)
            tip_lbl  = QLabel(tip)
            tip_lbl.setWordWrap(True)
            row.addWidget(icon_lbl)
            row.addWidget(tip_lbl, 1)
            tips_lay.addLayout(row)

        outer.addWidget(card_widget(tips_lay))

        # Feature overview
        feat_lay = QVBoxLayout()
        feat_lay.setSpacing(8)
        feat_title = QLabel("🔧  Features")
        feat_title.setObjectName("section_title")
        feat_lay.addWidget(feat_title)

        features = [
            ("🔍 Password Analyzer",   "Score, entropy, crack time, weakness detection"),
            ("📋 Wordlist Generator",  "Build targeted wordlists from personal data"),
            ("📄 Report Exporter",     "Generate and save detailed analysis reports"),
            ("⚙️  Settings",           "Theme switching and output directory config"),
        ]
        grid = QGridLayout()
        grid.setSpacing(10)
        for i, (feat, desc) in enumerate(features):
            f_lbl = QLabel(feat)
            f_lbl.setStyleSheet("font-weight: 600;")
            d_lbl = QLabel(desc)
            d_lbl.setStyleSheet("color: #6e7681;")
            grid.addWidget(f_lbl, i, 0)
            grid.addWidget(d_lbl, i, 1)

        feat_lay.addLayout(grid)
        outer.addWidget(card_widget(feat_lay))

        outer.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Disclaimer
        disc = QLabel(
            "⚠  Educational use only. Only test passwords you own or have permission to test."
        )
        disc.setStyleSheet("color: #f85149; font-size: 11px;")
        disc.setWordWrap(True)
        outer.addWidget(disc)


# ════════════════════════════════════════════════════════════════════
#  PAGE: PASSWORD ANALYZER
# ════════════════════════════════════════════════════════════════════

class AnalyzerPage(QWidget):
    def __init__(self):
        super().__init__()
        self._result = None
        self._password = ""
        self._build()

    # ── Public ─────────────────────────────────────────────────────
    def get_result(self):
        return self._result, self._password

    # ── Build UI ────────────────────────────────────────────────────
    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.setSpacing(20)

        # Title
        title = QLabel("🔍  Password Analyzer")
        title.setObjectName("page_title")
        sub = QLabel("Enter a password below to receive a full security analysis.")
        sub.setObjectName("subtitle")
        outer.addWidget(title)
        outer.addWidget(sub)
        outer.addWidget(make_separator())

        # ── Input card ──────────────────────────────────────────────
        input_lay = QVBoxLayout()
        input_lay.setSpacing(10)
        input_title = QLabel("Password Input")
        input_title.setObjectName("section_title")
        input_lay.addWidget(input_title)

        pw_row = QHBoxLayout()
        pw_row.setSpacing(8)

        self.pw_input = QLineEdit()
        self.pw_input.setPlaceholderText("Type or paste a password…")
        self.pw_input.setEchoMode(QLineEdit.Password)
        self.pw_input.setFixedHeight(38)
        self.pw_input.textChanged.connect(self._on_text_changed)

        self.show_btn = QPushButton("👁")
        self.show_btn.setObjectName("icon_btn")
        self.show_btn.setFixedSize(38, 38)
        self.show_btn.setToolTip("Show / hide password")
        self.show_btn.setCheckable(True)
        self.show_btn.clicked.connect(self._toggle_echo)

        pw_row.addWidget(self.pw_input, 1)
        pw_row.addWidget(self.show_btn)
        input_lay.addLayout(pw_row)

        self.analyze_btn = QPushButton("  Analyze Password")
        self.analyze_btn.setObjectName("primary_btn")
        self.analyze_btn.setFixedHeight(40)
        self.analyze_btn.clicked.connect(self._run_analysis)
        self.analyze_btn.setCursor(QCursor(Qt.PointingHandCursor))
        input_lay.addWidget(self.analyze_btn)

        outer.addWidget(card_widget(input_lay))

        # ── Results card ────────────────────────────────────────────
        results_lay = QVBoxLayout()
        results_lay.setSpacing(14)

        res_title = QLabel("Analysis Results")
        res_title.setObjectName("section_title")
        results_lay.addWidget(res_title)

        # Strength meter
        strength_lbl_row = QHBoxLayout()
        self.strength_label = QLabel("Strength")
        self.strength_score_label = QLabel("—")
        self.strength_score_label.setStyleSheet("color: #6e7681;")
        strength_lbl_row.addWidget(self.strength_label)
        strength_lbl_row.addStretch()
        strength_lbl_row.addWidget(self.strength_score_label)
        results_lay.addLayout(strength_lbl_row)

        self.strength_bar = QProgressBar()
        self.strength_bar.setRange(0, 4)
        self.strength_bar.setValue(0)
        self.strength_bar.setTextVisible(False)
        self.strength_bar.setFixedHeight(14)
        self._set_bar_color(self.strength_bar, "#484f58")
        results_lay.addWidget(self.strength_bar)

        # Grid: entropy / crack time / length / charset
        grid = QGridLayout()
        grid.setSpacing(10)
        labels = ["Entropy", "Crack Time Estimate", "Length", "Charset Size"]
        self.detail_values = {}
        for i, lbl in enumerate(labels):
            key_lbl = QLabel(lbl)
            key_lbl.setStyleSheet("color: #6e7681; font-size: 12px;")
            val_lbl = QLabel("—")
            val_lbl.setStyleSheet("font-weight: 600;")
            self.detail_values[lbl] = val_lbl
            r, c = divmod(i, 2)
            grid.addWidget(key_lbl, r * 2,     c)
            grid.addWidget(val_lbl, r * 2 + 1, c)

        results_lay.addLayout(grid)
        results_lay.addWidget(make_separator())

        # Suggestions
        sug_title = QLabel("📌  Recommendations")
        sug_title.setObjectName("section_title")
        results_lay.addWidget(sug_title)

        self.suggestions_area = QTextEdit()
        self.suggestions_area.setReadOnly(True)
        self.suggestions_area.setFixedHeight(120)
        self.suggestions_area.setPlaceholderText("Recommendations will appear here after analysis…")
        results_lay.addWidget(self.suggestions_area)

        outer.addWidget(card_widget(results_lay))
        outer.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

    # ── Slots ────────────────────────────────────────────────────────
    def _toggle_echo(self, checked):
        self.pw_input.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password)
        self.show_btn.setText("🙈" if checked else "👁")

    def _on_text_changed(self, text):
        """Live preview — lightweight char class check only."""
        if not text:
            self._reset_results()

    def _run_analysis(self):
        pw = self.pw_input.text()
        if not pw:
            QMessageBox.warning(self, "Empty Password",
                                "Please enter a password to analyze.")
            return

        self._password = pw
        result = analyze_password(pw)
        self._result = result
        self._display_result(result)
        logger.info("Analyzer page: analysis completed.")

    def _display_result(self, r: dict):
        # Strength bar
        score = r["score"]
        self.strength_bar.setValue(score)
        colors = {0: "#f85149", 1: "#f0883e", 2: "#d29922", 3: "#3fb950", 4: "#238636"}
        self._set_bar_color(self.strength_bar, colors.get(score, "#58a6ff"))
        self.strength_score_label.setText(
            f"{r['score_label']}  ({score}/4)"
        )
        self.strength_score_label.setStyleSheet(f"color: {colors.get(score, '#58a6ff')}; font-weight:600;")

        # Details
        self.detail_values["Entropy"].setText(
            f"{r['entropy']:.2f} bits  ({r['entropy_label']})"
        )
        self.detail_values["Crack Time Estimate"].setText(r["crack_time"])
        self.detail_values["Length"].setText(f"{r['length']} characters")
        self.detail_values["Charset Size"].setText(f"{r['charset_size']} symbols")

        # Suggestions
        sug_text = ""
        if r["patterns"]:
            sug_text += "⚠  Detected Patterns:\n"
            sug_text += "\n".join(f"  • {p}" for p in r["patterns"]) + "\n\n"
        sug_text += "📌  Recommendations:\n"
        sug_text += "\n".join(f"  • {s}" for s in r["suggestions"])
        self.suggestions_area.setPlainText(sug_text)

    def _reset_results(self):
        self.strength_bar.setValue(0)
        self._set_bar_color(self.strength_bar, "#484f58")
        self.strength_score_label.setText("—")
        self.strength_score_label.setStyleSheet("color: #6e7681;")
        for lbl in self.detail_values.values():
            lbl.setText("—")
        self.suggestions_area.clear()

    @staticmethod
    def _set_bar_color(bar: QProgressBar, color: str):
        bar.setStyleSheet(
            f"QProgressBar::chunk {{ background-color: {color}; border-radius: 6px; }}"
        )


# ════════════════════════════════════════════════════════════════════
#  PAGE: WORDLIST GENERATOR
# ════════════════════════════════════════════════════════════════════

class WordlistPage(QWidget):
    def __init__(self):
        super().__init__()
        self._wordlist: list[str] = []
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.setSpacing(20)

        title = QLabel("📋  Wordlist Generator")
        title.setObjectName("page_title")
        sub = QLabel("Enter personal information to generate a targeted wordlist.")
        sub.setObjectName("subtitle")
        outer.addWidget(title)
        outer.addWidget(sub)
        outer.addWidget(make_separator())

        # ── Form card ───────────────────────────────────────────────
        form_lay = QVBoxLayout()
        form_lay.setSpacing(10)
        form_title = QLabel("Personal Information")
        form_title.setObjectName("section_title")
        form_lay.addWidget(form_title)

        fields = [
            ("first_name",  "First Name",       "e.g. John"),
            ("last_name",   "Last Name",        "e.g. Smith"),
            ("pet_name",    "Pet Name",         "e.g. Buddy"),
            ("birth_year",  "Birth Year",       "e.g. 1990"),
            ("fav_number",  "Favourite Number", "e.g. 7"),
            ("city",        "City",             "e.g. London"),
        ]

        grid = QGridLayout()
        grid.setSpacing(10)
        self._fields: dict[str, QLineEdit] = {}

        for i, (key, label, placeholder) in enumerate(fields):
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #6e7681; font-size: 12px;")
            inp = QLineEdit()
            inp.setPlaceholderText(placeholder)
            inp.setFixedHeight(36)
            self._fields[key] = inp
            r, c = divmod(i, 2)
            grid.addWidget(lbl, r * 2,     c)
            grid.addWidget(inp, r * 2 + 1, c)

        form_lay.addLayout(grid)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        gen_btn = QPushButton("⚡  Generate Wordlist")
        gen_btn.setObjectName("primary_btn")
        gen_btn.setFixedHeight(40)
        gen_btn.clicked.connect(self._generate)
        gen_btn.setCursor(QCursor(Qt.PointingHandCursor))

        preview_btn = QPushButton("👁  Preview")
        preview_btn.setObjectName("secondary_btn")
        preview_btn.setFixedHeight(40)
        preview_btn.clicked.connect(self._preview)
        preview_btn.setCursor(QCursor(Qt.PointingHandCursor))

        export_btn = QPushButton("💾  Export")
        export_btn.setObjectName("secondary_btn")
        export_btn.setFixedHeight(40)
        export_btn.clicked.connect(self._export)
        export_btn.setCursor(QCursor(Qt.PointingHandCursor))

        btn_row.addWidget(gen_btn)
        btn_row.addWidget(preview_btn)
        btn_row.addWidget(export_btn)
        btn_row.addStretch()

        form_lay.addLayout(btn_row)
        outer.addWidget(card_widget(form_lay))

        # ── Preview card ────────────────────────────────────────────
        preview_lay = QVBoxLayout()
        preview_lay.setSpacing(8)

        row = QHBoxLayout()
        prev_title = QLabel("Preview")
        prev_title.setObjectName("section_title")
        self.count_label = QLabel("0 entries")
        self.count_label.setStyleSheet("color: #6e7681; font-size: 12px;")
        row.addWidget(prev_title)
        row.addStretch()
        row.addWidget(self.count_label)
        preview_lay.addLayout(row)

        self.preview_area = QTextEdit()
        self.preview_area.setReadOnly(True)
        self.preview_area.setMinimumHeight(200)
        self.preview_area.setPlaceholderText("Wordlist preview will appear here…")
        preview_lay.addWidget(self.preview_area)

        outer.addWidget(card_widget(preview_lay))
        outer.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def _collect_data(self) -> dict:
        return {k: v.text().strip() for k, v in self._fields.items()}

    def _generate(self):
        data = self._collect_data()
        if not any(data.values()):
            QMessageBox.warning(self, "No Input",
                                "Please fill in at least one field to generate a wordlist.")
            return
        self._wordlist = generate_wordlist(data)
        self.count_label.setText(f"{len(self._wordlist)} entries generated")
        self._preview()

    def _preview(self):
        if not self._wordlist:
            QMessageBox.information(self, "No Wordlist",
                                    "Generate a wordlist first.")
            return
        # Show first 500 for performance
        preview_text = "\n".join(self._wordlist[:500])
        if len(self._wordlist) > 500:
            preview_text += f"\n\n… and {len(self._wordlist) - 500} more entries (export to see all)"
        self.preview_area.setPlainText(preview_text)

    def _export(self):
        if not self._wordlist:
            QMessageBox.information(self, "No Wordlist",
                                    "Generate a wordlist before exporting.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Wordlist", "wordlist.txt", "Text Files (*.txt)"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(self._wordlist))
            QMessageBox.information(self, "Exported",
                                    f"Wordlist saved to:\n{path}")
            logger.info(f"Wordlist exported to: {path}")


# ════════════════════════════════════════════════════════════════════
#  PAGE: REPORTS
# ════════════════════════════════════════════════════════════════════

class ReportsPage(QWidget):
    def __init__(self, get_analysis_fn):
        """
        get_analysis_fn: callable that returns (result_dict, password_str)
        """
        super().__init__()
        self._get_analysis = get_analysis_fn
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.setSpacing(20)

        title = QLabel("📄  Reports")
        title.setObjectName("page_title")
        sub = QLabel("Generate and view the password analysis report.")
        sub.setObjectName("subtitle")
        outer.addWidget(title)
        outer.addWidget(sub)
        outer.addWidget(make_separator())

        # Buttons
        btn_row = QHBoxLayout()
        gen_btn = QPushButton("📝  Generate Report")
        gen_btn.setObjectName("primary_btn")
        gen_btn.setFixedHeight(40)
        gen_btn.clicked.connect(self._generate)
        gen_btn.setCursor(QCursor(Qt.PointingHandCursor))

        save_btn = QPushButton("💾  Save to File")
        save_btn.setObjectName("secondary_btn")
        save_btn.setFixedHeight(40)
        save_btn.clicked.connect(self._save)
        save_btn.setCursor(QCursor(Qt.PointingHandCursor))

        btn_row.addWidget(gen_btn)
        btn_row.addWidget(save_btn)
        btn_row.addStretch()
        outer.addLayout(btn_row)

        # Report view
        self.report_area = QTextEdit()
        self.report_area.setReadOnly(True)
        self.report_area.setMinimumHeight(400)
        self.report_area.setPlaceholderText(
            "Run a password analysis first, then click 'Generate Report'…"
        )
        outer.addWidget(self.report_area)
        outer.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def _generate(self):
        result, password = self._get_analysis()
        if result is None:
            QMessageBox.warning(self, "No Analysis",
                                "Please run a password analysis first (Password Analyzer page).")
            return
        report_text = generate_report(result, password=password, output_dir="output")
        self.report_area.setPlainText(report_text)

    def _save(self):
        text = self.report_area.toPlainText()
        if not text.strip():
            QMessageBox.information(self, "Empty Report",
                                    "Generate a report first.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Report", "password_report.txt", "Text Files (*.txt)"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            QMessageBox.information(self, "Saved", f"Report saved to:\n{path}")
            logger.info(f"Report saved to: {path}")


# ════════════════════════════════════════════════════════════════════
#  PAGE: SETTINGS
# ════════════════════════════════════════════════════════════════════

class SettingsPage(QWidget):
    theme_changed = Signal(bool)   # True = dark, False = light

    def __init__(self):
        super().__init__()
        self._dark = True
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.setSpacing(20)

        title = QLabel("⚙️  Settings")
        title.setObjectName("page_title")
        sub   = QLabel("Customise the toolkit to your preference.")
        sub.setObjectName("subtitle")
        outer.addWidget(title)
        outer.addWidget(sub)
        outer.addWidget(make_separator())

        # ── Appearance ──────────────────────────────────────────────
        appear_lay = QVBoxLayout()
        appear_lay.setSpacing(12)
        appear_title = QLabel("Appearance")
        appear_title.setObjectName("section_title")
        appear_lay.addWidget(appear_title)

        self.dark_cb = QCheckBox("Dark Theme")
        self.dark_cb.setChecked(True)
        self.dark_cb.stateChanged.connect(self._on_theme_toggle)
        appear_lay.addWidget(self.dark_cb)

        outer.addWidget(card_widget(appear_lay))

        # ── Export directory ────────────────────────────────────────
        export_lay = QVBoxLayout()
        export_lay.setSpacing(10)
        export_title = QLabel("Export Directory")
        export_title.setObjectName("section_title")
        export_lay.addWidget(export_title)

        dir_row = QHBoxLayout()
        self.dir_input = QLineEdit()
        self.dir_input.setText(os.path.abspath("output"))
        self.dir_input.setFixedHeight(36)
        browse_btn = QPushButton("Browse…")
        browse_btn.setObjectName("secondary_btn")
        browse_btn.setFixedHeight(36)
        browse_btn.clicked.connect(self._browse_dir)
        browse_btn.setCursor(QCursor(Qt.PointingHandCursor))
        dir_row.addWidget(self.dir_input, 1)
        dir_row.addWidget(browse_btn)
        export_lay.addLayout(dir_row)

        outer.addWidget(card_widget(export_lay))

        # ── Logs ────────────────────────────────────────────────────
        log_lay = QVBoxLayout()
        log_lay.setSpacing(10)
        log_title = QLabel("Logs")
        log_title.setObjectName("section_title")
        log_lay.addWidget(log_title)

        clear_btn = QPushButton("🗑  Clear Log File")
        clear_btn.setObjectName("danger_btn")
        clear_btn.setFixedHeight(36)
        clear_btn.clicked.connect(self._clear_logs)
        clear_btn.setCursor(QCursor(Qt.PointingHandCursor))
        log_lay.addWidget(clear_btn)

        outer.addWidget(card_widget(log_lay))
        outer.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Version info
        ver = QLabel("Password Security Toolkit  v1.0.0  •  Educational use only")
        ver.setStyleSheet("color: #484f58; font-size: 11px;")
        ver.setAlignment(Qt.AlignCenter)
        outer.addWidget(ver)

    def _on_theme_toggle(self, state):
        self._dark = bool(state)
        self.theme_changed.emit(self._dark)

    def _browse_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if d:
            self.dir_input.setText(d)

    def _clear_logs(self):
        log_path = os.path.join("logs", "activity.log")
        if os.path.exists(log_path):
            with open(log_path, "w") as f:
                f.write("")
            QMessageBox.information(self, "Logs Cleared",
                                    "activity.log has been cleared.")
        else:
            QMessageBox.information(self, "No Log File",
                                    "No log file found to clear.")


# ════════════════════════════════════════════════════════════════════
#  MAIN WINDOW
# ════════════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Password Security Toolkit")
        self.resize(1040, 720)
        self.setMinimumSize(800, 580)
        self._dark_theme = True
        self._build_ui()
        self.setStyleSheet(DARK_STYLE)
        self._nav_buttons[0].setProperty("active", "true")
        self._nav_buttons[0].style().unpolish(self._nav_buttons[0])
        self._nav_buttons[0].style().polish(self._nav_buttons[0])

    # ── Build ────────────────────────────────────────────────────────
    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        main_row = QHBoxLayout(root)
        main_row.setContentsMargins(0, 0, 0, 0)
        main_row.setSpacing(0)

        # ── Sidebar ─────────────────────────────────────────────────
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar_lay = QVBoxLayout(sidebar)
        sidebar_lay.setContentsMargins(0, 0, 0, 0)
        sidebar_lay.setSpacing(0)

        logo = QLabel("🔐 SecTK")
        logo.setObjectName("logo")
        logo.setObjectName("logo")
        tagline = QLabel("Password Security Toolkit")
        tagline.setObjectName("tagline")
        tagline.setWordWrap(True)
        sidebar_lay.addWidget(logo)
        sidebar_lay.addWidget(tagline)
        sidebar_lay.addWidget(make_separator())
        sidebar_lay.addSpacing(8)

        nav_items = [
            ("🏠   Dashboard",      0),
            ("🔍   Analyzer",       1),
            ("📋   Wordlist",        2),
            ("📄   Reports",         3),
            ("⚙️    Settings",       4),
        ]

        self._nav_buttons = []
        self._stack = QStackedWidget()

        for label, idx in nav_items:
            btn = QPushButton(label)
            btn.setObjectName("nav_btn")
            btn.setFixedHeight(42)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.clicked.connect(lambda _, i=idx: self._switch_page(i))
            sidebar_lay.addWidget(btn)
            self._nav_buttons.append(btn)

        sidebar_lay.addStretch()

        # Version label at bottom of sidebar
        ver_lbl = QLabel("v1.0.0")
        ver_lbl.setStyleSheet("color: #484f58; font-size: 10px; padding: 8px 16px;")
        sidebar_lay.addWidget(ver_lbl)

        # ── Pages ────────────────────────────────────────────────────
        self._analyzer_page = AnalyzerPage()
        self._settings_page = SettingsPage()
        self._settings_page.theme_changed.connect(self._apply_theme)

        pages = [
            DashboardPage(),
            self._analyzer_page,
            WordlistPage(),
            ReportsPage(self._analyzer_page.get_result),
            self._settings_page,
        ]

        scroll_pages = []
        for page in pages:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.NoFrame)
            scroll.setWidget(page)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self._stack.addWidget(scroll)
            scroll_pages.append(scroll)

        main_row.addWidget(sidebar)
        main_row.addWidget(self._stack, 1)

    # ── Slots ────────────────────────────────────────────────────────
    def _switch_page(self, idx: int):
        self._stack.setCurrentIndex(idx)
        for i, btn in enumerate(self._nav_buttons):
            active = "true" if i == idx else "false"
            btn.setProperty("active", active)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        logger.info(f"Navigated to page index {idx}")

    def _apply_theme(self, dark: bool):
        self.setStyleSheet(DARK_STYLE if dark else LIGHT_STYLE)
        self._dark_theme = dark
        logger.info(f"Theme switched to {'dark' if dark else 'light'}")
