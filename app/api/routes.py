from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_atlas_repo, get_commit_service, get_search_service, get_stage_service
from app.api.schemas import CommitRequest, CommitResponse, NodeResponse, SearchResponse, StageRequest, StageResponse
from app.core.domain import AtlasLink
from app.core.services import NotFoundError

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/atlas/nodes/stage", response_model=StageResponse)
def stage_node(payload: StageRequest, service=Depends(get_stage_service)) -> StageResponse:
    links = [AtlasLink(link_type=l.type, link_value=l.value) for l in payload.links]
    node = service.stage(
        idempotency_key=payload.idempotency_key,
        title=payload.title,
        principle=payload.principle,
        evidence=payload.evidence,
        confidence=payload.confidence,
        last_verified=payload.last_verified,
        links=links,
    )
    return StageResponse(id=node.id, status=node.status)


@router.post("/atlas/nodes/commit", response_model=CommitResponse)
def commit_node(payload: CommitRequest, service=Depends(get_commit_service)) -> CommitResponse:
    try:
        node = service.commit(idempotency_key=payload.idempotency_key)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return CommitResponse(id=node.id, status=node.status)


@router.get("/atlas/nodes/{node_id}", response_model=NodeResponse)
def get_node(node_id: str, repo=Depends(get_atlas_repo)) -> NodeResponse:
    node = repo.get_by_id(node_id)
    if not node or node.status != "committed":
        raise HTTPException(status_code=404, detail="node not found")
    links = repo.get_links(node_id)
    return NodeResponse(
        id=node.id,
        title=node.title,
        principle=node.principle,
        evidence=node.evidence,
        confidence=node.confidence,
        last_verified=node.last_verified,
        links=[{"type": l.link_type, "value": l.link_value} for l in links],
    )


@router.get("/atlas/search", response_model=SearchResponse)
def search(q: str, k: int = 5, service=Depends(get_search_service)) -> SearchResponse:
    results = service.search(query=q, k=k)
    return SearchResponse(results=results)
