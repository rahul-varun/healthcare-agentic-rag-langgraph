#!/usr/bin/env python3
"""Extract entities/relationships from PDF/Markdown files into Neo4j.

Usage:
    python scripts/extract_graph.py [directory]

Requires OPENROUTER_API_KEY (LLM-based extraction) and a running Neo4j instance.
Defaults to knowledge_base/ at the repo root.
"""
import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.config.settings import get_settings  # noqa: E402
from app.graph.extraction import extract_triples  # noqa: E402
from app.graph.neo4j_client import Neo4jClient  # noqa: E402
from app.ingestion.pipeline import ingest_directory  # noqa: E402


async def run(directory: str) -> None:
    settings = get_settings()
    chunks = ingest_directory(Path(directory))
    if not chunks:
        print(f"No PDF/Markdown files found under {directory}")
        return

    client = Neo4jClient(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password)
    total_triples = 0
    try:
        for chunk in chunks:
            triples = await extract_triples(chunk.text, chunk.metadata, settings)
            for triple in triples:
                client.upsert_triple(triple)
            total_triples += len(triples)
    finally:
        client.close()

    print(f"Extracted {total_triples} triples from {len(chunks)} chunks into Neo4j at {settings.neo4j_uri}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "directory",
        nargs="?",
        default=str(Path(__file__).resolve().parent.parent / "knowledge_base"),
    )
    args = parser.parse_args()
    asyncio.run(run(args.directory))


if __name__ == "__main__":
    main()
