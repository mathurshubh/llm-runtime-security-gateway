import re

PII_PATTERNS = {
    "aws_access_key": r"AKIA[0-9A-Z]{16}",

    "aws_secret_key":
    r"(?i)(aws_secret_access_key|secret access key|aws secret).{0,50}[A-Za-z0-9\/+=]{40}",

    "bearer_token": r"Bearer\s+[A-Za-z0-9\-\._~\+\/]+=*",

    "email": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",

    "password_assignment": r"password\s*=\s*.+",

    "jwt_token": r"eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9._-]+(?:\.[a-zA-Z0-9._-]+)?",

    "jwt_fragment": r"eyJ[a-zA-Z0-9_-]{5,}"
}


def detect_pii(prompt: str):

    findings = []

    for pii_type, pattern in PII_PATTERNS.items():

        matches = re.findall(pattern, prompt)

        if matches:
            findings.append({
                "type": pii_type,
                "value": matches
            })

    return findings