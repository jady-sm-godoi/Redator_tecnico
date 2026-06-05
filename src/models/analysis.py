from datetime import datetime
from uuid import uuid4, UUID
from enum import Enum
from pydantic import BaseModel, Field


class ModuleType(str, Enum):
    package = "package"
    module = "module"
    class_ = "class"
    function = "function"


class DepType(str, Enum):
    import_ = "import"
    inherit = "inherit"
    compose = "compose"
    call = "call"


class Significance(str, Enum):
    major = "major"
    minor = "minor"
    refactor = "refactor"
    fix = "fix"
    docs = "docs"


class Module(BaseModel):
    name: str
    path: str
    type: ModuleType
    docstring: str | None = None
    dependencies: list[str] = Field(default_factory=list)
    exported_symbols: list[str] = Field(default_factory=list)


class Dependency(BaseModel):
    source: str
    target: str
    type: DepType = DepType.import_
    is_external: bool = False


class CommitEvent(BaseModel):
    hash: str
    author: str
    date: datetime
    message: str
    files_changed: list[str] = Field(default_factory=list)
    significance: Significance = Significance.minor


class PRInsight(BaseModel):
    pr_number: int
    title: str
    description: str
    decision: str | None = None
    rationale: str | None = None
    date: datetime | None = None


class AnalysisResult(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    repo_url: str
    analyzed_at: datetime = Field(default_factory=datetime.now)
    module_map: list[Module] = Field(default_factory=list)
    dependency_graph: list[Dependency] = Field(default_factory=list)
    commit_timeline: list[CommitEvent] = Field(default_factory=list)
    pr_insights: list[PRInsight] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    total_files: int = 0
    total_loc: int = 0
