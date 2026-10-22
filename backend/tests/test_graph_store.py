import pytest
from app.core.graph_store import Neo4jGraphStore

@pytest.fixture(scope="module")
def graph_store():
    store = Neo4jGraphStore()
    if not store.verify_connectivity():
        pytest.skip("Neo4j is not reachable on localhost:7687")
    store.create_schema_and_indexes()
    yield store
    # Clean up test nodes
    with store.driver.session() as session:
        session.run("MATCH (n) WHERE n.id STARTS WITH 'TEST-' DETACH DELETE n")
    store.close()

def test_neo4j_connectivity_and_schema(graph_store: Neo4jGraphStore):
    assert graph_store.verify_connectivity() is True
    counts = graph_store.get_counts()
    assert "vector_indexes" in counts
    assert counts["vector_indexes"] >= 1

def test_ingest_and_query_hybrid(graph_store: Neo4jGraphStore):
    # Ingest test tactic
    graph_store.ingest_tactics([{
        "id": "TEST-TA0001",
        "name": "Test Initial Access",
        "short_name": "initial-access",
        "description": "Test tactic description"
    }])

    # Ingest test technique with dummy embedding
    dummy_vec = [0.05] * 384
    graph_store.ingest_techniques([{
        "id": "TEST-T1001",
        "name": "Test Technique",
        "description": "Adversary performs test technique action",
        "tactics": ["initial-access"],
        "is_subtechnique": False,
        "embedding": dummy_vec
    }])

    # Ingest test subtechnique
    graph_store.ingest_subtechniques([{
        "id": "TEST-T1001.001",
        "name": "Test Subtechnique",
        "description": "Detailed subtechnique action",
        "tactics": ["initial-access"],
        "is_subtechnique": True,
        "embedding": dummy_vec
    }])

    # Ingest test countermeasure
    graph_store.ingest_countermeasures([{
        "id": "TEST-D3-TEST",
        "name": "Test Defense",
        "description": "Defensive countermeasure for test",
        "tactic": "Detect"
    }])

    # Ingest relationships
    graph_store.ingest_subtechnique_relationships([{
        "type": "SUBTECHNIQUE_OF",
        "source_id": "TEST-T1001.001",
        "target_id": "TEST-T1001"
    }])

    graph_store.ingest_countermeasure_mappings([{
        "technique_id": "TEST-T1001",
        "countermeasure_id": "TEST-D3-TEST",
        "relationship_type": "DETECTS"
    }])

    # Query vector index with countermeasure traversal
    results = graph_store.query_vector_with_countermeasures(dummy_vec, top_k=5)
    assert len(results) > 0

    test_matches = [r for r in results if r["technique_id"] == "TEST-T1001"]
    assert len(test_matches) == 1
    match = test_matches[0]
    assert match["technique_name"] == "Test Technique"
    assert match["score"] > 0.9

    # Verify linked countermeasures traversal
    cms = match["countermeasures"]
    assert len(cms) == 1
    assert cms[0]["id"] == "TEST-D3-TEST"
    assert cms[0]["name"] == "Test Defense"
