# Output Format Contract

## Generated Document Structure

All generated documentation is Markdown (.md). Each repo produces:

```
docs/
├── README.md              # Overview: repo purpose, tech stack, quick links
├── architecture.md        # Architecture overview, component diagram, data flow
├── modules/               # Per-module documentation
│   ├── module-name.md
│   └── ...
├── decisions.md           # Architectural Decision Records extracted from PRs
├── history.md             # Git history timeline and evolution patterns
└── _meta.json             # Metadata (generation timestamp, source hash, etc.)
```

## README.md Template

```markdown
# <repo-name>

> Auto-generated documentation — generated <date>

## Overview

<brief summary of repo purpose based on code analysis>

## Tech Stack

<detected languages, frameworks, key dependencies>

## Project Structure

<high-level directory tree>

## Quick Links

- [Architecture](architecture.md)
- [Module Documentation](modules/)
- [Design Decisions](decisions.md)
- [Change History](history.md)
```

## _meta.json Schema

```json
{
  "generated_at": "2026-06-05T12:00:00Z",
  "source_hash": "abc123...",
  "repo_url": "https://github.com/owner/repo",
  "version": 1,
  "sections": ["architecture", "modules", "decisions", "history"],
  "stale_sections": []
}
```

## Staleness Contract

When `doc-rebuild check` runs, it compares current `source_hash` against stored hash in `_meta.json`. If mismatch:
- Flag `stale_sections` in `_meta.json`
- `update` regenerates only flagged sections
- Each section in `_meta.json` maps to a source file hash for granular staleness detection
