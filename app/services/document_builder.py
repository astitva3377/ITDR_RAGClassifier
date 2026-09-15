from ..models.models import Procedure, Technique

def build_techinque_doc(technique: Technique) -> str:
	return f"""
Technique ID: {technique.technique_id}
Technique Name: {technique.name}
Parent Technique: {technique.parent_technique_id or "None"}

Description:
{technique.description or ""}
""".strip()

def build_procedure_doc(procedure: Procedure, technique: Technique) -> str:
	return f"""
Technique ID: {technique.technique_id}
Technique Name: {technique.name}

Procedure:
{procedure.description or ""}
""".strip()