# Prometheus metrics used for runtime AI security telemetry

from prometheus_client import Counter


requests_total = Counter(
    "requests_total",
    "Total API requests"
)

blocked_requests_total = Counter(
    "blocked_requests_total",
    "Total blocked security violations"
)

redacted_outputs_total = Counter(
    "redacted_outputs_total",
    "Total redacted model responses"
)

policy_actions_total = Counter(
    "policy_actions_total",
    "Total policy engine actions",
    ["action"]
)

jwt_detections_total = Counter(
    "jwt_detections_total",
    "Total JWT detections"
)

aws_key_detections_total = Counter(
    "aws_key_detections_total",
    "Total AWS credential detections"
)

rate_limit_violations_total = Counter(
    "rate_limit_violations_total",
    "Total rate limit violations"
)