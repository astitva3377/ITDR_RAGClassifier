import pytest
import json
from pathlib import Path
from app.ingestion.bootstrap import bootstrap_knowledge_base
from app.core.graph_store import Neo4jGraphStore

@pytest.fixture
def mock_bootstrap_sources(tmp_path: Path):
    bundle = {
        "type": "bundle",
        "id": "bundle--bootstrap-test",
        "objects": [
            {
                "type": "x-mitre-tactic",
                "id": "x-mitre-tactic--ta0002",
                "name": "Execution",
                "description": "Execution tactic",
                "x_mitre_shortname": "execution",
                "external_references": [
                    {"source_name": "mitre-attack", "external_id": "TA0002"}
                ]
            },
            {
                "type": "attack-pattern",
                "id": "attack-pattern--t1059",
                "name": "Command and Scripting Interpreter",
                "description": "Adversaries abuse command and scripting interpreters to run commands.",
                "kill_chain_phases": [
                    {"kill_chain_name": "mitre-attack", "phase_name": "execution"}
                ],
                "x_mitre_is_subtechnique": False,
                "external_references": [
                    {"source_name": "mitre-attack", "external_id": "T1059"}
                ]
            },
            {
                "type": "attack-pattern",
                "id": "attack-pattern--t1059-001",
                "name": "PowerShell",
                "description": "Adversaries abuse PowerShell.",
                "kill_chain_phases": [
                    {"kill_chain_name": "mitre-attack", "phase_name": "execution"}
                ],
                "x_mitre_is_subtechnique": True,
                "external_references": [
                    {"source_name": "mitre-attack", "external_id": "T1059.001"}
                ]
            },
            {
                "type": "relationship",
                "id": "relationship--sub-1",
                "relationship_type": "subtechnique-of",
                "source_ref": "attack-pattern--t1059-001",
                "target_ref": "attack-pattern--t1059"
            }
        ]
    }
    stix_file = tmp_path / "stix.json"
    stix_file.write_text(json.dumps(bundle), encoding="utf-8")

    matrix_data = [
        {
            "@id": "d3f:Detect",
            "rdfs:label": "Detect",
            "children": [
                {
                    "@id": "d3f:FileAnalysis",
                    "d3f:d3fend-id": "D3-FA",
                    "rdfs:label": "File Analysis",
                    "d3f:definition": "Analyzing file properties.",
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
        }
    ]
    mappings_file = tmp_path / "mappings.json"
    mappings_file.write_text(json.dumps(mappings_data), encoding="utf-8")

    return str(stix_file), str(matrix_file), str(mappings_file)

@pytest.mark.asyncio
async def test_bootstrap_knowledge_base_populates_neo4j(mock_bootstrap_sources):
    stix_file, matrix_file, mappings_file = mock_bootstrap_sources
    store = Neo4jGraphStore()
    if not store.verify_connectivity():
        pytest.skip("Neo4j not reachable")
    store.close()

    result = await bootstrap_knowledge_base(
        stix_source=stix_file,
        d3fend_matrix_source=matrix_file,
        d3fend_mappings_source=mappings_file,
        embed_batch_size=10
    )

    assert result["status"] == "success"
    assert result["tactics_count"] >= 1
    assert result["techniques_count"] >= 1
    assert result["subtechniques_count"] >= 1
    assert result["countermeasures_count"] >= 1
    assert result["subtechnique_relationships_count"] >= 1
    assert result["mappings_count"] >= 1
    assert len(result["verification"]) > 0
    assert result["verification"][0]["technique_id"] == "T1059"
