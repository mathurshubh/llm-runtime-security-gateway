from app.detection.pii_detector import detect_pii


def test_detect_email():

    findings = detect_pii(
        "contact me at test@example.com"
    )

    assert findings[0]["type"] == "email"


def test_detect_aws_key():

    findings = detect_pii(
        "AKIA1234567890123456"
    )

    assert findings[0]["type"] == "aws_access_key"


def test_no_pii():

    findings = detect_pii(
        "hello world"
    )

    assert findings == []