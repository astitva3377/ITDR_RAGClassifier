import pytest
import json
from fastapi.testclient import TestClient
from app.main import app
from app.core.graph_store import Neo4jGraphStore
from cli.main import check_status

@pytest.fixture(scope="module")
def ensure_sample_data_in_db():
    store = Neo4jGraphStore()
    if not store.verify_connectivity():
        pytest.skip("Neo4j not reachable")
    store.create_schema_and_indexes()
    dummy_vec = [0.1] * 384
    store.ingest_techniques([{
        "id": "T1059",
        "name": "Command and Scripting Interpreter",
        "description": "Adversaries may abuse command and script interpreters to execute commands.",
        "tactics": ["execution"],
        "is_subtechnique": False,
        "embedding": dummy_vec
    }])
    store.ingest_countermeasures([{
        "id": "D3-FA",
        "name": "File Analysis",
        "description": "Analyzing file properties.",
        "tactic": "Detect"
    }])
    store.ingest_countermeasure_mappings([{
        "technique_id": "T1059",
        "countermeasure_id": "D3-FA",
        "relationship_type": "DETECTS"
    }])
    store.close()

def test_api_status_endpoint(ensure_sample_data_in_db):
    client = TestClient(app)
    # Test /api/status
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["neo4j_connected"] is True
    assert "counts" in data
    assert data["counts"]["techniques"] >= 1
    assert data["counts"]["countermeasures"] >= 1
    assert data["attack_indexed"] is True
    assert data["d3fend_indexed"] is True
    assert data["vector_index_active"] is True
    assert "test_query" in data
    assert len(data["test_query"]) >= 1
    assert data["test_query"][0]["technique_id"] == "T1059"
    assert len(data["test_query"][0]["countermeasures"]) >= 1

def test_cli_status_check(ensure_sample_data_in_db):
    status_data = check_status()
    assert status_data["neo4j_connected"] is True
    assert status_data["attack_indexed"] is True
    assert status_data["d3fend_indexed"] is True
    assert len(status_data["test_query"]) >= 1
    assert status_data["test_query"][0]["technique_id"] == "T1059"
