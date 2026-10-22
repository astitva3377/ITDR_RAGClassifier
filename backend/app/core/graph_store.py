"""Neo4j 5+ Unified Property Graph and Vector Index Manager."""
from typing import Any, Dict, List, Optional
from neo4j import GraphDatabase, Driver
from app.core.config import settings

class Neo4jGraphStore:
    def __init__(
        self,
        uri: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
    ):
        self.uri = uri or settings.NEO4J_URI
        self.user = user or settings.NEO4J_USER
        self.password = password or settings.NEO4J_PASSWORD
        self.database = database or settings.NEO4J_DATABASE
        self.driver: Driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def close(self) -> None:
        self.driver.close()

    def verify_connectivity(self) -> bool:
        """Verifies active connectivity to Neo4j instance."""
        try:
            self.driver.verify_connectivity()
            return True
        except Exception:
            return False

    def create_schema_and_indexes(self) -> None:
        """Creates uniqueness constraints and native Neo4j 5+ vector index."""
        with self.driver.session(database=self.database) as session:
            # 1. Uniqueness constraints
            session.run("CREATE CONSTRAINT technique_id_unique IF NOT EXISTS FOR (t:Technique) REQUIRE t.id IS UNIQUE")
            session.run("CREATE CONSTRAINT tactic_id_unique IF NOT EXISTS FOR (ta:Tactic) REQUIRE ta.id IS UNIQUE")
            session.run("CREATE CONSTRAINT countermeasure_id_unique IF NOT EXISTS FOR (c:Countermeasure) REQUIRE c.id IS UNIQUE")

            # 2. Native vector index on technique descriptions
            session.run("""
                CREATE VECTOR INDEX technique_embeddings IF NOT EXISTS
                FOR (m:Technique) ON (m.embedding)
                OPTIONS { indexConfig: {
                    `vector.dimensions`: 384,
                    `vector.similarity_function`: 'cosine'
                }}
            """)

    def ingest_tactics(self, tactics: List[Dict[str, Any]]) -> None:
        """Merges Tactic nodes in batch."""
        if not tactics:
            return
        query = """
        UNWIND $batch AS item
        MERGE (ta:Tactic {id: item.id})
        SET ta.name = item.name,
            ta.short_name = item.short_name,
            ta.description = item.description
        """
        with self.driver.session(database=self.database) as session:
            session.run(query, batch=tactics)

    def ingest_techniques(self, techniques: List[Dict[str, Any]]) -> None:
        """Merges top-level Technique nodes in batch."""
        if not techniques:
            return
        query = """
        UNWIND $batch AS item
        MERGE (t:Technique {id: item.id})
        SET t.name = item.name,
            t.description = item.description,
            t.tactics = item.tactics,
            t.is_subtechnique = false
        FOREACH (_ IN CASE WHEN item.embedding IS NOT NULL THEN [1] ELSE [] END |
            SET t.embedding = item.embedding
        )
        """
        with self.driver.session(database=self.database) as session:
            session.run(query, batch=techniques)

    def ingest_subtechniques(self, subtechniques: List[Dict[str, Any]]) -> None:
        """Merges Subtechnique nodes (labeled :Technique:Subtechnique) in batch."""
        if not subtechniques:
            return
        query = """
        UNWIND $batch AS item
        MERGE (t:Technique {id: item.id})
        SET t:Subtechnique,
            t.name = item.name,
            t.description = item.description,
            t.tactics = item.tactics,
            t.is_subtechnique = true
        FOREACH (_ IN CASE WHEN item.embedding IS NOT NULL THEN [1] ELSE [] END |
            SET t.embedding = item.embedding
        )
        """
        with self.driver.session(database=self.database) as session:
            session.run(query, batch=subtechniques)

    def ingest_countermeasures(self, countermeasures: List[Dict[str, Any]]) -> None:
        """Merges D3FEND Countermeasure nodes in batch."""
        if not countermeasures:
            return
        query = """
        UNWIND $batch AS item
        MERGE (c:Countermeasure {id: item.id})
        SET c.name = item.name,
            c.description = item.description,
            c.tactic = item.tactic
        """
        with self.driver.session(database=self.database) as session:
            session.run(query, batch=countermeasures)

    def ingest_subtechnique_relationships(self, relationships: List[Dict[str, Any]]) -> None:
        """Creates SUBTECHNIQUE_OF edges from subtechniques to parent techniques."""
        if not relationships:
            return
        query = """
        UNWIND $batch AS item
        MATCH (s:Technique {id: item.source_id})
        MATCH (p:Technique {id: item.target_id})
        MERGE (s)-[:SUBTECHNIQUE_OF]->(p)
        """
        with self.driver.session(database=self.database) as session:
            session.run(query, batch=relationships)

    def ingest_countermeasure_mappings(self, mappings: List[Dict[str, Any]]) -> None:
        """Creates COUNTERS or DETECTS edges between techniques and countermeasures."""
        if not mappings:
            return
        detects = [m for m in mappings if m.get("relationship_type") == "DETECTS"]
        counters = [m for m in mappings if m.get("relationship_type") != "DETECTS"]

        with self.driver.session(database=self.database) as session:
            if detects:
                session.run("""
                    UNWIND $batch AS item
                    MATCH (t:Technique {id: item.technique_id})
                    MATCH (c:Countermeasure {id: item.countermeasure_id})
                    MERGE (t)-[:DETECTS]->(c)
                """, batch=detects)
            if counters:
                session.run("""
                    UNWIND $batch AS item
                    MATCH (t:Technique {id: item.technique_id})
                    MATCH (c:Countermeasure {id: item.countermeasure_id})
                    MERGE (t)-[:COUNTERS]->(c)
                """, batch=counters)

    def get_counts(self) -> Dict[str, int]:
        """Returns node, relationship, and index counts from Neo4j."""
        counts = {
            "tactics": 0,
            "techniques": 0,
            "subtechniques": 0,
            "countermeasures": 0,
            "subtechnique_relationships": 0,
            "countermeasure_relationships": 0,
            "vector_indexes": 0,
        }
        with self.driver.session(database=self.database) as session:
            res = session.run("""
                RETURN
                    COUNT { MATCH (:Tactic) } AS tactics,
                    COUNT { MATCH (t:Technique) WHERE NOT t:Subtechnique } AS techniques,
                    COUNT { MATCH (:Subtechnique) } AS subtechniques,
                    COUNT { MATCH (:Countermeasure) } AS countermeasures,
                    COUNT { MATCH ()-[:SUBTECHNIQUE_OF]->() } AS subtechnique_relationships,
                    COUNT { MATCH ()-[:COUNTERS|DETECTS]->() } AS countermeasure_relationships
            """).single()
            if res:
                counts.update({
                    "tactics": res["tactics"],
                    "techniques": res["techniques"],
                    "subtechniques": res["subtechniques"],
                    "countermeasures": res["countermeasures"],
                    "subtechnique_relationships": res["subtechnique_relationships"],
                    "countermeasure_relationships": res["countermeasure_relationships"],
                })

            idx_res = session.run("SHOW VECTOR INDEXES").data()
            counts["vector_indexes"] = len(idx_res)

        return counts

    def query_vector_with_countermeasures(
        self,
        embedding: List[float],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Queries the native vector index and traverses linked D3FEND countermeasures."""
        query = """
        CALL db.index.vector.queryNodes('technique_embeddings', $k, $vec)
        YIELD node, score
        OPTIONAL MATCH (node)-[:COUNTERS|DETECTS]-(c:Countermeasure)
        RETURN
            node.id AS technique_id,
            node.name AS technique_name,
            node.description AS description,
            score,
            collect(DISTINCT CASE WHEN c IS NOT NULL THEN {
                id: c.id,
                name: c.name,
                tactic: c.tactic
            } ELSE NULL END) AS raw_countermeasures
        ORDER BY score DESC
        """
        results: List[Dict[str, Any]] = []
        with self.driver.session(database=self.database) as session:
            records = session.run(query, k=top_k, vec=embedding).data()
            for r in records:
                cms = [c for c in r.get("raw_countermeasures", []) if c is not None]
                results.append({
                    "technique_id": r["technique_id"],
                    "technique_name": r["technique_name"],
                    "description": r.get("description", ""),
                    "score": float(r["score"]),
                    "countermeasures": cms,
                })
        return results
