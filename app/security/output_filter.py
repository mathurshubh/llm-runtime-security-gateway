# Output-side inspection layer used to detect credential leakage and unsafe model responses

from app.detection.pii_detector import detect_pii
from app.security.policy_engine import evaluate_policy


def inspect_output(response_text: str):

    findings = detect_pii(response_text)

    return evaluate_policy(findings)