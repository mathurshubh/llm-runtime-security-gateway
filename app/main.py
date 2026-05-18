from fastapi import FastAPI
from pydantic import BaseModel
import requests

from app.detection.prompt_detector import analyze_prompt

app = FastAPI()

OLLAMA_URL = "http://localhost:11434/api/generate"


class ChatRequest(BaseModel):
    prompt: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat(request: ChatRequest):

    security_analysis = analyze_prompt(request.prompt)

    if security_analysis["blocked"]:
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