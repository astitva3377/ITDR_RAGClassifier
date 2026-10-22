"""MITRE D3FEND Ontology Loader & ATT&CK Relationship Linker."""
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

DEFAULT_D3FEND_MATRIX_URL = "https://d3fend.mitre.org/api/matrix.json"
DEFAULT_CACHE_DIR = Path("data")

class D3FENDLoader:
    def __init__(
        self,
        matrix_source: Optional[str] = None,
        mappings_source: Optional[str] = None,
    ):
        self.matrix_source = matrix_source or DEFAULT_D3FEND_MATRIX_URL
        self.mappings_source = mappings_source
        self._matrix_data: Optional[Any] = None
        self._mappings_data: Optional[List[Dict[str, Any]]] = None

    def fetch_or_load_matrix(self) -> Any:
        """Loads D3FEND matrix from local file, cache, or fetches from URL."""
        if self._matrix_data is not None:
            return self._matrix_data

        if self.matrix_source and os.path.exists(self.matrix_source):
            with open(self.matrix_source, "r", encoding="utf-8") as f:
                self._matrix_data = json.load(f)
            return self._matrix_data

        DEFAULT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cached_file = DEFAULT_CACHE_DIR / "d3fend_matrix.json"
        if cached_file.exists():
            with open(cached_file, "r", encoding="utf-8") as f:
                self._matrix_data = json.load(f)
            return self._matrix_data

        resp = requests.get(self.matrix_source, timeout=60)
        resp.raise_for_status()
        self._matrix_data = resp.json()

        try:
            with open(cached_file, "w", encoding="utf-8") as f:
                json.dump(self._matrix_data, f)
        except Exception:
            pass

        return self._matrix_data

    def fetch_or_load_mappings(self, technique_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Loads technique-to-countermeasure mappings from file or API."""
        if self._mappings_data is not None:
            return self._mappings_data

        if self.mappings_source and os.path.exists(self.mappings_source):
            with open(self.mappings_source, "r", encoding="utf-8") as f:
                self._mappings_data = json.load(f)
            return self._mappings_data

        DEFAULT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cached_mappings = DEFAULT_CACHE_DIR / "d3fend_attack_mappings.json"
        if cached_mappings.exists():
            with open(cached_mappings, "r", encoding="utf-8") as f:
                self._mappings_data = json.load(f)
            return self._mappings_data

        mappings: List[Dict[str, Any]] = []
        if technique_ids:
            seen: Set[Tuple[str, str]] = set()

            def fetch_single(tid: str) -> List[Dict[str, Any]]:
                single_mappings: List[Dict[str, Any]] = []
                url = f"https://d3fend.mitre.org/api/offensive-technique/attack/{tid}.json"
                try:
                    resp = requests.get(url, timeout=10)
                    if resp.status_code == 200:
                        data = resp.json()
                        bindings = data.get("off_to_def", {}).get("results", {}).get("bindings", [])
                        for b in bindings:
                            cm_id = b.get("def_tech_id", {}).get("value")
                            if not cm_id:
                                continue
                            tactic_label = b.get("def_tactic_label", {}).get("value", "")
                            rel_type = "DETECTS" if tactic_label == "Detect" else "COUNTERS"
                            single_mappings.append({
                                "technique_id": tid,
                                "countermeasure_id": cm_id,
                                "relationship_type": rel_type
                            })
                except Exception:
                    pass
                return single_mappings

            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = {executor.submit(fetch_single, tid): tid for tid in technique_ids}
                for future in as_completed(futures):
                    for m in future.result():
                        key = (m["technique_id"], m["countermeasure_id"])
                        if key not in seen:
                            seen.add(key)
                            mappings.append(m)

        self._mappings_data = mappings
        if mappings:
            try:
                with open(cached_mappings, "w", encoding="utf-8") as f:
                    json.dump(mappings, f, indent=2)
            except Exception:
                pass

        return self._mappings_data

    def parse_countermeasures(self) -> List[Dict[str, Any]]:
        """Extracts D3FEND countermeasures with id, name, description, and tactic."""
        data = self.fetch_or_load_matrix()
        countermeasures: Dict[str, Dict[str, Any]] = {}

        # Handle list format (matrix.json)
        if isinstance(data, list):
            def _walk(node: Dict[str, Any], current_tactic: str):
                tactic = current_tactic
                if "rdfs:label" in node and not node.get("d3f:d3fend-id"):
                    tactic = node.get("rdfs:label", current_tactic)

                cm_id = node.get("d3f:d3fend-id")
                if cm_id:
                    name = node.get("rdfs:label") or cm_id
                    desc = node.get("d3f:definition", "")
                    countermeasures[cm_id] = {
                        "id": cm_id,
                        "name": name,
                        "description": desc,
                        "tactic": tactic
                    }

                for child in node.get("children", []):
                    _walk(child, tactic)

            for tactic_root in data:
                tactic_name = tactic_root.get("rdfs:label", "General")
                _walk(tactic_root, tactic_name)

        # Handle graph format (d3fend.json)
        elif isinstance(data, dict) and "@graph" in data:
            for item in data.get("@graph", []):
                cm_id = item.get("d3f:d3fend-id")
                if cm_id:
                    countermeasures[cm_id] = {
                        "id": cm_id,
                        "name": item.get("rdfs:label") or cm_id,
                        "description": item.get("d3f:definition", ""),
                        "tactic": "Defensive"
                    }

        return list(countermeasures.values())

    def parse_all(self, technique_ids: Optional[List[str]] = None) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Extracts D3FEND countermeasures and mappings to ATT&CK techniques."""
        countermeasures = self.parse_countermeasures()
        mappings = self.fetch_or_load_mappings(technique_ids=technique_ids)
        return countermeasures, mappings
