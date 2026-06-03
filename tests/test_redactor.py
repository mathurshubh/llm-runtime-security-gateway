from app.security.redactor import (
    redact_sensitive_data
)


def test_redact_jwt():

    text = (
        "Bearer eyJabc.def.ghi"
    )

    result = redact_sensitive_data(
        text
    )

    assert "REDACTED" in result


def test_redact_aws_key():

    text = (
        "AKIA1234567890123456"
    )

    result = redact_sensitive_data(
        text
    )

    assert "REDACTED" in result


def test_safe_text_unchanged():

    text = (
        "Explain Zero Trust Architecture"
    )

    result = redact_sensitive_data(
        text
    )

    assert result == text