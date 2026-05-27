# Centralized runtime policy engine used for adaptive AI security enforcement


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


ACTION_PRIORITY = {
    "allow": 0,
    "log": 1,
    "redact": 2,
    "block": 3
}


def evaluate_policy(findings):

    final_action = "allow"

    for finding in findings:

        finding_type = finding["type"]

        action = POLICY_RULES.get(
            finding_type,
            "allow"
        )

        if ACTION_PRIORITY[action] > ACTION_PRIORITY[final_action]:
            final_action = action

    return {
        "action": final_action,
        "findings": findings
    }