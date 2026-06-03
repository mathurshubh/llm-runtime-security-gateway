# Output-side inspection layer used to detect credential leakage and unsafe model responses before data is returned to users.

from app.detection.pii_detector import detect_pii
from app.security.policy_engine import evaluate_policy


# Analyze model responses for sensitive information and apply centralized policy enforcement decisions.
def inspect_output(
    response_text: str
) -> dict:

    # Reuse the detection pipeline to identify credentials, tokens, and other sensitive content in model output.
    findings = detect_pii(
        response_text
    )

    # Delegate enforcement decisions to the policy engine to ensure consistent handling across the security pipeline.
    return evaluate_policy(
        findings
    )