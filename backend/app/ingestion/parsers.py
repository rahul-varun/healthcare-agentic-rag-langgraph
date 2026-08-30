import re
from dataclasses import dataclass, field
from pathlib import Path

import frontmatter
from pypdf import PdfReader


@dataclass
class ParsedUnit:
    text: str
    metadata: dict = field(default_factory=dict)


_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")


def parse_pdf(path: Path) -> list[ParsedUnit]:
    reader = PdfReader(str(path))
    units = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if not text.strip():
            continue
        units.append(
            ParsedUnit(
                text=text,
                metadata={
                    "source_type": "pdf",
                    "document_name": path.name,
                    "page": page_number,
                },
            )
        )
    return units


def parse_markdown(path: Path) -> list[ParsedUnit]:
    post = frontmatter.load(path)
    base_metadata = {"source_type": "markdown", "document": path.name, **post.metadata}

    units: list[ParsedUnit] = []
    heading_stack: list[tuple[int, str]] = []
    buffer: list[str] = []

    def flush():
        section_text = "\n".join(buffer).strip()
        if section_text:
            units.append(
                ParsedUnit(
                    text=section_text,
                    metadata={
                        **base_metadata,
                        "heading_path": [title for _, title in heading_stack],
                    },
                )
            )
        buffer.clear()

    for line in post.content.splitlines():
        match = _HEADING_RE.match(line)
        if match:
            flush()
            level, title = len(match.group(1)), match.group(2).strip()
            while heading_stack and heading_stack[-1][0] >= level:
                heading_stack.pop()
            heading_stack.append((level, title))
        else:
            buffer.append(line)
    flush()

    return units


def parse_file(path: Path) -> list[ParsedUnit]:
    if path.suffix.lower() == ".pdf":
        return parse_pdf(path)
    if path.suffix.lower() in (".md", ".markdown"):
        return parse_markdown(path)
    raise ValueError(f"Unsupported file type: {path.suffix}")
