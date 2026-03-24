"""
entropy_calculator.py
---------------------
Calculates Shannon entropy for passwords based on character set composition.

Entropy formula: E = L × log2(N)
  where L = password length, N = size of character pool used
"""

import math
import logging

logger = logging.getLogger("PasswordToolkit")


def detect_charset_size(password: str) -> dict:
    """
    Detect which character classes are present in the password.

    Returns a dict with:
      - has_lower: bool
      - has_upper: bool
      - has_digits: bool
      - has_symbols: bool
      - charset_size: total unique character pool size
    """
    has_lower   = any(c.islower() for c in password)
    has_upper   = any(c.isupper() for c in password)
    has_digits  = any(c.isdigit() for c in password)
    has_symbols = any(not c.isalnum() for c in password)

    charset_size = 0
    if has_lower:   charset_size += 26
    if has_upper:   charset_size += 26
    if has_digits:  charset_size += 10
    if has_symbols: charset_size += 32  # printable ASCII symbols

    return {
        "has_lower":    has_lower,
        "has_upper":    has_upper,
        "has_digits":   has_digits,
        "has_symbols":  has_symbols,
        "charset_size": charset_size,
    }


def calculate_entropy(password: str) -> float:
    """
    Calculate bit entropy of a password.

    Returns entropy in bits (float). Returns 0.0 for empty passwords.
    """
    if not password:
        return 0.0

    info = detect_charset_size(password)
    n = info["charset_size"]

    if n == 0:
        return 0.0

    entropy = len(password) * math.log2(n)
    logger.debug(f"Entropy calculated: {entropy:.2f} bits for length={len(password)}, charset={n}")
    return round(entropy, 2)


def entropy_label(entropy: float) -> str:
    """Return a human-readable label for an entropy value."""
    if entropy < 28:
        return "Very Weak"
    elif entropy < 36:
        return "Weak"
    elif entropy < 60:
        return "Moderate"
    elif entropy < 80:
        return "Strong"
    else:
        return "Very Strong"


def get_entropy_details(password: str) -> dict:
    """
    Full entropy report for a password.

    Returns:
      entropy, charset_size, length, label, and character class flags.
    """
    info   = detect_charset_size(password)
    ent    = calculate_entropy(password)
    label  = entropy_label(ent)

    return {
        "entropy":      ent,
        "charset_size": info["charset_size"],
        "length":       len(password),
        "label":        label,
        "has_lower":    info["has_lower"],
        "has_upper":    info["has_upper"],
        "has_digits":   info["has_digits"],
        "has_symbols":  info["has_symbols"],
    }
