from sqlalchemy.orm import Session
import json
from pathlib import Path

from ..models.models import (
	AttackGroup,
	Procedure,
	MalwareTool,
	Tactic,
	Technique,
	StixObject
)
from ..models.relationships import TechinqueTacticMap

def get_external_id(obj: dict) -> str | None:
	for reference in obj.get("external_references", []):
		if reference.get("source_name") == "mitre-attack":
			return reference.get("external_id")
	return None

def ingest_stix_objects(
	session: Session,
	objects: list[dict]
) -> None:
	for obj in objects:
		stix_id = obj.get("id")

		if not stix_id:
			continue

		existing = session.query(StixObject).filter_by(
			stix_id=stix_id
		).first()

		if existing:
			continue

		session.add(
			StixObject(
				stix_id=stix_id,
				object_type=obj.get("type"),
				object_json=obj
			)
		)

		session.commit()

def ingest_tactics(
	session: Session,
	objects: list[dict]
) -> None:
	for obj in objects:
		if obj.get("type") != "x-mitre-tactic":
			continue

		stix_id = obj["id"]

		existing = session.query(Tactic).filter_by(stix_id=stix_id).first()

		if existing:
			continue

		session.add(
			Tactic(
				stix_id=stix_id,
				name=obj["name"],
				short_name=obj["x_mitre_shortname"],
				description=obj.get("description")
			)
		)

		session.commit()

def ingest_techniques(
	session: Session,
	objects: list[dict]
) -> None:
	for obj in objects:
		if obj.get("type") != "attack-pattern":
			continue

		technique_id = get_external_id(obj)

		if not technique_id:
			continue

		existing = session.query(Technique).filter_by(technique_id=technique_id).first()

		if existing:
			continue

		is_subtechnique = obj.get("x_mitre_is_subtechnique", False)

		parent_technique_id = None

		if is_subtechnique and "." in technique_id:
			parent_technique_id = technique_id.split(".", 1)[0]

		url = None

		for reference in obj.get("external_references", []):
			if reference.get("source_name") == "mitre_attack":
				url = reference.get("url")
				break

		session.add(
			Technique(
				stix_id=obj["id"],
				technique_id=technique_id,
				name=obj["name"],
				description=obj.get("description"),
				parent_technique_id=parent_technique_id,
				is_subtechnique=is_subtechnique,
				url=url,
				deprecated=obj.get("x_mitre_deprecated", False),
				revoked=obj.get("revoked", False)
			)
		)

		session.commit()

def ingest_groups(
	session: Session,
	objects: list[dict]
) -> None:
	for obj in objects:
		if obj.get("type") != "intrusion-set":
			continue

		group_id = get_external_id(obj)

		exisiting = session.query(AttackGroup).filter_by(stix_id=obj["id"]).first()

		if exisiting:
			continue

		session.add(
			AttackGroup(
				stix_id=obj["id"],
				group_id=group_id,
				name=obj["name"],
				description=obj.get("description"),
				aliases=obj.get("aliases"),
				deprecated=obj.get("x_mitre_deprecated", False),
				revoked=obj.get("revoked", False)
			)
		)

		session.commit()

def ingest_tools(
	session: Session,
	objects: list[dict]
) -> None:
	for obj in objects:
		if obj.get("type") not in { "malware", "tool" }:
			continue

		tool_id = get_external_id(obj)

		existing = session.query(MalwareTool).filter_by(stix_id=obj["id"]).first()

		if existing:
			continue

		session.add(
			MalwareTool(
				stix_id=obj["id"],
				software_id=tool_id,
				name=obj["name"],
				description=obj.get("description"),
				software_type=obj["type"],
				aliases=obj.get("aliases"),
				deprecated=obj.get("x_mitre_deprecated", False),
				revoked=obj.get("revoked", False)
			)
		)

		session.commit()

def build_stix_maps(session: Session):
	techniques = {
		obj.stix_id: obj
		for obj in session.query(Technique).all()
	}

	groups = {
		obj.stix_id: obj
		for obj in session.query(AttackGroup).all()
	}

	software = {
		obj.stix_id: obj
		for obj in session.query(MalwareTool).all()
	}

	tactics = {
		obj.stix_id: obj
		for obj in session.query(Tactic).all()
	}

	return techniques, groups, software, tactics

def ingest_technique_tactics(
	session: Session,
	objects: list[dict],
) -> None:

	techniques = {
		obj.technique_id: obj
		for obj in session.query(Technique).all()
	}

	tactics = {
		obj.short_name: obj
		for obj in session.query(Tactic).all()
	}

	for obj in objects:
		if obj.get("type") != "attack-pattern":
			continue

		technique_id = get_external_id(obj)

		if not technique_id:
			continue

		technique = techniques.get(technique_id)

		if not technique:
			continue

		for phase in obj.get("kill_chain_phases", []):
			if phase.get("kill_chain_name") != "mitre-attack":
				continue

			short_name = phase.get("phase_name")

			tactic = tactics.get(short_name)

			if not tactic:
				continue

			existing = session.query(TechinqueTacticMap).filter_by(
				technique_id=technique.id,
				tactic_id=tactic.id
			).first()

			if existing:
				continue

			session.add(
				TechinqueTacticMap(
					technique_id=technique.id,
					tactic_id=tactic.id
				)
			)

			session.commit()

def ingest_procedures(
	session: Session,
	objects: list[dict]
) -> None:

	techniques, groups, software, _ = build_stix_maps(session)

	for obj in objects:
		if obj.get("type") != "relationship":
			continue
		if obj.get("relationship_type") != "uses":
			continue

		source_ref = obj.get("source_ref")
		target_ref = obj.get("target_ref")

		technique = techniques.get(target_ref)

		if not technique:
			continue

		group = groups.get(source_ref)
		software_obj = software.get(source_ref)

		if not group and not software_obj:
			continue

		existing = session.query(Procedure).filter_by(stix_id=obj["id"]).first()

		if existing:
			continue

		session.add(
			Procedure(
				stix_id=obj["id"],
				technique_id=technique.id,
				group_id=group.id if group else None,
				software_id=software_obj.id if software_obj else None,
				description=obj.get("description")
			)
		)

		session.commit()

def ingest_file(
	session: Session,
	file_path: str
) -> None:
	path = Path(file_path)

	with path.open('r', encoding='utf-8') as f:
		bundle = json.load(f)
	objects = bundle.get("objects", [])
	print(f'Loaded {len(objects)} STIX objects')

	print('Ingesting raw STIX...')
	ingest_stix_objects(session, objects)

	print('Ingesting Tactics...')
	ingest_tactics(session, objects)

	print('Ingesting Techniques...')
	ingest_techniques(session, objects)

	print('Ingesting Groups...')
	ingest_groups(session, objects)

	print('Ingesting Softwares...')
	ingest_tools(session, objects)

	print('Building Relation Map...')
	ingest_technique_tactics(session, objects)

	print('Ingesting procedures...')
	ingest_procedures(session, objects)

	print('Ingestion complete')