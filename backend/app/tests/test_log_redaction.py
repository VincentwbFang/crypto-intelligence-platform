from app.observability.redaction import REDACTED, redact_headers, redact_log_message, redact_sensitive_data


def test_sensitive_data_is_redacted() -> None:
    payload = {
        "access_token": "abc",
        "refresh_token": "def",
        "nested": {"password": "secret", "safe": "value"},
    }
    redacted = redact_sensitive_data(payload)
    assert redacted["access_token"] == REDACTED
    assert redacted["refresh_token"] == REDACTED
    assert redacted["nested"]["password"] == REDACTED
    assert redacted["nested"]["safe"] == "value"


def test_sensitive_headers_are_redacted() -> None:
    headers = redact_headers({"Authorization": "Bearer token", "X-Request-ID": "req"})
    assert headers["Authorization"] == REDACTED
    assert headers["X-Request-ID"] == "req"


def test_sensitive_log_message_is_redacted() -> None:
    message = redact_log_message("password=secret access_token=abc api_key=xyz")
    assert "secret" not in message
    assert "abc" not in message
    assert "xyz" not in message
    assert REDACTED in message

