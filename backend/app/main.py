"""FastAPI Application Entry Point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router, get_system_status

app = FastAPI(
    title="Threat Bulletin to MITRE ATT&CK & D3FEND GraphRAG",
    description="Unified CTI extraction and GraphRAG mapper using LangGraph and Neo4j",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "ITDR_RAGClassifier"}

@app.get("/status")
async def root_status():
    """Status endpoint alias at root path."""
    return await get_system_status()
