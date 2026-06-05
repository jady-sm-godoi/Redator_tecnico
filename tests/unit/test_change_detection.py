from pathlib import Path
from src.models.documentation import DocMetadata, SectionMetadata, save_doc_metadata
from src.models.analysis import Module, ModuleType, AnalysisResult
from src.generators.orchestrator import DocOrchestrator
from src.analyzers.structure import StructureAnalyzer, compute_module_hashes


class TestChangeDetection:
    """T039 — Unit tests for change detection between stored metadata and current code."""

    def test_detect_no_changes(self, tmp_path):
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        (repo_dir / "app.py").write_text("import os\n\ndef main():\n    pass\n")
        (repo_dir / "utils.py").write_text("def helper():\n    return 42\n")

        doc_dir = tmp_path / "docs"
        doc_dir.mkdir()

        analyzer = StructureAnalyzer(repo_dir)
        analysis = analyzer.analyze()
        hashes = compute_module_hashes(repo_dir)

        from src.models.documentation import Documentation, DocSection
        doc = Documentation(
            repo_url="https://github.com/test/repo",
            sections=[
                DocSection(title="Architecture Overview", level=1,
                           content="# Overview\n...", source_modules=["app.py", "utils.py"]),
            ],
            source_hash=DocOrchestrator._compute_static_hash(analysis),
        )
        save_doc_metadata(doc, doc_dir, module_content_hashes=hashes)

        current_hashes = compute_module_hashes(repo_dir)
        stale, _ = DocOrchestrator.detect_static_stale(doc_dir, current_hashes, analysis)
        assert not any(s for _, s in stale), "Expected no stale sections"

    def test_detect_new_module(self, tmp_path):
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        (repo_dir / "app.py").write_text("import os\n\ndef main():\n    pass\n")

        doc_dir = tmp_path / "docs"
        doc_dir.mkdir()

        analyzer = StructureAnalyzer(repo_dir)
        old_analysis = analyzer.analyze()
        old_hashes = compute_module_hashes(repo_dir)

        from src.models.documentation import Documentation, DocSection
        doc = Documentation(
            repo_url="https://github.com/test/repo",
            sections=[
                DocSection(title="Architecture Overview", level=1,
                           content="# Overview\n...", source_modules=["app.py"]),
            ],
            source_hash=DocOrchestrator._compute_static_hash(old_analysis),
        )
        save_doc_metadata(doc, doc_dir, module_content_hashes=old_hashes)

        (repo_dir / "utils.py").write_text("def helper():\n    return 42\n")

        current_hashes = compute_module_hashes(repo_dir)
        analyzer2 = StructureAnalyzer(repo_dir)
        new_analysis = analyzer2.analyze()
        stale, _ = DocOrchestrator.detect_static_stale(doc_dir, current_hashes, new_analysis)
        assert len(stale) > 0

    def test_detect_modified_module(self, tmp_path):
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        (repo_dir / "app.py").write_text("import os\n\ndef main():\n    pass\n")

        doc_dir = tmp_path / "docs"
        doc_dir.mkdir()

        analyzer = StructureAnalyzer(repo_dir)
        old_analysis = analyzer.analyze()
        old_hashes = compute_module_hashes(repo_dir)

        from src.models.documentation import Documentation, DocSection
        doc = Documentation(
            repo_url="https://github.com/test/repo",
            sections=[
                DocSection(title="Architecture Overview", level=1,
                           content="# Overview\n...", source_modules=["app.py"]),
            ],
            source_hash=DocOrchestrator._compute_static_hash(old_analysis),
        )
        save_doc_metadata(doc, doc_dir, module_content_hashes=old_hashes)

        (repo_dir / "app.py").write_text("import json\nimport os\n\ndef main():\n    return json.dumps(dict())\n")

        current_hashes = compute_module_hashes(repo_dir)
        analyzer2 = StructureAnalyzer(repo_dir)
        new_analysis = analyzer2.analyze()
        stale, _ = DocOrchestrator.detect_static_stale(doc_dir, current_hashes, new_analysis)
        assert len(stale) > 0

    def test_detect_removed_module(self, tmp_path):
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        (repo_dir / "app.py").write_text("import os\n\ndef main():\n    pass\n")
        (repo_dir / "utils.py").write_text("def helper():\n    return 42\n")

        doc_dir = tmp_path / "docs"
        doc_dir.mkdir()

        analyzer = StructureAnalyzer(repo_dir)
        old_analysis = analyzer.analyze()
        old_hashes = compute_module_hashes(repo_dir)

        from src.models.documentation import Documentation, DocSection
        doc = Documentation(
            repo_url="https://github.com/test/repo",
            sections=[
                DocSection(title="Architecture Overview", level=1,
                           content="# Overview\n...", source_modules=["app.py", "utils.py"]),
            ],
            source_hash=DocOrchestrator._compute_static_hash(old_analysis),
        )
        save_doc_metadata(doc, doc_dir, module_content_hashes=old_hashes)

        (repo_dir / "utils.py").unlink()

        current_hashes = compute_module_hashes(repo_dir)
        analyzer2 = StructureAnalyzer(repo_dir)
        new_analysis = analyzer2.analyze()
        stale, _ = DocOrchestrator.detect_static_stale(doc_dir, current_hashes, new_analysis)
        assert len(stale) > 0

    def test_first_run_no_meta_returns_empty(self, tmp_path):
        doc_dir = tmp_path / "docs"
        doc_dir.mkdir()
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        (repo_dir / "app.py").write_text("import os\n\ndef main():\n    pass\n")

        current_hashes = compute_module_hashes(repo_dir)
        analyzer = StructureAnalyzer(repo_dir)
        analysis = analyzer.analyze()
        stale, meta = DocOrchestrator.detect_static_stale(doc_dir, current_hashes, analysis)
        assert stale == []
        assert meta is None

    def test_corrupted_meta_returns_empty(self, tmp_path):
        doc_dir = tmp_path / "docs"
        doc_dir.mkdir()
        (doc_dir / "_meta.json").write_text("{{invalid json!!")
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        (repo_dir / "app.py").write_text("import os\n\ndef main():\n    pass\n")

        current_hashes = compute_module_hashes(repo_dir)
        analyzer = StructureAnalyzer(repo_dir)
        analysis = analyzer.analyze()
        stale, meta = DocOrchestrator.detect_static_stale(doc_dir, current_hashes, analysis)
        assert stale == []
        assert meta is None
