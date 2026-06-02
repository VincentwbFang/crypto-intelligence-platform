from __future__ import annotations

import base64
import hashlib
import hmac
import os
import re

PBKDF2_ITERATIONS = 210_000
WEAK_PASSWORDS = {"password", "12345678", "qwerty123", "admin123"}


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return "pbkdf2_sha256${}${}${}".format(
        PBKDF2_ITERATIONS,
        base64.urlsafe_b64encode(salt).decode("ascii"),
        base64.urlsafe_b64encode(digest).decode("ascii"),
    )


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations, salt_b64, digest_b64 = password_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        salt = base64.urlsafe_b64decode(salt_b64.encode("ascii"))
        expected = base64.urlsafe_b64decode(digest_b64.encode("ascii"))
        actual = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            int(iterations),
        )
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False


def validate_password_strength(password: str) -> list[str]:
    errors: list[str] = []
    lowered = password.lower()
    if len(password) < 8:
        errors.append("Password must be at least 8 characters.")
    if not re.search(r"[A-Za-z]", password):
        errors.append("Password must include at least one letter.")
    if not re.search(r"\d", password):
        errors.append("Password must include at least one number.")
    if lowered in WEAK_PASSWORDS:
        errors.append("Password is too common.")
    return errors
