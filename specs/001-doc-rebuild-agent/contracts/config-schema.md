# Configuration Contract

## Config File Location

- User-level: `~/.config/doc-rebuild/config.yml`
- Repo-level: `.doc-rebuild.yml` (in repo root, sharable)

## Config Schema (YAML)

```yaml
# ~/.config/doc-rebuild/config.yml (user-level, contains credentials)
repositories:
  - url: https://github.com/owner/repo
    branch: main
    credentials:
      provider: github  # github | gitlab
      token_ref: 001    # key to encrypted token in ~/.config/doc-rebuild/credentials/
    sub_path: null      # optional monorepo sub-path

generation:
  output_dir: ./docs      # default output directory
  include_prs: true       # include PR analysis
  include_history: true   # include git history analysis
  max_commit_depth: 1000  # max commits to analyze

  llm:
    model: llama3-70b-8192  # Groq model
    temperature: 0.3
    max_tokens: 8192
```

## Credential Storage

- Encrypted file: `~/.config/doc-rebuild/credentials/`
- One file per credential, named by hash of repo URL
- Encrypted with Fernet (symmetric AES-128-CBC + HMAC)
- Master key derived from user passphrase or stored in OS keyring

## Repository-level Config (`.doc-rebuild.yml`)

```yaml
# .doc-rebuild.yml (checked into repo, sharable with team)
doc_rebuild:
  generate:
    output_dir: docs/
    include_prs: true
    include_history: true
    llm:
      model: llama3-70b-8192
```
