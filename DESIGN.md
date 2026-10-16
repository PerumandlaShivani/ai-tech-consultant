# DESIGN.md — AI Tech Consultant

## 1. System Overview

The project contains three Python/FastAPI services:

1. **Knowledge Brain:** collects support articles and provides keyword-based search.
2. **Inbox Agent:** classifies customer emails and prepares suggested replies.
3. **Meeting-to-Scope:** extracts potential requirements from meeting transcripts and produces draft scopes.

The Inbox Agent and Meeting-to-Scope service query the Knowledge Brain API for potentially relevant support resources.

## 2. Architecture

```text
Brilliant Directories Sitemap
              |
              v
     Sitemap Reader
              |
              v
      Article Scraper
              |
              v
        articles.json
              |
              v
    Knowledge Brain API
         Port 8000
          /       \
         v         v
   Inbox Agent   Meeting-to-Scope
    Port 8001       Port 8002
         |              |
         v              v
   Draft Email     Draft Scope
         |              |
         v              v
   Human Review    Human Review
```

## 3. Task 1 — Knowledge Brain

### Data ingestion

The sitemap reader downloads the support sitemap and extracts URLs. The article scraper retrieves a limited initial batch of solution pages, extracts page text, and stores the resulting records in JSON.

Each saved record includes a title, URL, and content.

### Retrieval

The `/search` endpoint uses keyword matching. It assigns greater weight to matching title words than to matching content words and returns up to three matching articles.

### Limitations

The current prototype does not provide semantic search, a Claude-generated answer, automated daily sitemap synchronization, complete image handling, or a human-feedback learning pipeline.

## 4. Task 2 — Inbox Agent

The `/draft` endpoint accepts the sender, subject, and email body.

The service classifies the email using keyword rules, then sends the email text to the Knowledge Brain search endpoint. It prepares a draft response containing potentially relevant article links when available.

Replies are not automatically sent. Human approval is required.

### Limitations

Classification is rule-based. The current prototype does not yet implement Claude-powered drafting, learning from human edits, or a validated automation policy based on consecutive unchanged drafts.

## 5. Task 3 — Meeting-to-Scope

The `/generate-scope` endpoint accepts a meeting transcript and an optional previous scope.

The service extracts sentences containing selected requirement-related keywords, queries the Knowledge Brain, and produces a draft scope.

If a previous scope is supplied, simple keyword rules flag potential scope changes. Task estimates are left for human review.

### Limitations

This is not yet a full multi-agent workflow. Extraction is rule-based, scope-change detection is not semantic, and effort estimates are not automatically calculated.

## 6. API Communication

| Service | Endpoint | Purpose |

| Knowledge Brain | `POST /search` | Retrieve potentially relevant articles |
| Inbox Agent | `POST /draft` | Prepare a customer email draft |
| Meeting-to-Scope | `POST /generate-scope` | Prepare a scope draft |

The services communicate over localhost during development. HTTPX is used for calls from the two downstream services to the Knowledge Brain.

## 7. Error Handling and Safety

The downstream services handle HTTP request errors when contacting the Knowledge Brain and can continue with an empty source list. A missing knowledge source should not be interpreted as proof that a requested feature is unsupported.

Human review is required before email replies or proposed scopes are sent externally.

## 8. Future Improvements

- Integrate Claude as the central reasoning model.
- Improve article extraction, image references, and sitemap change detection.
- Add semantic retrieval and grounded answers with citations.
- Add human-feedback capture and evaluation.
- Build a validated multi-agent transcript analysis pipeline.
- Implement scope comparison and estimation with explicit uncertainty.
- Add automated tests, structured logging, configuration, and model cost/latency tracking.
