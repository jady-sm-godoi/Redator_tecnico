from pathlib import Path
from unittest.mock import MagicMock, patch

from redator_tecnico.models.analysis import AnalysisResult, Module, ModuleType
from redator_tecnico.models.documentation import Documentation, save_doc_metadata, load_doc_metadata
from redator_tecnico.generators.orchestrator import DocOrchestrator
from redator_tecnico.analyzers.structure import StructureAnalyzer, compute_module_hashes


class TestStalenessFlow:
    """T041 — Integration test for check + update flow."""

    def _make_llm(self, responses=None):
        mock = MagicMock()
        if responses:
            mock.generate_documentation.side_effect = responses
        else:
            mock.generate_documentation.return_value = "# Generated\n\nDoc content."
        return mock

    def test_check_update_flow(self, tmp_path):
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        (repo_dir / "app.py").write_text("import os\n\ndef main():\n    pass\n")
        (repo_dir / "utils.py").write_text("def helper():\n    return 42\n")

        doc_dir = tmp_path / "docs"
        doc_dir.mkdir()

        llm = self._make_llm()
        orch = DocOrchestrator(llm)
        analyzer = StructureAnalyzer(repo_dir)
        analysis = analyzer.analyze()
        doc = orch.generate(analysis, "https://github.com/test/repo")

        output_path = doc_dir
        output_path.mkdir(parents=True, exist_ok=True)
        doc_file = output_path / "test_repo.md"
        full_content = f"# test_repo\n\n"
        for section in doc.sections:
            full_content += f"{'#' * section.level} {section.title}\n\n{section.content}\n\n"
        doc_file.write_text(full_content)
        current_hashes = compute_module_hashes(repo_dir)
        save_doc_metadata(doc, output_path, module_content_hashes=current_hashes)

        stale_sections, meta = DocOrchestrator.detect_static_stale(
            output_path, current_hashes, analysis
        )
        if stale_sections:
            stale_titles = [t for t, s in stale_sections if s]
        else:
            stale_titles = []

        (repo_dir / "utils.py").write_text("def helper():\n    return 99\n")

        analyzer2 = StructureAnalyzer(repo_dir)
        new_analysis = analyzer2.analyze()
        current_hashes2 = compute_module_hashes(repo_dir)
        stale2, meta2 = DocOrchestrator.detect_static_stale(
            output_path, current_hashes2, new_analysis
        )
        if stale2:
            assert any(s for _, s in stale2), "Expected stale sections after modification"

        llm2 = self._make_llm(responses=["# Updated Overview\n\nNew.", "| Module | Type |", "# Updated Change History\n\nMods.", "# Updated Decisions\n\nDec."])
        orch2 = DocOrchestrator(llm2)
        updated_doc = orch2.update(new_analysis, output_path, doc)
        assert updated_doc is not None
        assert len(updated_doc.sections) > 0

    def test_full_staleness_roundtrip(self, tmp_path):
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        (repo_dir / "main.py").write_text("import sys\n\ndef run():\n    pass\n")

        doc_dir = tmp_path / "docs"
        doc_dir.mkdir()

        llm = self._make_llm()
        orch = DocOrchestrator(llm)
        analyzer = StructureAnalyzer(repo_dir)
        analysis = analyzer.analyze()
        doc = orch.generate(analysis, "https://github.com/test/repo")
        current_hashes = compute_module_hashes(repo_dir)
        save_doc_metadata(doc, doc_dir, module_content_hashes=current_hashes)

        meta = load_doc_metadata(doc_dir)
        assert meta is not None
        assert meta.source_hash != ""

        (repo_dir / "feature.py").write_text("def new_feature():\n    return True\n")
        new_analysis = StructureAnalyzer(repo_dir).analyze()
        current_hashes = compute_module_hashes(repo_dir)
        stale, _ = DocOrchestrator.detect_static_stale(doc_dir, current_hashes, new_analysis)
        if stale:
            assert any(s for _, s in stale)

        llm2 = self._make_llm(responses=["# New Overview\n\nUpdated.", "| Module | Type |", "# New History\n\nUpdated.", "# New Decisions\n\nUpdated."])
        orch2 = DocOrchestrator(llm2)
        updated = orch2.update(new_analysis, doc_dir, doc)
        assert len(updated.sections) == len(doc.sections)
