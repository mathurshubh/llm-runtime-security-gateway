# Response sanitization layer used to redact sensitive credentials and token artifacts before content is returned to users.

import re


# Regular expressions used to identify sensitive credentials, tokens, and secret material that should never be exposed.
REDACTION_PATTERNS = {

    "jwt_token":
        r"eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9._-]+(?:\.[a-zA-Z0-9._-]+)?",

    "jwt_fragment":
        r"eyJ[a-zA-Z0-9_-]{5,}",

    "bearer_token":
        r"Bearer\s+[A-Za-z0-9\-\._~\+\/]+=*",

    "aws_access_key":
        r"AKIA[0-9A-Z]{16}",

    "aws_secret_key":
        r"(?i)(aws_secret_access_key|secret access key|aws secret).{0,50}[A-Za-z0-9\/+=]{40}",
}


# Replace detected secrets with standardized redaction markers while preserving the surrounding response content.
def redact_sensitive_data(
    text: str
) -> str:

    redacted_text = text

    for secret_type, pattern in REDACTION_PATTERNS.items():

        # Apply redaction for every supported secret category detected in the response.
        redacted_text = re.sub(
            pattern,
            f"[REDACTED_{secret_type.upper()}]",
            redacted_text
        )

    return redacted_text