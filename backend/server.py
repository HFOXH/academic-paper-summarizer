from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
from typing import Optional, List, Dict
import json
import uuid
from datetime import datetime
from openai import OpenAI

load_dotenv()

app = FastAPI()

# CORS
origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔑 OPENAI CLIENT
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


# =========================
# PROMPT SYSTEM
# =========================

SYSTEM_PROMPT = """
You are an expert academic research assistant specializing in making scholarly work accessible across disciplines.

You MUST generate exactly three sections:

## Plain Language Summary
## Key Findings & Methodology
## Critical Analysis & Follow-up Questions

Rules:
- Do not hallucinate
- If missing info, say so
- Be precise and structured
- Adapt to user level
"""


# =========================
# INPUT MODEL
# =========================

class PaperRequest(BaseModel):
    paper_title: str = Field(..., min_length=10, max_length=300)
    paper_text: str = Field(..., min_length=100, max_length=5000)
    research_field: str
    target_audience_level: str = Field(
        ..., pattern="^(undergraduate|graduate|expert)$"
    )
    session_id: Optional[str] = None


class PaperResponse(BaseModel):
    response: str
    session_id: str


# =========================
# PROMPT BUILDER
# =========================

def build_user_prompt(r: PaperRequest) -> str:
    return f"""
Paper Title: {r.paper_title}

Research Field: {r.research_field}

Audience Level: {r.target_audience_level}

Paper Text:
{r.paper_text}

Generate structured analysis in the required format.
"""


# =========================
# OPENAI CALL
# =========================

def call_openai(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=2000
        )

        return response.choices[0].message.content

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# MEMORY (opcional simple local)
# =========================

MEMORY_DIR = "/tmp/memory"


def get_path(session_id: str):
    return os.path.join(MEMORY_DIR, f"{session_id}.json")


def load_memory(session_id: str):
    path = get_path(session_id)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []


def save_memory(session_id: str, data):
    os.makedirs(MEMORY_DIR, exist_ok=True)
    with open(get_path(session_id), "w") as f:
        json.dump(data, f, indent=2)


# =========================
# MAIN ENDPOINT
# =========================

@app.post("/analyze", response_model=PaperResponse)
async def analyze(request: PaperRequest):

    try:
        session_id = request.session_id or str(uuid.uuid4())

        user_prompt = build_user_prompt(request)

        result = call_openai(user_prompt)

        memory = load_memory(session_id)
        memory.append({
            "paper_title": request.paper_title,
            "response": result,
            "timestamp": datetime.now().isoformat()
        })
        save_memory(session_id, memory)

        return PaperResponse(
            response=result,
            session_id=session_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# HEALTH
# =========================

@app.get("/health")
def health():
    return {
        "status": "ok",
        "model": MODEL
    }