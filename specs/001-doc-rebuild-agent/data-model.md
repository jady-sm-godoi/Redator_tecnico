# Data Model: Auto Documentation Rebuild Agent

## RepositoryConnection

Configuration for accessing a remote Git repository.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique connection identifier |
| url | string | Repository URL (https://github.com/owner/repo) |
| provider | enum | `github` or `gitlab` |
| branch | string | Target branch (default: main/master) |
| credentials_ref | string | Reference to encrypted credential key in config |
| sub_path | string? | Monorepo sub-path for targeted analysis |
| created_at | datetime | Connection creation timestamp |
| updated_at | datetime | Last connection modification |

## CredentialConfig

Encrypted token storage per repository.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique credential identifier |
| repo_url | string | Repository URL (key for lookup) |
| encrypted_token | bytes | Fernet-encrypted access token |
| token_type | enum | `pat` (personal access token), `oauth` |
| created_at | datetime | Credential creation timestamp |

## AnalysisResult

Output from repository analysis, consumed by documentation generator.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique analysis identifier |
| repo_url | string | Source repository URL |
| analyzed_at | datetime | Analysis completion timestamp |
| module_map | Module[] | List of detected modules/components |
| dependency_graph | Dependency[] | Module dependency relationships |
| commit_timeline | CommitEvent[] | Chronological significant changes |
| pr_insights | PRInsight[] | Key decisions extracted from PRs |
| languages | string[] | Detected programming languages |
| total_files | int | Count of analyzed source files |
| total_loc | int | Total lines of code |

### Module

| Field | Type | Description |
|-------|------|-------------|
| name | string | Module/component name |
| path | string | File path relative to repo root |
| type | enum | `package`, `module`, `class`, `function` |
| docstring | string? | Existing docstring if present |
| dependencies | string[] | Names of modules this module depends on |
| exported_symbols | string[] | Public API surface (classes, functions, constants) |

### Dependency

| Field | Type | Description |
|-------|------|-------------|
| source | string | Dependent module name |
| target | string | Dependency module name |
| type | enum | `import`, `inherit`, `compose`, `call` |
| is_external | bool | Is dependency an external library? |

### CommitEvent

| Field | Type | Description |
|-------|------|-------------|
| hash | string | Commit SHA |
| author | string | Commit author |
| date | datetime | Commit timestamp |
| message | string | Commit message |
| files_changed | string[] | Files modified in commit |
| significance | enum | `major`, `minor`, `refactor`, `fix`, `docs` |

### PRInsight

| Field | Type | Description |
|-------|------|-------------|
| pr_number | int | Pull request number |
| title | string | PR title |
| description | string | PR description body |
| decision | string? | Architectural decision extracted from PR |
| rationale | string? | Reasoning behind the decision |
| date | datetime | PR merge/close date |

## Documentation

Generated technical document output.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique document identifier |
| repo_url | string | Source repository URL |
| generated_at | datetime | Generation timestamp |
| format | string | Always `markdown` |
| sections | DocSection[] | Document sections |
| changelog | ChangelogEntry[] | Generation history for incremental updates |
| source_hash | string | Git tree hash at analysis time (for change detection) |

### DocSection

| Field | Type | Description |
|-------|------|-------------|
| title | string | Section heading |
| level | int | Heading level (1-6) |
| content | string | Markdown content |
| source_modules | string[] | Modules that informed this section |
| stale | bool | Flagged as potentially outdated |

### ChangelogEntry

| Field | Type | Description |
|-------|------|-------------|
| version | int | Generation version number |
| date | datetime | When generated |
| changed_sections | string[] | Sections that changed from previous version |
| trigger | string | What triggered regeneration |
