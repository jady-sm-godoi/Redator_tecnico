from pathlib import Path
import git
from github import Github
from src.connectors.base import BaseConnector
from src.models.repo import RepositoryConnection


class GitHubConnector(BaseConnector):
    def __init__(self, connection: RepositoryConnection):
        super().__init__(connection)
        self._api: Github | None = None
        self._repo_name = connection.url.rstrip("/").split("github.com/")[-1]

    def _get_api(self, token: str) -> Github:
        if self._api is None:
            self._api = Github(token)
        return self._api

    def clone_repo(self, target_dir: Path, token: str) -> None:
        clone_url = f"https://x-access-token:{token}@github.com/{self._repo_name}.git"
        git.Repo.clone_from(clone_url, target_dir, depth=1)

    def list_files(self, repo_dir: Path) -> list[Path]:
        files: list[Path] = []
        for path in repo_dir.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(repo_dir)
            if any(part.startswith(".") for part in rel.parts):
                continue
            files.append(rel)
        return sorted(files)

    def get_repo_name(self) -> str:
        return self._repo_name

    def get_default_branch(self) -> str:
        return self.connection.branch

    def fetch_prs(self, token: str, state: str = "merged") -> list[dict]:
        api = self._get_api(token)
        repo = api.get_repo(self._repo_name)
        prs = repo.get_pulls(state=state)
        results = []
        for pr in prs:
            results.append({
                "number": pr.number,
                "title": pr.title,
                "description": pr.body or "",
                "date": pr.merged_at or pr.created_at,
            })
        return results
