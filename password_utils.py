# password_utils.py
import string
import random
import re

COMMON_PATTERNS = [
    "password", "123456", "qwerty", "abc123", "111111", "iloveyou",
    "admin", "welcome", "monkey", "login", "letmein"
]

def generate_password(length=12, use_lower=True, use_upper=True, use_digits=True, use_symbols=True, avoid_ambiguous=False):
    """
    Generate a random password with the selected character sets.
    If avoid_ambiguous is True, remove characters that are often confusing.
    """
    ambiguous_chars = "Il1O0"
    pool = ""
    if use_lower:
        pool += string.ascii_lowercase
    if use_upper:
        pool += string.ascii_uppercase
    if use_digits:
        pool += string.digits
    if use_symbols:
        pool += string.punctuation
    if avoid_ambiguous:
        pool = "".join(ch for ch in pool if ch not in ambiguous_chars)
    if not pool:
        raise ValueError("At least one character type must be selected.")
    return ''.join(random.choice(pool) for _ in range(length))

def check_password_strength(password):
    """
    Evaluate the password strength and return a detailed breakdown:
    
    - **Length**: Up to 40 points (5 points per character beyond 7, capped at 40).
    - **Lowercase**: 10 points if present.
    - **Uppercase**: 10 points if present.
    - **Digits**: 20 points if present.
    - **Symbols**: 20 points if present.
    
    Total score is capped at 100.
    """
    breakdown = {}
    length = len(password)
    breakdown['length'] = min(40, (length - 7) * 5) if length >= 8 else length * 5
    breakdown['lowercase'] = 10 if any(c.islower() for c in password) else 0
    breakdown['uppercase'] = 10 if any(c.isupper() for c in password) else 0
    breakdown['digits'] = 20 if any(c.isdigit() for c in password) else 0
    breakdown['symbols'] = 20 if any(c in string.punctuation for c in password) else 0
    total = sum(breakdown.values())
    breakdown['total'] = min(total, 100)
    return breakdown

def detect_common_patterns(password):
    """
    Check if the password contains common weak patterns or repeated characters.
    Returns a list of warnings.
    """
    warnings = []
    lower_pwd = password.lower()
    for pattern in COMMON_PATTERNS:
        if pattern in lower_pwd:
            warnings.append(f"Contains common pattern: '{pattern}'")
    # Check for sequential or repeated characters (e.g., "aaa" or "1234")
    if re.search(r'(.)\1\1', password):
        warnings.append("Contains repeated characters.")
    if re.search(r'(0123|1234|2345|3456|4567|5678|6789)', password):
        warnings.append("Contains sequential numbers.")
    return warnings

def password_recommendations(breakdown, warnings):
    """
    Generate recommendations based on the breakdown and common pattern warnings.
    """
    recommendations = []
    if breakdown['length'] < 40:
        recommendations.append("Increase the password length (8+ characters recommended).")
    if breakdown['lowercase'] == 0:
        recommendations.append("Add lowercase letters.")
    if breakdown['uppercase'] == 0:
        recommendations.append("Add uppercase letters.")
    if breakdown['digits'] == 0:
        recommendations.append("Include numbers.")
    if breakdown['symbols'] == 0:
        recommendations.append("Include symbols (e.g. !, @, #).")
    if warnings:
        recommendations.append("Avoid common patterns or repeated sequences: " + ", ".join(warnings))
    return recommendations