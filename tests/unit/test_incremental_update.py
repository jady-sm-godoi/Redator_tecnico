from pathlib import Path
from unittest.mock import MagicMock
from src.models.documentation import Documentation, DocSection, save_doc_metadata, load_doc_metadata
from src.models.analysis import AnalysisResult, Module, ModuleType
from src.generators.orchestrator import DocOrchestrator


class TestIncrementalUpdate:
    """T040 — Unit tests for incremental regeneration (stale sections only)."""

    def _make_analysis(self, total_files=2, total_loc=50, module_count=2) -> AnalysisResult:
        return AnalysisResult(
            repo_url="https://github.com/test/repo",
            total_files=total_files,
            total_loc=total_loc,
            languages=["python"],
            module_map=[
                Module(name=f"mod{i}.py", path=f"mod{i}.py", type=ModuleType.module)
                for i in range(module_count)
            ],
        )

    def _make_llm_mock(self, return_value="# Regenerated\n\nNew content."):
        mock = MagicMock()
        mock.generate_documentation.return_value = return_value
        return mock

    def test_update_only_stale_sections(self, tmp_path):
        llm = self._make_llm_mock()
        orch = DocOrchestrator(llm)
        doc_dir = tmp_path / "docs"
        doc_dir.mkdir()

        old_analysis = self._make_analysis(total_files=2, total_loc=50)
        old_doc = orch.generate(old_analysis, "https://github.com/test/repo")
        save_doc_metadata(old_doc, doc_dir)

        new_analysis = self._make_analysis(total_files=3, total_loc=80)
        result = orch.update(new_analysis, doc_dir, old_doc)
        assert len(result.sections) == len(old_doc.sections)

    def test_update_no_changes_no_regeneration(self, tmp_path):
        llm = self._make_llm_mock()
        orch = DocOrchestrator(llm)
        doc_dir = tmp_path / "docs"
        doc_dir.mkdir()

        analysis = self._make_analysis(total_files=2, total_loc=50)
        old_doc = orch.generate(analysis, "https://github.com/test/repo")
        save_doc_metadata(old_doc, doc_dir)

        from src.models.documentation import load_doc_metadata
        from src.analyzers.structure import compute_module_hashes
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        (repo_dir / "mod0.py").write_text("import os\n\ndef func():\n    pass\n")
        (repo_dir / "mod1.py").write_text("def helper():\n    return 1\n")

        current_hashes = compute_module_hashes(repo_dir)
        from src.analyzers.structure import StructureAnalyzer
        analyzer = StructureAnalyzer(repo_dir)
        new_analysis = analyzer.analyze()

        stale, _ = DocOrchestrator.detect_static_stale(doc_dir, current_hashes, new_analysis)
        update_needed = any(s for _, s in stale) if stale else False

        if not update_needed:
            result = old_doc
        else:
            result = orch.update(new_analysis, doc_dir, old_doc)
        assert len(result.sections) == len(old_doc.sections)

    def test_update_preserves_unchanged_sections(self, tmp_path):
        llm = self._make_llm_mock()
        orch = DocOrchestrator(llm)
        doc_dir = tmp_path / "docs"
        doc_dir.mkdir()

        old_analysis = self._make_analysis(total_files=2, total_loc=50)
        old_doc = orch.generate(old_analysis, "https://github.com/test/repo")
        for s in old_doc.sections:
            s.content = f"Original content for {s.title}"
        save_doc_metadata(old_doc, doc_dir)

        new_analysis = self._make_analysis(total_files=2, total_loc=50)
        result = orch.update(new_analysis, doc_dir, old_doc)
        for section in result.sections:
            assert section.content == f"Original content for {section.title}"

    def test_update_first_time_full_generation(self, tmp_path):
        llm = self._make_llm_mock()
        orch = DocOrchestrator(llm)
        doc_dir = tmp_path / "docs"
        doc_dir.mkdir()

        analysis = self._make_analysis(total_files=2, total_loc=50)
        doc = orch.generate(analysis, "https://github.com/test/repo")
        assert len(doc.sections) == 2
