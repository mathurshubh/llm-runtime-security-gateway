from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import uuid
import os

from app.detection.prompt_detector import analyze_prompt
from app.telemetry.logger import logger

from fastapi import Depends

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

from app.security.event_store import (
    store_security_event,
    get_security_events,
    get_security_summary
)

from opentelemetry import trace

from opentelemetry.sdk.trace import TracerProvider

from opentelemetry.instrumentation.fastapi import (
    FastAPIInstrumentor
)

from opentelemetry.sdk.resources import Resource

from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter
)

from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor
)

app = FastAPI()

# Configure OpenTelemetry resource metadata used by Jaeger and downstream observability platforms.
resource = Resource.create(
    {
        "service.name": "llm-runtime-security-gateway"
    }
)

trace.set_tracer_provider(
    TracerProvider(
        resource=resource
    )
)

tracer = trace.get_tracer(__name__)

# Export distributed traces to Jaeger for security pipeline observability, latency analysis, and runtime debugging.
otlp_exporter = OTLPSpanExporter(
    endpoint="localhost:4317",
    insecure=True
)

trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(
        otlp_exporter
    )
)

# Automatically capture request-level traces for all FastAPI endpoints in addition to custom security spans.
FastAPIInstrumentor.instrument_app(app)


OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate"

)


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


@app.get("/security/events")
def security_events(
    api_user: dict = Depends(
        require_role(["admin"])
    )
):

    return {
        "event_count": len(
            get_security_events()
        ),
        "events": get_security_events()
    }


@app.get("/security/summary")
def security_summary(
    api_user: dict = Depends(
        require_role(["admin"])
    )
):

    return get_security_summary()


# Issue signed JWT access tokens used for authentication and downstream RBAC authorization decisions.
@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):

    user = authenticate_user(
        form_data.username,
        form_data.password
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

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

# Primary gateway entrypoint. Requests traverse authentication, authorization, rate limiting, security inspection, policy 
# enforcement, model inference, and output filtering before a response is returned to the client.   
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
    # Enforce per-user distributed rate limits before any expensive security processing or model inference occurs.
    check_rate_limit(
        api_user["username"],
        api_user["username"]
    )

    requests_total.inc()

    # Perform input-side security inspection before forwarding prompts to the LLM runtime
    with tracer.start_as_current_span(
        "Prompt Inspection"
    ):

        security_analysis = analyze_prompt(
            request.prompt
        )

        pii_findings = detect_pii(
            request.prompt
        )

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

    # Normalize findings from multiple detection engines into a common structure consumed by the risk and policy engines.
    combined_findings = []

    for finding in security_analysis["findings"]:

        combined_findings.append({
            "type": "prompt_injection",
            "value": finding
        })

    for finding in pii_findings:

        combined_findings.append(finding)
    
    # Aggregate findings into centralized risk scoring and policy enforcement workflows.
    with tracer.start_as_current_span(
        "Policy Engine"
    ) as span:

        risk_analysis = calculate_risk(
            combined_findings
        )

        policy_result = evaluate_policy(
            combined_findings
        )

        span.set_attribute(
            "findings.count",
            len(combined_findings)
        )

        span.set_attribute(
            "policy.action",
            policy_result["action"]
        )

        span.set_attribute(
            "risk.score",
            risk_analysis["risk_score"]
        )

        span.set_attribute(
            "risk.severity",
            risk_analysis["severity"]
        )

    policy_actions_total.labels(
        action=policy_result["action"]
    ).inc()
    
    # High-risk requests are terminated before reaching the LLM runtime to reduce prompt injection and abuse exposure.
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

        # Persist security-relevant decisions for auditability, incident investigation, and analytics.
        store_security_event(
            event_type="policy_violation",
            user=api_user["username"],
            details={
            "severity": risk_analysis["severity"],
            "risk_score": risk_analysis["risk_score"],
            "findings": combined_findings,
            "action": "block"
        }
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

    # Only requests that pass policy enforcement are forwarded to the underlying LLM runtime.
    with tracer.start_as_current_span(
        "Ollama Inference"
    ):

        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=60
        )

        response.raise_for_status()

        response_data = response.json()

        model_output = response_data.get(
            "response",
            ""
        )

    # Inspect model output before returning response to prevent credential and token leakage
    with tracer.start_as_current_span(
        "Output Inspection"
    ):

        output_analysis = inspect_output(
            model_output
        )

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

        # Record output-side security violations to support post-incident analysis and security reporting.
        store_security_event(
            event_type="output_security_violation",
            user=api_user["username"],
            details={
                "findings": output_analysis["findings"],
                "action": "redacted"
            }
        )

        response_data["response"] = redacted_output

        return response_data

    return response_data
