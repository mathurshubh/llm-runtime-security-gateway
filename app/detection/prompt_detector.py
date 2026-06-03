# Heuristic prompt injection and jailbreak detection layer for inbound prompts.


# Common prompt injection and jailbreak phrases frequently used to manipulate model behavior, bypass safeguards, or expose hidden instructions.
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


# Analyze inbound prompts for known prompt injection and jailbreak indicators.
def analyze_prompt(prompt: str) -> dict:

    findings = []

    # Normalize input to enable case-insensitive pattern matching.
    lowered_prompt = prompt.lower()

    for pattern in SUSPICIOUS_PATTERNS:

        if pattern in lowered_prompt:
            findings.append(pattern)

    # Risk increases proportionally with the number of suspicious indicators observed.
    risk_score = len(findings) * 25

    severity = "low"

    if risk_score >= 50:
        severity = "high"

    elif risk_score >= 25:
        severity = "medium"

    # Requests containing multiple prompt injection indicators are considered high risk.
    return {
        "risk_score": risk_score,
        "severity": severity,
        "findings": findings,
        "blocked": risk_score >= 50
    }