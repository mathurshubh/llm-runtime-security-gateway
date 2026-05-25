from logging import critical


SEVERITY_SCORES = {
    "prompt_injection": {
        "severity": "high",
        "score": 70
    },

    "aws_access_key": {
        "severity": "critical",
        "score": 90
    },

    "bearer_token": {
        "severity": "critical",
        "score": 90
    },

    "jwt_token": {
        "severity": "critical",
        "score": 90
    },

    "password_assignment": {
        "severity": "high",
        "score": 80
    },

    "email": {
        "severity": "low",
        "score": 20
    }
    
}


def calculate_risk(findings):

    total_score = 0
    severities = []

    for finding in findings:

        finding_type = finding["type"]

        if finding_type in SEVERITY_SCORES:

            config = SEVERITY_SCORES[finding_type]

            total_score += config["score"]
            severities.append(config["severity"])

    highest_severity = "low"

    if "critical" in severities:
        highest_severity = "critical"

    elif "high" in severities:
        highest_severity = "high"

    elif "medium" in severities:
        highest_severity = "medium"

    return {
        "risk_score": total_score,
        "severity": highest_severity
    }