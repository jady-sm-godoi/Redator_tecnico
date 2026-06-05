from pathlib import Path
from unittest.mock import MagicMock, patch
from redator_tecnico.connectors.gitlab import GitLabConnector
from redator_tecnico.models.repo import RepositoryConnection


class TestGitLabConnector:
    def setup_method(self):
        self.conn = RepositoryConnection(
            url="https://gitlab.com/test-owner/test-project",
            provider="gitlab",
        )
        self.connector = GitLabConnector(self.conn)

    def test_get_repo_name(self):
        assert self.connector.get_repo_name() == "test-owner/test-project"

    def test_get_default_branch(self):
        assert self.connector.get_default_branch() == "main"

    def test_list_files_excludes_hidden(self, tmp_path):
        (tmp_path / "lib").mkdir()
        (tmp_path / "lib" / "main.rb").write_text("puts 'hello'")
        (tmp_path / ".gitkeep").write_text("")
        files = self.connector.list_files(tmp_path)
        assert Path("lib/main.rb") in files
        assert Path(".gitkeep") not in files
        assert len(files) == 1

    @patch("redator_tecnico.connectors.gitlab.git.Repo.clone_from")
    def test_clone_repo(self, mock_clone):
        self.connector.clone_repo(tmp_path := Path("/tmp/test-clone"), "fake-token")
        expected_url = "https://oauth2:fake-token@gitlab.com/test-owner/test-project.git"
        mock_clone.assert_called_once_with(expected_url, tmp_path, depth=1)

    @patch("redator_tecnico.connectors.gitlab.gitlab.Gitlab")
    def test_fetch_merge_requests(self, mock_gitlab_cls):
        mock_api = MagicMock()
        mock_gitlab_cls.return_value = mock_api
        mock_project = MagicMock()
        mock_api.projects.get.return_value = mock_project

        mock_mr = MagicMock()
        mock_mr.iid = 42
        mock_mr.title = "Add feature"
        mock_mr.description = "Description here"
        from datetime import datetime
        mock_mr.merged_at = datetime(2024, 6, 1)
        mock_mr.created_at = datetime(2024, 6, 1)
        mock_project.mergerequests.list.return_value = [mock_mr]

        mrs = self.connector.fetch_merge_requests("fake-token")
        assert len(mrs) == 1
        assert mrs[0]["title"] == "Add feature"
        assert mrs[0]["number"] == 42
