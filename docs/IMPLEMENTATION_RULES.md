4821"}

# IMPLEMENTATION RULES – AI APARTMENT SUPPORT SYSTEM

---

## 1. GENERAL RULES (MANDATORY)

- Follow instructions EXACTLY
- Do NOT modify architecture
- Do NOT rename files
- Do NOT introduce abstractions
- Do NOT add extra features
- Do NOT explain code
- If unclear → STOP

---

## 2. DATA INGESTION RULES (CRITICAL)

### 2.1 CONTENT FIELD

- MUST contain clean, human-readable text
- MUST NOT contain:
  - JSON
  - PDF metadata
  - blob data
  - structured objects

---

### 2.2 METADATA FIELD

MUST ONLY contain:

{
"apartment": "<string>",
"type": "faq" | "policy"
}

DO NOT add any other fields.

---

## 3. PDF INGESTION RULES

- Extract ONLY readable text
- Remove extra spaces
- Chunk text:
  - size = 500 characters
  - overlap = 100 characters
- Skip chunks < 50 characters

---

## 4. EMBEDDING RULES

- Model: text-embedding-3-small
- Generate embedding per chunk
- Do NOT batch unrelated content

---

## 5. DATABASE RULES

- Table: documents
- Insert format:

{
"content": "<text>",
"embedding": <vector>,
"metadata": {
"apartment": "...",
"type": "..."
}
}

---

## 6. STRICT PROHIBITIONS

NEVER:

- Store raw PDF structure
- Store file metadata
- Store nested JSON inside content
- Modify schema
- Add new columns

---

## 7. RESPONSE RULES

When generating email responses:

Structure MUST be:

Dear Guest,

<message>

Best regards,  
Apartment Support Team

---

## 8. FAILURE HANDLING

If rules are violated:

- STOP execution
- Fix issue before continuing
- Do NOT proceed with incorrect dat

---

## 9. RETRIEVAL RULES (CRITICAL)

- ALL answers MUST come from Supabase vector search
- NEVER answer from model knowledge for apartment-specific data
- ALWAYS retrieve before answering

---

## 10. VECTOR SEARCH RULES

- MUST call: match_documents
- MUST pass:
  - query_embedding
  - match_count = 5
  - apartment_filter

- MUST filter using:

metadata->>'apartment' = apartment_filter
OR metadata->>'apartment' = 'general'

---

## 11. MULTILINGUAL RULES

- ALWAYS normalize input to English before embedding
- Input may be:
  - Italian
  - English
  - mixed language

- DO NOT rely on keywords
- Use semantic meaning

---

## 12. INTENT DETECTION RULES

Classify input as:

- "question"
- "non_question"

Rules:

- Statements like:
  "I sent deposit"
  "Thanks"
  → non_question

- Requests, issues, or inquiries
  → question

---

## 13. RESPONSE GENERATION RULES

IF type = "non_question":

- Respond politely
- Do NOT query vector DB
- Keep response short (1–3 sentences)

---

IF type = "question":

- MUST:
  1. generate embedding
  2. retrieve documents
  3. answer using retrieved content ONLY

---

## 14. FALLBACK RULE

If no relevant documents found:

Return EXACTLY:

"I couldn't find that information in the apartment documents."

---

## 15. APARTMENT CONTEXT RULE

IF apartment is missing:

- DO NOT query vector DB
- Ask user for apartment name
- Provide general guidance if possible

---

## 16. TOOL USAGE RULES (FOR AI AGENTS)

- Supabase vector store is the ONLY knowledge tool
- Google Sheets MUST NOT be used at runtime
- FAQ MUST already be inside vector DB
- Do NOT mix sources

---

## 17. PERFORMANCE RULES

- Limit retrieval to top 5 results
- Avoid unnecessary repeated queries
- Do NOT re-embed same text multiple times

---

## 18. API CONTRACT RULES

- FastAPI MUST expose endpoint: POST /support
- Input MUST match webhook contract
- Output MUST match:

{
"reply": "<email>"
}

- DO NOT return JSON structures beyond this
- DO NOT return raw model output
- DO NOT return debug data

---
