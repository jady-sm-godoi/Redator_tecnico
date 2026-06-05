from pathlib import Path
from datetime import datetime
from src.models.analysis import AnalysisResult
from src.models.documentation import Documentation, DocSection


DOC_SECTION_PROMPT = """Based on the following source code analysis, generate a documentation section.

Repository languages: {languages}
Total files: {files}
Total lines of code: {loc}

Modules found:
{modules}

Dependencies:
{dependencies}

Generate a Markdown section describing the architecture and module structure."""


class DocOrchestrator:
    def __init__(self, llm_client):
        self.llm = llm_client

    def generate(self, analysis: AnalysisResult, repo_url: str) -> Documentation:
        sections: list[DocSection] = []

        overview_section = self._generate_overview(analysis)
        sections.append(overview_section)

        modules_section = DocSection(
            title="Module Reference",
            level=2,
            content=self._build_module_table(analysis),
            source_modules=[m.name for m in analysis.module_map],
        )
        sections.append(modules_section)

        doc = Documentation(
            repo_url=repo_url,
            sections=sections,
            source_hash=self._compute_hash(analysis),
        )
        return doc

    def _generate_overview(self, analysis: AnalysisResult) -> DocSection:
        modules_list = "\n".join(f"- `{m.name}` ({m.type.value})" for m in analysis.module_map[:20])
        deps_list = "\n".join(
            f"- `{d.source}` → `{d.target}`" for d in analysis.dependency_graph[:20]
        )

        prompt = DOC_SECTION_PROMPT.format(
            languages=", ".join(analysis.languages),
            files=analysis.total_files,
            loc=analysis.total_loc,
            modules=modules_list or "(none)",
            dependencies=deps_list or "(none)",
        )
        content = self.llm.generate_documentation(prompt)

        return DocSection(
            title="Architecture Overview",
            level=1,
            content=content,
            source_modules=[m.name for m in analysis.module_map],
        )

    def _build_module_table(self, analysis: AnalysisResult) -> str:
        lines = ["| Module | Type | Lines |", "|--------|------|-------|"]
        for m in analysis.module_map[:50]:
            lines.append(f"| `{m.name}` | {m.type.value} | - |")
        return "\n".join(lines)

    def _compute_hash(self, analysis: AnalysisResult) -> str:
        raw = f"{analysis.total_files}:{analysis.total_loc}:{len(analysis.module_map)}"
        import hashlib
        return hashlib.sha256(raw.encode()).hexdigest()[:12]
