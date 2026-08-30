import hashlib
from dataclasses import dataclass, field
from pathlib import Path

from app.ingestion.chunking import chunk_text
from app.ingestion.parsers import parse_file

SUPPORTED_SUFFIXES = {".pdf", ".md", ".markdown"}


@dataclass
class Chunk:
    id: str
    text: str
    metadata: dict = field(default_factory=dict)


def ingest_file(path: Path) -> list[Chunk]:
    units = parse_file(path)
    chunks: list[Chunk] = []
    for unit_index, unit in enumerate(units):
        for piece_index, piece in enumerate(chunk_text(unit.text)):
            chunk_id = hashlib.sha256(
                f"{path}:{unit_index}:{piece_index}:{piece}".encode()
            ).hexdigest()
            chunks.append(Chunk(id=chunk_id, text=piece, metadata=unit.metadata))
    return chunks


def ingest_directory(directory: Path) -> list[Chunk]:
    chunks: list[Chunk] = []
    for path in sorted(directory.rglob("*")):
        # Skip dotfiles — notably macOS AppleDouble "._name.ext" sidecars, which
        # exFAT/network volumes create for every real file and which otherwise
        # match SUPPORTED_SUFFIXES just like their real counterpart.
        if path.name.startswith("."):
            continue
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES:
            chunks.extend(ingest_file(path))
    return chunks
