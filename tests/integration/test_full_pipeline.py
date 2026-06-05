from pathlib import Path
from unittest.mock import MagicMock, patch
from redator_tecnico.models.repo import RepositoryConnection
from redator_tecnico.analyzers.structure import StructureAnalyzer
from redator_tecnico.generators.llm_client import GroqClient
from redator_tecnico.generators.orchestrator import DocOrchestrator


class TestFullPipeline:
    def test_analyze_and_generate(self, tmp_path):
        src = tmp_path / "project"
        src.mkdir()
        (src / "mod.py").write_text(
            '"""A sample module."""\n\n'
            "import os\n\n"
            "def greet(name: str) -> str:\n"
            '    """Return a greeting."""\n'
            '    return f"Hello, {name}"\n'
        )
        (src / "utils.py").write_text(
            '"""Utility functions."""\n\n'
            "from datetime import datetime\n\n"
            "def now() -> str:\n"
            '    return str(datetime.now())\n'
        )

        analyzer = StructureAnalyzer(src)
        analysis = analyzer.analyze()

        assert analysis.total_files == 2
        assert "python" in analysis.languages
        assert len(analysis.module_map) == 2

        mock_llm = MagicMock(spec=GroqClient)
        mock_llm.generate_documentation.return_value = "# Architecture\n\nGenerated overview."

        orchestrator = DocOrchestrator(mock_llm)
        doc = orchestrator.generate(analysis, "https://github.com/test/repo")

        assert doc.repo_url == "https://github.com/test/repo"
        assert len(doc.sections) == 2
        assert doc.sections[0].title == "Architecture Overview"
        assert doc.sections[1].title == "Module Reference"
        mock_llm.generate_documentation.assert_called_once()

    def test_pipeline_empty_repo_graceful(self, tmp_path):
        analyzer = StructureAnalyzer(tmp_path)
        analysis = analyzer.analyze()

        assert analysis.total_files == 0
        assert analysis.languages == []
        assert analysis.module_map == []
        assert analysis.dependency_graph == []

        mock_llm = MagicMock(spec=GroqClient)
        mock_llm.generate_documentation.return_value = "# No modules found."

        orchestrator = DocOrchestrator(mock_llm)
        doc = orchestrator.generate(analysis, "https://github.com/empty/repo")

        assert len(doc.sections) == 2
        assert doc.source_hash != ""
    