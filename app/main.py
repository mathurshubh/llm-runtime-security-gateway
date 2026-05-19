from fastapi import FastAPI
from pydantic import BaseModel
import requests
import uuid

from app.detection.prompt_detector import analyze_prompt
from app.telemetry.logger import logger

from fastapi import Depends
from app.auth.api_key_auth import validate_api_key

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

    security_analysis = analyze_prompt(request.prompt)

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

    payload = {
        "model": "llama3",
        "prompt": request.prompt,
        "stream": False,
        "keep_alive": "0m"
    }

    response = requests.post(OLLAMA_URL, json=payload)

    return response.json()