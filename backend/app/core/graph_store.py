"""Neo4j 5+ Unified Property Graph and Vector Index Manager."""
from neo4j import GraphDatabase
from app.core.config import settings

class Neo4jGraphStore:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
        
    def close(self):
        self.driver.close()
        
    def create_vector_indexes(self):
        """Creates native Neo4j 5+ vector search indexes for ATT&CK and D3FEND nodes."""
        pass
