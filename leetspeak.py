"""
leetspeak.py
------------
Converts plain text to common leet-speak substitutions used in
wordlist generation and password pattern detection.
"""

# Standard leet-speak substitution map
LEET_MAP = {
    'a': '@',
    'e': '3',
    'i': '1',
    'o': '0',
    's': '$',
    't': '7',
    'l': '1',
    'g': '9',
    'b': '6',
}


def to_leet(text: str) -> str:
    """
    Convert all applicable characters in *text* to their leet equivalents.

    Example:
        >>> to_leet("password")
        'p@$$w0rd'
    """
    return ''.join(LEET_MAP.get(ch.lower(), ch) for ch in text)


def leet_variations(text: str) -> list[str]:
    """
    Return a list of leet-speak variations for *text*:
      1. Full leet substitution
      2. Partial leet (only vowels)
      3. Original text (no change)

    Duplicates are removed while preserving order.
    """
    full_leet    = to_leet(text)
    vowels_only  = ''.join(LEET_MAP.get(ch, ch) if ch in 'aeiouAEIOU' else ch for ch in text)

    seen = set()
    result = []
    for variant in [text, vowels_only, full_leet]:
        if variant not in seen:
            seen.add(variant)
            result.append(variant)

    return result
