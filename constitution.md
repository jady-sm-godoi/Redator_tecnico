# Project Constitution

## Purpose

Build a production-ready AI Agent platform using Agno as the default
agent runtime, Groq for low-latency inference, and GitHub/GitLab
integrations.

The platform must be designed to allow replacement of:

- Agent runtime
- LLM providers
- Databases
- Vector databases
- External integrations

with minimal changes to application and domain code.

The architecture must prioritize:

- Maintainability
- Observability
- Testability
- Provider independence
- Clear separation of responsibilities
- Production readiness

---

# Core Principles

## Simplicity First

Prefer simple and explicit solutions over complex abstractions.

Avoid premature optimization.

## Single Responsibility

Modules, services, tools, use cases, and agents must have a single,
well-defined responsibility.

## Dependency Inversion

Business rules must not depend on frameworks, SDKs, databases, or
external services.

All external integrations must be accessed through ports.

## Framework Independence

Business logic must remain independent from:

- FastAPI
- Agno
- Groq
- SQLAlchemy
- GitHub SDKs
- GitLab SDKs
- Vector databases

Frameworks are implementation details.

---

# Architecture

## Architectural Style

This project follows the Hexagonal Architecture
(Ports and Adapters) pattern.

The domain is the center of the system.

External systems communicate with the application through adapters.

```text
                    ┌──────────────────┐
                    │     FastAPI      │
                    └────────┬─────────┘
                             │
                     Inbound Adapter
                             │
                             ▼

┌──────────────────────────────────────────────────────┐
│                    Application                       │
│                  Use Cases / Flows                   │
└───────────────────────┬──────────────────────────────┘
                        │
                        ▼

┌──────────────────────────────────────────────────────┐
│                       Domain                         │
│                Entities / Rules / Ports             │
└───────────────────────┬──────────────────────────────┘
                        │
                        ▼

         Outbound Ports (Protocols / Contracts)

      ┌──────────┬──────────┬──────────┬──────────┐
      ▼          ▼          ▼          ▼
  GitHub     GitLab      Groq      Database
  Adapter    Adapter    Adapter     Adapter
```

## Dependency Rule

Dependencies must always point inward.

```text
Adapters → Application → Domain

Domain → nothing
```

The domain layer must never import:

- adapters
- infrastructure
- FastAPI
- Agno
- Groq SDKs
- database implementations
- external SDKs

The application layer may depend only on:

- domain
- ports
- DTOs

Adapters may depend on external libraries.

---

# Project Structure

```text
src/
├── domain/
│   ├── entities/
│   ├── value_objects/
│   ├── services/
│   ├── ports/
│   ├── events/
│   └── exceptions/
│
├── application/
│   ├── use_cases/
│   ├── workflows/
│   ├── dto/
│   └── services/
│
├── adapters/
│   ├── inbound/
│   │   └── fastapi/
│   │
│   └── outbound/
│       ├── agno/
│       ├── groq/
│       ├── github/
│       ├── gitlab/
│       ├── sqlite/
│       ├── postgres/
│       └── vectorstore/
│
├── infrastructure/
│   ├── config/
│   ├── logging/
│   ├── telemetry/
│   ├── security/
│   └── dependency_injection/
│
├── prompts/
│   ├── system/
│   ├── agents/
│   ├── tools/
│   └── templates/
│
└── tests/
    ├── unit/
    ├── integration/
    └── contract/
```

---

# Domain Layer

## Responsibilities

The domain layer contains:

- Business rules
- Entities
- Value objects
- Domain services
- Domain events
- Port definitions

The domain layer must remain pure Python.

The domain layer must never depend on:

- Databases
- Frameworks
- APIs
- Agent frameworks
- LLM providers

---

# Ports

Every external dependency must be represented by a port.

Ports belong to:

```text
domain/ports/
```

Ports must use Protocol.

Example:

```python
from typing import Protocol

class LLMProviderPort(Protocol):
    async def generate(
        self,
        prompt: str,
    ) -> str:
        ...
```

