"""Unified API Routes."""
from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from typing import Optional

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
async def get_system_status():
    """System health, Neo4j connectivity, and dataset indexing state."""
    return {
        "neo4j_connected": False,
        "attack_indexed": False,
        "d3fend_indexed": False,
        "active_llm": "pending_configuration"
    }
