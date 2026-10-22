"""Automated First-Load Downloader and Indexer."""
import logging
from typing import Any, Dict, List, Optional
from sentence_transformers import SentenceTransformer
from app.core.config import settings
from app.core.graph_store import Neo4jGraphStore
from app.ingestion.stix_loader import STIXLoader
from app.ingestion.d3fend_loader import D3FENDLoader

logger = logging.getLogger(__name__)

async def bootstrap_knowledge_base(
    stix_source: Optional[str] = None,
    d3fend_matrix_source: Optional[str] = None,
    d3fend_mappings_source: Optional[str] = None,
    embedding_model_name: Optional[str] = None,
    embed_batch_size: int = 64,
) -> Dict[str, Any]:
    """Automatically downloads latest official STIX 2.1 and D3FEND ontologies and indexes into Neo4j."""
    store = Neo4jGraphStore()
    if not store.verify_connectivity():
        raise ConnectionError(f"Could not connect to Neo4j at {store.uri}")

    try:
        # 1. Provision Constraints and Native Vector Index
        store.create_schema_and_indexes()

        # 2. Parse MITRE ATT&CK STIX 2.1
        stix_loader = STIXLoader(source=stix_source)
        tactics, techniques, subtechniques, relationships = stix_loader.parse_all()

        # 3. Parse MITRE D3FEND Matrix and Mappings
        d3fend_loader = D3FENDLoader(
            matrix_source=d3fend_matrix_source,
            mappings_source=d3fend_mappings_source
        )
        all_tech_ids = [t["id"] for t in techniques] + [t["id"] for t in subtechniques]
        countermeasures, mappings = d3fend_loader.parse_all(technique_ids=all_tech_ids)

        # 4. Generate Embeddings for Techniques and Subtechniques
        model_name = embedding_model_name or settings.EMBEDDING_MODEL_NAME
        embedder = SentenceTransformer(model_name)

        if techniques:
            tech_texts = [f"{t['name']}: {t.get('description', '')}" for t in techniques]
            tech_embeddings = embedder.encode(tech_texts, batch_size=embed_batch_size, show_progress_bar=False)
            for t, emb in zip(techniques, tech_embeddings):
                t["embedding"] = emb.tolist()

        if subtechniques:
            sub_texts = [f"{t['name']}: {t.get('description', '')}" for t in subtechniques]
            sub_embeddings = embedder.encode(sub_texts, batch_size=embed_batch_size, show_progress_bar=False)
            for t, emb in zip(subtechniques, sub_embeddings):
                t["embedding"] = emb.tolist()

        # 5. Ingest Graph Nodes and Edges into Neo4j
        store.ingest_tactics(tactics)
        store.ingest_techniques(techniques)
        store.ingest_subtechniques(subtechniques)
        store.ingest_countermeasures(countermeasures)
        store.ingest_subtechnique_relationships(relationships)
        store.ingest_countermeasure_mappings(mappings)

        # 6. Verification Vector Query
        verification_results: List[Dict[str, Any]] = []
        if techniques and "embedding" in techniques[0]:
            verification_results = store.query_vector_with_countermeasures(
                techniques[0]["embedding"],
                top_k=3
            )

        final_counts = store.get_counts()

        return {
            "status": "success",
            "tactics_count": len(tactics),
            "techniques_count": len(techniques),
            "subtechniques_count": len(subtechniques),
            "countermeasures_count": len(countermeasures),
            "subtechnique_relationships_count": len(relationships),
            "mappings_count": len(mappings),
            "database_counts": final_counts,
            "verification": verification_results
        }
    finally:
        store.close()
