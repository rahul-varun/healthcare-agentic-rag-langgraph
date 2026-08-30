from dataclasses import dataclass


@dataclass
class EvidenceChunk:
    text: str
    metadata: dict
    score: float
