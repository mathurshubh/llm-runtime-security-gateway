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

    return {
        "risk_score": risk_score,
        "findings": findings,
        "blocked": risk_score >= 50
    }