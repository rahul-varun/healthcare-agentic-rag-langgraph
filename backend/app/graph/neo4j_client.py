from functools import lru_cache

from neo4j import GraphDatabase

from app.config.settings import get_settings
from app.graph.schema import ALLOWED_RELATIONS
from app.models.triple import Triple


class GraphError(RuntimeError):
    pass


def _validate_relation(predicate: str) -> str:
    if predicate not in ALLOWED_RELATIONS:
        raise GraphError(f"Unknown relation type: {predicate}")
    return predicate


def _clamp_hops(max_hops: int, low: int = 1, high: int = 5) -> int:
    return max(low, min(high, int(max_hops)))


def build_upsert_query(predicate: str) -> str:
    """Relationship types can't be parameterized in Cypher, so the validated
    predicate is interpolated directly — safe only because _validate_relation
    rejects anything outside the fixed ALLOWED_RELATIONS set."""
    relation = _validate_relation(predicate)
    return (
        "MERGE (s:Entity {name: $subject}) "
        "ON CREATE SET s.type = $subject_type "
        "MERGE (o:Entity {name: $object}) "
        "ON CREATE SET o.type = $object_type "
        f"MERGE (s)-[r:{relation}]->(o) "
        "SET r.source_document = $source_document, "
        "r.source_page = $source_page, "
        "r.heading_path = $heading_path"
    )


def build_related_query(max_hops: int) -> str:
    hops = _clamp_hops(max_hops)
    return (
        f"MATCH (a:Entity {{name: $name}})-[r*1..{hops}]-(b:Entity) "
        "RETURN a.name AS source, b.name AS target, "
        "[rel IN r | type(rel)] AS relationships LIMIT 50"
    )


def build_path_query(max_hops: int) -> str:
    hops = _clamp_hops(max_hops)
    return (
        f"MATCH path = shortestPath((a:Entity {{name: $a}})-[*..{hops}]-(b:Entity {{name: $b}})) "
        "RETURN [n IN nodes(path) | n.name] AS nodes, "
        "[rel IN relationships(path) | type(rel)] AS relationships"
    )


class Neo4jClient:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self) -> None:
        self.driver.close()

    def upsert_triple(self, triple: Triple) -> None:
        query = build_upsert_query(triple.predicate)
        with self.driver.session() as session:
            session.run(
                query,
                subject=triple.subject,
                subject_type=triple.subject_type,
                object=triple.object,
                object_type=triple.object_type,
                source_document=triple.source_document,
                source_page=triple.source_page,
                heading_path=triple.heading_path or [],
            )

    def related(self, entity_name: str, max_hops: int = 1) -> list[dict]:
        query = build_related_query(max_hops)
        with self.driver.session() as session:
            return [record.data() for record in session.run(query, name=entity_name)]

    def path_between(self, entity_a: str, entity_b: str, max_hops: int = 5) -> list[dict]:
        query = build_path_query(max_hops)
        with self.driver.session() as session:
            return [record.data() for record in session.run(query, a=entity_a, b=entity_b)]


@lru_cache
def get_neo4j_client() -> Neo4jClient:
    settings = get_settings()
    return Neo4jClient(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password)
