from pathlib import Path
from src.analyzers.structure import StructureAnalyzer


class TestStructureAnalyzer:
    def test_analyze_python_module(self, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        mod = src / "math_ops.py"
        mod.write_text(
            "import os\n"
            "from sys import path\n\n\n"
            '"""Math operations module."""\n\n\n'
            "def add(a, b):\n"
            "    return a + b\n"
        )
        analyzer = StructureAnalyzer(tmp_path)
        result = analyzer.analyze()
        assert result.total_files == 1
        assert "python" in result.languages
        assert len(result.module_map) == 1
        assert result.module_map[0].name == "src/math_ops.py"

    def test_analyze_empty_directory(self, tmp_path):
        analyzer = StructureAnalyzer(tmp_path)
        result = analyzer.analyze()
        assert result.total_files == 0
        assert result.languages == []

    def test_analyze_ignores_hidden_files(self, tmp_path):
        (tmp_path / ".env").write_text("SECRET=1")
        (tmp_path / "app.py").write_text("print('hello')")
        (tmp_path / ".config" / "settings.yml").mkdir(parents=True)
        analyzer = StructureAnalyzer(tmp_path)
        result = analyzer.analyze()
        assert result.total_files == 1
        assert result.module_map[0].name == "app.py"

    def test_analyze_detects_dependencies(self, tmp_path):
        (tmp_path / "main.py").write_text(
            "import json\nfrom pathlib import Path\nimport os\n"
        )
        analyzer = StructureAnalyzer(tmp_path)
        result = analyzer.analyze()
        mod = result.module_map[0]
        assert "json" in mod.dependencies
        assert "pathlib" in mod.dependencies
        assert "os" in mod.dependencies

    def test_analyze_package_init(self, tmp_path):
        pkg_dir = tmp_path / "mypackage"
        pkg_dir.mkdir(parents=True)
        (pkg_dir / "__init__.py").write_text('"""My package."""\n')
        analyzer = StructureAnalyzer(tmp_path)
        result = analyzer.analyze()
        pkg = result.module_map[0]
        assert pkg.type.value == "package"
        assert pkg.path.endswith("__init__.py")

    def test_analyze_multiple_languages(self, tmp_path):
        (tmp_path / "script.py").write_text("x = 1")
        (tmp_path / "script.js").write_text("const x = 1;")
        (tmp_path / "script.go").write_text("package main\nfunc main() {}")
        analyzer = StructureAnalyzer(tmp_path)
        result = analyzer.analyze()
        assert result.total_files == 3
        assert "python" in result.languages
        assert "javascript" in result.languages
        assert "go" in result.languages

    def test_analyze_dependency_graph(self, tmp_path):
        (tmp_path / "utils.py").write_text("def helper(): pass\n")
        (tmp_path / "main.py").write_text("import utils\nfrom sys import path\n")
        analyzer = StructureAnalyzer(tmp_path)
        result = analyzer.analyze()
        assert len(result.dependency_graph) >= 2
        assert any(d.source == "main.py" and d.target == "utils" for d in result.dependency_graph)
        assert any(d.source == "main.py" and d.target == "sys" for d in result.dependency_graph)