Required ports include:

- LLMProviderPort
- AgentRuntimePort
- GitProviderPort
- RepositoryPort
- KnowledgePort
- EventPublisherPort

Application code must depend only on ports.

---

# Adapters

Adapters implement ports.

Adapters are implementation details.

Examples:

- GroqAdapter
- GitHubAdapter
- GitLabAdapter
- SQLiteRepository
- PostgreSQLRepository
- QdrantKnowledgeRepository
- AgnoAdapter

Adapters may depend on:

- SDKs
- Frameworks
- Databases

The domain must never depend on adapters.

Adapters must be replaceable without changes to business logic.

---

# Technology Stack

## Backend

- Python 3.12+
- FastAPI
- Pydantic v2

## Agent Runtime

- Agno

## Package Management

- uv

## Type Checking

- Pyright (strict mode)

## Database

### Development

- SQLite

### Production

- PostgreSQL

## Migrations

- Alembic

## Observability

- OpenTelemetry
- Structured Logging

---

# AI Architecture

## Agent Runtime Isolation

Agno is the default runtime implementation.

Agno must be isolated behind a port.

Example:

```python
class AgentRuntimePort(Protocol):
    async def execute(
        self,
        request: AgentRequest,
    ) -> AgentResponse:
        ...
```

Example implementation:

```python
class AgnoAdapter(AgentRuntimePort):
    ...
```

Replacing Agno must require changes only inside adapters.

## Agent Design

Agents should be:

- Small
- Focused
- Independently testable

Avoid monolithic agents.

---

# LLM Provider Strategy

Groq is the default LLM provider.

Providers must be abstracted.

Application code must never depend directly on:

- Groq SDK
- OpenAI SDK
- Anthropic SDK

Example:

```python
class LLMProviderPort(Protocol):
    async def generate(
        self,
        prompt: str,
    ) -> str:
        ...
```

---

# Tool Design

Tools are first-class components.

Every tool must:

- Have a single responsibility
- Be deterministic whenever possible
- Be independently testable
- Expose explicit schemas

Each tool must define:

- Input schema
- Output schema
- Error handling strategy

Tools must not depend directly on:

- FastAPI
- Agno
- Groq

Tools must be executable without an agent runtime.

---

# Prompt Management

Prompts are application assets.

Prompts must:

- Be version controlled
- Be reusable
- Be testable
- Be stored outside business logic

Directory:

```text
prompts/
├── system/
├── agents/
├── tools/
└── templates/
```

Avoid inline prompts in services or route handlers.

---

# Knowledge & RAG Architecture

Knowledge retrieval must remain isolated from agent logic.

## Knowledge Port

Example:

```python
class KnowledgePort(Protocol):
    async def search(
        self,
        query: str,
    ) -> list[Document]:
        ...
```

Agent workflows must never depend on:

- pgvector
- Qdrant
- Pinecone
- Weaviate

Vector stores are implementation details.

Knowledge providers must be replaceable through adapters.

---

# Configuration

Use:

- Pydantic Settings

Rules:

- No direct access to environment variables
- No os.getenv outside configuration modules
- Environment-specific settings must be isolated

Example:

```python
settings.groq_api_key
settings.database_url
```

---

# API Standards

Use FastAPI best practices.

## Requirements

- Async endpoints whenever supported
- Dependency injection
- Pydantic request models
- Pydantic response models

API routes must never contain business logic.

Routes must invoke use cases.

---

# GitHub & GitLab Integration

Integrations must be isolated through ports.

Examples:

```python
class GitProviderPort(Protocol):
    ...
```

Implementations:

- GitHubAdapter
- GitLabAdapter

Requirements:

- Retry handling
- Timeout handling
- Structured error mapping

Business logic must never call SDKs directly.

---

# Typing Standards

Type annotations are mandatory.

All public functions must define:

- Parameter types
- Return types

Prefer:

- Protocol
- TypedDict
- dataclass
- Enum

Avoid:

```python
Any
```

unless strongly justified.

---

