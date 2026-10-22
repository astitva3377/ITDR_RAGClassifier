import pytest
import json
from pathlib import Path
from app.ingestion.d3fend_loader import D3FENDLoader

@pytest.fixture
def sample_d3fend_matrix(tmp_path: Path):
    matrix_data = [
        {
            "@id": "d3f:Detect",
            "rdfs:label": "Detect",
            "children": [
                {
                    "@id": "d3f:FileAnalysis",
                    "d3f:d3fend-id": "D3-FA",
                    "rdfs:label": "File Analysis",
                    "d3f:definition": "Analyzing file properties and contents to detect malicious activity.",
                    "children": []
                }
            ]
        },
        {
            "@id": "d3f:Harden",
            "rdfs:label": "Harden",
            "children": [
                {
                    "@id": "d3f:AccountLocking",
                    "d3f:d3fend-id": "D3-AL",
                    "rdfs:label": "Account Locking",
                    "d3f:definition": "Locking user accounts after failed login attempts.",
                    "children": []
                }
            ]
        }
    ]
    matrix_file = tmp_path / "matrix.json"
    matrix_file.write_text(json.dumps(matrix_data), encoding="utf-8")

    mappings_data = [
        {
            "technique_id": "T1059",
            "countermeasure_id": "D3-FA",
            "relationship_type": "DETECTS"
        },
        {
            "technique_id": "T1078",
            "countermeasure_id": "D3-AL",
            "relationship_type": "COUNTERS"
        }
    ]
    mappings_file = tmp_path / "mappings.json"
    mappings_file.write_text(json.dumps(mappings_data), encoding="utf-8")

    return str(matrix_file), str(mappings_file)

def test_d3fend_loader_parses_countermeasures_and_mappings(sample_d3fend_matrix):
    matrix_file, mappings_file = sample_d3fend_matrix
    loader = D3FENDLoader(matrix_source=matrix_file, mappings_source=mappings_file)
    countermeasures, mappings = loader.parse_all()

    # Verify countermeasures
    assert len(countermeasures) == 2
    cm_map = {c["id"]: c for c in countermeasures}
    assert "D3-FA" in cm_map
    assert cm_map["D3-FA"]["name"] == "File Analysis"
    assert cm_map["D3-FA"]["tactic"] == "Detect"
    assert "D3-AL" in cm_map
    assert cm_map["D3-AL"]["tactic"] == "Harden"

    # Verify mappings
    assert len(mappings) == 2
    rel_map = {(m["technique_id"], m["countermeasure_id"]): m["relationship_type"] for m in mappings}
    assert rel_map[("T1059", "D3-FA")] == "DETECTS"
    assert rel_map[("T1078", "D3-AL")] == "COUNTERS"
