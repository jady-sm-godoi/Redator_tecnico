from pathlib import Path
from unittest.mock import MagicMock, patch
from redator_tecnico.connectors.github import GitHubConnector
from redator_tecnico.models.repo import RepositoryConnection


class TestGitHubConnector:
    def setup_method(self):
        self.conn = RepositoryConnection(
            url="https://github.com/test-owner/test-repo",
            provider="github",
        )
        self.connector = GitHubConnector(self.conn)

    def test_get_repo_name(self):
        assert self.connector.get_repo_name() == "test-owner/test-repo"

    def test_get_default_branch(self):
        assert self.connector.get_default_branch() == "main"

    def test_list_files_excludes_hidden(self, tmp_path):
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "app.py").write_text("print('hello')")
        (tmp_path / ".env").write_text("SECRET=1")
        (tmp_path / ".hidden" / "file.txt").mkdir(parents=True)
        (tmp_path / ".hidden" / "file.txt" / "x").write_text("ignored")

        files = self.connector.list_files(tmp_path)
        assert Path("src/app.py") in files
        assert Path(".env") not in files
        assert len(files) == 1

    @patch("redator_tecnico.connectors.github.git.Repo.clone_from")
    def test_clone_repo(self, mock_clone):
        self.connector.clone_repo(tmp_path := Path("/tmp/test-clone"), "fake-token")
        expected_url = "https://x-access-token:fake-token@github.com/test-owner/test-repo.git"
        mock_clone.assert_called_once_with(expected_url, tmp_path, depth=1)

    @patch("redator_tecnico.connectors.github.Github")
    def test_fetch_prs(self, mock_github):
        mock_api = MagicMock()
        mock_github.return_value = mock_api
        mock_repo = MagicMock()
        mock_api.get_repo.return_value = mock_repo

        mock_pr = MagicMock()
        mock_pr.number = 1
        mock_pr.title = "Fix bug"
        mock_pr.body = "Fixes the bug"
        from datetime import datetime
        mock_pr.merged_at = datetime(2024, 1, 1)
        mock_pr.created_at = datetime(2024, 1, 1)
        mock_repo.get_pulls.return_value = [mock_pr]

        prs = self.connector.fetch_prs("fake-token")
        assert len(prs) == 1
        assert prs[0]["title"] == "Fix bug"
        assert prs[0]["number"] == 1
