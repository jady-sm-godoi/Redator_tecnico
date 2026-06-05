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
# Exit 0 = up to date, 1 = stale sections
```

### 4. Update stale sections

```bash
doc-rebuild update https://github.com/owner/repo
```

## Configuration

Config stored at `~/.config/doc-rebuild/config.yml`. Team-sharable via `.doc-rebuild.yml` in repo root.
