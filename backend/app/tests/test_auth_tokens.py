from app.auth.tokens import (
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
    verify_access_token,
    verify_refresh_token,
)


def test_access_token_validates() -> None:
    token = create_access_token("user-1", "workspace-1")
    payload = verify_access_token(token)
    assert payload["sub"] == "user-1"
    assert payload["workspace_id"] == "workspace-1"


def test_invalid_access_token_fails() -> None:
    try:
        verify_access_token("not-a-token")
    except ValueError:
        assert True
    else:
        raise AssertionError("Invalid token should fail.")


def test_refresh_token_hash_verifies() -> None:
    raw, token_hash = create_refresh_token()
    assert verify_refresh_token(raw, token_hash)
    assert not verify_refresh_token("wrong", token_hash)
    assert hash_refresh_token(raw) == token_hash
