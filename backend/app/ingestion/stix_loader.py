"""MITRE Enterprise ATT&CK STIX 2.1 Loader and Embedder."""
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import requests

DEFAULT_ENTERPRISE_ATTACK_URL = (
    "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
)
DEFAULT_CACHE_DIR = Path("data")

class STIXLoader:
    def __init__(self, source: Optional[str] = None):
        self.source = source or DEFAULT_ENTERPRISE_ATTACK_URL
        self._data: Optional[Dict[str, Any]] = None

    def fetch_or_load(self) -> Dict[str, Any]:
        """Loads STIX data from local file, cache, or fetches from URL."""
        if self._data is not None:
            return self._data

        # If source is an existing local file
        if os.path.exists(self.source):
            with open(self.source, "r", encoding="utf-8") as f:
                self._data = json.load(f)
            return self._data

        # Check local cache dir
        DEFAULT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cached_file = DEFAULT_CACHE_DIR / "enterprise-attack.json"
        if cached_file.exists():
            with open(cached_file, "r", encoding="utf-8") as f:
                self._data = json.load(f)
            return self._data

        # Download from URL
        resp = requests.get(self.source, timeout=60)
        resp.raise_for_status()
        self._data = resp.json()

        # Cache locally
        try:
            with open(cached_file, "w", encoding="utf-8") as f:
                json.dump(self._data, f)
        except Exception:
            pass

        return self._data

    def _extract_mitre_id(self, obj: Dict[str, Any]) -> Optional[str]:
        for ref in obj.get("external_references", []):
            if ref.get("source_name") in ("mitre-attack", "mitre-enterprise-attack"):
                return ref.get("external_id")
        return None

    def parse_all(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Extracts tactics, techniques, subtechniques, and subtechnique-of relationships."""
        data = self.fetch_or_load()
        objects = data.get("objects", [])

        tactics: List[Dict[str, Any]] = []
        techniques: List[Dict[str, Any]] = []
        subtechniques: List[Dict[str, Any]] = []
        relationships: List[Dict[str, Any]] = []

        stix_id_to_mitre_id: Dict[str, str] = {}

        # 1. Tactics
        for obj in objects:
            if obj.get("type") == "x-mitre-tactic":
                tactic_id = self._extract_mitre_id(obj)
                if tactic_id:
                    tactics.append({
                        "id": tactic_id,
                        "name": obj.get("name", ""),
                        "description": obj.get("description", ""),
                        "short_name": obj.get("x_mitre_shortname", "")
                    })
                    stix_id_to_mitre_id[obj.get("id")] = tactic_id

        # 2. Techniques & Subtechniques
        for obj in objects:
            if obj.get("type") == "attack-pattern" and not obj.get("revoked", False):
                mitre_id = self._extract_mitre_id(obj)
                if not mitre_id:
                    continue

                is_sub = bool(obj.get("x_mitre_is_subtechnique", False))
                tactic_phases = [
                    phase.get("phase_name")
                    for phase in obj.get("kill_chain_phases", [])
                    if phase.get("kill_chain_name") == "mitre-attack"
                ]

                tech_record = {
                    "id": mitre_id,
                    "name": obj.get("name", ""),
                    "description": obj.get("description", ""),
                    "tactics": tactic_phases,
                    "is_subtechnique": is_sub,
                    "stix_id": obj.get("id")
                }

                stix_id_to_mitre_id[obj.get("id")] = mitre_id

                if is_sub:
                    subtechniques.append(tech_record)
                else:
                    techniques.append(tech_record)

        # 3. Relationships
        for obj in objects:
            if obj.get("type") == "relationship":
                rel_type = obj.get("relationship_type")
                source_stix = obj.get("source_ref")
                target_stix = obj.get("target_ref")

                if rel_type == "subtechnique-of":
                    source_mitre = stix_id_to_mitre_id.get(source_stix)
                    target_mitre = stix_id_to_mitre_id.get(target_stix)
                    if source_mitre and target_mitre:
                        relationships.append({
                            "type": "SUBTECHNIQUE_OF",
                            "source_id": source_mitre,
                            "target_id": target_mitre
                        })

        return tactics, techniques, subtechniques, relationships
