from unittest.mock import MagicMock, patch
from src.analyzers.pr_analyzer import PRAnalyzer
from src.connectors.github import GitHubConnector
from src.connectors.gitlab import GitLabConnector
from src.models.repo import RepositoryConnection


class TestPRAnalyzer:
    def setup_method(self):
        self.gh_conn = RepositoryConnection(
            url="https://github.com/test/repo", provider="github"
        )
        self.gl_conn = RepositoryConnection(
            url="https://gitlab.com/test/repo", provider="gitlab"
        )

    def test_analyze_github_returns_pr_insights(self):
        connector = GitHubConnector(self.gh_conn)
        raw_prs = [
            {"number": 1, "title": "Add auth", "description": "Decision: Use JWT\nRationale: Stateless", "date": None},
            {"number": 2, "title": "Fix bug", "description": "Fixes login", "date": None},
        ]
        connector.fetch_prs = MagicMock(return_value=raw_prs)

        analyzer = PRAnalyzer(connector)
        insights = analyzer.analyze("fake-token")
        assert len(insights) == 2
        assert insights[0].pr_number == 1
        assert insights[0].title == "Add auth"
        assert insights[0].decision == "Use JWT"
        assert insights[0].rationale == "Stateless"

    def test_analyze_gitlab_returns_mr_insights(self):
        connector = GitLabConnector(self.gl_conn)
        raw_mrs = [
            {"number": 42, "title": "Refactor API", "description": "**Decision:** Use REST\n**Why:** Simpler", "date": None},
        ]
        connector.fetch_merge_requests = MagicMock(return_value=raw_mrs)

        analyzer = PRAnalyzer(connector)
        insights = analyzer.analyze("fake-token")
        assert len(insights) == 1
        assert insights[0].pr_number == 42
        assert insights[0].decision == "Use REST"
        assert insights[0].rationale == "Simpler"

    def test_analyze_empty_prs(self):
        connector = GitHubConnector(self.gh_conn)
        connector.fetch_prs = MagicMock(return_value=[])
        analyzer = PRAnalyzer(connector)
        insights = analyzer.analyze("fake-token")
        assert insights == []

    def test_extract_decision_no_markers(self):
        analyzer = PRAnalyzer(GitHubConnector(self.gh_conn))
        decision, rationale = analyzer._extract_decision("Just some description")
        assert decision is None
        assert rationale is None

    def test_extract_decision_with_markers(self):
        analyzer = PRAnalyzer(GitHubConnector(self.gh_conn))
        text = "Some text\nDecision: Use Postgres\nRationale: Already in stack\nMore text"
        decision, rationale = analyzer._extract_decision(text)
        assert decision == "Use Postgres"
        assert rationale == "Already in stack"
