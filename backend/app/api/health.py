import asyncio

from fastapi import APIRouter
from neo4j.exceptions import GqlError

from app.graph.neo4j_client import get_neo4j_client
from app.retrieval.retriever import get_retriever
from app.tools.sql_tool import check_connection

router = APIRouter(tags=["health"])


@router.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}


def _check_vector_store() -> str:
    try:
        get_retriever().vector_store.count()
        return "up"
    except Exception:
        return "down"


def _check_neo4j() -> str:
    try:
        get_neo4j_client().related("__healthcheck__", max_hops=1)
        return "up"
    except GqlError:
        return "down"


def _check_postgres() -> str:
    return "up" if check_connection() else "down"


@router.get("/api/health/ready")
async def readiness() -> dict:
    # Dependencies are checked off the event loop (asyncio.to_thread) since
    # they're blocking sync calls — a connection attempt to an unreachable host
    # would otherwise stall every other concurrent request.
    vector_store, neo4j, postgres = await asyncio.gather(
        asyncio.to_thread(_check_vector_store),
        asyncio.to_thread(_check_neo4j),
        asyncio.to_thread(_check_postgres),
    )
    # The agent degrades gracefully without Neo4j/Postgres (Phase 4), so this
    # reports component status rather than failing the whole probe.
    return {"vector_store": vector_store, "neo4j": neo4j, "postgres": postgres}
