from app.db.database import Base, SessionLocal, engine
from app.services.attack_ingestion import ingest_file
from app.services.embedding_service import EmbeddingService
from app.services.indexer_service import RAGIndexer

def ingest_json_attack_file():
	Base.metadata.create_all(bind=engine)

	session = SessionLocal()

	try:
		ingest_file(session=session, file_path='data\\enterprise-attack.json')
	finally:
		session.close()

def create_index_vectors():
	Base.metadata.create_all(bind=engine)

	session = SessionLocal()

	try:
		indexer = RAGIndexer(session=session, embedding_service=EmbeddingService())
		indexer.index_techniques()
		indexer.index_procedures()
	finally:
		session.close()

if __name__ == "__main__":
	create_index_vectors()