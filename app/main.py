from fastapi import FastAPI
from pydantic import BaseModel
import requests
import uuid

from app.detection.prompt_detector import analyze_prompt
from app.telemetry.logger import logger

from fastapi import Depends
from app.auth.api_key_auth import validate_api_key

from app.middleware.rate_limiter import check_rate_limit

from app.detection.pii_detector import detect_pii

app = FastAPI()

OLLAMA_URL = "http://localhost:11434/api/generate"


class ChatRequest(BaseModel):
    prompt: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat(
    request: ChatRequest,
    api_user: dict = Depends(validate_api_key)
):    
    
    check_rate_limit(
        api_user["api_key"],
        api_user["user"]
    )

    security_analysis = analyze_prompt(request.prompt)

    pii_findings = detect_pii(request.prompt)

    email_findings = [
        finding
        for finding in pii_findings
        if finding["type"] == "email"
    ]

    if email_findings:

        logger.info(
            "\n📧 EMAIL DETECTED 📧",
            user=api_user["user"],
            api_key=api_user["api_key"],
            findings=email_findings
        )
        
    high_risk_pii = [
        "aws_access_key",
        "bearer_token",
        "password_assignment"
    ]

    detected_high_risk = any(
        finding["type"] in high_risk_pii
        for finding in pii_findings
    )

    if security_analysis["blocked"]:
        logger.warning(
            "\n🚨 PROMPT BLOCKED 🚨",
            event_id=str(uuid.uuid4()),
            user=api_user["user"],
            severity=security_analysis["severity"],
            risk_score=security_analysis["risk_score"],
            findings=", ".join(security_analysis["findings"]),
            prompt=request.prompt,
        )
        return {
            "status": "blocked",
            "security_analysis": security_analysis
        }
    
    if detected_high_risk:

        logger.warning(
            "\n🚨 PII / SECRET DETECTED 🚨",
            user=api_user["user"],
            api_key=api_user["api_key"],
            findings=pii_findings
        )

        return {
            "status": "blocked",
            "reason": "Sensitive data detected",
            "findings": pii_findings
        }

    payload = {
        "model": "llama3",
        "prompt": request.prompt,
        "stream": False,
        "keep_alive": "0m"
    }

    response = requests.post(OLLAMA_URL, json=payload)

    return response.json()