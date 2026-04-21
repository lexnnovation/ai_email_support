# BUILD TASKS – AI APARTMENT SUPPORT SYSTEM (EXECUTION MODE)

## GLOBAL RULES

- Execute tasks strictly in order
- Do NOT skip any task
- Do NOT modify architecture
- Do NOT rename files unless instructed
- Do NOT add extra features
- If a task fails, STOP and fix before continuing

---

## PHASE 1: PROJECT INITIALIZATION

### Task 1: Initialize project

Run:

uv init ai-support-system

Then:

cd ai-support-system

---

### Task 2: Install dependencies

Run:

uv add fastapi uvicorn openai supabase python-dotenv

---

### Task 3: Create project structure

Create the following folders and files:

app/
app/main.py

app/api/
app/api/routes.py

app/services/
app/services/ai_service.py
app/services/embedding_service.py
app/services/retrieval_service.py

app/db/
app/db/supabase_client.py

app/models/
app/models/schemas.py

app/core/
app/core/config.py

---

## PHASE 2: ENVIRONMENT SETUP

### Task 4: Create environment file

Create `.env` in root:

OPENAI_API_KEY=your_openai_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

---

### Task 5: Load environment variables

In `app/core/config.py`:

- Import dotenv
- Load environment variables
- Expose variables:
  - OPENAI_API_KEY
  - SUPABASE_URL
  - SUPABASE_KEY

---

## PHASE 3: DATABASE SETUP (SUPABASE)

### Task 6: Enable pgvector

Run in Supabase SQL editor:

create extension if not exists vector;

---

### Task 7: Create documents table

Run:

create table documents (
id bigserial primary key,
content text not null,
embedding vector(1536),
apartment text not null,
type text not null,
created_at timestamp default now()
);

---

### Task 8: Create RPC function

Run:

create function match_documents (
query_embedding vector,
match_count int,
apartment_filter text
)
returns table (
id bigint,
content text,
similarity float
)
language sql
as $$
select
id,
content,
1 - (embedding <=> query_embedding) as similarity
from documents
where apartment = apartment_filter
or apartment = 'general'
order by embedding <=> query_embedding
limit match_count;

$$
;

---

## PHASE 4: DATABASE CLIENT

### Task 9: Implement Supabase client

File: app/db/supabase_client.py

Requirements:

- Import create_client from supabase
- Read URL and KEY from config
- Initialize client
- Export client as `supabase`

---

## PHASE 5: EMBEDDING SERVICE

### Task 10: Implement embedding service

File: app/services/embedding_service.py

Requirements:

- Initialize OpenAI client
- Create function:

get_embedding(text: str) -> list

- Use model:
  text-embedding-3-small

- Return embedding array

---

## PHASE 6: RETRIEVAL SERVICE

### Task 11: Implement retrieval service

File: app/services/retrieval_service.py

Requirements:

- Import supabase client
- Create function:

retrieve_documents(query_embedding, apartment)

- Call RPC: match_documents
- Pass:
  - query_embedding
  - match_count = 5
  - apartment_filter = apartment

- Return list of results

---

## PHASE 7: AI SERVICE

### Task 12: Implement AI service

File: app/services/ai_service.py

Responsibilities:

1. Normalize input (translate to English)
2. Detect intent:
   - "question"
   - "non_question"
3. If non_question:
   → return short email response
4. If question:
   → generate embedding
   → retrieve documents
5. If no results:
   → return fallback email
6. If results:
   → generate final answer using best document

---

### Task 13: Email format (MANDATORY)

All responses must follow EXACTLY:

Dear Guest,

<message>

Best regards,
Apartment Support Team

---

### Task 14: Fallback response

Use EXACT text:

I couldn't find that information in the apartment documents.

---

## PHASE 8: REQUEST SCHEMA

### Task 15: Create schema

File: app/models/schemas.py

Create model:

SupportRequest:
- chatInput: str
- apartment: Optional[str]

---

## PHASE 9: API ROUTES

### Task 16: Create route

File: app/api/routes.py

Create endpoint:

POST /support

Flow:

- Receive request
- Call AI service
- Return:

{
  "reply": "..."
}

---

## PHASE 10: MAIN APPLICATION

### Task 17: Setup FastAPI app

File: app/main.py

Requirements:

- Initialize FastAPI
- Include routes
- Add health endpoint:

GET /

Return:

{ "status": "ok" }

---

## PHASE 11: RUN APPLICATION

### Task 18: Start server

Run:

uv run uvicorn app.main:app --reload

---

## PHASE 12: N8N INTEGRATION

### Task 19: Configure HTTP Request

POST to:

http://localhost:8000/support

Body:

{
  "chatInput": "={{ $json.body }}",
  "apartment": ""
}

---

### Task 20: Gmail reply

Use:

{{$json.reply}}

---

## PHASE 13: DATA INGESTION

### Task 21: Prepare FAQ format

Each row MUST be:

Question + Answer combined:

"Question: ... Answer: ..."

---

### Task 22: Insert into Supabase

- Generate embeddings
- Insert:
  - content
  - embedding
  - apartment = "general"
  - type = "faq"

---

## PHASE 14: TESTING

### Task 23: Test scenarios

- Italian message → must translate
- No apartment → must ask for it
- FAQ question → must match
- Unknown question → fallback
- Simple message → non_question

---

## COMPLETION CRITERIA

System is complete when:

- Email is received and replied automatically
- Correct FAQ answers are returned
- Apartment filtering works
- System handles multilingual input
- No crashes occur

---

## FINAL RULE

DO NOT ADD FEATURES
DO NOT CHANGE FLOW
FOLLOW EXACTLY
$$
