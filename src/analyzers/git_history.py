from pathlib import Path
from datetime import datetime
import git
from src.models.analysis import CommitEvent, Significance


class GitHistoryAnalyzer:
    def __init__(self, repo_dir: Path):
        self.repo_dir = repo_dir
        self.repo = git.Repo(repo_dir)

    def analyze(self, max_depth: int = 1000) -> list[CommitEvent]:
        commits: list[CommitEvent] = []
        try:
            head = self.repo.head.commit
        except (ValueError, Exception):
            return commits
        for i, commit in enumerate(self.repo.iter_commits()):
            if i >= max_depth:
                break
            files_changed = list(
                {item.b_path for item in commit.diff(commit.parents[0]) if item.b_path}
                if commit.parents
                else {item.b_path for item in commit.diff(None) if item.b_path}
            )
            commits.append(
                CommitEvent(
                    hash=commit.hexsha[:8],
                    author=str(commit.author),
                    date=datetime.fromtimestamp(commit.authored_date),
                    message=commit.message.strip(),
                    files_changed=sorted(files_changed),
                    significance=self._classify(commit.message),
                )
            )
        return commits

    def _classify(self, message: str) -> Significance:
        msg_lower = message.lower()
        if any(w in msg_lower for w in ["breaking", "major", "redesign", "rewrite"]):
            return Significance.major
        if any(w in msg_lower for w in ["refactor", "restructure", "reorganize"]):
            return Significance.refactor
        if any(w in msg_lower for w in ["fix", "bug", "hotfix", "patch"]):
            return Significance.fix
        if any(w in msg_lower for w in ["docs", "documentation", "readme"]):
            return Significance.docs
        return Significance.minor
