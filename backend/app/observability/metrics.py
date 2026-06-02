from __future__ import annotations

import threading
import time
from collections import defaultdict
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

MetricKey = tuple[tuple[str, str], ...]


class MetricsRegistry:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.counters: dict[str, dict[MetricKey, float]] = defaultdict(lambda: defaultdict(float))
        self.histograms: dict[str, dict[MetricKey, list[float]]] = defaultdict(lambda: defaultdict(list))
        self.gauges: dict[str, dict[MetricKey, float]] = defaultdict(lambda: defaultdict(float))

    def inc(self, name: str, labels: dict[str, Any] | None = None, amount: float = 1.0) -> None:
        with self._lock:
            self.counters[name][_labels(labels)] += amount

    def observe(self, name: str, value: float, labels: dict[str, Any] | None = None) -> None:
        with self._lock:
            self.histograms[name][_labels(labels)].append(value)

    def gauge_inc(self, name: str, labels: dict[str, Any] | None = None) -> None:
        with self._lock:
            self.gauges[name][_labels(labels)] += 1

    def gauge_dec(self, name: str, labels: dict[str, Any] | None = None) -> None:
        with self._lock:
            self.gauges[name][_labels(labels)] -= 1

    def render(self) -> str:
        lines: list[str] = []
        with self._lock:
            for name, series in self.counters.items():
                lines.append(f"# TYPE {name} counter")
                for labels, value in series.items():
                    lines.append(f"{name}{_format_labels(labels)} {value}")
            for name, series in self.gauges.items():
                lines.append(f"# TYPE {name} gauge")
                for labels, value in series.items():
                    lines.append(f"{name}{_format_labels(labels)} {value}")
            for name, series in self.histograms.items():
                lines.append(f"# TYPE {name} summary")
                for labels, values in series.items():
                    count = len(values)
                    total = sum(values)
                    lines.append(f"{name}_count{_format_labels(labels)} {count}")
                    lines.append(f"{name}_sum{_format_labels(labels)} {total}")
        return "\n".join(lines) + "\n"

    def reset(self) -> None:
        with self._lock:
            self.counters.clear()
            self.histograms.clear()
            self.gauges.clear()


metrics_registry = MetricsRegistry()


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/metrics":
            return await call_next(request)
        labels = {
            "method": request.method,
            "route": _route_label(request.url.path),
            "service": "api",
        }
        metrics_registry.gauge_inc("http_requests_in_progress", labels)
        start = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            duration = time.perf_counter() - start
            metrics_registry.gauge_dec("http_requests_in_progress", labels)
            labels["status_code"] = str(status_code)
            metrics_registry.inc("http_requests_total", labels)
            metrics_registry.observe("http_request_duration_seconds", duration, labels)


def track_feature_event(feature: str, amount: float = 1.0) -> None:
    metric_name = {
        "ai": "ai_requests_total",
        "market_ingestion": "market_ingestion_total",
        "signal_generation": "signal_generation_total",
        "alert_evaluation": "alert_evaluation_total",
        "backtest": "backtest_runs_total",
        "paper_order": "paper_orders_total",
    }.get(feature, "app_feature_events_total")
    metrics_registry.inc(metric_name, {"feature": feature}, amount)


def _labels(labels: dict[str, Any] | None) -> MetricKey:
    if not labels:
        return tuple()
    return tuple(sorted((str(key), str(value)) for key, value in labels.items()))


def _format_labels(labels: MetricKey) -> str:
    if not labels:
        return ""
    body = ",".join(f'{key}="{_escape_label(value)}"' for key, value in labels)
    return "{" + body + "}"


def _escape_label(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _route_label(path: str) -> str:
    if path.startswith("/auth"):
        return "/auth/*"
    if path.startswith("/ai"):
        return "/ai/*"
    if path.startswith("/signals"):
        return "/signals/*"
    if path.startswith("/alerts"):
        return "/alerts/*"
    if path.startswith("/backtests"):
        return "/backtests/*"
    if path.startswith("/paper"):
        return "/paper/*"
    if path.startswith("/market"):
        return "/market/*"
    if path.startswith("/system"):
        return "/system/*"
    return path

