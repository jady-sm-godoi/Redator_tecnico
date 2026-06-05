from datetime import datetime
from uuid import uuid4, UUID
from enum import Enum
from pydantic import BaseModel, Field


class Provider(str, Enum):
    github = "github"
    gitlab = "gitlab"


class TokenType(str, Enum):
    pat = "pat"
    oauth = "oauth"


class RepositoryConnection(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    url: str
    provider: Provider
    branch: str = "main"
    credentials_ref: str = ""
    sub_path: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class CredentialConfig(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    repo_url: str
    encrypted_token: bytes
    token_type: TokenType = TokenType.pat
    created_at: datetime = Field(default_factory=datetime.now)
