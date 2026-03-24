"""
main.py
-------
Entry point for the Password Security Toolkit.

Sets up logging, ensures required directories exist, then launches the GUI.

Run with:
    python main.py
"""

import os
import sys
import logging
from datetime import datetime


# ── Directory bootstrap ────────────────────────────────────────────────────────
for d in ("output", "logs", "assets/icons"):
    os.makedirs(d, exist_ok=True)

# ── Logging setup ──────────────────────────────────────────────────────────────
LOG_FILE = os.path.join("logs", "activity.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)-8s]  %(name)s  —  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger("PasswordToolkit")
logger.info("=" * 60)
logger.info("Password Security Toolkit — Session started")
logger.info(f"Timestamp : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
logger.info("=" * 60)

# ── Ensure the local package directory is on the path ─────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Launch GUI ─────────────────────────────────────────────────────────────────
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from gui_main import MainWindow


def main():
    # Enable high-DPI scaling on Windows / Linux
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps,    True)

    app = QApplication(sys.argv)
    app.setApplicationName("Password Security Toolkit")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("SecTK")

    window = MainWindow()
    window.show()

    logger.info("GUI window displayed successfully.")
    exit_code = app.exec()

    logger.info(f"Session ended — exit code {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
