# Quickstart: Auto Documentation Rebuild Agent

## Prerequisites

- Python 3.12+
- GitHub or GitLab personal access token (read-only)

## Installation

```bash
pip install redator-tecnico
```

## Usage

### 1. Initialize a repository

```bash
doc-rebuild init https://github.com/owner/repo
# Prompts for token → stored encrypted
```

### 2. Generate documentation

```bash
doc-rebuild generate https://github.com/owner/repo --output ./docs
```

Output: Markdown files in `./docs/` with architecture overview, module docs, design decisions, and change history.

### 3. Check for staleness

```bash
doc-rebuild check https://github.com/owner/repo
```

Sections shown as `[STALE]` or `[FRESH]`. Use `--json` for machine-readable output.

```bash
doc-rebuild check https://github.com/owner/repo --json
```

### 4. Update stale sections

```bash
doc-rebuild update https://github.com/owner/repo
```

### 5. List repositories

```bash
doc-rebuild list
# or machine-readable:
doc-rebuild list --json
```

### 6. View configuration

```bash
doc-rebuild config-view
```

### 7. Version

```bash
doc-rebuild --version
```

## Configuration

Config stored at `~/.config/doc-rebuild/config.yml`. Team-sharable via `.doc-rebuild.yml` in repo root.
