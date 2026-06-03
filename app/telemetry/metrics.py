# Prometheus metrics used for runtime AI security telemetry, monitoring dashboards, and operational reporting.

from prometheus_client import Counter

# Gateway Metrics

# Total requests received by the gateway.
requests_total = Counter(
    "requests_total",
    "Total API requests"
)

# Requests blocked by policy enforcement before LLM execution.
blocked_requests_total = Counter(
    "blocked_requests_total",
    "Total blocked security violations"
)

# Model responses requiring output redaction.
redacted_outputs_total = Counter(
    "redacted_outputs_total",
    "Total redacted model responses"
)

# Policy decisions grouped by action type (allow, log, redact, block).
policy_actions_total = Counter(
    "policy_actions_total",
    "Total policy engine actions",
    ["action"]
)

# Detection Metrics

# JWT tokens or token fragments detected in model output.
jwt_detections_total = Counter(
    "jwt_detections_total",
    "Total JWT detections"
)

# AWS credential detections identified during output inspection.
aws_key_detections_total = Counter(
    "aws_key_detections_total",
    "Total AWS credential detections"
)

# Security Analytics Metrics

# Total security events persisted to the event store.
security_events_total = Counter(
    "security_events_total",
    "Total security events"
)

# Requests blocked due to policy violations.
policy_violations_total = Counter(
    "policy_violations_total",
    "Total policy violations"
)

# Output-side security violations requiring redaction.
output_security_violations_total = Counter(
    "output_security_violations_total",
    "Total output security violations"
)

# RBAC authorization failures on protected endpoints.
authorization_denied_total = Counter(
    "authorization_denied_total",
    "Total authorization denied events"
)

# Requests rejected by distributed rate-limiting controls.
rate_limit_violations_total = Counter(
    "rate_limit_violations_total",
    "Total rate limit violations"
)