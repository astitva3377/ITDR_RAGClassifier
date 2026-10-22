"""Unified API Routes."""
from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from typing import Optional, Dict, Any
from app.core.config import settings
from app.core.graph_store import Neo4jGraphStore
from app.ingestion.bootstrap import bootstrap_knowledge_base

router = APIRouter()

@router.post("/analyze")
async def analyze_threat_bulletin(
    text: Optional[str] = Form(None),
    url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    confidence_threshold: float = Form(0.6),
    top_k: int = Form(5),
):
    """Unified endpoint accepting raw text, advisory URL, or PDF/TXT/MD file upload."""
    if not text and not url and not file:
        raise HTTPException(
            status_code=400,
            detail="At least one input modality must be provided: 'text', 'url', or 'file'."
        )
    return {
        "status": "received",
        "message": "Scaffold endpoint ready for LangGraph pipeline integration",
        "params": {
            "has_text": bool(text),
            "has_url": bool(url),
            "has_file": file.filename if file else None,
            "confidence_threshold": confidence_threshold,
            "top_k": top_k,
        }
    }

@router.get("/status")
async def get_system_status() -> Dict[str, Any]:
    """System health, Neo4j connectivity, dataset indexing state, and vector verification."""
    store = Neo4jGraphStore()
    if not store.verify_connectivity():
        return {
            "neo4j_connected": False,
            "attack_indexed": False,
            "d3fend_indexed": False,
            "vector_index_active": False,
            "counts": {},
            "test_query": []
        }
    try:
        counts = store.get_counts()
        attack_indexed = counts.get("techniques", 0) > 0 or counts.get("subtechniques", 0) > 0
        d3fend_indexed = counts.get("countermeasures", 0) > 0
        vector_index_active = counts.get("vector_indexes", 0) > 0

        test_query_results = []
        if vector_index_active and attack_indexed:
            dummy_vec = [0.1] * settings.EMBEDDING_DIMENSION
            test_query_results = store.query_vector_with_countermeasures(dummy_vec, top_k=2)

        return {
            "neo4j_connected": True,
            "attack_indexed": attack_indexed,
            "d3fend_indexed": d3fend_indexed,
            "vector_index_active": vector_index_active,
            "counts": counts,
            "test_query": test_query_results
        }
    finally:
        store.close()

@router.post("/bootstrap")
async def trigger_bootstrap():
    """Trigger automated download, embedding, and indexing of MITRE ATT&CK and D3FEND."""
    result = await bootstrap_knowledge_base()
    return result
