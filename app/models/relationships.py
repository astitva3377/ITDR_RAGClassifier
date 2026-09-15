from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped
from ..db.database import Base

class TechinqueTacticMap(Base):
	__tablename__ = "technique_tactic_map"

	technique_id: Mapped[int] = mapped_column(
		ForeignKey("techniques.id"),
		primary_key=True
	)

	tactic_id: Mapped[int] = mapped_column(
		ForeignKey("tactics.id"),
		primary_key=True
	)