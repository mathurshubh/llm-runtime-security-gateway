SUSPICIOUS_PATTERNS = [
    "ignore previous instructions",
    "reveal system prompt",
    "developer mode",
    "bypass safety",
    "pretend you are",
    "jailbreak",
    "do anything now",
    "system prompt",
]


def analyze_prompt(prompt: str):

    findings = []

    lowered_prompt = prompt.lower()

    for pattern in SUSPICIOUS_PATTERNS:
        if pattern in lowered_prompt:
            findings.append(pattern)

    risk_score = len(findings) * 25

    severity = "low"

    if risk_score >= 50:
        severity = "high"
    elif risk_score >= 25:
        severity = "medium"

    return {
    "risk_score": risk_score,
    "severity": severity,
    "findings": findings,
    "blocked": risk_score >= 50
    }