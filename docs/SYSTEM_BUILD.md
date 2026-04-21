# AI APARTMENT SUPPORT SYSTEM – PRODUCTION BUILD SPEC

---

## 0. EXECUTION CONTRACT (MANDATORY)

This document is a STRICT BUILD SPECIFICATION.

The coding agent MUST:

- Follow ALL instructions EXACTLY
- NOT change architecture
- NOT rename files
- NOT introduce alternative approaches
- NOT simplify logic
- NOT skip steps
- NOT add optional improvements

If any ambiguity occurs:
→ STOP and DO NOT proceed

This system MUST be implemented as defined.

---

## 1. OBJECTIVE

Build a production-grade AI-powered apartment support system that:

- Automatically replies to emails
- Handles multilingual input (Italian, English, etc.)
- Retrieves answers using vector search
- Supports multiple apartments
- Uses a single source of truth (Supabase)

---

## 2. SYSTEM ARCHITECTURE (FIXED)

Gmail → n8n → FastAPI → Supabase → FastAPI → n8n → Gmail Reply

---

## 3. COMPONENT RESPONSIBILITIES (NON-NEGOTIABLE)

### n8n

- ONLY handles:
  - email ingestion
  - HTTP call to FastAPI
  - email reply
- MUST NOT:
  - perform AI reasoning
  - perform ranking
  - perform logic

---

### FastAPI

- MUST handle ALL:
  - normalization
  - intent detection
  - embedding generation
  - vector retrieval
  - response generation

---

### Supabase

- MUST be the ONLY knowledge source
- MUST store:
  - FAQ
  - apartment data

---

### OpenAI

- MUST be used for:
  - embeddings
  - language understanding
  - response generation

---

## 4. TECH STACK (LOCKED)

- Python 3.11+
- FastAPI
- uv (MANDATORY package manager)
- Supabase (Postgres + pgvector)
- OpenAI API
- n8n
- Gmail API

NO substitutions allowed.

---

## 5. PROJECT STRUCTURE (MUST MATCH EXACTLY)

app/
├── main.py
├── api/
│ └── routes.py
│
├── services/
│ ├── ai_service.py
│ ├── embedding_service.py
│ ├── retrieval_service.py
│
├── db/
│ └── supabase_client.py
│
├── models/
│ └── schemas.py
│
└── core/
└── config.py

---

## 6. ENVIRONMENT SETUP

### Install uv

```bash
curl -Ls https://astral.sh/uv/install.sh | sh
```

---

## 7. N8N WEBHOOK CONTRACT (MANDATORY)

### 7.1 REQUEST FLOW

n8n MUST call FastAPI endpoint:

POST /support

Request body MUST be:

{
"chatInput": "<email body>",
"apartment": "<string or empty>"
}

- chatInput = raw email text
- apartment = extracted value or empty string

---

### 7.2 RESPONSE FORMAT (STRICT)

FastAPI MUST return:

{
"reply": "<formatted email text>"
}

- reply MUST be plain text
- reply MUST follow email format

---

### 7.3 EMAIL FORMAT (ENFORCED)

All responses MUST be:

Dear Guest,

<message>

Best regards,  
Apartment Support Team

---

### 7.4 N8N RESPONSIBILITY

n8n MUST:

- extract email body
- send HTTP request to FastAPI
- receive response.reply
- send reply email

n8n MUST NOT:

- perform AI logic
- perform ranking
- perform translation
- perform retrieval

---

### 7.5 ERROR HANDLING

If FastAPI fails:

- n8n MUST NOT send empty response
- n8n SHOULD log error
- n8n MAY retry request

---

### 7.6 TIMEOUT RULE

FastAPI response MUST be < 10 seconds

---

### 7.7 LANGUAGE HANDLING

n8n sends RAW input
FastAPI handles ALL language processing

---
