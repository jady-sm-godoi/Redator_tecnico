---

description: "Task list for Auto Documentation Rebuild Agent implementation"

---

# Tasks: Auto Documentation Rebuild Agent

**Input**: Design documents from `specs/001-doc-rebuild-agent/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Test tasks included. Tests must be written FIRST and FAIL before implementation (TDD).

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no deps)
- **[Story]**: User story (US1, US2, US3)
- File paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependency setup, basic structure

- [X] T001 Initialize Python project with pyproject.toml and dependencies (agno, groq, PyGithub, python-gitlab, cryptography, typer, tree-sitter, gitpython)
- [X] T002 [P] Create directory structure: src/cli/, src/connectors/, src/analyzers/, src/generators/, src/models/, src/config/, tests/unit/, tests/integration/, tests/fixtures/
- [X] T003 [P] Configure pytest with pytest-vcr, pytest-mock in pyproject.toml
- [X] T004 [P] Create `src/__init__.py` and all subpackage `__init__.py` files

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 [P] Create RepositoryConnection model in src/models/repo.py
- [X] T006 [P] Create CredentialConfig model in src/models/repo.py
- [X] T007 [P] Create AnalysisResult model (Module, Dependency) in src/models/analysis.py
- [X] T008 [P] Create Documentation model (DocSection, ChangelogEntry) in src/models/documentation.py
- [X] T009 [P] Implement config management in src/config/settings.py (config file load/save, paths)
- [X] T010 Implement encrypted credential storage in src/config/crypto.py (Fernet encrypt/decrypt)
- [X] T011 [P] Setup CLI entry point structure in src/cli/main.py (typer app with placeholder commands)

### Tests for Foundational ⚠️

- [X] T012 [P] Unit test for config load/save in tests/unit/test_config.py (5 tests)
- [X] T013 [P] Unit test for credential encrypt/decrypt in tests/unit/test_crypto.py (4 tests)

**Checkpoint**: Foundation ready — user story implementation can begin

---

## Phase 3: User Story 1 - Repo Connection and Doc Generation (Priority: P1) 🎯 MVP

**Goal**: Engineer connects a client repo via CLI, agent analyzes source code and generates Markdown documentation covering architecture, modules, and data flow.

**Independent Test**: Provide a public GitHub/GitLab repo URL → run `doc-rebuild generate` → verify Markdown docs produced with module overview, architecture, and component relationships.

### Tests for User Story 1 ⚠️

- [X] T014 [P] [US1] Contract test for GitHub connector in tests/unit/test_github_connector.py
- [X] T015 [P] [US1] Contract test for GitLab connector in tests/unit/test_gitlab_connector.py
- [X] T016 [P] [US1] Unit test for structure analyzer in tests/unit/test_structure_analyzer.py
- [X] T017 [P] [US1] Unit test for LLM client in tests/unit/test_llm_client.py
- [X] T018 [US1] Integration test for full pipeline (init + generate) in tests/integration/test_full_pipeline.py

### Implementation for User Story 1

- [X] T019 [P] [US1] Implement base connector interface in src/connectors/base.py
- [X] T020 [P] [US1] Implement GitHub connector in src/connectors/github.py (clone/fetch repo, list files)
- [X] T021 [P] [US1] Implement GitLab connector in src/connectors/gitlab.py (clone/fetch repo, list files)
- [X] T022 [US1] Implement code structure analyzer in src/analyzers/structure.py (tree-sitter module detection per language)
- [X] T023 [P] [US1] Implement Groq LLM client in src/generators/llm_client.py
- [X] T024 [US1] Implement doc generation orchestrator in src/generators/orchestrator.py (Agno agent: structure → LLM → Markdown output)
- [X] T025 [US1] Wire CLI `init` command in src/cli/main.py (repo URL, branch, credential prompt)
- [X] T026 [US1] Wire CLI `generate` command in src/cli/main.py (repo URL, output dir)
- [X] T027 [US1] Wire CLI `list` command in src/cli/main.py (show configured repos)
- [X] T028 [US1] Add progress feedback (stderr) during analysis and generation phases per FR-009
- [X] T029 [US1] Handle empty/unsupported repos gracefully per FR-008

**Checkpoint**: User Story 1 fully functional — docs generated from public repos

---

## Phase 4: User Story 2 - Contextual Analysis via Git History and PRs (Priority: P2)

**Goal**: Team lead gets docs enriched with architectural decisions from commit history and PR descriptions.

**Independent Test**: Provide repo with 10+ PRs and descriptive commits → run `doc-rebuild generate` → verify output includes decision rationale section and change timeline.

### Tests for User Story 2 ⚠️

- [X] T030 [P] [US2] Unit test for git history analyzer in tests/unit/test_git_history.py
- [X] T031 [P] [US2] Unit test for PR analyzer in tests/unit/test_pr_analyzer.py
- [X] T032 [US2] Integration test for enriched generation in tests/integration/test_enriched_generation.py

### Implementation for User Story 2

- [X] T033 [P] [US2] Create CommitEvent model in src/models/analysis.py
- [X] T034 [P] [US2] Create PRInsight model in src/models/analysis.py
- [X] T035 [US2] Implement git history analyzer in src/analyzers/git_history.py (gitpython: commit iteration, diff analysis, significance classification)
- [X] T036 [US2] Implement PR analyzer in src/analyzers/pr_analyzer.py (PyGithub/python-gitlab: PR description, discussion, decision extraction)
- [X] T037 [US2] Extend doc generation orchestrator to incorporate commit timeline and PR insights into output
- [X] T038 [US2] Update CLI `generate` with `--include-prs` and `--include-history` flags (default: true)

**Checkpoint**: User Story 1 AND 2 both functional independently

---

## Phase 5: User Story 3 - Documentation Updates on Code Changes (Priority: P3)

**Goal**: Dev team keeps docs in sync — agent detects code changes and regenerates affected sections.

**Independent Test**: Generate docs for a repo → add new module → run `doc-rebuild check` → verify stale detection → run `doc-rebuild update` → verify only new sections regenerated.

### Tests for User Story 3 ⚠️

- [X] T039 [P] [US3] Unit test for change detection in tests/unit/test_change_detection.py
- [X] T040 [P] [US3] Unit test for incremental regeneration in tests/unit/test_incremental_update.py
- [X] T041 [US3] Integration test for check + update flow in tests/integration/test_staleness_flow.py

### Implementation for User Story 3

- [X] T042 [US3] Store source_hash in generated doc metadata (_meta.json) for change detection
- [X] T043 [US3] Implement change detection in src/analyzers/structure.py (compare current tree hash vs stored hash)
- [X] T044 [US3] Wire CLI `check` command in src/cli/main.py (compare hashes, report stale sections)
- [X] T045 [US3] Implement incremental doc regeneration per FR-010 (regenerate only stale sections)
- [X] T046 [US3] Wire CLI `update` command in src/cli/main.py (incremental regeneration)
- [X] T047 [US3] Wire CLI `config` command in src/cli/main.py (view/edit config)
- [X] T048 [US3] Handle edge cases: first-time run with no hash, corrupted _meta.json, removed modules

**Checkpoint**: All user stories independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple stories

- [X] T049 [P] Add rate-limit handling for GitHub (5000/hr) and GitLab (2000/hr) API calls
- [X] T050 [P] Add retry logic for transient API failures in connectors
- [X] T051 [P] Add --json output format for CLI commands (machine-readable)
- [X] T052 [P] Add `--version` flag to CLI
- [X] T053 [P] Run quickstart.md validation (verify all CLI commands work)
- [X] T054 Add user-friendly CLI help text for all commands
- [X] T055 Add proper logging throughout (stdout for output, stderr for status)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational — no dependency on other stories
- **US2 (Phase 4)**: Depends on Foundational + US1 (US1 connectors needed for repo access)
- **US3 (Phase 5)**: Depends on Foundational + US1 + US2 (US1 generation, US2 git history for hash detection)
- **Polish (Phase 6)**: Depends on all desired stories complete

### User Story Dependencies

- **US1 (P1)**: Start after Foundational — no deps on other stories
- **US2 (P2)**: Start after Foundational + US1 connectors — independently testable with US1's connector output
- **US3 (P3)**: Start after Foundational + US1 + US2 — relies on hash tracking from initial generation

### Within Each User Story

- Tests written FIRST, verify FAIL before any implementation
- Models before services
- Services before CLI integration
- Core implementation before edge cases
- Tests must PASS before story considered complete
- Story complete before moving to next priority

### Parallel Opportunities

- T002, T003, T004 (Setup) can run in parallel
- T005, T006, T007, T008, T009, T011 (Foundational) can run in parallel
- T012, T013 (Foundational tests) can run in parallel
- T014, T015, T016, T017 (US1 tests) can run in parallel
- T019, T020, T021, T023 (US1 connectors + LLM) can run in parallel
- T030, T031 (US2 tests) can run in parallel
- T033, T034 (US2 models) can run in parallel
- T039, T040 (US3 tests) can run in parallel
- T049, T050, T051, T052, T053 (Polish) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch tests in parallel (write first, expect FAIL):
Task: "Contract test for GitHub connector in tests/unit/test_github_connector.py"
Task: "Contract test for GitLab connector in tests/unit/test_gitlab_connector.py"
Task: "Unit test for structure analyzer in tests/unit/test_structure_analyzer.py"
Task: "Unit test for LLM client in tests/unit/test_llm_client.py"

# Launch connectors + LLM client in parallel (make tests pass):
Task: "Implement base connector interface in src/connectors/base.py"
Task: "Implement GitHub connector in src/connectors/github.py"
Task: "Implement GitLab connector in src/connectors/gitlab.py"
Task: "Implement Groq LLM client in src/generators/llm_client.py"

# Then block on structure analyzer (uses connectors):
Task: "Implement code structure analyzer in src/analyzers/structure.py"

# Then orchestrator (uses structure + LLM), CLI wiring:
Task: "Implement doc generation orchestrator in src/generators/orchestrator.py"
Task: "Wire CLI init/generate/list commands in src/cli/main.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: `doc-rebuild generate` on a public repo → Markdown docs produced
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 → Test independently → Deploy/Demo (MVP!)
3. Add US2 → Test independently → Deploy/Demo
4. Add US3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story
- Each user story independently completable and testable
- TDD: tests written FIRST, verify FAIL, then implement until PASS
- Tests within each phase marked [P] can run in parallel
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
