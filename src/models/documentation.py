from datetime import datetime
from uuid import uuid4, UUID
from pydantic import BaseModel, Field


class DocSection(BaseModel):
    title: str
    level: int = 1
    content: str = ""
    source_modules: list[str] = Field(default_factory=list)
    stale: bool = False


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
