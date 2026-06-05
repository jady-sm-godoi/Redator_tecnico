# CLI Command Contract

## Binary

`doc-rebuild` (installed via pip as `redator-tecnico`)

## Commands

### doc-rebuild init

Initialize configuration for a new repository.

```
doc-rebuild init <repo-url> [--branch <branch>] [--sub-path <path>]
```

Interactive prompt for credential entry (token stored encrypted).

### doc-rebuild generate

Analyze repository and generate documentation.

```
doc-rebuild generate <repo-url> [--output <dir>] [--force]
```

- `--output`: Target directory for generated docs (default: `./docs/`)
- `--force`: Regenerate everything, ignore cache

### doc-rebuild check

Check if documentation is stale (detect code changes).

```
doc-rebuild check <repo-url>
```

Exit code 0 = up to date, 1 = stale sections detected.

### doc-rebuild update

Regenerate only stale sections.

```
doc-rebuild update <repo-url>
```

### doc-rebuild list

List configured repositories.

```
doc-rebuild list
```

### doc-rebuild config

View/manage configuration.

```
doc-rebuild config [--show-keys]
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Generic error |
| 2 | Config/auth error |
| 3 | API rate limited |
| 4 | Repo not found / no access |

## Output Format

- Success: Markdown written to stdout or `--output` dir
- Progress: status messages to stderr (JSON-lines or human-readable)
