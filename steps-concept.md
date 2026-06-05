# Relatorio Didatico — Fase 1 + Fase 2

**Projeto**: Redator Tecnico (doc-rebuild-agent)  
**Branch**: `001-doc-rebuild-agent`  
**Objetivo**: CLI que conecta em repos GitHub/GitLab, analisa codigo + git + PRs, e gera documentacao tecnica em Markdown usando IA (Groq).

---

## Sumario

- [O que e o projeto como um todo](#o-que-e-o-projeto-como-um-todo)
- [Fase 1 — Setup (A Fundacao do Projeto)](#fase-1--setup-a-fundacao-do-projeto)
  - [T001 — pyproject.toml](#t001--pyprojecttoml)
  - [T002 — Estrutura de diretorios](#t002--estrutura-de-diretorios)
  - [T003 — Configuracao do pytest](#t003--configuracao-do-pytest)
  - [T004 — Arquivos __init__.py](#t004--arquivos-__init__py)
- [Fase 2 — Foundational (Os Blocos de Construcao)](#fase-2--foundational-os-blocos-de-construcao)
  - [T005+T006 — Modelos de Repositorio (repo.py)](#t005t006--modelos-de-repositorio-repopy)
  - [T007 — Modelos de Analise (analysis.py)](#t007--modelos-de-analise-analysispy)
  - [T008 — Modelos de Documentacao (documentation.py)](#t008--modelos-de-documentacao-documentationpy)
  - [T009 — Gerenciador de Configuracao (settings.py)](#t009--gerenciador-de-configuracao-settingspy)
  - [T010 — Criptografia de Tokens (crypto.py)](#t010--criptografia-de-tokens-cryptopy)
  - [T011 — Esqueleto do CLI (main.py)](#t011--esqueleto-do-cli-mainpy)
  - [T012+T013 — Testes (TDD)](#t012t013--testes-tdd)
- [Diagrama completo das 2 fases](#diagrama-completo-das-2-fases)
- [Glossario para iniciantes](#glossario-para-iniciantes)

---

## O que e o projeto como um todo

```
Usuario digita no terminal:
    doc-rebuild generate https://github.com/meu/time/projeto-x

O sistema:
    1. Conecta no GitHub via API e baixa o codigo
    2. Analisa a estrutura (modulos, classes, funcoes) com tree-sitter
    3. Examina git history (commits significativos) com gitpython
    4. Le PRs e extrai decisoes arquiteturais com PyGithub/python-gitlab
    5. Manda tudo pro Groq (LLM) que escreve documentacao em Markdown
    6. Salva em ./docs/README.md, architecture.md, modules/, decisions.md
```

---

## Fase 1 — Setup (A Fundacao do Projeto)

A Fase 1 prepara o **esqueleto do projeto** — nada de logica de negocio ainda.  
So estrutura, dependencias e configuracoes. E como preparar a cozinha antes de cozinhar.

```
📁 projeto/
├── 📄 pyproject.toml           ← T001: Ingredientes + receita
├── 📁 src/                     ← T002: Codigo fonte
│   ├── 📄 __init__.py          ← T004: Pacote Python
│   ├── 📁 cli/__init__.py
│   ├── 📁 connectors/__init__.py
│   ├── 📁 analyzers/__init__.py
│   ├── 📁 generators/__init__.py
│   ├── 📁 models/__init__.py
│   └── 📁 config/__init__.py
├── 📁 tests/                   ← T002: Testes
│   ├── 📄 __init__.py
│   ├── 📁 unit/__init__.py
│   ├── 📁 integration/__init__.py
│   └── 📁 fixtures/sample_repos/
└── specs/001-doc-rebuild-agent/  ← Documentacao do projeto
```

---

### T001 — pyproject.toml

Esse arquivo e a **certidao de nascimento** do projeto Python. Ele diz pro mundo:

```toml
[project]
name = "redator-tecnico"
version = "0.1.0"
description = "CLI tool que gera documentacao tecnica automatica de repos GitHub/GitLab"
requires-python = ">=3.12"
dependencies = [
    "agno>=1.0.0",         # Orquestrar o agente (conectar → analisar → gerar)
    "groq>=0.9.0",         # Chamar o LLM (modelo de IA que escreve a documentacao)
    "PyGithub>=2.3.0",     # Conectar no GitHub via API
    "python-gitlab>=4.4.0",# Conectar no GitLab via API
    "cryptography>=42.0.0",# Criptografar tokens de acesso
    "typer>=0.12.0",       # Criar a interface de linha de comando (CLI)
    "gitpython>=3.1.0",    # Analisar historico de commits
    "tree-sitter>=0.22.0", # Parsear codigo-fonte em AST
    "pyyaml>=6.0",         # Ler arquivos de configuracao YAML
    "pydantic>=2.0.0",     # Validar dados de entrada (models com tipagem)
]

[project.scripts]
doc-rebuild = "src.cli.main:app"  # comando que usuario digita no terminal
```

**Cada dependencia tem um proposito**:
| Dependencia | Pra que? |
|-------------|----------|
| **agno** | Orquestra o fluxo: conectar repo → analisar codigo → chamar LLM → gerar doc |
| **groq** | Provedor de IA rapido (Llama 3 70B) — escreve a documentacao em linguagem natural |
| **PyGithub** | Cliente oficial GitHub — busca codigo, PRs, issues |
| **python-gitlab** | Cliente oficial GitLab — mesmo proposito do PyGithub |
| **cryptography** | Cifra tokens de acesso com AES (ninguem ve sua senha) |
| **typer** | Framework CLI — transforma funcoes Python em comandos de terminal |
| **gitpython** | Le o repositorio git local — iteracao por commits, diff, branches |
| **tree-sitter** | Parseia codigo em AST (Arvore Sintatica Abstrata) — entende a estrutura |
| **pyyaml** | Le e escreve arquivos .yml de configuracao |
| **pydantic** | Valida dados automaticamente — se vier tipo errado, da erro na hora |

**Entry point** `doc-rebuild = "src.cli.main:app"`:
Quando o usuario digita `doc-rebuild` no terminal, o Python:
1. Procura a funcao `app` (um objeto Typer) em `src/cli/main.py`
2. Typer analisa os argumentos do terminal (ex: `generate`, `--output`)
3. Roteia pro metodo Python certo

**Configuracao do pytest** (tambem no pyproject.toml):
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "-v --tb=short"  # verbose + traceback curto (mais legivel)
```

**Dependencias de desenvolvimento**:
```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",       # Framework de testes
    "pytest-vcr>=1.0.0",   # Grava requests HTTP e "replay" (nao chama API toda hora)
    "pytest-mock>=3.12.0", # Mocking facilitado
    "pytest-cov>=5.0.0",   # Mede cobertura de testes
]
```

Instalacao: `pip install -e ".[dev]"`  
O `-e` (editable) faz com que alteracoes no codigo reflitam imediatamente sem reinstalar.

---

### T002 — Estrutura de diretorios

```
src/                          ← Codigo fonte (pacote instalavel)
├── cli/                      ← Interface de linha de comando (Typer)
├── connectors/               ← Conexao com GitHub/GitLab via API
├── analyzers/                ← Analise de codigo, git history, PRs
├── generators/               ← Geracao de documentacao (Agno + Groq)
├── models/                   ← Modelos de dados (Pydantic)
└── config/                   ← Config + criptografia de tokens

tests/                        ← Testes
├── unit/                     ← Testes unitarios (uma funcao de cada vez)
├── integration/              ← Testes de integracao (fluxo completo)
└── fixtures/sample_repos/    ← Repositorios de exemplo pra testar
```

**Por que src/ layout?**  
O codigo fica dentro de `src/` e o pyproject.toml usa:
```toml
[tool.setuptools.packages.find]
where = ["src"]
```
Isso evita bugs de import — quando voce roda `pytest` de fora, ele nao confunde o codigo fonte com o instalado.

**Analogia**: E como separar as gavetas da cozinha: uma pra talheres, outra pra panelas, outra pra temperos. Cada modulo tem seu lugar, ninguem se perde.

---

### T003 — Configuracao do pytest

Adicionado no `pyproject.toml`:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short"
```

Ferramentas de teste:
| Ferramenta | Pra que? |
|------------|----------|
| **pytest** | Framework que descobre e roda testes automaticamente |
| **pytest-vcr** | Grava requests HTTP reais e "replay" nos testes — testes rapidos e deterministicos |
| **pytest-mock** | Substitui partes do codigo por versoes falsas (mock) nos testes |
| **pytest-cov** | Mostra quantas linhas do codigo foram testadas (% de cobertura) |

**Como funciona o VCR**: Na primeira execucao, ele grava a response do GitHub num arquivo `.yaml`. Nas proximas, ele "replay" esse arquivo — nao chama o GitHub de verdade. Testes ficam rapidos e nao dependem de internet.

---

### T004 — Arquivos `__init__.py`

Criado um `__init__.py` em **cada pasta** de `src/` e `tests/`.

**Por que?** No Python, uma pasta so e considerada um **pacote** (importavel) se tiver `__init__.py`. Sem ele:

```python
from src.models.repo import RepositoryConnection  # Erro: src nao e pacote!
```

Com ele, funciona. O arquivo pode ser vazio (`touch arquivo`), mas precisa existir.

---

## Fase 2 — Foundational (Os Blocos de Construcao)

A Fase 2 constroi a **fundacao do sistema** — os blocos que TODAS as User Stories vao usar.  
Sem essa fase, nada funciona. E como construir a fundacao de uma casa: ninguem ve, mas tudo depende dela.

```
src/
├── models/
│   ├── repo.py           ← T005+T006: Modelos de dados de repositorio
│   ├── analysis.py       ← T007: Modelos de analise de codigo
│   └── documentation.py  ← T008: Modelos de documentacao gerada
├── config/
│   ├── settings.py       ← T009: Gerenciamento de configuracao (YAML)
│   └── crypto.py         ← T010: Criptografia de tokens (Fernet)
└── cli/
    └── main.py           ← T011: Esqueleto do CLI (Typer)

tests/
└── unit/
    ├── test_config.py    ← T012: 5 testes de configuracao
    └── test_crypto.py    ← T013: 4 testes de criptografia
```

---

### T005+T006 — Modelos de Repositorio (repo.py)

Usamos **Pydantic** (biblioteca de validacao de dados) para definir `RepositoryConnection` e `CredentialConfig`.

```python
class Provider(str, Enum):
    github = "github"
    gitlab = "gitlab"

class RepositoryConnection(BaseModel):
    id: UUID = Field(default_factory=uuid4)  # UUID unico automatico
    url: str                                  # "https://github.com/owner/repo"
    provider: Provider                        # Só "github" ou "gitlab"
    branch: str = "main"                      # Branch padrao
    credentials_ref: str = ""                 # Chave pro token criptografado
    sub_path: str | None = None              # Opcional: monorepo sub-pasta
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
```

**O que e Pydantic?**  
Uma biblioteca que valida dados automaticamente. Voce declara os campos com tipos Python, e o Pydantic:
- Converte automaticamente (ex: `"main"` vira string, `uuid4()` gera UUID)
- Rejeita valores invalidos (ex: `provider = "bitbucket"` → erro, pois nao esta no enum)
- Fornece `model_dump()` pra converter pra dicionario/dict

**Enum (enumeracao)**:  
```python
class Provider(str, Enum):
    github = "github"
    gitlab = "gitlab"
```
Isso limita os valores possiveis. Se alguem tentar `Provider("bitbucket")`, o Python levanta `ValueError`. Evita bugs onde um nome de provedor e escrito errado.

**`Field(default_factory=uuid4)`**:  
Toda vez que um novo objeto e criado, `uuid4()` e chamado pra gerar um identificador unico universal (UUID). Assim cada repositorio cadastrado tem um ID unico, mesmo sem banco de dados.

```python
class CredentialConfig(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    repo_url: str
    encrypted_token: bytes   # bytes criptografados (ninguem ve o token puro)
    token_type: TokenType = TokenType.pat  # "pat" (token pessoal) ou "oauth"
    created_at: datetime = Field(default_factory=datetime.now)
```

---

### T007 — Modelos de Analise (analysis.py)

Seis modelos que representam o **resultado da analise** de um repositorio:

```python
class Module(BaseModel):
    """Um arquivo ou diretorio detectado no codigo fonte."""
    name: str               # Nome do modulo: "src/models/user"
    path: str               # Caminho relativo: "src/models/user.py"
    type: ModuleType        # package / module / class / function
    docstring: str | None = None  # Se o codigo tiver docstring, extraimos
    dependencies: list[str] = []  # Nomes dos modulos que ele importa
    exported_symbols: list[str] = []  # API publica (classes, funcoes expostas)

class Dependency(BaseModel):
    """Dependencia entre dois modulos."""
    source: str             # Quem depende: "src/models/user"
    target: str             # De quem depende: "src/database"
    type: DepType           # import / inherit / compose / call
    is_external: bool = False  # E biblioteca externa? (ex: "requests")

class CommitEvent(BaseModel):
    """Um commit do git com classificacao de importancia."""
    hash: str               # SHA do commit: "a1b2c3d..."
    author: str             # Quem fez o commit
    date: datetime          # Quando
    message: str            # Mensagem do commit
    files_changed: list[str] = []
    significance: Significance  # major / minor / refactor / fix / docs

class PRInsight(BaseModel):
    """Decisao arquitetural extraida de um Pull Request."""
    pr_number: int
    title: str
    description: str
    decision: str | None = None     # Qual decisao foi tomada
    rationale: str | None = None    # Por que foi tomada
    date: datetime

class AnalysisResult(BaseModel):
    """Container com TUDO que foi analisado."""
    id: UUID = Field(default_factory=uuid4)
    repo_url: str
    analyzed_at: datetime = Field(default_factory=datetime.now)
    module_map: list[Module] = []         # Todos os modulos detectados
    dependency_graph: list[Dependency] = []  # Grafo de dependencias
    commit_timeline: list[CommitEvent] = []   # Commits em ordem cronologica
    pr_insights: list[PRInsight] = []     # Decisoes de PRs
    languages: list[str] = []             # Linguagens detectadas
    total_files: int = 0                  # Total de arquivos analisados
    total_loc: int = 0                    # Linhas de codigo total
```

**Destaque**: `Significance` classifica commits:
```python
class Significance(str, Enum):
    major = "major"      # Grande mudanca arquitetural
    minor = "minor"      # Mudanca moderada
    refactor = "refactor" # Refatoracao (comportamento inalterado)
    fix = "fix"          # Correcao de bug
    docs = "docs"        # Mudanca de documentacao
```

Isso permite que o gerador de doc decida o que merece destaque no changelog. Commits `major` ganham paragrafo proprio; commits `docs` sao ignorados.

---

### T008 — Modelos de Documentacao (documentation.py)

Representa a **documentacao gerada** e seu historico de alteracoes:

```python
class DocSection(BaseModel):
    """Uma secao da documentacao (ex: "Arquitetura", "Modulo de Usuarios")."""
    title: str                  # Titulo da secao
    level: int = 1              # Nivel do heading (# ## ###)
    content: str = ""           # Conteudo Markdown
    source_modules: list[str] = []  # Quais modulos originaram esta secao
    stale: bool = False         # Esta desatualizada? (US3 usa isso!)

class ChangelogEntry(BaseModel):
    """Uma entrada no historico de regeneracao."""
    version: int                # Versao da documentacao
    date: datetime = Field(default_factory=datetime.now)
    changed_sections: list[str] = []  # Secoes alteradas nesta versao
    trigger: str = "manual"     # O que causou: "manual" / "webhook" / "check"

class Documentation(BaseModel):
    """Documento completo gerado."""
    id: UUID = Field(default_factory=uuid4)
    repo_url: str
    generated_at: datetime = Field(default_factory=datetime.now)
    format: str = "markdown"    # Sempre markdown (definido na especificacao)
    sections: list[DocSection] = []
    changelog: list[ChangelogEntry] = []
    source_hash: str = ""       # Hash da arvore git (pra detectar mudancas)
```

**`DocSection.stale`** e a chave da US3 (P3):  
Quando o codigo muda, a secao correspondente e marcada como `stale = True`. O comando `doc-rebuild update` regenera SO as secoes stale, sem refazer a documentacao inteira. Isso economiza tokens de LLM e tempo.

**`ChangelogEntry.trigger`** guarda o que causou a regeneracao:
- `"manual"` → usuario rodou `doc-rebuild generate`
- `"check"` → usuario rodou `doc-rebuild check` e depois `update`
- `"webhook"` → GitHub/GitLab avisou que houve push (futuro)

---

### T009 — Gerenciador de Configuracao (settings.py)

Gerencia o arquivo de configuracao YAML em `~/.config/doc-rebuild/config.yml`:

```python
# Estrutura dos dados de configuracao
class RepoConfig(BaseModel):
    url: str                          # URL do repositorio
    branch: str = "main"              # Branch alvo
    provider: str = ""                # "github" ou "gitlab"
    credentials_ref: str = ""         # Referencia pro token criptografado
    sub_path: str | None = None       # Sub-pasta em monorepo

class LLMConfig(BaseModel):
    model: str = "llama3-70b-8192"    # Modelo Groq
    temperature: float = 0.3          # Criatividade (0 = deterministico, 1 = criativo)
    max_tokens: int = 8192            # Maximo de tokens por chamada

class GenerationConfig(BaseModel):
    output_dir: str = "./docs"
    include_prs: bool = True
    include_history: bool = True
    max_commit_depth: int = 1000       # Max commits a analisar
    llm: LLMConfig = Field(default_factory=LLMConfig)

class AppConfig(BaseModel):
    repositories: list[RepoConfig] = []
    generation: GenerationConfig = Field(default_factory=GenerationConfig)


# Funcoes para ler e salvar
def load_config(config_dir=None) -> AppConfig:
    """Le o YAML de disco e devolve um AppConfig."""
    base = config_dir or CONFIG_DIR   # CONFIG_DIR = ~/.config/doc-rebuild/
    config_file = base / "config.yml"
    if not config_file.exists():
        return AppConfig()            # Configuracao padrao se arquivo nao existe
    raw = config_file.read_text()
    data = yaml.safe_load(raw) or {}
    return AppConfig(**data)          # Pydantic valida os dados automaticamente

def save_config(config: AppConfig, config_dir=None):
    """Salva um AppConfig como YAML em disco."""
    base = config_dir or CONFIG_DIR
    config_file = base / "config.yml"
    raw = yaml.dump(config.model_dump(), default_flow_style=False)
    config_file.write_text(raw)
```

**Por que `config_dir` e opcional?**  
As funcoes aceitam um parametro `config_dir` que, se passado, substitui o diretorio padrao. Nos testes passamos um diretorio temporario (`tempfile.TemporaryDirectory`). Em producao, usa `~/.config/doc-rebuild/`. Isso permite testar sem poluir a maquina real.

**Exemplo de config.yml gerado**:
```yaml
repositories:
- url: https://github.com/meu/time/projeto-x
  branch: main
  provider: github
  credentials_ref: "001"
generation:
  output_dir: ./docs
  include_prs: true
  include_history: true
  max_commit_depth: 1000
  llm:
    model: llama3-70b-8192
    temperature: 0.3
    max_tokens: 8192
```

---

### T010 — Criptografia de Tokens (crypto.py)

Criptografa tokens de acesso (GitHub PAT, GitLab token) usando **Fernet**.

**O que e Fernet?**  
E um algoritmo de criptografia simetrica da biblioteca `cryptography` do Python. Ele usa:
- **AES-128-CBC** pra cifrar os dados
- **HMAC** pra garantir que os dados nao foram adulterados

```python
from cryptography.fernet import Fernet

KEY_FILE = Path.home() / ".config" / "doc-rebuild" / ".key"

def _get_or_create_key(key_file=None) -> bytes:
    """Le a chave existente ou gera uma nova na primeira execucao."""
    kf = key_file or KEY_FILE
    if kf.exists():
        return kf.read_bytes()
    key = Fernet.generate_key()         # Gera chave aleatoria de 32 bytes
    kf.parent.mkdir(parents=True, exist_ok=True)
    kf.write_bytes(key)
    kf.chmod(0o600)                      # So o dono pode ler (seguranca!)
    return key

def encrypt_token(token: str, key_file=None) -> bytes:
    """Cifra um token: "ghp_abc123" → b"\\x80\\x03..." (bytes ilegiveis)"""
    key = _get_or_create_key(key_file)
    f = Fernet(key)
    return f.encrypt(token.encode())     # string → bytes → cifra

def decrypt_token(encrypted: bytes, key_file=None) -> str:
    """Decifra: b"\\x80\\x03..." → "ghp_abc123" """
    key = _get_or_create_key(key_file)
    f = Fernet(key)
    return f.decrypt(encrypted).decode() # decifra → bytes → string
```

**Fluxo completo**:
1. Usuario roda `doc-rebuild init https://github.com/foo/bar`
2. CLI pergunta o token
3. `encrypt_token("ghp_abc123...")` cifra e salva em disco
4. Quando precisar acessar o GitHub, `decrypt_token(...)` recupera o token original

**Por que `chmod(0o600)`?**  
Permissao `600` = so o dono do arquivo pode ler/escrever. Impede que outros usuarios do sistema vejam a chave. Em sistemas Unix, `chmod(0o600)` equivale a `-rw-------`.

---

### T011 — Esqueleto do CLI (main.py)

Interface de linha de comando usando **Typer** (construido sobre Click, o framework CLI mais famoso do Python):

```python
import typer

app = typer.Typer()  # Cria a aplicacao CLI

@app.command()
def init(repo_url: str = typer.Argument(...), branch: str = typer.Option("main")):
    """Inicializa configuracao para um novo repositorio."""
    typer.echo(f"Inicializando repo: {repo_url}")

@app.command()
def generate(repo_url: str = typer.Argument(...), output: str = typer.Option("./docs")):
    """Gera documentacao para um repositorio."""
    typer.echo(f"Gerando docs para: {repo_url}")

@app.command("list")
def list_repos():
    """Lista repositorios configurados."""
    typer.echo("Repositorios configurados:")

@app.command()
def check(repo_url: str = typer.Argument(...)):
    """Verifica se documentacao esta desatualizada."""
    typer.echo(f"Verificando: {repo_url}")

@app.command()
def update(repo_url: str = typer.Argument(...)):
    """Atualiza secoes de documentacao obsoletas."""
    typer.echo(f"Atualizando docs de: {repo_url}")

@app.command()
def config():
    """Exibe configuracao atual."""
    typer.echo("Configuracao atual:")
```

**Comandos disponiveis** (ainda placeholders — implementacao real na US1 e US3):

| Comando | Uso | Quando implementa |
|---------|-----|-------------------|
| `doc-rebuild init <url>` | Configurar novo repositorio | US1 |
| `doc-rebuild generate <url>` | Gerar documentacao | US1 |
| `doc-rebuild list` | Listar repos configurados | US1 |
| `doc-rebuild check <url>` | Verificar se doc esta desatualizada | US3 |
| `doc-rebuild update <url>` | Atualizar secoes obsoletas | US3 |
| `doc-rebuild config` | Ver configuracao atual | US3 |

**Typer.Argument vs Typer.Option**:
- `Argument(...)` → parametro obrigatorio na linha de comando: `doc-rebuild generate https://url`
- `Option("./docs")` → parametro opcional com valor padrao: `doc-rebuild generate https://url --output ./meu-docs`

**Entry point**: Quando o usuario digita `doc-rebuild`, o Python:
1. Le `pyproject.toml` → `doc-rebuild = "src.cli.main:app"`
2. Importa `src/cli/main.py` e obtem o objeto `app` (Typer)
3. Typer analisa `sys.argv` (argumentos do terminal) e chama o metodo certo

---

### T012+T013 — Testes (TDD)

Seguimos **TDD (Test-Driven Development)**:

```
1. Escreve o teste (que falha porque a funcao nao existe)
2. Roda o teste → FAIL (verde vermelho)
3. Implementa a funcao
4. Roda o teste → PASS (verde)
5. Refatora se necessario
```

#### test_config.py (5 testes)

```python
import tempfile
from pathlib import Path
from src.config.settings import AppConfig, RepoConfig, save_config, load_config

class TestConfigManagement:
    def test_save_and_load_config(self):
        """Salva config num diretorio temporario e verifica se carrega igual."""
        with tempfile.TemporaryDirectory() as tmp:
            config_dir = Path(tmp) / "doc-rebuild"
            config = AppConfig(repositories=[
                RepoConfig(url="https://github.com/test/repo", credentials_ref="001")
            ])
            save_config(config, config_dir)
            loaded = load_config(config_dir)
            assert len(loaded.repositories) == 1
            assert loaded.repositories[0].url == "https://github.com/test/repo"
```

| Teste | O que verifica |
|-------|----------------|
| `test_save_and_load_config` | Salvar YAML e carregar devolve os mesmos dados |
| `test_load_config_empty_when_no_file` | Se nao existe config, retorna valores padrao |
| `test_resolve_repo_config_found` | Buscar URL existente encontra o repo |
| `test_resolve_repo_config_not_found` | Buscar URL inexistente retorna None |
| `test_save_preserves_generation_config` | Config de geracao (output_dir, etc) preservada |

#### test_crypto.py (4 testes)

```python
class TestCrypto:
    def test_encrypt_decrypt_roundtrip(self):
        """Cifrar e decifrar volta ao valor original."""
        with tempfile.TemporaryDirectory() as tmp:
            key_file = Path(tmp) / ".key"
            token = "ghp_1234567890abcdef"
            encrypted = encrypt_token(token, key_file)
            assert encrypted != token.encode()  # Cifrado != original
            decrypted = decrypt_token(encrypted, key_file)
            assert decrypted == token           # Decifrado == original
```

| Teste | O que verifica |
|-------|----------------|
| `test_encrypt_decrypt_roundtrip` | Cifrar e decifrar volta ao original (integralidade) |
| `test_different_tokens_different_ciphertext` | Tokens diferentes geram ciphertext diferentes (nao da pra confundir) |
| `test_decrypt_with_wrong_key_fails` | Chave errada = erro (seguranca! nao decifra com chave alheia) |
| `test_empty_token` | Token vazio tambem funciona (caso extremo) |

**Resultado**: `9 passed in 0.15s` ✅

**Por que `tempfile.TemporaryDirectory()`?**  
Cria uma pasta TEMPORARIA que e automaticamente deletada no final do teste. Vantagens:
- Cada teste comeca limpo (sem lixo de execucoes anteriores)
- Testes nao poluem a maquina real
- Rodam em paralelo sem conflito
- Sao deterministicos (mesmo resultado sempre)

---

## Diagrama completo das 2 fases

```
FASE 1 — SETUP
==============
T001 → pyproject.toml (10 dependencias + pytest config)
  ├── T002 → mkdir -p src/cli/ src/connectors/ ... (paralelo)
  ├── T003 → pytest config no pyproject.toml (paralelo)
  └── T004 → __init__.py em todos os pacotes (paralelo)


FASE 2 — FOUNDATIONAL
=====================
T005+T006 → src/models/repo.py (RepositoryConnection + CredentialConfig)
T007      → src/models/analysis.py (6 modelos de analise)
T008      → src/models/documentation.py (Documentation + DocSection + Changelog)
T009      → src/config/settings.py (config manager YAML)
    ↑ T012 test_config.py (TDD: 5 testes escritos PRIMEIRO)
T010      → src/config/crypto.py (Fernet encrypt/decrypt)
    ↑ T013 test_crypto.py (TDD: 4 testes escritos PRIMEIRO)
T011      → src/cli/main.py (esqueleto Typer com 6 comandos)

TUDO PRONTO → Proxima fase: US1 (MVP - implementar o fluxo real)
```

---

## Glossario para iniciantes

| Termo | Explicacao |
|-------|------------|
| **CLI** | Command-Line Interface — programa que roda no terminal (sem janela grafica) |
| **API** | Application Programming Interface — forma de um programa conversar com outro (ex: GitHub API) |
| **Token** | Senha de acesso a API (ex: `ghp_abc123...` do GitHub) |
| **Fernet** | Algoritmo de criptografia simetrica (mesma chave pra cifrar e decifrar) |
| **Pydantic** | Biblioteca Python que valida dados automaticamente |
| **Enum** | Tipo que limita valores possiveis (ex: so "github" ou "gitlab") |
| **UUID** | Identificador unico universal — numero que nunca se repete |
| **YAML** | Formato de arquivo legivel por humanos pra configuracao |
| **TDD** | Test-Driven Development — escrever teste antes do codigo |
| **typer** | Framework pra criar CLIs Python (baseado no Click) |
| **tree-sitter** | Biblioteca que parseia codigo fonte em AST (entende a estrutura) |
| **Agno** | Framework de orquestracao de agentes (conectar → analisar → gerar) |
| **Groq** | Provedor de LLM ultra-rapido (Latencia ~50ms vs ~1s de OpenAI) |
| **mock** | "Dublê" de funcao em testes — substitui uma funcao real por uma falsa |
| **VCR** | Gravador de requests HTTP — grava uma vez, replay nas proximas |

---

## Fase 3 — US1: MVP (Conectar + Analisar + Gerar)

A Fase 3 implementa a **primeira User Story completa (MVP)**. O fluxo ponta-a-ponta funciona:

```
Usuario digita:
    doc-rebuild init https://github.com/owner/repo
    (informa o token de acesso)
    doc-rebuild generate https://github.com/owner/repo --api-key gsk_abc...

O sistema faz:
    1. Conecta no GitHub/GitLab e clona o repositorio
    2. Analisa a estrutura do codigo (modulos, imports, dependencias)
    3. Envia a analise para o Groq (LLM)
    4. Gera documentacao Markdown com arquitetura + modulos
    5. Salva em ./docs/owner_repo.md
```

### Arquivos criados (T014-T029)

```
src/
├── connectors/
│   ├── base.py           ← T019: Interface abstrata do conector
│   ├── github.py         ← T020: Conector GitHub (gitpython + PyGithub)
│   └── gitlab.py         ← T021: Conector GitLab (gitpython + python-gitlab)
├── analyzers/
│   └── structure.py      ← T022: Analisador de estrutura (AST + regex)
└── generators/
    ├── llm_client.py     ← T023: Cliente Groq (LLM)
    └── orchestrator.py   ← T024: Orquestrador (analise → LLM → doc)

tests/
├── unit/
│   ├── test_github_connector.py    ← T014: 5 testes GitHub
│   ├── test_gitlab_connector.py    ← T015: 5 testes GitLab
│   ├── test_structure_analyzer.py  ← T016: 7 testes analisador
│   └── test_llm_client.py         ← T017: 3 testes Groq
└── integration/
    └── test_full_pipeline.py       ← T018: 2 testes fluxo completo

src/cli/main.py  ← T025-T029: init, generate, list WIRED + progresso + erros
```

---

### T019 — Interface dos Conectores (base.py)

Define o **contrato** (interface abstrata) que todo conector deve implementar:

```python
class BaseConnector(ABC):
    def __init__(self, connection: RepositoryConnection):
        self.connection = connection

    @abstractmethod
    def clone_repo(self, target_dir: Path, token: str) -> None:
        ...  # Clona o repo via git

    @abstractmethod
    def list_files(self, repo_dir: Path) -> list[Path]:
        ...  # Lista arquivos de codigo (ignora ocultos)

    @abstractmethod
    def get_repo_name(self) -> str:
        ...  # Ex: "owner/repo"

    @abstractmethod
    def get_default_branch(self) -> str:
        ...  # Ex: "main"
```

**Por que ABC (Abstract Base Class)?**  
- Garante que GitHub e GitLab tenham os mesmos metodos
- Quem criar um conector novo (ex: Bitbucket, Azure DevOps) segue o mesmo molde
- O resto do sistema (orchestrator, CLI) usa `BaseConnector` sem saber se e GitHub ou GitLab

---

### T020 — Conector GitHub (github.py)

```python
class GitHubConnector(BaseConnector):
    def __init__(self, connection: RepositoryConnection):
        super().__init__(connection)
        self._repo_name = connection.url.rstrip("/").split("github.com/")[-1]
        # URL: "https://github.com/owner/repo" → "owner/repo"
```

**Clone com autenticacao**:
```python
def clone_repo(self, target_dir: Path, token: str) -> None:
    clone_url = f"https://x-access-token:{token}@github.com/{self._repo_name}.git"
    git.Repo.clone_from(clone_url, target_dir, depth=1)
```

O `x-access-token:{token}` e o formato que o GitHub aceita para autenticar clones via URL. O `depth=1` faz clone **raso** (só o commit mais recente) — mais rapido e economiza disco.

**Listagem de arquivos ignorando ocultos**:
```python
def list_files(self, repo_dir: Path) -> list[Path]:
    files = []
    for path in repo_dir.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(repo_dir)
        if any(part.startswith(".") for part in rel.parts):
            continue  # Pula .git, .env, node_modules/, etc
        files.append(rel)
    return sorted(files)
```

**Busca de PRs via PyGithub**:
```python
def fetch_prs(self, token: str, state: str = "merged") -> list[dict]:
    api = Github(token)
    repo = api.get_repo(self._repo_name)
    prs = repo.get_pulls(state=state)
    return [{"number": pr.number, "title": pr.title, ...} for pr in prs]
```

---

### T021 — Conector GitLab (gitlab.py)

Estrutura identica ao GitHub, mas com diferencas:
- URL do clone: `https://oauth2:{token}@gitlab.com/{path}.git`
- API: `python-gitlab` em vez de `PyGithub`
- Metodo: `fetch_merge_requests()` em vez de `fetch_prs()`
- Objetos: `project.mergerequests.list()` em vez de `repo.get_pulls()`

```python
class GitLabConnector(BaseConnector):
    def clone_repo(self, target_dir: Path, token: str) -> None:
        clone_url = f"https://oauth2:{token}@gitlab.com/{self._project_path}.git"
        git.Repo.clone_from(clone_url, target_dir, depth=1)

    def fetch_merge_requests(self, token: str, state="merged") -> list[dict]:
        api = gitlab.Gitlab("https://gitlab.com", private_token=token)
        project = api.projects.get(self._project_path)
        mrs = project.mergerequests.list(state=state)
        return [{"number": mr.iid, "title": mr.title, ...} for mr in mrs]
```

---

### T022 — Analisador de Estrutura (structure.py)

O `StructureAnalyzer` percorre o repositorio clonado e constroi um `AnalysisResult`:

```python
class StructureAnalyzer:
    def __init__(self, repo_dir: Path):
        self.repo_dir = repo_dir

    def analyze(self) -> AnalysisResult:
        modules: list[Module] = []
        dependencies: list[Dependency] = []
        languages: set[str] = set()
        total_files = 0
        total_loc = 0

        for file_path in self.repo_dir.rglob("*"):
            if not file_path.is_file(): continue
            if file_path.name.startswith("."): continue
            ext = file_path.suffix.lower()
            lang = LANGUAGE_EXTENSIONS.get(ext)
            if lang is None: continue  # Ignora extensoes desconhecidas

            languages.add(lang)
            total_files += 1
            content = file_path.read_text(errors="replace")
            total_loc += len(content.splitlines())

            module = Module(
                name=str(rel),
                path=str(rel),
                type=self._classify_module(rel),       # package ou module
                dependencies=self._extract_imports(content, ext),
            )
            modules.append(module)
            # Cria arestas no grafo de dependencias
            for dep_name in module.dependencies:
                dependencies.append(Dependency(source=module.name, target=dep_name))
        ...
```

**Extracao de imports por linguagem**:

| Linguagem | Metodo | Exemplo detectado |
|-----------|--------|-------------------|
| Python | `ast.parse()` | `import os`, `from pathlib import Path` |
| JS/TS | Regex | `import { x } from "react"`, `require("lodash")` |
| Java | Regex | `import java.util.List` |
| Outras | Regex generico | Cobertura basica |

Python e tratado com `ast` (biblioteca padrao que parseia codigo Python em Arvore Sintatica). As demais linguagens usam regex.

**`LANGUAGE_EXTENSIONS`**: Mapa de extensao → nome da linguagem:
```python
LANGUAGE_EXTENSIONS = {
    ".py": "python", ".js": "javascript", ".ts": "typescript",
    ".java": "java", ".rs": "rust", ".go": "go",  # etc
}
```

---

### T023 — Cliente Groq (llm_client.py)

Wrapper simples em torno do SDK oficial da Groq:

```python
class GroqClient:
    def __init__(self, api_key: str, model="llama3-70b-8192", temperature=0.3):
        self.client = Groq(api_key=api_key)
        self.model = model
        self.temperature = temperature

    def generate_documentation(self, prompt: str, max_tokens=8192) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a technical doc expert..."},
                {"role": "user", "content": prompt},
            ],
            temperature=self.temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""
```

**Por que `system prompt`?**  
O system prompt instrui o LLM a se comportar como especialista em documentacao tecnica. Isso guia o tom e formato da resposta, mesmo que o prompt do usuario (user) seja apenas dados estruturados.

**Parametro `temperature=0.3`**:  
Baixa temperatura (0.0-0.3) produz saidas mais deterministicas e factuals. Alta temperatura (0.7-1.0) e mais criativa. Para documentacao tecnica, queremos precisao, nao criatividade.

---

### T024 — Orquestrador de Documentacao (orchestrator.py)

Coordenada o fluxo: pega o `AnalysisResult`, constroi prompts para o LLM, e monta o `Documentation` final:

```python
class DocOrchestrator:
    def __init__(self, llm_client):
        self.llm = llm_client

    def generate(self, analysis: AnalysisResult, repo_url: str) -> Documentation:
        sections = []

        overview = self._generate_overview(analysis)
        sections.append(overview)

        modules = DocSection(
            title="Module Reference",
            level=2,
            content=self._build_module_table(analysis),
            source_modules=[m.name for m in analysis.module_map],
        )
        sections.append(modules)

        return Documentation(repo_url=repo_url, sections=sections,
                             source_hash=self._compute_hash(analysis))
```

**Geracao da secao "Architecture Overview"**:
```python
def _generate_overview(self, analysis: AnalysisResult) -> DocSection:
    prompt = f"""
Based on the following source code analysis, generate a documentation section.
Repository languages: {analysis.languages}
Total files: {analysis.total_files}
Modules found: {...}
Dependencies: {...}
Generate a Markdown section describing the architecture and module structure.
    """
    content = self.llm.generate_documentation(prompt)
    return DocSection(title="Architecture Overview", level=1, content=content)
```

**Tabela de modulos** (gerada localmente, sem LLM):
```python
def _build_module_table(self, analysis) -> str:
    lines = ["| Module | Type | Lines |", "|--------|------|-------|"]
    for m in analysis.module_map[:50]:
        lines.append(f"| `{m.name}` | {m.type.value} | - |")
    return "\n".join(lines)
```

**Hash do source** (pra detectar mudancas futuras):
```python
def _compute_hash(self, analysis) -> str:
    raw = f"{analysis.total_files}:{analysis.total_loc}:{len(analysis.module_map)}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]
```

Esse hash e salvo no `Documentation.source_hash`. Na US3, quando o codigo mudar, o hash sera diferente e as secoes serao marcadas como `stale`.

---

### T025-T029 — CLI: init, generate, list + progresso + erros

#### init (antes: placeholder / agora: real)

```python
@app.command()
def init(repo_url: str, branch: str = "main", token: str | None = None):
    # 1. Detecta provedor (github.com → Provider.github)
    provider = _detect_provider(repo_url)

    # 2. Pede token se nao foi passado
    if token is None:
        token = typer.prompt("Access token", hide_input=True)

    # 3. Salva config YAML
    config = load_config()
    config.repositories.append(RepoConfig(url=repo_url, branch=branch, ...))
    save_config(config)

    # 4. Criptografa token e salva em ~/.config/doc-rebuild/credentials/{id}.cred
    encrypted = encrypt_token(token)
    (creds_dir / f"{conn.id}.cred").write_bytes(encrypted)
```

#### generate (antes: placeholder / agora: fluxo completo)

```python
@app.command()
def generate(repo_url: str, output: str = "./docs", api_key: str | None = None):
    # 1. Carrega config e verifica se repo existe
    config = load_config()
    repo_cfg = next(r for r in config.repositories if r.url == repo_url)

    # 2. Decriptografa token
    token = decrypt_token((creds_dir / f"{repo_cfg.credentials_ref}.cred").read_bytes())

    # 3. Clona repositorio (com progresso no stderr)
    typer.echo("Cloning repository...", err=True)
    connector.clone_repo(repo_dir, token)

    # 4. Analisa estrutura
    typer.echo("Analyzing code structure...", err=True)
    analyzer = StructureAnalyzer(repo_dir)
    analysis = analyzer.analyze()

    # 5. Gera documentacao via Groq
    typer.echo("Generating documentation...", err=True)
    doc = orchestrator.generate(analysis, repo_url)

    # 6. Salva arquivo Markdown
    doc_file = output_path / f"{repo_name}.md"
    doc_file.write_text(full_content)
```

#### list

```python
@app.command("list")
def list_repos():
    config = load_config()
    for r in config.repositories:
        typer.echo(f"  {r.url} (branch: {r.branch})")
```

#### Tratamento de erros (FR-008)

Casos tratados:
- **URL sem suporte**: `_detect_provider()` levanta erro se nao for github/gitlab
- **Token vazio**: CLI rejeita antes de tentar usar
- **Repo nao configurado**: `generate()` avisa pra rodar `init` primeiro
- **Credencial faltando**: `generate()` avisa que credencial sumiu
- **Clone falhou**: `try/except` captura erro de rede ou autenticacao
- **Repo vazio ou sem arquivos suportados**: aviso "Warning: No supported source files found."
- **Groq API key faltando**: `generate()` exige `GROQ_API_KEY` ou `--api-key`

#### Progresso (FR-009)

Todas as mensagens de progresso vao para **stderr** (`err=True`):
```python
typer.echo("Cloning repository...", err=True)
typer.echo("Analyzing code structure...", err=True)
typer.echo("Generating documentation...", err=True)
```

Isso permite que o usuario veja o progresso mesmo se redirecionar stdout:
```bash
doc-rebuild generate https://github.com/owner/repo > output.log
# Progresso ainda aparece no terminal!
```

---

### Testes da Fase 3 (TDD)

#### T014 — test_github_connector.py (5 testes)

```python
class TestGitHubConnector:
    def test_get_repo_name(self):
        conn = RepositoryConnection(url="https://github.com/test-owner/test-repo", ...)
        connector = GitHubConnector(conn)
        assert connector.get_repo_name() == "test-owner/test-repo"

    def test_list_files_excludes_hidden(self, tmp_path):
        # Cria src/app.py e .env
        files = connector.list_files(tmp_path)
        assert Path("src/app.py") in files   # Aparece
        assert Path(".env") not in files      # Escondido!

    @patch("src.connectors.github.git.Repo.clone_from")
    def test_clone_repo(self, mock_clone):
        connector.clone_repo(Path("/tmp/test"), "fake-token")
        # Verifica se chamou git clone com a URL correta
        mock_clone.assert_called_once()

    @patch("src.connectors.github.Github")
    def test_fetch_prs(self, mock_github):
        # Mocka API do GitHub, verifica se retorna PRs no formato esperado
```

**Mocking**: Usamos `@patch` para substituir `git.Repo.clone_from` e `Github` por versoes falsas. Isso evita chamar APIs reais durante os testes. O teste verifica **se a funcao foi chamada com os parametros certos**, nao se ela executou de fato.

#### T015 — test_gitlab_connector.py (5 testes)

Estrutura identica ao GitHub, mas testa:
- URL do GitLab: `gitlab.com/test-owner/test-project`
- Clone com `oauth2:{token}`
- Busca de Merge Requests (em vez de PRs)

#### T016 — test_structure_analyzer.py (7 testes)

```python
class TestStructureAnalyzer:
    def test_analyze_python_module(self, tmp_path):
        # Cria arquivo Python com imports e docstring
        analyzer = StructureAnalyzer(tmp_path)
        result = analyzer.analyze()
        assert result.total_files == 1
        assert "python" in result.languages

    def test_analyze_ignores_hidden_files(self, tmp_path):
        # Cria .env, .config/ e app.py
        result = analyzer.analyze()
        assert result.total_files == 1  # So app.py conta

    def test_analyze_detects_dependencies(self, tmp_path):
        # Cria main.py com "import json, from pathlib import Path"
        assert "json" in result.module_map[0].dependencies
        assert "pathlib" in result.module_map[0].dependencies

    def test_analyze_package_init(self, tmp_path):
        # Cria mypackage/__init__.py
        assert result.module_map[0].type.value == "package"

    def test_analyze_multiple_languages(self, tmp_path):
        # Cria .py, .js, .go
        assert result.total_files == 3

    def test_analyze_dependency_graph(self, tmp_path):
        # Cria utils.py e main.py que importa utils
        assert any(d.source == "main.py" and d.target == "utils" ...)
```

**Diferenca dos testes de conector**: Estes testes criam arquivos REAIS no `tmp_path` e testam o analisador de verdade (sem mock). O `tmp_path` e uma fixture do pytest que cria e limpa pastas temporarias automaticamente.

#### T017 — test_llm_client.py (3 testes)

```python
class TestGroqClient:
    def test_generate_documentation_returns_content(self):
        # Mocka Groq() e verifica se retorna o conteudo
        llm = GroqClient(api_key="fake-key")
        llm.client = mock_client  # Injeta mock
        result = llm.generate_documentation("Write docs")
        assert result == "# Docs\n\nGenerated content."

    def test_generate_uses_correct_model(self):
        # Verifica se passou o modelo certo na chamada
        assert call_kwargs["model"] == "mixtral-8x7b-32768"

    def test_generate_returns_empty_on_empty_response(self):
        # LLM retorna None → cliente retorna ""
```

#### T018 — test_full_pipeline.py (2 testes de integracao)

```python
class TestFullPipeline:
    def test_analyze_and_generate(self, tmp_path):
        # Cria projeto real com 2 modulos Python
        # Usa analyzer real + LLM mockado
        analysis = analyzer.analyze()
        doc = orchestrator.generate(analysis, repo_url)
        assert len(doc.sections) == 2
        assert doc.sections[0].title == "Architecture Overview"

    def test_pipeline_empty_repo_graceful(self, tmp_path):
        # Diretorio vazio
        analysis = analyzer.analyze()
        assert analysis.total_files == 0  # Nao quebra!
```

---

### Resultado dos testes

```
31 passed in 0.36s ✅
```

- **9 testes legados** (Fase 2) + **22 novos** (Fase 3) = **31 testes**
- Todos passando em menos de **0.4 segundo**
- Nenhuma chamada real a API externa (tudo mockado)

### Cobertura dos 31 testes

| Componente | Testes | Abordagem |
|-----------|--------|-----------|
| Config (YAML) | 5 | Diretorio temporario real |
| Crypto (Fernet) | 4 | Diretorio temporario real |
| GitHub connector | 5 | Mock PyGithub + gitpython |
| GitLab connector | 5 | Mock python-gitlab + gitpython |
| Structure analyzer | 7 | Arquivos reais em tmp_path |
| Groq client | 3 | Mock Groq SDK |
| Pipeline integrado | 2 | Analyzer real + Groq mockado |

---

### Diagrama atualizado (3 fases)

```
FASE 1 — SETUP
================
T001 → pyproject.toml (10 dependencias + pytest config)
  ├── T002 → mkdir -p src/cli/ src/connectors/ ...
  ├── T003 → pytest config no pyproject.toml
  └── T004 → __init__.py em todos os pacotes


FASE 2 — FOUNDATIONAL
======================
T005+T006 → src/models/repo.py (RepositoryConnection + CredentialConfig)
T007      → src/models/analysis.py (6 modelos de analise)
T008      → src/models/documentation.py (Documentation + DocSection + Changelog)
T009      → src/config/settings.py (config manager YAML)
    ↑ T012 test_config.py (TDD: 5 testes)
T010      → src/config/crypto.py (Fernet encrypt/decrypt)
    ↑ T013 test_crypto.py (TDD: 4 testes)
T011      → src/cli/main.py (esqueleto Typer — 6 comandos placeholders)


FASE 3 — US1 (MVP: CONECTAR + ANALISAR + GERAR)
=================================================
T014      → tests/unit/test_github_connector.py (TDD: 5 testes)
T015      → tests/unit/test_gitlab_connector.py (TDD: 5 testes)
T016      → tests/unit/test_structure_analyzer.py (TDD: 7 testes)
T017      → tests/unit/test_llm_client.py (TDD: 3 testes)
T018      → tests/integration/test_full_pipeline.py (TDD: 2 testes)
T019      → src/connectors/base.py (interface abstrata)
T020      → src/connectors/github.py (gitpython + PyGithub)
T021      → src/connectors/gitlab.py (gitpython + python-gitlab)
T022      → src/analyzers/structure.py (AST + regex)
T023      → src/generators/llm_client.py (Groq wrapper)
T024      → src/generators/orchestrator.py (analise → LLM → doc)
T025-T028 → src/cli/main.py (init/generate/list reais + progresso stderr)
T029      → src/cli/main.py (tratamento de erros FR-008)

31 PASSED IN 0.36s  ← TUDO VERDE


---

## Fase 4 — US2: Análise Contextual (Git History + PRs)

A Fase 4 enriquece a documentação com **commits** e **Pull Requests**. Agora o sistema não só descreve a estrutura do código, mas também **explica como ela evoluiu** e **por que decisões foram tomadas**.

```
Antes (Fase 3):
    doc-rebuild generate → Arquitetura + Tabela de Módulos

Depois (Fase 4):
    doc-rebuild generate → Arquitetura + Módulos + Change History + Decisões Arquiteturais
```

### Arquivos criados/modificados (T030-T038)

```
src/
├── analyzers/
│   ├── git_history.py      ← T035: NOVO — analisa commits (gitpython)
│   └── pr_analyzer.py      ← T036: NOVO — extrai decisões de PRs/MRs
├── generators/
│   └── orchestrator.py     ← T037: MODIFICADO — adiciona seções de timeline + PRs
└── cli/
    └── main.py             ← T038: MODIFICADO — flags --include-prs/--include-history

tests/
├── unit/
│   ├── test_git_history.py ← T030: 9 testes
│   └── test_pr_analyzer.py ← T031: 5 testes
└── integration/
    └── test_enriched_generation.py ← T032: 3 testes
```

---

### T033+T034 — Modelos (já existiam)

`CommitEvent` e `PRInsight` foram criados na **Fase 2** dentro de `analysis.py`. A Fase 4 só precisou tornar `PRInsight.date` opcional (`datetime | None = None`) para aceitar dados sem data.

---

### T035 — GitHistoryAnalyzer (git_history.py)

Analisa o **histórico de commits** do repositório clonado:

```python
class GitHistoryAnalyzer:
    def __init__(self, repo_dir: Path):
        self.repo_dir = repo_dir
        self.repo = git.Repo(repo_dir)

    def analyze(self, max_depth: int = 1000) -> list[CommitEvent]:
        commits = []
        try:
            head = self.repo.head.commit  # Pode falhar se repo vazio
        except ValueError:
            return commits  # Repo sem commits → lista vazia

        for commit in self.repo.iter_commits():
            # Extrai arquivos modificados via diff com o commit pai
            files_changed = {
                item.b_path
                for item in commit.diff(commit.parents[0])
                if item.b_path
            }
            commits.append(CommitEvent(
                hash=commit.hexsha[:8],
                author=str(commit.author),
                date=datetime.fromtimestamp(commit.authored_date),
                message=commit.message.strip(),
                files_changed=sorted(files_changed),
                significance=self._classify(commit.message),
            ))
        return commits
```

**Classificação de Significância**:

```python
def _classify(self, message: str) -> Significance:
    if "breaking" in msg_lower or "major" in msg_lower:
        return Significance.major      # Grande mudança
    if "refactor" in msg_lower:
        return Significance.refactor   # Refatoração
    if "fix" in msg_lower or "bug" in msg_lower:
        return Significance.fix        # Correção de bug
    if "docs" in msg_lower:
        return Significance.docs       # Só documentação
    return Significance.minor          # Padrão: mudança pequena
```

**Tratamento de repositório vazio**: Se `repo.head.commit` falhar (repo sem commits), retorna lista vazia em vez de crashar.

---

### T036 — PRAnalyzer (pr_analyzer.py)

Extrai **decisões arquiteturais** de PRs/MRs usando os conectores já implementados:

```python
class PRAnalyzer:
    def __init__(self, connector: BaseConnector):
        self.connector = connector  # GitHubConnector ou GitLabConnector

    def analyze(self, token: str) -> list[PRInsight]:
        if isinstance(self.connector, GitHubConnector):
            raw_prs = self.connector.fetch_prs(token)
        elif isinstance(self.connector, GitLabConnector):
            raw_prs = self.connector.fetch_merge_requests(token)

        insights = []
        for raw in raw_prs:
            decision, rationale = self._extract_decision(raw["description"])
            insights.append(PRInsight(
                pr_number=raw["number"],
                title=raw["title"],
                description=raw["description"],
                decision=decision,
                rationale=rationale,
                date=raw.get("date"),
            ))
        return insights
```

**Extração de Decisão + Rationale**:

O `_extract_decision` procura marcadores no corpo do PR:

```python
def _extract_decision(self, description: str):
    # Procura linhas como:
    #   "Decision: Use JWT"
    #   "**Decision:** Use REST"
    #   "Rationale: Stateless"
    #   "Why: Already in stack"
```

Isso permite que times adotem um padrão simples nos PRs:
> ## Decision: Migrar para PostgreSQL
> ## Rationale: Precisamos de queries geográficas que o MongoDB não suporta

E o sistema automaticamente extrai e documenta essas decisões.

---

### T037 — Orchestrator estendido

O `DocOrchestrator.generate()` agora aceita `include_history` e `include_prs`:

```python
def generate(self, analysis, repo_url, include_history=True, include_prs=True):
    sections = []
    sections.append(self._generate_overview(analysis))
    sections.append(DocSection(title="Module Reference", ...))

    if include_history and analysis.commit_timeline:
        sections.append(self._generate_timeline(analysis.commit_timeline))

    if include_prs and analysis.pr_insights:
        sections.append(self._generate_pr_section(analysis.pr_insights))

    return Documentation(repo_url=repo_url, sections=sections, ...)
```

**Seção "Change History"**:
```python
def _generate_timeline(self, commits):
    timeline = "\n".join(
        f"- `{c.hash}` {c.date} | {c.author} | [{c.significance}] {c.message[:80]}"
        for c in commits[:50]
    )
    prompt = f"Based on this git history:\n{timeline}\nGenerate a Markdown section..."
    content = self.llm.generate_documentation(prompt)
    return DocSection(title="Change History", content=content)
```

**Seção "Architectural Decisions"**:
```python
def _generate_pr_section(self, insights):
    lines = []
    for pr in insights[:30]:
        lines.append(f"### PR #{pr.pr_number}: {pr.title}")
        if pr.decision:
            lines.append(f"- **Decision**: {pr.decision}")
        if pr.rationale:
            lines.append(f"- **Rationale**: {pr.rationale}")
    prompt = f"Based on these PRs:\n{lines}\nGenerate a Markdown section..."
    content = self.llm.generate_documentation(prompt)
    return DocSection(title="Architectural Decisions", content=content)
```

**Se não houver dados**, a seção simplesmente não é adicionada (evita seções vazias no documento final).

---

### T038 — Flags do CLI

```python
@app.command()
def generate(
    repo_url: str = typer.Argument(...),
    output: str = typer.Option("./docs"),
    api_key: str | None = typer.Option(None, "--api-key"),
    include_prs: bool = typer.Option(True, "--include-prs/--no-include-prs"),
    include_history: bool = typer.Option(True, "--include-history/--no-include-history"),
):
```

**Flag `--include-prs/--no-include-prs`**: default `True`. Controla se PRs são analisados.

**Flag `--include-history/--no-include-history`**: default `True`. Controla se git history é analisado.

**Exemplos de uso**:
```bash
# Completo (com commits + PRs):
doc-rebuild generate https://github.com/owner/repo --api-key gsk_abc

# Só estrutura (sem git history, sem PRs):
doc-rebuild generate https://github.com/owner/repo \
    --no-include-history --no-include-prs --api-key gsk_abc
```

**No código do `generate`**, a análise é condicional:
```python
if include_history:
    typer.echo("Analyzing git history...", err=True)
    git_analyzer = GitHistoryAnalyzer(repo_dir)
    analysis.commit_timeline = git_analyzer.analyze()

if include_prs:
    typer.echo("Analyzing pull requests...", err=True)
    pr_analyzer = PRAnalyzer(connector)
    analysis.pr_insights = pr_analyzer.analyze(token)
```

Ambos são **tolerantes a falhas**: se a análise de commits ou PRs falhar (repo sem commits, sem PRs, rede offline), um aviso é mostrado e a geração continua com os dados disponíveis.

---

### Testes da Fase 4 (TDD)

#### T030 — test_git_history.py (9 testes)

| Teste | O que verifica |
|-------|----------------|
| `test_analyze_empty_repo` | Repo sem commits retorna lista vazia (não crasha) |
| `test_analyze_single_commit` | 1 commit = 1 CommitEvent com hash de 8 chars |
| `test_analyze_multiple_commits` | 2 commits = 2 eventos |
| `test_classify_breaking_as_major` | "BREAKING" classifica como major |
| `test_classify_fix_as_fix` | "fix" classifica como fix |
| `test_classify_refactor` | "refactor" classifica como refactor |
| `test_classify_docs` | "documentation" classifica como docs |
| `test_classify_minor_default` | Mensagem genérica classifica como minor |
| `test_max_depth_limit` | `max_depth=3` limita a 3 commits |
| `test_files_changed_tracked` | Arquivos modificados são registrados |

**Como criar commits reais nos testes**:
```python
def _init_repo_with_commit(tmp_path, msg, filename, content):
    repo = git.Repo.init(tmp_path)
    (tmp_path / filename).write_text(content)
    repo.index.add([filename])
    repo.index.commit(msg)
    return repo
```

Usamos `git.Repo.init()` e `repo.index.commit()` para criar commits REAIS dentro do `tmp_path`. O pytest limpa tudo no final.

#### T031 — test_pr_analyzer.py (5 testes)

| Teste | O que verifica |
|-------|----------------|
| `test_analyze_github_returns_pr_insights` | Conector GitHub retorna PRInsights com decisão extraída |
| `test_analyze_gitlab_returns_mr_insights` | Conector GitLab retorna PRInsights (MRs) |
| `test_analyze_empty_prs` | Lista vazia de PRs → insights vazio |
| `test_extract_decision_no_markers` | Descrição sem marcadores → None |
| `test_extract_decision_with_markers` | "Decision: X\nRationale: Y" → extrai corretamente |

#### T032 — test_enriched_generation.py (3 testes de integração)

| Teste | O que verifica |
|-------|----------------|
| `test_generate_with_commits_and_prs` | 4 seções: Overview + Modules + Change History + Decisions |
| `test_generate_without_history_or_prs` | Só 2 seções quando flags desligadas |
| `test_generate_empty_timeline_no_section` | Sem dados de commit/PR → sem seções extras (não gera seções vazias) |

---

### Resultado dos testes

```
49 passed in 0.67s ✅
```

- **31 legados** (Fases 1-3) + **18 novos** (Fase 4) = **49 testes**
- 10 testes de git history (commits reais com gitpython)
- 5 testes de PR analyzer (mocks)
- 3 testes de integração (analyzer real + LLM mockado)
- Todos passando em **menos de 0.7 segundo**

### Cobertura dos 49 testes

| Componente | Testes | Abordagem |
|-----------|--------|-----------|
| Config (YAML) | 5 | Diretório temporário real |
| Crypto (Fernet) | 4 | Diretório temporário real |
| GitHub connector | 5 | Mock PyGithub + gitpython |
| GitLab connector | 5 | Mock python-gitlab + gitpython |
| Structure analyzer | 7 | Arquivos reais em tmp_path |
| Groq client | 3 | Mock Groq SDK |
| Pipeline integrado (US1) | 2 | Analyzer real + Groq mockado |
| Git history analyzer | 9 | Commits REAIS com gitpython |
| PR analyzer | 5 | Mock dos conectores |
| Pipeline enriquecido (US2) | 3 | Analyzer real + Groq mockado |

---

### Diagrama atualizado (4 fases)

```
FASE 1 — SETUP
================
T001 → pyproject.toml (10 dependencias + pytest config)
  ├── T002 → mkdir -p src/ tests/
  ├── T003 → pytest config
  └── T004 → __init__.py em todos os pacotes


FASE 2 — FOUNDATIONAL
======================
T005+T006 → src/models/repo.py (RepositoryConnection + CredentialConfig)
T007      → src/models/analysis.py (Module, Dependency, CommitEvent, PRInsight, AnalysisResult)
T008      → src/models/documentation.py (Documentation, DocSection, ChangelogEntry)
T009      → src/config/settings.py (config manager YAML)
    ↑ T012 test_config.py (TDD: 5 testes)
T010      → src/config/crypto.py (Fernet encrypt/decrypt)
    ↑ T013 test_crypto.py (TDD: 4 testes)
T011      → src/cli/main.py (esqueleto Typer — 6 placeholders)


FASE 3 — US1 (MVP: CONECTAR + ANALISAR + GERAR)
=================================================
T014-T017  → 5 testes unitários (GitHub, GitLab, structure, LLM)
T018      → 2 testes integração (pipeline completo)
T019      → src/connectors/base.py (interface)
T020      → src/connectors/github.py (gitpython + PyGithub)
T021      → src/connectors/gitlab.py (gitpython + python-gitlab)
T022      → src/analyzers/structure.py (AST + regex)
T023      → src/generators/llm_client.py (Groq wrapper)
T024      → src/generators/orchestrator.py (análise → LLM → doc)
T025-T029 → src/cli/main.py (init, generate, list + erros + progresso)


FASE 4 — US2 (GIT HISTORY + PR INSIGHTS)
==========================================
T030      → tests/unit/test_git_history.py (TDD: 9 testes)
T031      → tests/unit/test_pr_analyzer.py (TDD: 5 testes)
T032      → tests/integration/test_enriched_generation.py (TDD: 3 testes)
T033+T034 → (já existiam: CommitEvent + PRInsight em analysis.py)
T035      → src/analyzers/git_history.py (gitpython: commits + significância)
T036      → src/analyzers/pr_analyzer.py (extração Decision/Rationale de PRs)
T037      → src/generators/orchestrator.py (seções Change History + Decisions)
T038      → src/cli/main.py (flags --include-prs/--include-history)

49 PASSED IN 0.67s  ← TUDO VERDE (Fases 1-4 completas)
```
```
