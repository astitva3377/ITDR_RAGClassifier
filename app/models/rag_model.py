from dataclasses import dataclass
from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from ..db.database import Base

class RAGDocument(Base):
	__tablename__ = "rag_documents"

	id: Mapped[int] = mapped_column(primary_key=True)

	document_type: Mapped[str] = mapped_column(
		String(50),
		nullable=False,
		index=True
	)

	technique_id: Mapped[str] = mapped_column(
		ForeignKey("techniques.technique_id"),
		nullable=False,
		index=True
	)

	content: Mapped[str] = mapped_column(Text, nullable=False)

	embedding = mapped_column(
		Vector(768),
		nullable=False
	)


@dataclass
class RetrievalResult:
	technique_id: str
	technique_name: str
	document_type: str
	content: str
	retrieval_similarity: float

@dataclass
class GroupedResult:
	technique_id: str
	technique_name: str
	technique_description: str | None
	best_retrieval_similarity: float
	supporting_documents: list[RetrievalResult]