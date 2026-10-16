# AI Tech Consultant — Capstone Project

## Overview

AI Tech Consultant is a prototype consisting of three connected services for customer support, email assistance, and meeting scope analysis.

### Task 1: Knowledge Brain
- Reads URLs from the Brilliant Directories support sitemap.
- Downloads support articles and stores them in JSON.
- Searches saved articles using keyword matching.
- Returns potentially relevant article excerpts and source URLs through a FastAPI endpoint.

### Task 2: Inbox Agent
- Classifies customer emails into categories such as Billing, Technical Support, Account Management, and General Inquiry.
- Generates draft customer replies.
- Queries the Knowledge Brain for potentially relevant support resources.
- Requires human approval before sending replies.

### Task 3: Meeting-to-Scope
- Accepts meeting transcripts.
- Extracts sentences that may represent tasks or requirements.
- Produces a draft scope with tasks requiring human estimation.
- Flags possible scope changes using keyword-based rules.
- Queries the Knowledge Brain for potentially relevant documentation.
- Requires human approval before client delivery.

## Technology Stack

- Python
- FastAPI
- HTTPX
- Beautiful Soup
- XML parsing
- JSON
- Uvicorn

## Prerequisites

- Python 3.12 or compatible version
- Internet connection for initial sitemap and article retrieval

## Installation

Open PowerShell in the project directory and install the dependencies:

```powershell
py -m pip install fastapi "uvicorn[standard]" httpx beautifulsoup4 lxml
```

## Running the Services

Open three separate terminals.

**Terminal 1 — Knowledge Brain**

```powershell
cd task1-knowledge-brain
py -m uvicorn main:app --reload --port 8000
```

**Terminal 2 — Inbox Agent**

```powershell
cd task2-inbox-agent
py -m uvicorn main:app --reload --port 8001
```

**Terminal 3 — Meeting-to-Scope**

```powershell
cd task3-meeting-to-scope
py -m uvicorn main:app --reload --port 8002
```

Run these commands from the main project directory. If using a virtual environment, activate it in each terminal before starting the service.

## API Documentation

| Service | API documentation |
|---|---|
| Knowledge Brain | http://127.0.0.1:8000/docs |
| Inbox Agent | http://127.0.0.1:8001/docs |
| Meeting-to-Scope | http://127.0.0.1:8002/docs |

### Main Endpoints

- `GET /health` — Knowledge Brain health check
- `GET /articles/count` — Number of saved articles
- `POST /search` — Search the saved knowledge base
- `POST /draft` — Classify an email and prepare a draft reply
- `POST /generate-scope` — Generate a draft scope from a meeting transcript

## Testing

Test the endpoints using the interactive Swagger UI at `/docs`. Record actual responses and test results in `EVALS.md`.

## Current Limitations

This is an early working prototype. Search uses keyword matching rather than semantic retrieval. Email drafting and scope extraction use deterministic rules rather than a Claude-powered agent. Scope-change detection is preliminary, and task estimates require human review. Full sitemap synchronization, human-feedback learning, comprehensive model comparisons, and the complete evaluation suite remain to be implemented and verified.

## Human Review and Safety

Email replies and proposed scopes are drafts only. They must be reviewed by a human before being sent to a customer.

## Project Status

The three API services have been started, and successful HTTP responses have been observed during initial testing. Further integration testing, evaluation, and completion of the capstone requirements are required.