# Code Quality Standards

## Formatting

Maximum line length:

```text
79
```

Use:

```bash
ruff format
```

## Linting

Use:

```bash
ruff check
```

All code must pass linting before merge.

---

# Ruff Exceptions

Suppress warnings only when readability or architecture would suffer.

## E501

Allowed for:

- Long URLs
- Complex regex
- Explicit assertion messages

```python
# noqa: E501
```

## PLR0913

Allowed when introducing an object would add unnecessary complexity.

```python
# noqa: PLR0913
```

## PLR2004

Allowed for domain-specific constants.

```python
# noqa: PLR2004
```

## PLC0415

Allowed for:

- Circular import avoidance
- Optional dependency loading
- Startup optimization

```python
# noqa: PLC0415
```

---

# Imports

Imports belong at the top of the file.

Local imports are allowed only under PLC0415 conditions.

---

# Static Type Checking

Use:

```bash
pyright
```

Configuration:

```text
strict mode
```

All code must pass type checking before merge.

---

# Testing Standards

Testing is mandatory.

## Unit Tests

Required for:

- Domain entities
- Value objects
- Domain services
- Tools
- Utilities
- Use cases

## Integration Tests

Required for:

- Agent workflows
- API endpoints
- Adapter implementations

## Contract Tests

Required for:

- Ports
- Adapter compliance

---

# AI Testing

AI-specific testing rules:

- Mock LLM responses
- No external LLM dependency during CI
- No network dependency during CI
- Agent workflows must be reproducible

Tests must validate:

- Tool invocation
- Structured outputs
- Failure scenarios
- Retry behavior

---

# Observability

Observability is mandatory.

## Logging

Use structured logging.

Development:

```text
Human-readable logs
```

Production:

```text
JSON logs
```

Every execution should include:

- request_id
- session_id
- execution_id

When available:

- user_id
- repository_id

---

# Tracing

Use OpenTelemetry.

Trace:

- API requests
- Agent execution
- Tool execution
- Database operations
- External API calls
- LLM requests

---

# Security

Never hardcode:

- Tokens
- Passwords
- Secrets
- API keys

Use environment-based configuration.

## Validation

Validate:

- External API responses
- Tool inputs
- LLM outputs

Never trust generated content without validation.

---

# Database Standards

Use Alembic migrations.

Rules:

- No manual schema changes
- All schema changes must be versioned
- Schema changes must be reversible

---

# Architecture Enforcement

## Forbidden Imports in Domain

Domain must never import:

- FastAPI
- Agno
- Groq
- SQLAlchemy
- Databases
- GitHub SDKs
- GitLab SDKs

## Application Rules

Application may depend only on:

- Domain
- Ports
- DTOs

Application must not import:

- SDK implementations
- Database implementations

## Adapter Rules

Adapters may import:

- SDKs
- Databases
- Frameworks

Adapters implement ports.

## Infrastructure Rules

Infrastructure provides:

- Configuration
- Logging
- Tracing
- Security
- Dependency injection

Infrastructure must not contain business rules.

---

# Git Standards

## Branch Naming

Examples:

```text
feature/github-sync
fix/repository-auth
refactor/agent-runtime
chore/dependencies
```

---

# Commit Messages

Use Conventional Commits.

Allowed types:

```text
feat:
fix:
refactor:
chore:
test:
docs:
```

Examples:

```text
feat: add GitHub repository synchronization
fix: handle GitLab pagination
refactor: simplify agent orchestration
test: add workflow integration coverage
docs: update API documentation
```

---

# Documentation

Public modules, classes, and functions should include docstrings.

Complex workflows must be documented.

Architecture decisions must be recorded as ADRs.

Location:

```text
docs/adr/
```

---

# Definition of Done

A feature is complete only when:

- Implementation is finished
- Unit tests are implemented
- Integration tests are implemented
- Contract tests are implemented
- Ruff passes
- Pyright passes
- Documentation is updated
- Observability is included
- No secrets are exposed
- CI passes successfully
- Architectural rules are respected