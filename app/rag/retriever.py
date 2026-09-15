from collections import defaultdict
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..models.models import Technique
from ..models.rag_model import RAGDocument, RetrievalResult, GroupedResult
from ..services.embedding_service import EmbeddingService

class RagRetriever:

	def __init__(
		self,
		session: Session,
		embedder: EmbeddingService
	) -> None:
		self.session = session
		self.embedder = embedder

	def retrieve(self, query: str, top_k: int = 50):
		query_embedding = self.embedder.embed(query)

		distance = RAGDocument.embedding.cosine_distance(query_embedding)

		stmt = (
			select(RAGDocument, Technique.technique_id, Technique.name, distance.label('distance'))
			.join(Technique, RAGDocument.technique_id == Technique.technique_id)
			.order_by(distance)
			.limit(top_k)
		)

		rows = self.session.execute(stmt).all()

		return [
			RetrievalResult(
				technique_id=technique_id,
				technique_name=technique_name,
				document_type=doc.document_type,
				content=doc.content,
				retrieval_similarity=1-float(distance)
			)
			for (doc, technique_id, technique_name, distance) in rows
		]

	def group_by_technique(self, results: list[RetrievalResult]) -> list[GroupedResult]:
		grouped = defaultdict(list)

		for result in results:
			grouped[result.technique_id].append(result)

		technique_results = []

		for technique_id, documents in grouped.items():
			documents.sort(
				key=lambda x: x.retrieval_similarity,
				reverse=True
			)

			best = documents[0]

			technique_results.append(
				GroupedResult(
					technique_id=technique_id,
					technique_name=best.technique_name,
					technique_description=None,
					best_retrieval_similarity=best.retrieval_similarity,
					supporting_documents=documents
				)
			)

		technique_results.sort(
			key=lambda x: x.best_retrieval_similarity,
			reverse=True
		)

		return technique_results

	def get_candidates(self, query: str, top_k = 50, top_n = 15, max_evidence = 3):
		retrieved = self.retrieve(query=query, top_k=top_k)
		grouped = self.group_by_technique(results=retrieved)

		candidates = []

		for item in grouped[:top_n]:
			evidence = []

			for doc in item.supporting_documents[:max_evidence]:
				evidence.append({
					"text": doc.content,
					"retrieval_similarity": doc.retrieval_similarity
				})

			candidates.append({
				"technique_id": item.technique_id,
				"technique_name": item.technique_name,
				"technique_description": None,
				"best_similarity": item.best_retrieval_similarity,
				"evidence": evidence
			})

		technique_ids = [
			candidate["technique_id"]
			for candidate in candidates
		]

		stmt = (
			select(Technique)
			.where(Technique.technique_id.in_(technique_ids))
		)

		techniques = self.session.scalars(stmt).all()

		technique_map = {
			technique.technique_id: technique
			for technique in techniques
		}

		for candidate in candidates:
			technique = technique_map.get(candidate["technique_id"])
			if technique is None:
				continue
			candidate["technique_name"] = technique.name
			candidate["technique_description"] = technique.description

		return candidates