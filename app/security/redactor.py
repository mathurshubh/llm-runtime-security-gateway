import re


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


def redact_sensitive_data(text: str):

    redacted_text = text

    for secret_type, pattern in REDACTION_PATTERNS.items():

        redacted_text = re.sub(
            pattern,
            f"[REDACTED_{secret_type.upper()}]",
            redacted_text
        )

    return redacted_text