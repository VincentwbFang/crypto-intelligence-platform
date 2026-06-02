import json
import logging

from app.core.config import settings
from app.observability.logging import JsonLogFormatter, build_logging_config


def test_json_logging_contains_required_fields(monkeypatch) -> None:
    monkeypatch.setattr(settings, "ENABLE_JSON_LOGGING", True)
    record = logging.LogRecord("test", logging.INFO, __file__, 1, "hello", (), None)
    parsed = json.loads(JsonLogFormatter().format(record))
    assert parsed["service"]
    assert parsed["environment"]
    assert parsed["version"]
    assert parsed["message"] == "hello"


def test_local_logging_mode_uses_readable_formatter(monkeypatch) -> None:
    monkeypatch.setattr(settings, "ENABLE_JSON_LOGGING", False)
    config = build_logging_config("INFO")
    assert config["handlers"]["console"]["formatter"] == "readable"
