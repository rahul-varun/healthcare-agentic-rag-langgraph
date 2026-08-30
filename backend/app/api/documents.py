from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.security.auth import require_api_key
from app.config.settings import get_settings
from app.ingestion.pipeline import SUPPORTED_SUFFIXES, ingest_file
from app.retrieval.embeddings import get_embedding_model
from app.retrieval.retriever import get_retriever
from app.retrieval.vector_store import ChromaVectorStore

router = APIRouter(tags=["documents"], dependencies=[Depends(require_api_key)])

_REPO_ROOT = Path(__file__).resolve().parents[3]
_KNOWLEDGE_BASE_DIR = _REPO_ROOT / "knowledge_base"
_SUPPORTED_SUFFIXES = SUPPORTED_SUFFIXES
_UPLOAD_DIR = _KNOWLEDGE_BASE_DIR / "uploads"


@router.get("/api/documents")
async def list_documents() -> dict:
    documents = []
    if _KNOWLEDGE_BASE_DIR.exists():
        for path in sorted(_KNOWLEDGE_BASE_DIR.rglob("*")):
            # Skip dotfiles — see app/ingestion/pipeline.py for why (AppleDouble
            # sidecars on this project's exFAT volume).
            if path.name.startswith("."):
                continue
            if path.is_file() and path.suffix.lower() in _SUPPORTED_SUFFIXES:
                documents.append(
                    {
                        "name": path.name,
                        "type": path.suffix.lstrip(".").lower(),
                        "size_bytes": path.stat().st_size,
                        "relative_path": str(path.relative_to(_KNOWLEDGE_BASE_DIR)),
                    }
                )
    return {"documents": documents}


@router.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...)) -> dict:
    """Store and index one PDF/Markdown knowledge document."""
    original_name = Path(file.filename or "").name
    suffix = Path(original_name).suffix.lower()
    if suffix not in _SUPPORTED_SUFFIXES:
        raise HTTPException(status_code=400, detail="Only PDF, .md, and .markdown files are supported")
    if not original_name:
        raise HTTPException(status_code=400, detail="A filename is required")

    settings = get_settings()
    content = await file.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status_code=413, detail=f"File is larger than {settings.max_upload_size_mb} MB")

    _UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    destination = _UPLOAD_DIR / original_name
    destination.write_bytes(content)
    try:
        chunks = ingest_file(destination)
        if not chunks:
            raise ValueError("No readable text was found in the document")
        embedding_model = get_embedding_model(settings.embedding_model)
        embeddings = embedding_model.embed([chunk.text for chunk in chunks])
        vector_store = ChromaVectorStore(settings.chroma_persist_dir)
        vector_store.add(
            ids=[chunk.id for chunk in chunks],
            texts=[chunk.text for chunk in chunks],
            embeddings=embeddings,
            metadatas=[chunk.metadata for chunk in chunks],
        )
        get_retriever.cache_clear()
    except Exception as exc:
        destination.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=f"Could not read or index document: {exc}") from exc

    return {"name": original_name, "type": suffix[1:], "chunks": len(chunks), "status": "indexed"}
