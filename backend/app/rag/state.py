"""LangGraph State Definition."""
from typing import TypedDict, List, Dict, Any, Optional, Literal, Union

class ThreatAnalysisState(TypedDict):
    raw_input: Union[str, bytes]
    input_type: Literal["text", "url", "file"]
    clean_text: str
    observables: List[str]
    attack_candidates: List[Dict[str, Any]]
    validated_attacks: List[Dict[str, Any]]
    d3fend_recommendations: List[Dict[str, Any]]
    executive_summary: str
    confidence_metrics: Dict[str, float]
    errors: List[str]
