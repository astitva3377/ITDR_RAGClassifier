"""Command-Line Interface for Threat Bulletin Analysis."""
import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.core.graph_store import Neo4jGraphStore
from app.ingestion.bootstrap import bootstrap_knowledge_base

def check_status() -> Dict[str, Any]:
    """Verifies Neo4j connectivity, dataset indexing state, and runs a test vector query."""
    store = Neo4jGraphStore()
    connected = store.verify_connectivity()
    if not connected:
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

def main():
    parser = argparse.ArgumentParser(description="Threat Bulletin to MITRE ATT&CK & D3FEND CLI")
    parser.add_argument("--status", action="store_true", help="Check system health, Neo4j connectivity, and dataset indexing state")
    parser.add_argument("--bootstrap", action="store_true", help="Ingest official MITRE ATT&CK and D3FEND ontologies into Neo4j")
    parser.add_argument("--file", help="Path to PDF/TXT/MD bulletin file")
    parser.add_argument("--url", help="Advisory URL")
    parser.add_argument("--text", help="Raw text string")
    parser.add_argument("--output", help="Output path for JSON report", default=None)
    args = parser.parse_args()

    if args.status:
        status = check_status()
        formatted = json.dumps(status, indent=2)
        print(formatted)
        if args.output:
            Path(args.output).write_text(formatted, encoding="utf-8")
        return

    if args.bootstrap:
        print("Starting knowledge base bootstrap...")
        summary = asyncio.run(bootstrap_knowledge_base())
        formatted = json.dumps(summary, indent=2)
        print(formatted)
        if args.output:
            Path(args.output).write_text(formatted, encoding="utf-8")
        return

    print("Threat Intel GraphRAG CLI Initialized.")

if __name__ == "__main__":
    main()
