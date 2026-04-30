# SRL Email Support

AI-powered apartment guest email support system. Automatically answers guest questions about parking, WiFi, check-in, amenities, and more using FAQ and policy document retrieval.

## Setup

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- OpenAI API key
- Supabase project with pgvector extension

### Install

```bash
git clone <repo-url>
cd ai_email_support
uv sync
cp .env.example .env
# Edit .env with your actual keys
```

### Environment Variables

| Variable         | Description                                   |
| ---------------- | --------------------------------------------- |
| `OPENAI_API_KEY` | OpenAI API key for GPT-4o-mini and embeddings |
| `SUPABASE_URL`   | Supabase project URL                          |
| `SUPABASE_KEY`   | Supabase service role key                     |

### Ingest Data

```bash
# Ingest all data (XLSX + PDFs)
uv run python ingest.py

# Re-ingest PDFs only (clears old PDF data first)
uv run python ingest.py --pdfs-only
```

### Run Locally

```bash
uv run uvicorn app.main:app --reload
```

Server starts at `http://127.0.0.1:8000`

## API

### `GET /`

Health check. Returns `{"status": "ok"}`.

### `POST /support`

Process a guest email and return an AI-generated reply.

**Request body:**

```json
{
  "chatInput": "Email body text",
  "apartment": "",
  "subject": "Email subject line"
}
```

**Response:**

```json
{
  "reply": "Dear Guest,\n\n...\n\nBest regards,\nApartment Support Team"
}
```

## Deploy on VPS

```bash
# Clone and install
git clone <repo-url>
cd ai_email_support
uv sync
cp .env.example .env
# Edit .env with production keys

# Run with uvicorn
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

For production, use a process manager (systemd) and reverse proxy (nginx).

## n8n Integration

HTTP Request node body:

```json
{
  "chatInput": "={{ $json.body }}",
  "apartment": "",
  "subject": "={{ $json.subject }}"
}
```
