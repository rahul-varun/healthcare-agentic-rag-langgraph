#!/usr/bin/env python3
"""Ingest PDF/Markdown files from a directory into the vector store.

Usage:
    python scripts/ingest.py [directory]

Defaults to knowledge_base/ at the repo root.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.config.settings import get_settings  # noqa: E402
from app.ingestion.pipeline import ingest_directory  # noqa: E402
from app.retrieval.embeddings import get_embedding_model  # noqa: E402
from app.retrieval.vector_store import ChromaVectorStore  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "directory",
        nargs="?",
        default=str(Path(__file__).resolve().parent.parent / "knowledge_base"),
    )
    args = parser.parse_args()

    settings = get_settings()
    chunks = ingest_directory(Path(args.directory))
    if not chunks:
        print(f"No PDF/Markdown files found under {args.directory}")
        return

    embedding_model = get_embedding_model(settings.embedding_model)
    vector_store = ChromaVectorStore(settings.chroma_persist_dir)

    embeddings = embedding_model.embed([c.text for c in chunks])
    vector_store.add(
        ids=[c.id for c in chunks],
        texts=[c.text for c in chunks],
        embeddings=embeddings,
        metadatas=[c.metadata for c in chunks],
    )
    print(f"Ingested {len(chunks)} chunks from {args.directory} into {settings.chroma_persist_dir}")


if __name__ == "__main__":
    main()
