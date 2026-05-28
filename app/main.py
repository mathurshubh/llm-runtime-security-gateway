from fastapi import FastAPI
from pydantic import BaseModel
import requests
import uuid

from app.detection.prompt_detector import analyze_prompt
from app.telemetry.logger import logger

from fastapi import Depends

from app.auth.jwt_auth import validate_jwt_token

from app.middleware.rate_limiter import check_rate_limit

from app.detection.pii_detector import detect_pii

from app.security.risk_engine import calculate_risk

from app.security.output_filter import inspect_output

from app.security.redactor import redact_sensitive_data

from app.security.policy_engine import evaluate_policy

from fastapi.responses import PlainTextResponse

from prometheus_client import generate_latest

from app.telemetry.metrics import (
    requests_total,
    blocked_requests_total,
    redacted_outputs_total,
    policy_actions_total,
    jwt_detections_total,
    aws_key_detections_total
)

from fastapi.security import OAuth2PasswordRequestForm

from app.auth.jwt_auth import (
    authenticate_user,
    create_access_token
)

from app.auth.rbac import require_role


app = FastAPI()

OLLAMA_URL = "http://localhost:11434/api/generate"


class ChatRequest(BaseModel):
    prompt: str


@app.get("/health")
def health():
    return {"status": "ok"}


    
@app.get("/admin/policies")
def admin_policies(
    api_user: dict = Depends(
        require_role(["admin"])
    )
):    

    return {
        "status": "success",
        "message": "Admin policy access granted",
        "user": api_user["username"],
        "role": api_user["role"]
    }


@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):

    user = authenticate_user(
        form_data.username,
        form_data.password
    )

    if not user:

        return {
            "status": "error",
            "message": "Invalid username or password"
        }

    access_token = create_access_token({
        "sub": user["username"],
        "role": user["role"]
    })

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.get("/metrics")
def metrics():

    return PlainTextResponse(
        generate_latest().decode("utf-8")
    )

   

@app.post("/chat")
def chat(
    request: ChatRequest,
    api_user: dict = Depends(
        require_role([
            "admin",
            "analyst",
            "user"
        ])
    )
):
    check_rate_limit(
        api_user["username"],
        api_user["username"]
    )

    requests_total.inc()

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
            user=api_user["username"],
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

    policy_result = evaluate_policy(combined_findings)

    policy_actions_total.labels(
        action=policy_result["action"]
    ).inc()

    if policy_result["action"] == "block":

        blocked_requests_total.inc()

        logger.warning(
            "\n🚨 SECURITY POLICY VIOLATION 🚨",
            user=api_user["username"],
            event_id=str(uuid.uuid4()),
            findings=combined_findings,
            risk_score=risk_analysis["risk_score"],
            severity=risk_analysis["severity"],
            action="block"
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

        redacted_outputs_total.inc()

        # Redact sensitive content while preserving safe explanatory context for the user
        redacted_output = redact_sensitive_data(model_output)

        for finding in output_analysis["findings"]:

            if finding["type"] in [
                "jwt_token",
                "jwt_fragment"
            ]:
                jwt_detections_total.inc()

            if finding["type"] in [
                "aws_access_key",
                "aws_secret_key"
            ]:
                aws_key_detections_total.inc()

        logger.warning(
            "\n🚨 OUTPUT SECURITY VIOLATION 🚨",
            user=api_user["username"],
            findings=output_analysis["findings"],
            action="redacted",
            event_id=str(uuid.uuid4())
        )
    
        response_data["response"] = redacted_output

        return response_data

    return response_data
