from abc import ABC, abstractmethod
from pathlib import Path
from src.models.repo import RepositoryConnection


class BaseConnector(ABC):
    def __init__(self, connection: RepositoryConnection):
        self.connection = connection

    @abstractmethod
    def clone_repo(self, target_dir: Path, token: str) -> None:
        ...

    @abstractmethod
    def list_files(self, repo_dir: Path) -> list[Path]:
        ...

    @abstractmethod
    def get_repo_name(self) -> str:
        ...

    @abstractmethod
    def get_default_branch(self) -> str:
        ...
