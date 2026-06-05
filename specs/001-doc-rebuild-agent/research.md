# Research: Auto Documentation Rebuild Agent

## Decision: Agent Orchestration Framework

**Decision**: Agno
**Rationale**: Agno provides multi-step agent workflow orchestration with built-in tool integration, structured output parsing, and LLM-agnostic design. Lower overhead than LangChain, more structured than raw function calls.
**Alternatives considered**: LangChain (heavier, more complex), Custom Python orchestration (more code to maintain), CrewAI (less mature)

## Decision: LLM Provider

**Decision**: Groq (Llama 3 70B for analysis, Llama 3 8B for formatting)
**Rationale**: Low latency inference (50-100ms vs 1-3s for cloud APIs), competitive output quality, generous free tier. Llama 3 70B handles complex code analysis; 8B handles formatting and structuring.
**Alternatives considered**: OpenAI (higher cost, higher latency), Anthropic Claude (higher cost), Local models (too slow without GPU)

## Decision: GitHub API Client

**Decision**: PyGithub
**Rationale**: Mature library (14+ years), full GitHub REST API coverage, active maintenance, type-annotated.
**Alternatives considered**: Raw requests (more boilerplate), GitHub GraphQL API (steeper learning curve, unnecessary for read-only access)

## Decision: GitLab API Client

**Decision**: python-gitlab
**Rationale**: Official GitLab SDK, complete API coverage, supports both REST and GraphQL, pagination built-in.
**Alternatives considered**: Raw requests (more boilerplate, no pagination helpers)

## Decision: Code Structure Analysis

**Decision**: tree-sitter + language-specific parsers
**Rationale**: Parses code into AST - reliable module/function/class detection across languages. Supports 40+ languages. More accurate than regex.
**Alternatives considered**: regex-based scanning (fragile, misses nested structures), custom parsers (too much work per language), language servers (heavy, per-language installation)

## Decision: Credential Encryption

**Decision**: cryptography library (Fernet symmetric encryption)
**Rationale**: AES-128-CBC with HMAC authentication, simple API, key derived from user-provided passphrase or system keyring.
**Alternatives considered**: keyring (OS keyring dependency, less portable), env vars only (no persistence), plaintext config (insecure)

## Decision: Git History Analysis

**Decision**: gitpython library
**Rationale**: Pure Python git access, supports commit iteration, diff analysis, branch inspection. Well-maintained.
**Alternatives considered**: subprocess git calls (fragile, platform-dependent), raw libgit2 bindings (complex)
