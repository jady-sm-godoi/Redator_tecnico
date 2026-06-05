import hashlib
from pathlib import Path
from redator_tecnico.models.analysis import Module, ModuleType, Dependency, DepType, AnalysisResult


LANGUAGE_EXTENSIONS: dict[str, str] = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".jsx": "jsx",
    ".java": "java",
    ".rs": "rust",
    ".go": "go",
    ".rb": "ruby",
    ".php": "php",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".hpp": "cpp",
    ".cs": "c_sharp",
    ".swift": "swift",
    ".kt": "kotlin",
    ".r": "r",
}


class StructureAnalyzer:
    def __init__(self, repo_dir: Path):
        self.repo_dir = repo_dir

    def analyze(self) -> AnalysisResult:
        modules: list[Module] = []
        dependencies: list[Dependency] = []
        languages: set[str] = set()
        total_files = 0
        total_loc = 0

        for file_path in self.repo_dir.rglob("*"):
            if not file_path.is_file():
                continue
            if file_path.name.startswith("."):
                continue
            ext = file_path.suffix.lower()
            lang = LANGUAGE_EXTENSIONS.get(ext)
            if lang is None:
                continue

            languages.add(lang)
            total_files += 1
            content = file_path.read_text(errors="replace")
            total_loc += len(content.splitlines())

            rel = file_path.relative_to(self.repo_dir)
            module = Module(
                name=str(rel),
                path=str(rel),
                type=self._classify_module(rel),
                docstring=self._extract_docstring(content, ext),
                dependencies=self._extract_imports(content, ext),
            )
            modules.append(module)

            for dep_name in module.dependencies:
                dependencies.append(
                    Dependency(
                        source=module.name,
                        target=dep_name,
                        type=DepType.import_,
                        is_external=not any(m.name.startswith(dep_name.split(".")[0]) for m in modules),
                    )
                )

        return AnalysisResult(
            repo_url="",
            module_map=modules,
            dependency_graph=dependencies,
            languages=sorted(languages),
            total_files=total_files,
            total_loc=total_loc,
        )

    def _classify_module(self, rel_path: Path) -> ModuleType:
        if rel_path.name == "__init__.py":
            return ModuleType.package
        return ModuleType.module

    def _extract_docstring(self, content: str, ext: str) -> str | None:
        if ext == ".py":
            import ast
            try:
                tree = ast.parse(content)
                doc = ast.get_docstring(tree)
                return doc
            except SyntaxError:
                return None
        return None

    def _extract_imports(self, content: str, ext: str) -> list[str]:
        imports: list[str] = []
        if ext == ".py":
            import ast
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name.split(".")[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.append(node.module.split(".")[0])
            except SyntaxError:
                pass
        else:
            import re
            for pat in [
                r'^import\s+(\S+)',
                r'^from\s+(\S+)\s+import',
                r'require\([\'"](\S+?)[\'"]\)',
                r'import\s+[\w{}]+\s+from\s+[\'"](\S+?)[\'"]',
            ]:
                for m in re.finditer(pat, content, re.MULTILINE):
                    name = m.group(1).split("/")[0].split(".")[0]
                    imports.append(name)
        return imports


def compute_module_hashes(repo_dir: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for file_path in repo_dir.rglob("*"):
        if not file_path.is_file():
            continue
        if file_path.name.startswith("."):
            continue
        ext = file_path.suffix.lower()
        if ext not in LANGUAGE_EXTENSIONS:
            continue
        rel = str(file_path.relative_to(repo_dir))
        content = file_path.read_bytes()
        hashes[rel] = hashlib.sha256(content).hexdigest()[:12]
    return hashes
