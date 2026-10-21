# Threat Bulletin to MITRE ATT&CK & D3FEND GraphRAG

An enterprise-grade Cyber Threat Intelligence (CTI) GraphRAG system that ingests threat bulletins (raw text, URLs, or PDF/TXT/MD uploads) and maps adversary behaviors to **MITRE ATT&CK Enterprise TTPs** and **MITRE D3FEND Defensive Countermeasures** with evidence snippets, confidence scores, and remediation rationale.

---

## 🛠️ Technology Stack
- **RAG & Agent Orchestration**: LangGraph & LangChain (`StateGraph` multi-node workflow)
- **Knowledge Graph & Vectors**: Neo4j 5+ (Cypher property graph + native vector indexing)
- **Backend**: FastAPI (Python 3.10), Pydantic v2, Server-Sent Events (SSE)
- **Frontend**: React, Vite, Tailwind CSS, Lucide Icons
- **Evaluation**: `tumeteor/mitre-ttp-mapping` multi-label benchmark harness + Ragas

---

## 🚀 Quickstart

### 1. Start Neo4j Database
```bash
docker-compose up -d
```
Neo4j Browser will be available at `http://localhost:7474` (User: `neo4j`, Password: `password`).

### 2. Backend Setup
```bash
cd backend
py -3.10 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 📂 Project Structure
```
ITDR_RAGClassifier/
├── backend/           # FastAPI application & LangGraph pipeline
├── frontend/          # React + Vite + Tailwind dashboard
├── eval/              # tumeteor benchmark & Ragas evaluation suite
├── cli/               # Command-line interface
├── data/              # Local cache for STIX & D3FEND ontologies
└── docker-compose.yml # Pre-configured Neo4j 5 container
```
