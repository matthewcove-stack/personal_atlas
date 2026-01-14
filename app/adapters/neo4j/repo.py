from neo4j import GraphDatabase

from app.config import settings
from app.core.domain import AtlasLink, AtlasNode


class Neo4jGraphRepository:
    def __init__(self) -> None:
        self._driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )

    def upsert_node(self, node: AtlasNode, links: list[AtlasLink]) -> None:
        with self._driver.session() as session:
            session.execute_write(self._upsert_node, node, links)

    @staticmethod
    def _upsert_node(tx, node: AtlasNode, links: list[AtlasLink]) -> None:
        tx.run(
            """
            MERGE (n:AtlasNode {id: $id})
            SET n.title = $title,
                n.principle = $principle,
                n.confidence = $confidence,
                n.last_verified = $last_verified
            """,
            id=node.id,
            title=node.title,
            principle=node.principle,
            confidence=node.confidence,
            last_verified=str(node.last_verified),
        )
        for link in links:
            label = {
                "project": "Project",
                "material": "Material",
                "tool": "Tool",
            }.get(link.link_type, "Reference")
            tx.run(
                f"""
                MERGE (t:{label} {{name: $value}})
                WITH t
                MATCH (n:AtlasNode {{id: $id}})
                MERGE (n)-[:RELATES_TO]->(t)
                """,
                id=node.id,
                value=link.link_value,
            )
