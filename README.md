# Clinical Evidence Multi-Agent AI

## 1. Project Overview

Clinical Evidence Multi-Agent AI is an AI-powered clinical research assistance platform designed to retrieve, evaluate, organize and summarize medical research evidence using a Retrieval-Augmented Generation (RAG) pipeline and multiple specialized AI agents.

The platform integrates FastAPI, LangGraph, Gemini, HuggingFace embeddings, ChromaDB, BM25, React and PostgreSQL.

**Important:** This system supports clinical evidence research. It is not a diagnostic or autonomous treatment system and does not replace qualified professional judgment.

## 2. Key Features

- Multi-agent clinical evidence processing
- Clinical question understanding and PICO extraction
- Patient context processing and basic de-identification
- PDF research document ingestion
- Hybrid Dense and Sparse retrieval
- ChromaDB vector search
- BM25 keyword retrieval
- Cross-encoder reranking
- Evidence quality screening
- Safety policy validation
- Evidence-grounded report generation
- Citation validation
- Human-in-the-loop approval workflow
- JWT authentication
- Clinical case management
- Evaluation framework
- React dashboard
- Docker deployment configuration

## 3. Seven AI Agents

1. Intake Scope Agent
2. Patient Context Agent
3. Evidence Retrieval Agent
4. Evidence Quality Agent
5. Safety Policy Agent
6. Summary Generation Agent
7. Output Validation Agent

## 4. Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Backend | FastAPI |
| Agent Framework | LangGraph |
| LLM | Google Gemini |
| RAG Framework | LangChain |
| Embeddings | HuggingFace Sentence Transformers |
| Vector Database | ChromaDB |
| Sparse Retrieval | BM25 |
| Reranking | Cross-Encoder |
| Relational Database | PostgreSQL / SQLite |
| Frontend | React + TypeScript |
| Build Tool | Vite |
| Validation | Pydantic |
| Deployment | Docker Compose |

## 5. Project Architecture

User submits a clinical research question.

The Intake Scope Agent structures the question. The Patient Context Agent processes relevant context. The Evidence Retrieval Agent retrieves relevant passages using hybrid RAG.

The Evidence Quality Agent assesses study characteristics and limitations. The Safety Policy Agent checks for unsafe requests and missing evidence.

The Summary Generation Agent prepares an evidence-grounded research summary. The Output Validation Agent checks the report structure and citations.

Finally, the report enters a human review workflow. Only an authorized reviewer can approve a valid report.

## 6. RAG Pipeline

1. Document ingestion
2. PDF text extraction
3. Text cleaning
4. Chunking
5. Embedding generation
6. Dense retrieval
7. Sparse retrieval
8. Hybrid retrieval using Reciprocal Rank Fusion
9. Cross-encoder reranking
10. Evidence context construction
11. Citation-aware generation

## 7. Project Structure

The backend contains agents, APIs, core configuration, database, graph orchestration, guardrails, models, RAG, services and utilities.

The frontend contains React pages, components, hooks, authentication context and API services.

The evaluation directory contains retrieval, groundedness, citation, answer quality and safety evaluation modules.

## 8. Installation

Create a Python virtual environment:

```bash
python -m venv .venv
```

Activate on Windows:

```powershell
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure environment variables using `.env.example` as a reference.

Add a valid Gemini API key to `.env`.

## 9. Run Backend

```bash
uvicorn backend.main:app --reload
```

Backend:

http://127.0.0.1:8000

API documentation:

http://127.0.0.1:8000/docs

## 10. Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend:

http://127.0.0.1:5173

## 11. Run with Docker

From the project root:

```bash
docker compose -f docker/docker-compose.yml up --build
```

Frontend:

http://localhost:8080

Backend:

http://localhost:8000

## 12. Evaluation

The evaluation framework provides implementations for:

- Precision@K
- Recall@K
- Mean Reciprocal Rank
- Groundedness heuristic
- Citation accuracy and coverage
- Answer structure quality
- Safety checks

Synthetic evaluation examples are included. Actual model evaluation requires running the workflow against the evaluation dataset and recording its outputs.

## 13. Security and Privacy

- Password hashing
- JWT authentication
- Role-based review authorization
- Basic pattern-based de-identification
- Prompt injection screening
- File extension and upload size validation
- Audit logging infrastructure

This prototype has not been independently security-certified or clinically validated. Do not upload identifiable patient records or use it for real clinical decisions.

## 14. Future Enhancements

- Persistent LangGraph checkpoints
- OCR for scanned research documents
- Advanced clinical de-identification
- Validated evidence grading
- Semantic groundedness evaluation
- Full audit and access control
- Production monitoring
- Clinical expert evaluation

## 15. Conclusion

Clinical Evidence Multi-Agent AI demonstrates how multi-agent orchestration and Retrieval-Augmented Generation can support structured clinical research workflows through evidence retrieval, quality screening, safety checks, citation validation and human review.