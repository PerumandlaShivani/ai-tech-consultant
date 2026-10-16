
import re

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Meeting-to-Scope Agent")

KNOWLEDGE_API = "http://127.0.0.1:8000/search"


class ScopeRequest(BaseModel):
    transcript: str
    previous_scope: str = ""


def extract_tasks(transcript: str):
    """Extract action-like sentences as draft tasks."""
    sentences = re.split(r"(?<=[.!?])\s+|\n+", transcript)
    keywords = (
        "need", "should", "must", "add", "create",
        "build", "implement", "update", "integrate",
        "require", "include", "remove", "change"
    )

    tasks = []
    for sentence in sentences:
        sentence = sentence.strip(" -\t")
        if len(sentence) > 10 and any(
            word in sentence.lower() for word in keywords
        ):
            tasks.append(sentence)

    return tasks[:20]


@app.get("/")
def home():
    return {"status": "healthy", "service": "Meeting-to-Scope"}


@app.post("/generate-scope")
async def generate_scope(request: ScopeRequest):
    tasks = extract_tasks(request.transcript)

    # Ask Task 1 for potentially relevant product documentation.
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                KNOWLEDGE_API,
                json={"question": request.transcript[:1500]},
            )
            response.raise_for_status()
            knowledge = response.json()
    except httpx.HTTPError:
        knowledge = {"sources": []}

    sources = [
        {"title": item.get("title", ""), "url": item.get("url", "")}
        for item in knowledge.get("sources", [])
    ]

    previous = request.previous_scope.strip()
    transcript_lower = request.transcript.lower()

    # Simple keyword comparison; this is a preliminary change flag,
    # not a semantic determination of scope changes.
    change_terms = [
        "add", "additional", "new feature", "also need",
        "out of scope", "change request", "remove"
    ]
    change_flag = bool(previous) and any(
        term in transcript_lower for term in change_terms
    )

    return {
        "status": "draft",
        "proposed_scope": {
            "summary": (
                "Draft scope extracted from the meeting transcript. "
                "Confirm details with the customer before approval."
            ),
            "tasks": [
                {
                    "task": task,
                    "estimate_hours": None,
                    "estimate_note": (
                        "Requires human estimation; no estimate "
                        "has been generated."
                    ),
                }
                for task in tasks
            ],
        },
        "previous_scope_provided": bool(previous),
        "potential_scope_change": change_flag,
        "change_review_note": (
            "Review the transcript against the previous scope manually. "
            "This keyword-based flag can miss or over-report changes."
            if previous
            else "Provide previous_scope to enable a preliminary comparison."
        ),
        "knowledge_sources": sources,
        "requires_human_approval": True,
        "sent_to_client": False,
    }
