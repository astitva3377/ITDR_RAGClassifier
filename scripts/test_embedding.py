from app.db.database import SessionLocal
from app.models.models import Technique
from app.models.rag_model import RAGDocument
from app.services.document_builder import build_techinque_doc
from app.services import embedding_service
from app.services.embedding_service import EmbeddingService

embedding_service = EmbeddingService(model="text-embedding-nomic-embed-text-v1.5")


# print("Vector dimension:", len(vector))
# print("First 10 values:", vector[:10])

session = SessionLocal()
technique = session.query(Technique).first()
doc = build_techinque_doc(technique=technique)
print(doc)
vector = embedding_service.embed(doc)
ragdoc = RAGDocument(
	document_type="technique",
	technique_id=technique.id,
	content=doc,
	embedding=vector
)

print(ragdoc)