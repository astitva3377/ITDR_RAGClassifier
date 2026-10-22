import pytest
import json
from pathlib import Path
from app.ingestion.stix_loader import STIXLoader

@pytest.fixture
def sample_stix_bundle(tmp_path: Path):
    bundle = {
        "type": "bundle",
        "id": "bundle--test-id",
        "objects": [
            {
                "type": "x-mitre-tactic",
                "id": "x-mitre-tactic--ta0002",
                "name": "Execution",
                "description": "The adversary is trying to run malicious code.",
                "x_mitre_shortname": "execution",
                "external_references": [
                    {"source_name": "mitre-attack", "external_id": "TA0002"}
                ]
            },
            {
                "type": "attack-pattern",
                "id": "attack-pattern--t1059",
                "name": "Command and Scripting Interpreter",
                "description": "Adversaries may abuse command and script interpreters.",
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
                "description": "Adversaries may abuse PowerShell commands and scripts.",
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
            },
            {
                "type": "attack-pattern",
                "id": "attack-pattern--revoked",
                "name": "Old Revoked Technique",
                "description": "Revoked",
                "revoked": True,
                "external_references": [
                    {"source_name": "mitre-attack", "external_id": "T9999"}
                ]
            }
        ]
    }
    file_path = tmp_path / "sample_stix.json"
    file_path.write_text(json.dumps(bundle), encoding="utf-8")
    return str(file_path)

def test_stix_loader_parses_tactics_techniques_and_relationships(sample_stix_bundle: str):
    loader = STIXLoader(sample_stix_bundle)
    tactics, techniques, subtechniques, relationships = loader.parse_all()

    # Verify tactics
    assert len(tactics) == 1
    tactic = tactics[0]
    assert tactic["id"] == "TA0002"
    assert tactic["name"] == "Execution"
    assert tactic["short_name"] == "execution"

    # Verify techniques
    assert len(techniques) == 1
    tech = techniques[0]
    assert tech["id"] == "T1059"
    assert tech["name"] == "Command and Scripting Interpreter"
    assert tech["is_subtechnique"] is False
    assert "execution" in tech["tactics"]

    # Verify subtechniques
    assert len(subtechniques) == 1
    sub = subtechniques[0]
    assert sub["id"] == "T1059.001"
    assert sub["name"] == "PowerShell"
    assert sub["is_subtechnique"] is True

    # Verify relationships
    assert len(relationships) == 1
    rel = relationships[0]
    assert rel["type"] == "SUBTECHNIQUE_OF"
    assert rel["source_id"] == "T1059.001"
    assert rel["target_id"] == "T1059"
