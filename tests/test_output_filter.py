from app.security.output_filter import (
    inspect_output
)


def test_jwt_output_redacted():

    result = inspect_output(
        "eyJabc.def.ghi"
    )

    assert result["action"] == "redact"


def test_email_output_logged():

    result = inspect_output(
        "contact me at test@example.com"
    )

    assert result["action"] == "log"


def test_safe_output_allowed():

    result = inspect_output(
        "Zero Trust is a security model."
    )

    assert result["action"] == "allow"


def test_prompt_injection_output_allowed():

    result = inspect_output(
        "ignore previous instructions"
    )

    assert result["action"] == "allow"