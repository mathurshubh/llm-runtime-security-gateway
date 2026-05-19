SUSPICIOUS_PATTERNS = [
    "ignore previous instructions",
    "ignore all previous instructions",
    "ignore last prompts",
    "reveal system prompt",
    "system prompt",
    "developer mode",
    "bypass safety",
    "pretend you are",
    "jailbreak",
    "do anything now",
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