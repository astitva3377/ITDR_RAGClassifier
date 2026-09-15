from sqlalchemy import ForeignKey, String, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from ..db.database import Base

class StixObject(Base):
	__tablename__ = "stix_objects"

	id: Mapped[int] = mapped_column(primary_key=True)

	stix_id: Mapped[str] = mapped_column(
		String(255),
		unique=True,
		nullable=False,
		index=True
	)

	object_type: Mapped[str] = mapped_column(
		String(100),
		nullable=False,
		index=True
	)

	object_json: Mapped[dict] = mapped_column(
		JSONB,
		nullable=False
	)

class Tactic(Base):
	__tablename__ = "tactics"

	id: Mapped[int] = mapped_column(primary_key=True)

	stix_id: Mapped[str] = mapped_column(
		String(255),
		unique=True,
		nullable=False,
		index=True
	)

	name: Mapped[str] = mapped_column(
		String(255),
		nullable=False
	)

	short_name: Mapped[str] = mapped_column(
		String(100),
		nullable=False,
		unique=True
	)

	description: Mapped[str | None] = mapped_column(Text)

class Technique(Base):
	__tablename__ = "techniques"

	id: Mapped[int] = mapped_column(primary_key=True)

	stix_id: Mapped[str] = mapped_column(
		String(255),
		unique=True,
		nullable=False,
		index=True
	)

	technique_id: Mapped[str] = mapped_column(
		String(50),
		unique=True,
		nullable=False,
		index=True
	)

	name: Mapped[str] = mapped_column(
		String(255),
		nullable=False
	)

	description: Mapped[str | None] = mapped_column(Text)

	parent_technique_id: Mapped[str | None] = mapped_column(
		String(50),
		index=True
	)

	is_subtechnique: Mapped[bool] = mapped_column(
		Boolean,
		default=False,
		nullable=False
	)

	url: Mapped[str | None] = mapped_column(Text)

	deprecated: Mapped[bool] = mapped_column(
		Boolean, 
		default=False,
		nullable=False
	)

	revoked: Mapped[bool] = mapped_column(
		Boolean,
		default=False,
		nullable=False
	)

class AttackGroup(Base):
	__tablename__ = "attack_groups"

	id: Mapped[int] = mapped_column(primary_key=True)

	stix_id: Mapped[str] = mapped_column(
		String(255),
		unique=True,
		nullable=False,
		index=True
	)

	group_id: Mapped[str | None] = mapped_column(
		String(50),
		unique=True,
		index=True
	)

	name: Mapped[str] = mapped_column(
		String(255),
		nullable=False
	)

	description: Mapped[str | None] = mapped_column(Text)

	aliases: Mapped[list | None] = mapped_column(JSONB)

	deprecated: Mapped[bool] = mapped_column(
		Boolean, 
		default=False
	)

	revoked: Mapped[bool] = mapped_column(
		Boolean,
		default=False
	)

class MalwareTool(Base):
	__tablename__ = "malwares_tools"

	id: Mapped[int] = mapped_column(primary_key=True)

	stix_id: Mapped[str] = mapped_column(
		String(255),
		unique=True,
		nullable=False,
		index=True
	)

	software_id: Mapped[str | None] = mapped_column(
		String(50),
		unique=True,
		index=True
	)

	name: Mapped[str] = mapped_column(
		String(255),
		nullable=False
	)

	description: Mapped[str | None] = mapped_column(Text)

	software_type: Mapped[str] = mapped_column(
		String(50),
		nullable=False
	)

	aliases: Mapped[list | None] = mapped_column(JSONB)

	deprecated: Mapped[bool] = mapped_column(
		Boolean,
		default=False
	)

	revoked: Mapped[bool] = mapped_column(
		Boolean,
		default=False
	)

class Procedure(Base):
	__tablename__ = "procedures"

	id: Mapped[int] = mapped_column(primary_key=True)

	stix_id: Mapped[str] = mapped_column(
		String(255),
		unique=True,
		nullable=False,
		index=True
	)

	technique_id: Mapped[int] = mapped_column(
		ForeignKey("techniques.id"),
		nullable=False,
		index=True
	)

	group_id: Mapped[int | None] = mapped_column(
		ForeignKey("attack_groups.id"),
		nullable=True,
		index=True
	)

	software_id: Mapped[int | None] = mapped_column(
		ForeignKey("malwares_tools.id"),
		nullable=True,
		index=True
	)

	description: Mapped[str | None] = mapped_column(Text)