"""
password_analyzer.py
--------------------
Core password analysis engine.

Uses zxcvbn for realistic strength estimation and supplements it with
our own entropy calculator for educational display purposes.
"""

import logging
import re
from entropy_calculator import get_entropy_details

logger = logging.getLogger("PasswordToolkit")

# Try to import zxcvbn; fall back gracefully if not installed
try:
    from zxcvbn import zxcvbn as _zxcvbn
    ZXCVBN_AVAILABLE = True
except ImportError:
    ZXCVBN_AVAILABLE = False
    logger.warning("zxcvbn not installed – falling back to basic analysis.")


# ──────────────────────────────────────────────
# Fallback crack-time strings when zxcvbn missing
# ──────────────────────────────────────────────
def _basic_crack_time(score: int) -> str:
    table = {
        0: "Instantly",
        1: "A few minutes",
        2: "Several hours",
        3: "A few months",
        4: "Centuries",
    }
    return table.get(score, "Unknown")


def _basic_score(password: str) -> int:
    """Very simple rule-based score (0-4) used when zxcvbn unavailable."""
    score = 0
    if len(password) >= 8:  score += 1
    if len(password) >= 12: score += 1
    if re.search(r'[A-Z]', password) and re.search(r'[a-z]', password): score += 1
    if re.search(r'\d', password): score += 1
    if re.search(r'[^A-Za-z0-9]', password): score += 1
    return min(score, 4)


# ──────────────────────────────────────────────
# Common pattern detectors
# ──────────────────────────────────────────────
COMMON_PATTERNS = [
    (r'^[a-zA-Z]+\d{1,4}$',    "Ends with short number sequence"),
    (r'(.)\1{2,}',              "Repeated characters detected"),
    (r'(012|123|234|345|456|567|678|789|890)', "Sequential digits"),
    (r'(abc|bcd|cde|def|efg)', "Sequential letters"),
    (r'password|passwd|pass|qwerty|letmein|admin|welcome', "Common dictionary word"),
]


def detect_patterns(password: str) -> list[str]:
    """Return a list of detected weakness patterns."""
    warnings = []
    lower = password.lower()
    for pattern, message in COMMON_PATTERNS:
        if re.search(pattern, lower):
            warnings.append(message)
    return warnings


# ──────────────────────────────────────────────
# Suggestion builder
# ──────────────────────────────────────────────
def build_suggestions(password: str, score: int, entropy_info: dict) -> list[str]:
    suggestions = []

    if len(password) < 12:
        suggestions.append("Use at least 12 characters for better security.")
    if not entropy_info["has_upper"]:
        suggestions.append("Add uppercase letters (A–Z).")
    if not entropy_info["has_lower"]:
        suggestions.append("Add lowercase letters (a–z).")
    if not entropy_info["has_digits"]:
        suggestions.append("Include numbers (0–9).")
    if not entropy_info["has_symbols"]:
        suggestions.append("Add special characters (!, @, #, $, %).")
    if score <= 1:
        suggestions.append("Avoid dictionary words and predictable patterns.")
    if not suggestions:
        suggestions.append("Great password! Consider using a password manager.")

    return suggestions


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────
def analyze_password(password: str) -> dict:
    """
    Full password analysis.

    Returns:
        score           (int, 0–4)
        score_label     (str)
        entropy         (float, bits)
        entropy_label   (str)
        crack_time      (str)
        suggestions     (list[str])
        patterns        (list[str])
        length          (int)
        charset_size    (int)
        zxcvbn_feedback (dict)  – empty dict if zxcvbn unavailable
    """
    if not password:
        return _empty_result()

    entropy_info = get_entropy_details(password)
    patterns     = detect_patterns(password)

    if ZXCVBN_AVAILABLE:
        result      = _zxcvbn(password)
        score       = result["score"]
        crack_time  = result["crack_times_display"].get(
            "offline_slow_hashing_1e4_per_second", "Unknown"
        )
        zx_feedback = result.get("feedback", {})
        # Merge zxcvbn suggestions with our own
        zx_suggestions = zx_feedback.get("suggestions", [])
    else:
        score       = _basic_score(password)
        crack_time  = _basic_crack_time(score)
        zx_feedback = {}
        zx_suggestions = []

    our_suggestions = build_suggestions(password, score, entropy_info)
    all_suggestions = list(dict.fromkeys(zx_suggestions + our_suggestions))  # dedup

    score_labels = {0: "Very Weak", 1: "Weak", 2: "Fair", 3: "Strong", 4: "Very Strong"}

    logger.info(f"Password analyzed | score={score} | entropy={entropy_info['entropy']:.1f} bits")

    return {
        "score":           score,
        "score_label":     score_labels.get(score, "Unknown"),
        "entropy":         entropy_info["entropy"],
        "entropy_label":   entropy_info["label"],
        "crack_time":      crack_time,
        "suggestions":     all_suggestions,
        "patterns":        patterns,
        "length":          entropy_info["length"],
        "charset_size":    entropy_info["charset_size"],
        "has_lower":       entropy_info["has_lower"],
        "has_upper":       entropy_info["has_upper"],
        "has_digits":      entropy_info["has_digits"],
        "has_symbols":     entropy_info["has_symbols"],
        "zxcvbn_feedback": zx_feedback,
    }


def _empty_result() -> dict:
    return {
        "score": 0, "score_label": "N/A", "entropy": 0.0,
        "entropy_label": "N/A", "crack_time": "N/A",
        "suggestions": ["Please enter a password."], "patterns": [],
        "length": 0, "charset_size": 0,
        "has_lower": False, "has_upper": False,
        "has_digits": False, "has_symbols": False,
        "zxcvbn_feedback": {},
    }
