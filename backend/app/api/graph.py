from fastapi import APIRouter, Depends, HTTPException
from neo4j.exceptions import GqlError
from pydantic import BaseModel

from app.graph.neo4j_client import GraphError, get_neo4j_client
from app.security.auth import require_api_key

router = APIRouter(tags=["graph"], dependencies=[Depends(require_api_key)])


class GraphQueryRequest(BaseModel):
    entity: str
    other_entity: str | None = None
    max_hops: int = 2


class GraphQueryResponse(BaseModel):
    results: list[dict]


@router.post("/api/graph/query", response_model=GraphQueryResponse)
async def graph_query(request: GraphQueryRequest) -> GraphQueryResponse:
    client = get_neo4j_client()
    try:
        if request.other_entity:
            results = client.path_between(request.entity, request.other_entity, max_hops=request.max_hops)
        else:
            results = client.related(request.entity, max_hops=request.max_hops)
    except GraphError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except GqlError as exc:
        # Covers both driver-level failures (e.g. ServiceUnavailable when Neo4j
        # isn't reachable) and server-side Cypher errors (Neo4jError) — both
        # inherit from GqlError, not from each other.
        raise HTTPException(status_code=503, detail=f"Graph query failed: {exc}") from exc
    return GraphQueryResponse(results=results)
