# Structured logging configuration used across the gateway for security events, operational telemetry, and debugging.

import logging
import structlog


# Configure the standard Python logging backend.
logging.basicConfig(
    format="%(message)s",
    level=logging.INFO,
)

# Configure structlog to emit structured, timestamped logs suitable for security investigations and operational monitoring.
structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(
        logging.INFO
    ),
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
    ],
)

# Shared application logger used throughout the gateway.
logger = structlog.get_logger()