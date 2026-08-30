# HealthAgent AI

HealthAgent AI is an evidence-first healthcare assistant for asking questions about symptoms, treatments, medicines, health guidelines, and uploaded medical documents.

It uses document-grounded Agentic RAG: the system retrieves relevant passages from your knowledge base, runs specialist checks, generates an answer, verifies the evidence, and applies a medical-safety guardrail before returning the response.

> **Medical disclaimer:** HealthAgent AI is an educational and document-retrieval tool. It is not a doctor, does not diagnose conditions, and must not replace professional medical advice. Always confirm medicines, doses, and treatment decisions with a qualified clinician.


## What it includes

- Evidence-grounded healthcare Q&A with page-level sources
- PDF and Markdown upload from the Knowledge Base screen
- Automatic parsing, chunking, embedding, and Chroma indexing
- Hybrid retrieval: dense embeddings + BM25 + reciprocal-rank fusion + reranking
- LangGraph workflow with input guardrails, query classification, rewriting, planning, retrieval, specialist review, evidence verification, and output safety checks
- Specialist review layers for clinical information, medication safety, and web evidence
- Optional Tavily web search for current external evidence
- English, Hindi, Hinglish, and Tamil response modes
- Agent activity trace showing what happened during each answer
- Evaluation screen for retrieval metrics
- Optional Langfuse observability

## Architecture

```text
User question
    ↓
Input safety → classify → rewrite → plan
    ↓
Hybrid document retrieval ── optional web search / graph / data tools
    ↓
Clinical review → medication-safety review → web-evidence review
    ↓
Answer generation → evidence verification → medical output guardrail
    ↓
Answer + citations + activity trace
```

Detailed design notes are in [`learning/docs/`](learning/docs/) and the project reference is [`learning/skills.md`](learning/skills.md).

## Requirements

- Python 3.11 or newer
- Node.js 20 or newer
- npm
- An OpenRouter API key for answer generation
- Optional: Tavily, Langfuse, Neo4j, and PostgreSQL credentials for their respective features

Docker is not required. ChromaDB runs locally by default. Neo4j and PostgreSQL are optional integrations and must be provided as external services if those features are enabled.

## API keys and environment setup

Copy the safe environment template:

```bash
cp .env.example .env
```

Never commit `.env` or paste real secrets into GitHub. Use `.env.example` as the template.

### Required

| Variable | Purpose | Get it from |
| --- | --- | --- |
| `OPENROUTER_API_KEY` | LLM generation, classification, rewriting, specialist checks, and evidence verification | [OpenRouter API keys](https://openrouter.ai/settings/keys) |

The default model is `inclusionai/ling-3.0-flash-fin:free`. OpenRouter free models have daily rate limits. For more usage, wait for the reset, add credits, or select another model in `LLM_MODEL`.

### Optional

| Variable | Purpose | Get it from |
| --- | --- | --- |
| `TAVILY_API_KEY` | Current web-search evidence | [Tavily](https://app.tavily.com/) |
| `LANGFUSE_PUBLIC_KEY` | Trace and usage observability | [Langfuse](https://cloud.langfuse.com/) |
| `LANGFUSE_SECRET_KEY` | Langfuse server-side authentication | [Langfuse](https://cloud.langfuse.com/) |
| `API_KEY` | Protect backend endpoints with an `X-API-Key` header | Generate your own local secret |
| `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` | Knowledge-graph features | Your Neo4j deployment |
| `POSTGRES_URL` | Structured-data/SQL features | Your PostgreSQL deployment |

For local document Q&A, Tavily, Langfuse, `API_KEY`, Neo4j, and PostgreSQL can remain empty.

## Run locally

### 1. Backend

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --app-dir backend
```

The API runs at `http://localhost:8000`.

```bash
curl http://localhost:8000/api/health
```

Expected response:

```json
{"status":"ok"}
```

### 2. Frontend

In a second terminal:

```bash
cd frontend/next-app
cp .env.local.example .env.local
npm install
npm run dev
```

Open `http://localhost:3000`. If the backend `API_KEY` is set, put the same value in `NEXT_PUBLIC_API_KEY` inside `frontend/next-app/.env.local`.

## Upload PDFs and Markdown

1. Open **Knowledge Base** in the sidebar.
2. Click **Upload document** or **Choose file**.
3. Select a `.pdf`, `.md`, or `.markdown` file up to 25 MB.
4. Wait for the indexing confirmation.
5. Ask a question in **Ask HealthAgent**.

The backend saves uploads in `knowledge_base/uploads`, extracts text, creates chunks and embeddings, and updates the local Chroma index. Answer sources include the document name and page number when available.

The same flow is available through the API:

```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@/path/to/medical-guideline.pdf"
```

If `API_KEY` is configured, add `-H "X-API-Key: your_local_api_key"` to the command.

## Example questions

- I have a mild headache. What should I do first?
- What are the warning signs that need urgent medical care?
- What medicines are mentioned for this condition?
- What precautions are listed for this treatment?
- What does the uploaded guideline say about dehydration?
- Explain this medical document in simple Hinglish.
- Summarize the treatment options and cite the relevant pages.

## Useful API endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Basic health check |
| `GET` | `/api/health/ready` | Readiness and dependency check |
| `POST` | `/api/chat` | Ask a grounded healthcare question |
| `GET` | `/api/documents` | List indexed documents |
| `POST` | `/api/documents/upload` | Upload and index a PDF/Markdown file |
| `POST` | `/api/evaluation/run` | Run the retrieval smoke evaluation |
| `GET` | `/api/metrics` | View request and LLM metrics |

Interactive API documentation is available at `http://localhost:8000/docs`.

## Project structure

```text
backend/                 FastAPI API, LangGraph agents, retrieval, tools, guardrails
frontend/next-app/       Next.js healthcare dashboard
knowledge_base/uploads/  Uploaded PDFs and Markdown documents
data/chroma/             Local Chroma persistence (ignored by Git)
evaluation/              Retrieval datasets and reports
learning/                Architecture notes and project reference material
scripts/                 Ingestion, graph extraction, and evaluation utilities
```

## Verification

```bash
# Frontend
cd frontend/next-app && npm run lint

# Backend, from the project root
pytest backend/tests
```

## Security and privacy

- Keep all API keys in environment variables.
- Do not commit `.env`, `.env.local`, Chroma databases, caches, or `node_modules`.
- Do not upload identifiable patient records to a shared or public repository.
- Treat generated answers as guidance for document navigation, not prescriptions.
- Review citations and consult a clinician before acting on medical information.
