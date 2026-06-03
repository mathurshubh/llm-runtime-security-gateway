# Centralized runtime risk scoring engine used for adaptive AI security policy enforcement


# Scores are illustrative weights used for policy evaluation and analytics rather than formal risk metrics.

# Security findings are mapped to severity levels and weighted scores that contribute to an aggregate risk assessment.
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

    "jwt_fragment": {
        "severity": "high",
        "score": 70
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


# Aggregate findings into a cumulative risk score and derive the highest observed severity level.
def calculate_risk(findings):

    # Risk is accumulated across all findings to capture the combined impact of multiple security signals.
    total_score = 0
    severities = []

    for finding in findings:

        finding_type = finding["type"]

        if finding_type in SEVERITY_SCORES:

            config = SEVERITY_SCORES[finding_type]

            total_score += config["score"]
            severities.append(config["severity"])

    # Severity is determined by the highest-impact finding observed, regardless of aggregate score.
    highest_severity = "low"

    # Severity escalation follows a conservative model where critical findings always dominate lower severities.
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