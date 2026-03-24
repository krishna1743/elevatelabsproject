"""
report_generator.py
-------------------
Generates a formatted text report for a password analysis result.
Saves to /output/password_report.txt and returns the report as a string.
"""

import os
import logging
from datetime import datetime

logger = logging.getLogger("PasswordToolkit")

DISCLAIMER = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ⚠  SECURITY DISCLAIMER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  This tool is intended for EDUCATIONAL purposes only.
  Use it ethically and only on passwords you own or
  have explicit permission to test.
  Misuse may violate laws in your jurisdiction.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


def _strength_bar(score: int, width: int = 20) -> str:
    """Return an ASCII progress bar for a 0–4 score."""
    filled = int((score / 4) * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {score}/4"


def generate_report(analysis: dict, password: str = None,
                    output_dir: str = "output") -> str:
    """
    Build a text report from an analysis dict.

    Parameters
    ----------
    analysis   : dict returned by password_analyzer.analyze_password()
    password   : the analyzed password (shown masked in the report)
    output_dir : directory where the report file is written

    Returns
    -------
    The full report as a string.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Mask password: show first + last char, rest as *
    if password and len(password) > 2:
        masked = password[0] + "*" * (len(password) - 2) + password[-1]
    elif password:
        masked = "*" * len(password)
    else:
        masked = "(not provided)"

    suggestions_text = "\n".join(
        f"  • {s}" for s in analysis.get("suggestions", [])
    ) or "  • None"

    patterns_text = "\n".join(
        f"  ⚠ {p}" for p in analysis.get("patterns", [])
    ) or "  ✓ No obvious patterns detected"

    char_classes = []
    if analysis.get("has_lower"):    char_classes.append("Lowercase (a-z)")
    if analysis.get("has_upper"):    char_classes.append("Uppercase (A-Z)")
    if analysis.get("has_digits"):   char_classes.append("Digits (0-9)")
    if analysis.get("has_symbols"):  char_classes.append("Symbols (!@#…)")

    report = f"""
╔══════════════════════════════════════════════════════════════╗
║          Password Security Toolkit — Analysis Report         ║
╚══════════════════════════════════════════════════════════════╝

  Generated : {now}
  Password  : {masked}
  Length    : {analysis.get('length', 0)} characters

────────────────────────────────────────────────────────────
  STRENGTH ASSESSMENT
────────────────────────────────────────────────────────────
  Score     : {_strength_bar(analysis.get('score', 0))}
  Label     : {analysis.get('score_label', 'N/A')}

────────────────────────────────────────────────────────────
  ENTROPY
────────────────────────────────────────────────────────────
  Entropy   : {analysis.get('entropy', 0):.2f} bits  ({analysis.get('entropy_label', 'N/A')})
  Charset   : {analysis.get('charset_size', 0)} unique characters used

  Character Classes Present:
{chr(10).join('  ✓ ' + c for c in char_classes) or '  ✗ None detected'}

────────────────────────────────────────────────────────────
  ESTIMATED CRACK TIME
────────────────────────────────────────────────────────────
  {analysis.get('crack_time', 'N/A')}
  (Offline slow hashing, e.g. bcrypt @ 10,000 attempts/sec)

────────────────────────────────────────────────────────────
  DETECTED PATTERNS / WEAKNESSES
────────────────────────────────────────────────────────────
{patterns_text}

────────────────────────────────────────────────────────────
  RECOMMENDATIONS
────────────────────────────────────────────────────────────
{suggestions_text}

{DISCLAIMER}
"""

    # Save to file
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, "password_report.txt")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report)

    logger.info(f"Report saved to: {filepath}")
    return report
