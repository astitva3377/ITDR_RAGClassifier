import pprint
import json
from collections import defaultdict
from app.db.database import SessionLocal
from app.rag.retriever import RagRetriever
from app.services.embedding_service import EmbeddingService

TESTS = [
	{
		"text": "The attacker used PowerShell to execute commands",
		"expected": ["T1059.001"]
	},
	{
		"text": "The malware dumped credentials from LSASS",
		"expected": ["T1003.001"]
	},
	{
		"text": "Attacker created a scheduled task for persistence",
		"expected": ["T1053.005"]
	},
	{
		"text": "Adversary used RDP to access compromised system",
		"expected": ["T1021.001"]
	},
	{
		"text": "Malware downloaded another executable from a remote server",
		"expected": ["T1105"]
	}
]

TEST_EXEC = [
	"The malware downloaded another executable from a remote server.",
	"The malware downloaded a file from a remote server.",
	"The malware retrieved a payload from a remote server.",
	"The attacker transferred a tool from a remote system.",
	"The attacker downloaded a malicious payload."
]

def test_top_n():

	session = SessionLocal()

	embedder = EmbeddingService()
	retriever = RagRetriever(session=session, embedder=embedder)

	print('Original queries')
	for test in TESTS:
		print()
		print('='*70)
		print(f'Test: {test["text"]}')
		print(f'Expected: {test["expected"]}')
		print()
		raw = retriever.retrieve(query=test["text"])
		candidates = group_by_technique(raw)
		for candidate in candidates[:15]:
			print(candidate.technique_id, candidate.technique_name, candidate.best_similarity, len(candidate.supporting_documents))

	print('\n\n\n')
	print('Top 50 results for executable download query')
	for test in TEST_EXEC:
		print()
		print('='*70)
		print(f'Test: {test}')
		print()
		raw = retriever.retrieve(query=test, top_k=50)
		for i in group_by_technique(raw)[:15]:
			print(i.technique_id, i.technique_name, i.best_similarity, len(i.supporting_documents))

	print('\n\n\n')
	print('Top 100 results for executable download query')
	for test in TEST_EXEC:
		print()
		print('='*70)
		print(f'Test: {test}')
		print()
		raw = retriever.retrieve(query=test, top_k=100)
		for i in group_by_technique(raw)[:15]:
			print(i.technique_id, i.technique_name, i.best_similarity, len(i.supporting_documents))


	session.close()

def main():
	session = SessionLocal()
	
	embedder = EmbeddingService()
	retriever = RagRetriever(session=session, embedder=embedder)

	result = retriever.get_candidates(TESTS[0]["text"])

	print(json.dumps(result, indent=4))

if __name__ == '__main__':
	main()