# Output-side inspection layer used to detect credential leakage and unsafe model responses

from app.detection.pii_detector import detect_pii


def inspect_output(response_text: str):

    findings = detect_pii(response_text)

    action = "allow"

    high_risk_types = [
        "aws_access_key",
        "aws_secret_key",
        "bearer_token",
        "password_assignment",
        "jwt_token",
        "jwt_fragment"
    ]

    for finding in findings:

        if finding["type"] in high_risk_types:
            action = "redact"

    return {
        "action": action,
        "findings": findings
    }

