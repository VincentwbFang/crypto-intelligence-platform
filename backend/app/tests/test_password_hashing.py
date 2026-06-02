from app.auth.password import hash_password, validate_password_strength, verify_password


def test_password_hashes_verify_correctly() -> None:
    password_hash = hash_password("Password123")
    assert verify_password("Password123", password_hash)
    assert not verify_password("WrongPassword123", password_hash)


def test_weak_password_rejected() -> None:
    assert validate_password_strength("password")
    assert validate_password_strength("12345678")
    assert validate_password_strength("qwerty123")
    assert validate_password_strength("admin123")
