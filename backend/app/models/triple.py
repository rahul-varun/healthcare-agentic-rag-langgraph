from dataclasses import dataclass


@dataclass
class Triple:
    subject: str
    subject_type: str
    predicate: str
    object: str
    object_type: str
    source_document: str = ""
    source_page: int | None = None
    heading_path: list[str] | None = None
