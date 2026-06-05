from pathlib import Path
from unittest.mock import MagicMock, patch
from datetime import datetime
from src.models.repo import RepositoryConnection
from src.models.analysis import AnalysisResult, CommitEvent, PRInsight, Significance
from src.analyzers.structure import StructureAnalyzer
from src.generators.llm_client import GroqClient
from src.generators.orchestrator import DocOrchestrator


class TestEnrichedGeneration:
    def test_generate_with_commits_and_prs(self, tmp_path):
        src = tmp_path / "project"
        src.mkdir()
        (src / "app.py").write_text("import os\nprint('hello')\n")

        analyzer = StructureAnalyzer(src)
        analysis = analyzer.analyze()

        analysis.commit_timeline = [
            CommitEvent(hash="abc12345", author="dev1", date=datetime(2024, 1, 1),
                        message="feat: add login", files_changed=["app.py"],
                        significance=Significance.minor),
            CommitEvent(hash="def67890", author="dev2", date=datetime(2024, 2, 1),
                        message="BREAKING: redesign API", files_changed=["app.py"],
                        significance=Significance.major),
        ]
        analysis.pr_insights = [
            PRInsight(pr_number=1, title="Add auth", description="",
                      decision="Use JWT", rationale="Stateless", date=datetime(2024, 1, 15)),
        ]

        mock_llm = MagicMock(spec=GroqClient)
        mock_llm.generate_documentation.return_value = "# Generated content"

        orchestrator = DocOrchestrator(mock_llm)
        doc = orchestrator.generate(analysis, "https://github.com/test/repo",
                                    include_history=True, include_prs=True)

        assert len(doc.sections) == 4
        titles = [s.title for s in doc.sections]
        assert "Architecture Overview" in titles
        assert "Module Reference" in titles
        assert "Change History" in titles
        assert "Architectural Decisions" in titles

    def test_generate_without_history_or_prs(self, tmp_path):
        (tmp_path / "main.py").write_text("x = 1\n")

        analyzer = StructureAnalyzer(tmp_path)
        analysis = analyzer.analyze()
        analysis.commit_timeline = [CommitEvent(hash="a1", author="dev", date=datetime(2024, 1, 1),
                                                message="init", significance=Significance.minor)]
        analysis.pr_insights = [PRInsight(pr_number=1, title="PR1", description="", date=datetime(2024, 1, 1))]

        mock_llm = MagicMock(spec=GroqClient)
        mock_llm.generate_documentation.return_value = "# Content"

        orchestrator = DocOrchestrator(mock_llm)
        doc = orchestrator.generate(analysis, "https://github.com/test/repo",
                                    include_history=False, include_prs=False)

        titles = [s.title for s in doc.sections]
        assert "Change History" not in titles
        assert "Architectural Decisions" not in titles
        assert len(doc.sections) == 2

    def test_generate_empty_timeline_no_section(self, tmp_path):
        (tmp_path / "main.py").write_text("x = 1\n")

        analyzer = StructureAnalyzer(tmp_path)
        analysis = analyzer.analyze()

        mock_llm = MagicMock(spec=GroqClient)
        mock_llm.generate_documentation.return_value = "# Content"

        orchestrator = DocOrchestrator(mock_llm)
        doc = orchestrator.generate(analysis, "https://github.com/test/repo",
                                    include_history=True, include_prs=True)

        titles = [s.title for s in doc.sections]
        assert "Change History" not in titles
        assert "Architectural Decisions" not in titles
        assert len(doc.sections) == 2
