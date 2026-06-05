# Implementation Plan: Auto Documentation Rebuild Agent

**Branch**: `001-doc-rebuild-agent` | **Date**: 2026-06-05 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-doc-rebuild-agent/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

CLI tool that connects to GitHub/GitLab repos, analyzes source code, git history, and PRs, then generates Markdown technical documentation using LLM (Groq). Single-user tool, team-sharable config, encrypted credential storage.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**: Agno (agent orchestration), Groq SDK (LLM inference), PyGithub (GitHub API), python-gitlab (GitLab API)

**Storage**: Local filesystem (encrypted per-repo config, Markdown doc output, analysis cache)

**Testing**: pytest with pytest-vcr (record/replay API calls), pytest-mock

**Target Platform**: Linux, macOS, Windows (CLI - cross-platform Python)

**Project Type**: CLI tool

**Performance Goals**: <5 min for 100K LOC repos (SC-001), sub-minute structural change detection (SC-006)

**Constraints**: GitHub/GitLab API rate limits (5000 req/hr GH, 2000 req/hr GL for free tier), encrypted credential storage at rest

**Scale/Scope**: Single repo per invocation; team-sharable via config file checked into repo or shared manually

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution is a template with placeholder values — no enforceable constraints defined. Gate: PASS.

## Project Structure

### Documentation (this feature)

```text
specs/001-doc-rebuild-agent/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── cli/                    # CLI entry points (argparse/typer)
│   ├── __init__.py
│   └── main.py
├── connectors/             # GitHub/GitLab API connectors
│   ├── __init__.py
│   ├── base.py
│   ├── github.py
│   └── gitlab.py
├── analyzers/              # Code analysis logic
│   ├── __init__.py
│   ├── structure.py        # Module/component detection
│   ├── git_history.py      # Commit history analysis
│   └── pr_analyzer.py      # PR description/discussion analysis
├── generators/             # Documentation generation
│   ├── __init__.py
│   ├── orchestrator.py     # Agno agent workflow
│   └── llm_client.py       # Groq API client
├── models/                 # Data models/pydantic
│   ├── __init__.py
│   ├── repo.py
│   ├── analysis.py
│   └── documentation.py
├── config/                 # Config & credential management
│   ├── __init__.py
│   ├── settings.py
│   └── crypto.py           # Encrypted credential storage
└── __init__.py

tests/
├── __init__.py
├── unit/
│   ├── test_connectors.py
│   ├── test_analyzers.py
│   └── test_generators.py
├── integration/
│   └── test_full_pipeline.py
└── fixtures/
    └── sample_repos/
```

**Structure Decision**: Single Python project with domain-based package layout (src/ package). CLI, connectors, analyzers, generators, models, and config each in their own subpackage. Tests mirror this structure.

## Complexity Tracking

No constitution violations to justify.
