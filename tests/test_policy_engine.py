from app.security.policy_engine import evaluate_policy


def test_prompt_injection_block():

    findings = [
        {"type": "prompt_injection"}
    ]

    result = evaluate_policy(findings)

    assert result["action"] == "block"


def test_email_log():

    findings = [
        {"type": "email"}
    ]

    result = evaluate_policy(findings)

    assert result["action"] == "log"


def test_jwt_redact():

    findings = [
        {"type": "jwt_token"}
    ]

    result = evaluate_policy(findings)

    assert result["action"] == "redact"


def test_no_findings_allow():

    result = evaluate_policy([])

    assert result["action"] == "allow"


def test_most_restrictive_action_wins():

    findings = [
        {"type": "email"},
        {"type": "jwt_token"},
        {"type": "prompt_injection"}
    ]

    result = evaluate_policy(findings)

    assert result["action"] == "block"