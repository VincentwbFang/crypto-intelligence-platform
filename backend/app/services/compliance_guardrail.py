import copy
import re
from typing import Any

FORBIDDEN_PHRASES = (
    "buy now",
    "sell now",
    "short here",
    "long here",
    "use leverage",
    "5x leverage",
    "10x leverage",
    "guaranteed",
    "risk-free",
    "risk free",
    "sure profit",
    "will moon",
    "moon",
    "all in",
    "price target",
    "must buy",
    "must short",
)

REPLACEMENT_TEXT = "[removed unsafe wording]"


class ComplianceGuardrail:
    @classmethod
    def validate_ai_output(cls, output: dict[str, Any]) -> dict[str, Any]:
        sanitized_output = copy.deepcopy(output)
        warnings: list[str] = []

        cls._sanitize_value(sanitized_output, warnings)

        if warnings:
            sanitized_output["compliance_warnings"] = sorted(set(warnings))

        return {
            "safe": not warnings,
            "warnings": sorted(set(warnings)),
            "sanitized_output": sanitized_output,
        }

    @classmethod
    def _sanitize_value(cls, value: Any, warnings: list[str]) -> Any:
        if isinstance(value, dict):
            for key, child in value.items():
                value[key] = cls._sanitize_value(child, warnings)
            return value

        if isinstance(value, list):
            for index, child in enumerate(value):
                value[index] = cls._sanitize_value(child, warnings)
            return value

        if isinstance(value, str):
            return cls._sanitize_text(value, warnings)

        return value

    @classmethod
    def _sanitize_text(cls, text: str, warnings: list[str]) -> str:
        sanitized = text
        for phrase in FORBIDDEN_PHRASES:
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            if pattern.search(sanitized):
                warnings.append("Removed unsafe wording from AI output.")
                sanitized = pattern.sub(REPLACEMENT_TEXT, sanitized)
        return sanitized
