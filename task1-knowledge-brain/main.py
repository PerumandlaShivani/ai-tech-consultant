
import json
import re
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="AI Tech Consultant - Knowledge Brain")

DATA_FILE = Path(__file__).parent / "data" / "articles" / "articles.json"


def load_articles():
    if not DATA_FILE.exists():
        return []

    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def search_articles(question: str, limit: int = 3):
    articles = load_articles()
    words = set(re.findall(r"\b[a-zA-Z0-9]+\b", question.lower()))

    # Ignore common words that do not help search.
    stop_words = {
        "the", "is", "a", "an", "and", "or", "to",
        "of", "in", "for", "how", "what", "can", "i",
        "do", "my", "on", "with", "please"
    }
    words -= stop_words

    results = []

    for article in articles:
        title = article.get("title", "")
        content = article.get("content", "")
        url = article.get("url", "")

        title_words = set(
            re.findall(r"\b[a-zA-Z0-9]+\b", title.lower())
        )
        content_words = set(
            re.findall(r"\b[a-zA-Z0-9]+\b", content.lower())
        )

        title_matches = len(words & title_words)
        content_matches = len(words & content_words)
        score = title_matches * 3 + content_matches

        if score > 0:
            results.append({
                "title": title,
                "url": url,
                "content": content[:1500],
                "score": score,
            })

    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:limit]


class SearchRequest(BaseModel):
    question: str


@app.get("/")
async def home():
    return {
        "message": "Knowledge Brain is running!",
        "status": "success",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/articles/count")
async def article_count():
    return {"total_articles": len(load_articles())}


@app.post("/search")
async def search(request: SearchRequest):
    results = search_articles(request.question)

    if not results:
        return {
            "question": request.question,
            "message": (
                "I could not find a relevant article in the "
                "currently indexed knowledge base."
            ),
            "sources": [],
        }

    return {
        "question": request.question,
        "message": "Here are the most relevant articles I found.",
        "sources": results,
    }
