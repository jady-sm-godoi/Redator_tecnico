import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4, UUID
from pydantic import BaseModel, Field


META_FILENAME = "_meta.json"


class DocSection(BaseModel):
    title: str
    level: int = 1
    content: str = ""
    source_modules: list[str] = Field(default_factory=list)
    stale: bool = False


class SectionMetadata(BaseModel):
    title: str
    level: int = 1
    source_modules: list[str] = Field(default_factory=list)
    content_hash: str = ""


class DocMetadata(BaseModel):
    repo_url: str
    generated_at: datetime
    source_hash: str
    module_content_hashes: dict[str, str] = Field(default_factory=dict)
    sections: list[SectionMetadata] = Field(default_factory=list)


class ChangelogEntry(BaseModel):
    version: int
    date: datetime = Field(default_factory=datetime.now)
    changed_sections: list[str] = Field(default_factory=list)
    trigger: str = "manual"


class Documentation(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    repo_url: str
    generated_at: datetime = Field(default_factory=datetime.now)
    format: str = "markdown"
    sections: list[DocSection] = Field(default_factory=list)
    changelog: list[ChangelogEntry] = Field(default_factory=list)
    source_hash: str = ""


def save_doc_metadata(doc: Documentation, doc_dir: Path, module_content_hashes: dict[str, str] | None = None) -> None:
    meta = DocMetadata(
        repo_url=doc.repo_url,
        generated_at=doc.generated_at,
        source_hash=doc.source_hash,
        module_content_hashes=module_content_hashes or {},
        sections=[
            SectionMetadata(
                title=s.title,
                level=s.level,
                source_modules=s.source_modules,
                content_hash=_content_hash_for_section(s),
            )
            for s in doc.sections
        ],
    )
    meta_file = doc_dir / META_FILENAME
    meta_file.write_text(meta.model_dump_json(indent=2))


def load_doc_metadata(doc_dir: Path) -> DocMetadata | None:
    meta_file = doc_dir / META_FILENAME
    if not meta_file.exists():
        return None
    try:
        return DocMetadata(**json.loads(meta_file.read_text()))
    except (json.JSONDecodeError, ValueError):
        return None


def _content_hash_for_section(section: DocSection) -> str:
    import hashlib
    raw = section.title + ":" + ",".join(sorted(section.source_modules)) + ":" + str(section.level)
    return hashlib.sha256(raw.encode()).hexdigest()[:12]
