"""
wordlist_generator.py
---------------------
Generates a targeted password wordlist from personal information.

Strategy:
  1. Build base tokens from user data.
  2. Apply leet-speak variations.
  3. Apply case variations.
  4. Append common suffixes.
  5. Use itertools.product for combination generation.
  6. Deduplicate and save to /output/wordlist.txt.
"""

import os
import itertools
import logging
from datetime import datetime
from leetspeak import leet_variations

logger = logging.getLogger("PasswordToolkit")

# Suffix list covering common patterns attackers use
COMMON_SUFFIXES = [
    "", "1", "12", "123", "1234", "12345",
    "!", "!!", "@", "@123",
    "2023", "2024", "2025",
    "#1", "007", "666", "999",
]


def _case_variations(word: str) -> list[str]:
    """Return lower, upper, title, and camelCase variants of a word."""
    variants = {
        word.lower(),
        word.upper(),
        word.capitalize(),
    }
    return list(variants)


def _expand_token(token: str) -> list[str]:
    """
    Expand a single token into all its leet + case variants.
    """
    expanded = set()
    for leet in leet_variations(token):
        for case in _case_variations(leet):
            expanded.add(case)
    return list(expanded)


def generate_wordlist(user_data: dict, max_words: int = 5000) -> list[str]:
    """
    Generate a password wordlist from a dict of personal information.

    Expected keys (all optional, empty strings are ignored):
        first_name, last_name, pet_name, birth_year,
        fav_number, city

    Returns a deduplicated list of candidate passwords.
    """
    # ── 1. Collect raw tokens ──────────────────────────────────────
    raw_tokens = []
    for key in ("first_name", "last_name", "pet_name", "city"):
        val = user_data.get(key, "").strip()
        if val:
            raw_tokens.append(val)

    number_tokens = []
    for key in ("birth_year", "fav_number"):
        val = user_data.get(key, "").strip()
        if val:
            number_tokens.append(val)

    if not raw_tokens and not number_tokens:
        logger.warning("No user data provided for wordlist generation.")
        return []

    # ── 2. Expand all word tokens ──────────────────────────────────
    expanded_words = []
    for token in raw_tokens:
        expanded_words.extend(_expand_token(token))

    # ── 3. Build combinations ──────────────────────────────────────
    wordlist = set()

    # Single tokens with suffixes
    for word in expanded_words:
        for suffix in COMMON_SUFFIXES:
            wordlist.add(word + suffix)
            # word + number token + suffix
            for num in number_tokens:
                wordlist.add(word + num + suffix)

    # Two-word combinations
    if len(expanded_words) >= 2:
        for w1, w2 in itertools.product(expanded_words[:20], expanded_words[:20]):
            if w1 != w2:
                for suffix in COMMON_SUFFIXES[:8]:  # limit explosion
                    candidate = w1 + w2 + suffix
                    if 6 <= len(candidate) <= 20:
                        wordlist.add(candidate)

    # Number tokens with word tokens
    for num in number_tokens:
        for word in expanded_words:
            wordlist.add(word + num)
            wordlist.add(num + word)

    # ── 4. Trim to max_words ───────────────────────────────────────
    result = sorted(wordlist)[:max_words]
    logger.info(f"Wordlist generated: {len(result)} entries")
    return result


def save_wordlist(wordlist: list[str], output_dir: str = "output") -> str:
    """
    Save the wordlist to <output_dir>/wordlist.txt.
    Returns the full path to the saved file.
    """
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, "wordlist.txt")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# Password Wordlist — Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# Total entries: {len(wordlist)}\n\n")
        for word in wordlist:
            f.write(word + "\n")

    logger.info(f"Wordlist saved to: {filepath}")
    return filepath
