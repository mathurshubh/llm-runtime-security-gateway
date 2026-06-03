from app.security.risk_engine import calculate_risk


def test_prompt_injection_risk():

    findings = [
        {
            "type": "prompt_injection"
        }
    ]

    result = calculate_risk(findings)

    assert result["risk_score"] == 70
    assert result["severity"] == "high"


def test_email_risk():

    findings = [
        {
            "type": "email"
        }
    ]

    result = calculate_risk(findings)

    assert result["risk_score"] == 20
    assert result["severity"] == "low"


def test_critical_risk():

    findings = [
        {
            "type": "jwt_token"
        }
    ]

    result = calculate_risk(findings)

    assert result["risk_score"] == 90
    assert result["severity"] == "critical"


def test_multiple_findings():

    findings = [
        {
            "type": "email"
        },
        {
            "type": "prompt_injection"
        }
    ]

    result = calculate_risk(findings)

    assert result["risk_score"] == 90
    assert result["severity"] == "high"