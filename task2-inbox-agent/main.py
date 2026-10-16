
import os
import re

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Inbox Agent")

KNOWLEDGE_API = os.getenv(
    "KNOWLEDGE_API",
    "http://127.0.0.1:8000/search",
)


class EmailRequest(BaseModel):
    sender: str
    subject: str
    body: str


def classify_email(text: str) -> str:
    text = text.lower()

    if any(word in text for word in ["refund", "billing", "invoice", "payment"]):
        return "Billing"
    if any(word in text for word in ["error", "bug", "not working", "broken"]):
        return "Technical Support"
    if any(word in text for word in ["cancel", "subscription", "plan"]):
        return "Account Management"

    return "General Inquiry"


@app.get("/")
def home():
    return {"status": "healthy", "service": "Inbox Agent"}


@app.post("/draft")
async def draft_reply(email: EmailRequest):
    email_text = f"{email.subject}\n{email.body}"
    category = classify_email(email_text)

    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                KNOWLEDGE_API,
                json={"question": email_text},
            )

            print("Knowledge API status:", response.status_code)
            response.raise_for_status()

            knowledge = response.json()
            print(
                "Knowledge API sources:",
                len(knowledge.get("sources", [])),
            )

    except (httpx.HTTPError, ValueError) as error:
        print("Knowledge API error:", repr(error))
        knowledge = {"sources": []}


    sources = knowledge.get("sources", [])
    relevant_sources = [
        {
            "title": source.get("title", ""),
            "url": source.get("url", ""),
        }
        for source in sources
    ]

    if relevant_sources:
        source_text = "\n".join(
            f"- {item['title']}: {item['url']}"
            for item in relevant_sources
        )
        reply = (
            f"Hello,\n\n"
            f"Thank you for contacting us regarding "
            f"{email.subject}.\n\n"
            f"Our support knowledge base contains these potentially "
            f"relevant resources:\n{source_text}\n\n"
            f"Please review the resources above. If they do not resolve "
            f"your issue, reply with additional details so our team "
            f"can investigate.\n\n"
            f"Best regards,\nSupport Team"
        )
    else:
        reply = (
            "Hello,\n\n"
            "Thank you for contacting our support team. "
            "We need to review your request before providing a "
            "specific solution. A team member will follow up.\n\n"
            "Best regards,\nSupport Team"
        )

    return {
        "category": category,
        "sender": email.sender,
        "subject": email.subject,
        "draft_reply": reply,
        "sources": relevant_sources,
        "requires_human_approval": True,
        "automatically_sent": False,
    }
