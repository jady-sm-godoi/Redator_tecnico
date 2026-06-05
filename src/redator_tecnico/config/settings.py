from pathlib import Path
from typing import Optional
import yaml
from pydantic import BaseModel, Field


CONFIG_DIR = Path.home() / ".config" / "doc-rebuild"
CONFIG_FILE = CONFIG_DIR / "config.yml"


class RepoConfig(BaseModel):
    url: str
    branch: str = "main"
    provider: str = ""
    credentials_ref: str = ""
    sub_path: Optional[str] = None


class LLMConfig(BaseModel):
    model: str = "llama-3.3-70b-versatile"
    temperature: float = 0.3
    max_tokens: int = 8192


class GenerationConfig(BaseModel):
    output_dir: str = "./docs"
    include_prs: bool = True
    include_history: bool = True
    max_commit_depth: int = 1000
    llm: LLMConfig = Field(default_factory=LLMConfig)


class AppConfig(BaseModel):
    repositories: list[RepoConfig] = Field(default_factory=list)
    generation: GenerationConfig = Field(default_factory=GenerationConfig)


def _ensure_config_dir(config_dir: Path) -> Path:
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "credentials").mkdir(parents=True, exist_ok=True)
    return config_dir


def load_config(config_dir: Path | None = None) -> AppConfig:
    base = config_dir or CONFIG_DIR
    _ensure_config_dir(base)
    config_file = base / "config.yml"
    if not config_file.exists():
        return AppConfig()
    raw = config_file.read_text()
    data = yaml.safe_load(raw) or {}
    return AppConfig(**data)


def save_config(config: AppConfig, config_dir: Path | None = None) -> None:
    base = config_dir or CONFIG_DIR
    _ensure_config_dir(base)
    config_file = base / "config.yml"
    raw = yaml.dump(config.model_dump(), default_flow_style=False)
    config_file.write_text(raw)


def resolve_repo_config(repo_url: str, config_dir: Path | None = None) -> Optional[RepoConfig]:
    config = load_config(config_dir)
    for rc in config.repositories:
        if rc.url == repo_url:
            return rc
    return None
