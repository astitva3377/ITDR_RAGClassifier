from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.rag_model import RAGDocument
from ..models.models import Procedure, Technique
from .document_builder import build_procedure_doc, build_techinque_doc
from .embedding_service import EmbeddingService

class RAGIndexer:

	def __init__(
		self,
		session: Session,
		embedding_service: EmbeddingService
	) -> None:
		self.session = session
		self.embedding_service=embedding_service

	def index_techniques(self):
		techniques = self.session.scalars(
			select(Technique).where(
				Technique.deprecated == False,
				Technique.revoked == False
			)
		).all()

		for t in techniques:
			doc = build_techinque_doc(t)
			embedding = self.embedding_service.embed(doc)

			rag_doc = RAGDocument(
				document_type="technique",
				technique_id=t.technique_id,
				content=doc,
				embedding=embedding
			)

			self.session.add(rag_doc)
		self.session.commit()

	def index_procedures(self):
		procedures = self.session.scalars(
			select(Procedure)
		).all()

		for p in procedures:
			description = (p.description or "").strip()
			if not description:
				continue

			technique = self.session.get(
				Technique,
				p.technique_id
			)
			if technique is None:
				continue
			if technique.deprecated or technique.revoked:
				continue

			doc = build_procedure_doc(p, technique)

			embedding = self.embedding_service.embed(doc)

			rag_doc = RAGDocument(
				document_type="procedure",
				technique_id=technique.technique_id,
				content=doc,
				embedding=embedding
			)

			self.session.add(rag_doc)
		self.session.commit()