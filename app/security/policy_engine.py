# Centralized runtime policy engine used for adaptive AI security enforcement

# Detection engines identify security findings, while the policy engine maps findings to enforcement actions such as allow, log, redact, or block.
POLICY_RULES = {
    # Prompt attacks
    "prompt_injection": "block",

    # Secrets / credentials
    "aws_access_key": "redact",
    "aws_secret_key": "redact",
    "bearer_token": "redact",
    "jwt_token": "redact",
    "jwt_fragment": "redact",

    # Informational findings
    "email": "log"
}


# Multiple findings may produce different actions. The most restrictive action wins to ensure conservative enforcement.
ACTION_PRIORITY = {
    "allow": 0,
    "log": 1,
    "redact": 2,
    "block": 3
}


# Evaluate all findings and return the strongest enforcement action required for the request or response.
def evaluate_policy(findings):

    # Requests default to allow unless elevated by one or more security findings.
    final_action = "allow"

    for finding in findings:

        finding_type = finding["type"]

        action = POLICY_RULES.get(
            finding_type,
            "allow"
        )

        # Escalate to the highest-priority action observed across all findings.
        if ACTION_PRIORITY[action] > ACTION_PRIORITY[final_action]:
            final_action = action

    return {
        "action": final_action,
        "findings": findings
    }