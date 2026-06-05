from pathlib import Path
import git
import gitlab
from src.connectors.base import BaseConnector
from src.connectors.utils import retry, check_gitlab_rate_limit, warn_if_near_limit
from src.models.repo import RepositoryConnection


class GitLabConnector(BaseConnector):
    def __init__(self, connection: RepositoryConnection):
        super().__init__(connection)
        self._api: gitlab.Gitlab | None = None
        self._project_path = connection.url.rstrip("/").split("gitlab.com/")[-1]

    def _get_api(self, token: str) -> gitlab.Gitlab:
        if self._api is None:
            self._api = gitlab.Gitlab("https://gitlab.com", private_token=token)
        return self._api

    @retry(max_attempts=3, delay=1.0, backoff=2.0)
    def clone_repo(self, target_dir: Path, token: str) -> None:
        clone_url = f"https://oauth2:{token}@gitlab.com/{self._project_path}.git"
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
        return self._project_path

    def get_default_branch(self) -> str:
        return self.connection.branch

    @retry(max_attempts=3, delay=1.0, backoff=2.0)
    def fetch_merge_requests(self, token: str, state: str = "merged") -> list[dict]:
        api = self._get_api(token)
        remaining, limit, reset_time = check_gitlab_rate_limit(api)
        warn_if_near_limit(remaining, limit, reset_time, "GitLab")
        project = api.projects.get(self._project_path)
        mrs = project.mergerequests.list(state=state)
        results = []
        for mr in mrs:
            results.append({
                "number": mr.iid,
                "title": mr.title,
                "description": mr.description or "",
                "date": mr.merged_at or mr.created_at,
            })
        return results
