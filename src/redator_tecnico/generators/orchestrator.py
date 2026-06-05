from pathlib import Path
from datetime import datetime
from redator_tecnico.models.analysis import AnalysisResult, CommitEvent, PRInsight
from redator_tecnico.models.documentation import Documentation, DocSection, load_doc_metadata, save_doc_metadata


DOC_SECTION_PROMPT = """Based on the following source code analysis, generate a documentation section.

Repository languages: {languages}
Total files: {files}
Total lines of code: {loc}

Modules found:
{modules}

Dependencies:
{dependencies}

Generate a Markdown section describing the architecture and module structure."""

COMMIT_SECTION_PROMPT = """Based on the following git commit history, describe the evolution of this project:

{timeline}

Generate a Markdown section titled 'Change History' summarizing key developments."""

PR_SECTION_PROMPT = """Based on the following Pull Requests / Merge Requests, describe the architectural decisions made:

{insights}

Generate a Markdown section titled 'Architectural Decisions' summarizing the key decisions and rationale."""


class DocOrchestrator:
    def __init__(self, llm_client):
        self.llm = llm_client

    def generate(
        self,
        analysis: AnalysisResult,
        repo_url: str,
        include_history: bool = True,
        include_prs: bool = True,
    ) -> Documentation:
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

        if include_history and analysis.commit_timeline:
            timeline_section = self._generate_timeline(analysis.commit_timeline)
            sections.append(timeline_section)

        if include_prs and analysis.pr_insights:
            pr_section = self._generate_pr_section(analysis.pr_insights)
            sections.append(pr_section)

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

    def _generate_timeline(self, commits: list[CommitEvent]) -> DocSection:
        timeline = "\n".join(
            f"- `{c.hash}` {c.date.strftime('%Y-%m-%d')} | {c.author} | "
            f"[{c.significance.value}] {c.message[:80]}"
            for c in commits[:50]
        )
        prompt = COMMIT_SECTION_PROMPT.format(timeline=timeline or "(no commits)")
        content = self.llm.generate_documentation(prompt)
        return DocSection(
            title="Change History",
            level=1,
            content=content,
            source_modules=["git_history"],
        )

    def _generate_pr_section(self, insights: list[PRInsight]) -> DocSection:
        lines = []
        for pr in insights[:30]:
            lines.append(f"### PR #{pr.pr_number}: {pr.title}")
            if pr.decision:
                lines.append(f"- **Decision**: {pr.decision}")
            if pr.rationale:
                lines.append(f"- **Rationale**: {pr.rationale}")
            lines.append(f"- **Date**: {pr.date.strftime('%Y-%m-%d') if pr.date else 'N/A'}")
            lines.append("")
        table = "\n".join(lines) if lines else "(no PR insights)"

        prompt = PR_SECTION_PROMPT.format(insights=table)
        content = self.llm.generate_documentation(prompt)
        return DocSection(
            title="Architectural Decisions",
            level=1,
            content=content,
            source_modules=["pr_analyzer"],
        )

    def _compute_hash(self, analysis: AnalysisResult) -> str:
        raw = f"{analysis.total_files}:{analysis.total_loc}:{len(analysis.module_map)}"
        import hashlib
        return hashlib.sha256(raw.encode()).hexdigest()[:12]

    @staticmethod
    def _compute_static_hash(analysis: AnalysisResult) -> str:
        raw = f"{analysis.total_files}:{analysis.total_loc}:{len(analysis.module_map)}"
        import hashlib
        return hashlib.sha256(raw.encode()).hexdigest()[:12]

    @staticmethod
    def detect_static_stale(
        doc_dir: Path,
        current_module_hashes: dict[str, str],
        current_analysis: AnalysisResult,
    ) -> tuple[list[tuple[str, bool]], object | None]:
        meta = load_doc_metadata(doc_dir)
        if meta is None:
            return [], None

        stale_sections: list[tuple[str, bool]] = []
        overall_stale = DocOrchestrator._compute_static_hash(current_analysis) != meta.source_hash

        for sec_meta in meta.sections:
            source_set = set(sec_meta.source_modules)
            section_stale = overall_stale
            if not section_stale and meta.module_content_hashes:
                for mod in source_set:
                    current_hash = current_module_hashes.get(mod)
                    stored_hashes = meta.module_content_hashes
                    if stored_hashes.get(mod) != current_hash:
                        section_stale = True
                        break
            stale_sections.append((sec_meta.title, section_stale))

        return stale_sections, meta

    def update(
        self,
        analysis: AnalysisResult,
        doc_dir: Path,
        existing_doc: Documentation,
    ) -> Documentation:
        stale_sections, meta = DocOrchestrator.detect_static_stale(
            doc_dir,
            {},
            analysis,
        )

        new_sections: list[DocSection] = []
        if stale_sections:
            stale_map = dict(stale_sections)
            for section in existing_doc.sections:
                if stale_map.get(section.title, True):
                    title = section.title
                    if title == "Architecture Overview":
                        new_sections.append(self._generate_overview(analysis))
                    elif title == "Module Reference":
                        new_sections.append(DocSection(
                            title="Module Reference",
                            level=2,
                            content=self._build_module_table(analysis),
                            source_modules=[m.name for m in analysis.module_map],
                        ))
                    elif title == "Change History":
                        new_sections.append(self._generate_timeline(analysis.commit_timeline))
                    elif title == "Architectural Decisions":
                        new_sections.append(self._generate_pr_section(analysis.pr_insights))
                    else:
                        new_sections.append(section)
                else:
                    new_sections.append(section)
        else:
            new_sections = existing_doc.sections

        doc = Documentation(
            repo_url=existing_doc.repo_url,
            sections=new_sections,
            source_hash=self._compute_hash(analysis),
        )
        save_doc_metadata(doc, doc_dir)
        return doc
