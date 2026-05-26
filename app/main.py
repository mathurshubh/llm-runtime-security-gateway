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

from app.security.risk_engine import calculate_risk

from app.security.output_filter import inspect_output

from app.security.redactor import redact_sensitive_data

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

    # Perform input-side security inspection before forwarding prompts to the LLM runtime
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

    combined_findings = []

    for finding in security_analysis["findings"]:

        combined_findings.append({
            "type": "prompt_injection",
            "value": finding
        })

    for finding in pii_findings:

        combined_findings.append(finding)
    
    # Aggregate findings from multiple detectors into a centralized policy scoring engine
    risk_analysis = calculate_risk(combined_findings)

    if risk_analysis["severity"] in ["high", "critical"]:

        logger.warning(
            "\n🚨 SECURITY POLICY VIOLATION 🚨",
            user=api_user["user"],
            api_key=api_user["api_key"],
            event_id=str(uuid.uuid4()),
            findings=combined_findings,
            risk_score=risk_analysis["risk_score"],
            severity=risk_analysis["severity"]
        )

        return {
            "status": "blocked",
            "risk_analysis": risk_analysis,
            "findings": combined_findings
        }


    payload = {
        #"model": "llama3",
        "model": "llama3.2:3b",
        "prompt": request.prompt,
        "stream": False,
        "keep_alive": "30m"
    }

    # Forward sanitized request to local Ollama runtime
    response = requests.post(OLLAMA_URL, json=payload)

    response_data = response.json()

    model_output = response_data.get("response", "")

    # Inspect model output before returning response to prevent credential and token leakage
    output_analysis = inspect_output(model_output)

    if output_analysis["action"] == "redact":

        # Redact sensitive content while preserving safe explanatory context for the user
        redacted_output = redact_sensitive_data(model_output)

        logger.warning(
            "\n🚨 OUTPUT SECURITY VIOLATION 🚨",
            user=api_user["user"],
            api_key=api_user["api_key"],
            findings=output_analysis["findings"],
            action="redacted",
            event_id=str(uuid.uuid4())
        )
    
        response_data["response"] = redacted_output

        return response_data

    return response_data
