from app.detection.pii_detector import detect_pii


def inspect_output(response_text: str):

    findings = detect_pii(response_text)

    blocked = False

    high_risk_types = [
        "aws_access_key",
        "bearer_token",
        "password_assignment",
        "jwt_token"
    ]

    for finding in findings:

        if finding["type"] in high_risk_types:
            blocked = True

    return {
        "blocked": blocked,
        "findings": findings
    }

