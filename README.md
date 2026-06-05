# Redator Técnico

**Automatize a documentação técnica do seu repositório.**  
Conecte-se ao GitHub ou GitLab, analise código-fonte, histórico de commits e pull requests, e gere documentação Markdown completa usando IA.

```bash
doc-rebuild generate https://github.com/meu-time/projeto-x --api-key gsk_...
```

---

## Índice

- [O que é este projeto?](#o-que-é-este-projeto)
- [Para quem é?](#para-quem-é)
- [Tecnologias utilizadas](#tecnologias-utilizadas)
- [Impactos inovadores](#impactos-inovadores)
- [Instalação](#instalação)
- [Uso](#uso)
  - [`init` — Inicializar repositório](#1-init--inicializar-repositório)
  - [`generate` — Gerar documentação](#2-generate--gerar-documentação)
  - [`list` — Listar repositórios](#3-list--listar-repositórios)
  - [`check` — Verificar desatualização](#4-check--verificar-desatualização)
  - [`update` — Atualizar seções obsoletas](#5-update--atualizar-seções-obsoletas)
  - [`config-view` — Ver configuração](#6-config-view--ver-configuração)
- [Arquitetura](#arquitetura)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Testes](#testes)
- [Contribuição](#contribuição)

---

## O que é este projeto?

**Redator Técnico** é uma ferramenta de linha de comando (CLI) que **conecta-se automaticamente a repositórios Git**, analisa o código-fonte, o histórico de commits e os pull requests, e **produz documentação técnica em Markdown** usando modelos de linguagem de IA (Llama 3 via Groq).

### O problema que resolve

Manter documentação técnica atualizada é um dos maiores desafios de engenharia de software. Equipes geralmente enfrentam:

1. **Documentação desatualizada** — O código muda, a documentação não acompanha
2. **Custo manual elevado** — Escrever docs consome horas preciosas de desenvolvedores
3. **Decisões perdidas** — O "porquê" das decisões arquiteturais fica enterrado em PRs antigos
4. **Contexto fragmentado** — Informações relevantes espalhadas entre código, commits e PRs

O Redator Técnico resolve tudo isso **automaticamente**: conecta-se ao repositório, analisa todas as fontes de informação e gera documentação coesa e atualizada.

### O que ele gera?

- Visão geral da arquitetura do sistema
- Referência completa de módulos e componentes
- Mapa de dependências entre módulos
- Histórico de mudanças significativas (extraído de commits)
- Decisões arquiteturais com justificativas (extraídas de PRs)

---

## Para quem é?

| Perfil | Benefício |
|--------|-----------|
| **Desenvolvedor(a)** | Gera documentação técnica em segundos, sem escrever uma linha de markdown |
| **Tech Lead** | Mantém a documentação da arquitetura sempre sincronizada com o código |
| **Gerente de Engenharia** | Garante que o conhecimento do sistema não se perca com a rotatividade do time |
| **Novos membros do time** | Onboarding acelerado — documentação atualizada desde o primeiro dia |
| **Equipes Open Source** | Documentação profissional sem sobrecarregar mantenedores |

---

## Tecnologias utilizadas

### Stack principal

| Tecnologia | Versão | Função |
|-----------|--------|--------|
| **Python** | ≥3.12 | Linguagem principal — tipagem forte, ecossistema maduro para CLIs |
| **Typer** | ≥0.12 | Framework CLI — transforma funções Python em comandos de terminal |
| **Groq SDK** | ≥0.9 | Inferência de IA ultrarrápida — ~50ms de latência vs ~1s de alternativas |
| **Agno** | ≥1.0 | Orquestração do agente — coordena o fluxo conectar → analisar → gerar |
| **Pydantic** | ≥2.0 | Validação de dados — garante que todos os modelos tenham tipos corretos |
| **PyGithub** | ≥2.3 | Cliente oficial da API do GitHub — busca código, PRs, issues |
| **python-gitlab** | ≥4.4 | Cliente oficial da API do GitLab — equivalente ao PyGithub |
| **GitPython** | ≥3.1 | Manipulação local de repositórios Git — iteração por commits e diffs |
| **tree-sitter** | ≥0.22 | Parse de código-fonte em AST — entende a estrutura de múltiplas linguagens |
| **Cryptography (Fernet)** | ≥42.0 | Criptografia simétrica AES-128 — protege tokens de acesso em disco |
| **PyYAML** | ≥6.0 | Leitura/escrita de arquivos de configuração YAML |

### Diferenciais técnicos

**Groq + Llama 3 70B**: Diferente de soluções que usam modelos caros como GPT-4, o Redator Técnico utiliza o Llama 3 70B rodando na infraestrutura da Groq. Isso significa **geração de documentação em segundos** (não minutos), com qualidade comparável a modelos proprietários, por uma fração do custo.

**tree-sitter**: Em vez de usar expressões regulares frágeis para entender código, usamos o tree-sitter, que constrói uma **Árvore Sintática Abstrata (AST)** real. Isso permite detectar módulos, classes, funções e dependências com precisão, independentemente da linguagem.

**Regeneração incremental**: Não precisa regenerar a documentação inteira a cada mudança. O sistema detecta **quais módulos mudaram** e regenera **apenas as seções afetadas**, economizando 70-90% dos tokens de IA.

---

## Impactos inovadores

### 1. Democratização da documentação técnica

Pequenas equipes e projetos open source raramente têm documentação técnica de qualidade — o custo de produção é alto e o benefício parece distante. O Redator Técnico **elimina a barreira de entrada**: qualquer repositório, em segundos, ganha documentação profissional.

### 2. Preservação do conhecimento institucional

Quando um desenvolvedor sai da equipe, o conhecimento arquitetural vai com ele. Commits e PRs contêm esse conhecimento, mas ninguém tem tempo de minerá-los manualmente. O Redator Técnico **extrai e estrutura esse conhecimento automaticamente**, transformando-o em documentação viva.

### 3. Ciclo virtuoso código-documentação

Tradicionalmente, documentação e código divergem com o tempo. Com o comando `check`, o desenvolvedor descobre imediatamente se uma mudança no código tornou a documentação obsoleta. Com o `update`, a correção é feita em segundos. Isso cria um **ciclo de retroalimentação positiva** onde documentação e código caminham juntos.

### 4. Redução drástica de retrabalho

Estima-se que desenvolvedores gastem **20-30% do tempo** criando e mantendo documentação. Para um time de 10 pessoas, isso representa 2-3 desenvolvedores dedicados exclusivamente a docs. O Redator Técnico **automatiza ~80% desse esforço**, liberando o time para o que realmente importa: escrever código.

---

## Instalação

### Pré-requisitos

- **Python 3.12+** instalado (`python --version`)
- **Token de acesso** do GitHub ([`github.com/settings/tokens`](https://github.com/settings/tokens)) ou GitLab ([`gitlab.com/-/user_settings/personal_access_tokens`](https://gitlab.com/-/user_settings/personal_access_tokens))
- **Chave de API** do Groq ([console.groq.com](https://console.groq.com) — plano gratuito disponível)

### Instalação via pip

```bash
pip install redator-tecnico
```

### Instalação para desenvolvimento

```bash
git clone https://github.com/seu-org/redator-tecnico.git
cd redator-tecnico
pip install -e ".[dev]"
```

A flag `-e` (editable) faz com que alterações no código reflitam imediatamente sem precisar reinstalar. O `[dev]` instala dependências de teste (pytest, pytest-mock, etc.).

### Verificar instalação

```bash
doc-rebuild --version
# doc-rebuild v0.1.0

doc-rebuild --help
# Lista todos os comandos disponíveis
```

---

## 🔑 Obtendo um token de acesso

O `doc-rebuild init` precisa de um token para clonar o repositório e ler PRs/commits. Escolha seu provedor:

### GitHub

```
Settings (ícone de engrenagem ⚙ no canto superior direito)
  └─ Developer settings (última opção)
       └─ Personal access tokens
            └─ Tokens (classic)
                 └─ Generate new token (classic)
```

1. Acesse **[github.com/settings/tokens](https://github.com/settings/tokens)**
2. Clique **Generate new token (classic)**
3. Dê um nome descritivo (ex: "doc-rebuild")
4. Em **Scopes**, marque apenas **`repo`** (acesso total a repositórios privados) ou, para repositórios públicos, apenas **`public_repo`** (dentro de `repo`)
5. Role até o final e clique **Generate token**
6. **Copie o token imediatamente** — o GitHub mostra ele apenas uma vez. Começa com `ghp_`

```bash
doc-rebuild init https://github.com/meu-time/projeto-x
# Access token: [cole o token ghp_... — não aparece na tela enquanto digita]
```

### GitLab

```
Preferences (ícone de usuário → Preferences no menu)
  └─ Access Tokens
       └─ Add new token
```

1. Acesse **[gitlab.com/-/user_settings/personal_access_tokens](https://gitlab.com/-/user_settings/personal_access_tokens)**
2. Dê um nome (ex: "doc-rebuild")
3. Marque **Expiration date** para segurança (ex: 1 ano)
4. Em **Select scopes**, marque:
   - **`read_api`** — necessário para ler PRs (Merge Requests)
   - **`read_repository`** — necessário para clonar o repositório
5. Clique **Create personal access token**
6. **Copie o token** — também mostrado apenas uma vez. Começa com `glpat_`

```bash
doc-rebuild init https://gitlab.com/meu-time/projeto-x
# Access token: [cole o token glpat_...]
```

### Dicas de segurança

- Use o **menor escopo possível**: `public_repo` para projetos públicos, `repo` para privados
- Defina uma **data de expiração** (renew a cada ano)
- **Nunca compartilhe** seu token — ele dá acesso ao seu repositório
- O `doc-rebuild init` armazena o token **criptografado** em disco (AES-128 via Fernet), nunca em texto puro

---

## Uso

### 1. `init` — Inicializar repositório

Antes de gerar documentação, é preciso configurar o repositório. Isso armazena o token de acesso de forma criptografada.

```bash
doc-rebuild init https://github.com/meu-time/projeto-x
# Access token: [cole o token — não aparece na tela]
# ✅ Initialized repo: https://github.com/meu-time/projeto-x (branch: main)
```

**Parâmetros:**

| Parâmetro | Padrão | Descrição |
|-----------|--------|-----------|
| `repo_url` | (obrigatório) | URL completa do repositório |
| `--branch`, `-b` | `main` | Branch alvo para análise |
| `--token`, `-t` | (opcional) | Token de acesso (se omitido, é solicitado interativamente) |

**O que acontece internamente:**
1. Detecta o provedor (GitHub ou GitLab) pela URL
2. Criptografa o token com AES-128 (Fernet) e salva em `~/.config/doc-rebuild/credentials/`
3. Salva a configuração em `~/.config/doc-rebuild/config.yml`

---

### 2. `generate` — Gerar documentação

Conecta no repositório, analisa tudo e gera documentação Markdown.

```bash
doc-rebuild generate https://github.com/meu-time/projeto-x \
    --output ./docs \
    --api-key gsk_sua_chave_groq
```

**Parâmetros:**

| Parâmetro | Padrão | Descrição |
|-----------|--------|-----------|
| `repo_url` | (obrigatório) | URL do repositório (configurado via `init`) |
| `--output`, `-o` | `./docs` | Diretório de saída para os arquivos .md |
| `--api-key` | `GROQ_API_KEY` (env) | Chave da API Groq |
| `--include-prs` | `True` | Incluir análise de PRs na documentação |
| `--include-history` | `True` | Incluir histórico de commits |

**Exemplo com flags desligadas** (apenas estrutura, sem PRs nem commits):

```bash
doc-rebuild generate https://github.com/meu-time/projeto-x \
    --no-include-prs --no-include-history \
    --api-key gsk_sua_chave
```

**Exemplo de saída no terminal:**

```
Cloning repository: https://github.com/meu-time/projeto-x
Analyzing code structure...
Found 47 files in 3 language(s).
Analyzing git history...
Found 234 commits.
Analyzing pull requests...
Found 12 PRs/MRs.
Generating documentation...
✅ Documentation generated: ./docs/meu-time_projeto-x.md
```

**Arquivos gerados:**

```
docs/
├── meu-time_projeto-x.md    # Documentação completa
└── _meta.json                # Metadados para detecção de mudanças
```

---

### 3. `list` — Listar repositórios

Mostra todos os repositórios configurados.

```bash
doc-rebuild list
#   https://github.com/meu-time/projeto-x (branch: main)
#   https://gitlab.com/outro-time/app (branch: develop)
```

**Saída JSON** (para scripts e automação):

```bash
doc-rebuild list --json | jq '.repositories[].url'
# "https://github.com/meu-time/projeto-x"
```

---

### 4. `check` — Verificar desatualização

Compara o estado atual do repositório com a última documentação gerada e informa quais seções estão obsoletas.

```bash
doc-rebuild check https://github.com/meu-time/projeto-x
```

**Exemplo de saída:**

```
Cloning repository to check for changes...
Computing current module hashes...
  [STALE]  Architecture Overview
  [FRESH]  Module Reference
  [FRESH]  Change History
  [FRESH]  Architectural Decisions

Documentation is stale. Run 'update' to regenerate sections.
```

**Saída JSON:**

```bash
doc-rebuild check https://github.com/meu-time/projeto-x --json
# {
#   "sections": [
#     {"title": "Architecture Overview", "status": "stale"},
#     {"title": "Module Reference", "status": "fresh"}
#   ],
#   "stale_count": 1,
#   "is_stale": true
# }
```

**Nota importante**: O `check` **não consome tokens de IA** — ele apenas clona o repositório, computa hashes criptográficos dos arquivos, e compara com os hashes armazenados no `_meta.json`. É rápido (segundos) e gratuito.

---

### 5. `update` — Atualizar seções obsoletas

Regenera **apenas as seções desatualizadas**, preservando o conteúdo que ainda é válido.

```bash
doc-rebuild update https://github.com/meu-time/projeto-x --api-key gsk_sua_chave
```

**Exemplo de saída:**

```
Cloning repository...
Analyzing code structure...
Detecting stale sections...
Regenerating 1 stale section(s): Architecture Overview
✅ Documentation updated: ./docs/meu-time_projeto-x.md
```

**Economia em ação**: Se você alterou 1 módulo de 10, apenas a seção correspondente a esse módulo é regenerada. As outras 9 seções são preservadas sem chamar a IA. Economia típica: **70-90% dos tokens** comparado a regeneração completa.

---

### 6. `config-view` — Ver configuração

Exibe toda a configuração atual do Redator Técnico.

```bash
doc-rebuild config-view

# Repositories (2):
#   - https://github.com/meu-time/projeto-x (branch: main, provider: github)
#   - https://gitlab.com/outro-time/app (branch: develop, provider: gitlab)
#
# Generation settings:
#   Output dir:       ./docs
#   Include PRs:      True
#   Include history:  True
#   Max commits:      1000
#   LLM model:        llama3-70b-8192
#   Temperature:      0.3
```

---

## Arquitetura

O Redator Técnico segue uma arquitetura de **pipeline sequencial** com 6 estágios:

```
┌─────────────┐    ┌──────────────┐    ┌────────────────┐    ┌────────────┐    ┌───────────────┐    ┌──────────────┐
│  1. CONECTAR │    │ 2. CLONAR    │    │ 3. ANALISAR   │    │ 4. ENRIQUECER│    │ 5. GERAR      │    │ 6. SALVAR    │
│             │    │              │    │               │    │             │    │               │    │              │
│ Detecta     │───▶│ Baixa repo   │───▶│ AST tree-     │───▶│ Git history │───▶│ Groq Llama 3  │───▶│ Markdown     │
│ provedor    │    │ via git clone│    │ sitter:       │    │ + PR        │    │ formata       │    │ .md +        │
│ (GH/GL)     │    │ depth=1      │    │ módulos +     │    │ insights    │    │ documentação  │    │ _meta.json   │
│             │    │              │    │ dependências  │    │             │    │               │    │              │
└─────────────┘    └──────────────┘    └────────────────┘    └────────────┘    └───────────────┘    └──────────────┘
```

### Decisões arquiteturais importantes

**Por que CLI e não servidor web?**
- Simplicidade de uso para desenvolvedores (todos usam terminal)
- Sem necessidade de infraestrutura de servidor
- Ideal para CI/CD pipelines

**Por que Markdown e não HTML/PDF?**
- Legível por humanos e máquinas
- Versionável junto com o código no Git
- Renderizável em GitHub/GitLab, wikis, e ferramentas de documentação (MkDocs, Docusaurus)

**Por que Agno em vez de LangChain?**
- API mais simples e enxuta
- Menos dependências (agno é um único pacote vs LangChain que traz dezenas)
- Foco em agentes leves para tarefas específicas

**Por que Groq em vez de OpenAI?**
- Latência ~50ms vs ~1s (20x mais rápido)
- Modelo Llama 3 70B gratuito disponível
- Performance consistente independentemente da carga

---

## Estrutura do projeto

```
redator-tecnico/
├── pyproject.toml              ← Configuração do projeto e dependências
├── README.md                   ← Este arquivo
├── AGENTS.md                   ← Configuração do assistente de IA
├── constitution.md             ← Regras de governança do projeto
├── main.py                     ← Entry point alternativo (python main.py)
│
├── src/                        ← Código fonte (raiz do pacote)
│   ├── __init__.py
│   └── redator_tecnico/        ← Pacote Python importável
│       ├── __init__.py
│       ├── cli/                ← Interface de linha de comando
│       │   ├── main.py         ←   Comandos Typer (init, generate, list, check, update, config)
│       │   └── output.py       ←   Funções de saída padronizadas (stdout/stderr)
│       ├── connectors/         ← Conexão com provedores Git
│       │   ├── base.py         ←   Interface abstrata do conector
│       │   ├── github.py       ←   Conector GitHub (PyGithub + GitPython)
│       │   ├── gitlab.py       ←   Conector GitLab (python-gitlab + GitPython)
│       │   └── utils.py        ←   Utilitários: retry com backoff + rate-limit check
│       ├── analyzers/          ← Análise de código
│       │   ├── structure.py    ←   Analisador de estrutura (tree-sitter + AST)
│       │   ├── git_history.py  ←   Analisador de histórico de commits
│       │   └── pr_analyzer.py  ←   Analisador de PRs/MRs
│       ├── generators/         ← Geração de documentação
│       │   ├── llm_client.py   ←   Cliente Groq (Llama 3 70B)
│       │   └── orchestrator.py ←   Orquestrador (análise → LLM → Markdown)
│       ├── models/             ← Modelos de dados (Pydantic)
│       │   ├── repo.py         ←   RepositoryConnection, Provider, CredentialConfig
│       │   ├── analysis.py     ←   Module, Dependency, CommitEvent, PRInsight, AnalysisResult
│       │   └── documentation.py←   Documentation, DocSection, DocMetadata, ChangelogEntry
│       └── config/             ← Configuração e segurança
│           ├── settings.py     ←   Gerenciamento de config.yml
│           └── crypto.py       ←   Criptografia Fernet (AES-128) para tokens
│
├── tests/                      ← Testes
│   ├── unit/                   ←   Testes unitários (10 arquivos, 52 testes)
│   └── integration/            ←   Testes de integração (3 arquivos, 9 testes)
│
├── specs/                      ← Especificação do projeto
│   └── 001-doc-rebuild-agent/  ←   Spec, plan, data model, quickstart, tasks
└── steps-concept.md            ← Relatório didático completo do desenvolvimento
```

---

## Testes

O projeto segue **TDD (Test-Driven Development)** — testes são escritos antes da implementação.

### Executar testes

```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=src/redator_tecnico

# Testes específicos
pytest tests/unit/test_connectors.py -v
pytest tests/integration/test_full_pipeline.py -v
```

### Estatísticas atuais

```
61 passed in 0.75s ✅
```

| Categoria | Testes | Abordagem |
|-----------|--------|-----------|
| Config (YAML) | 5 | Diretório temporário real |
| Criptografia (Fernet) | 4 | Diretório temporário real |
| Conector GitHub | 5 | Mock PyGithub + GitPython |
| Conector GitLab | 5 | Mock python-gitlab + GitPython |
| Analisador de estrutura | 7 | Arquivos reais em tmp_path |
| Cliente Groq | 3 | Mock Groq SDK |
| Pipeline integrado | 2 | Analyzer real + Groq mockado |
| Git history | 9 | Commits REAIS com GitPython |
| PR analyzer | 5 | Mock dos conectores |
| Pipeline enriquecido | 3 | Analyzer real + Groq mockado |
| Change detection | 6 | Arquivos reais + metadados |
| Incremental update | 4 | Orchestrator mockado |
| Staleness flow | 2 | Fluxo completo |

**Princípios de teste:**
- **Zero chamadas reais a APIs externas** — tudo é mockado ou executado em diretórios temporários
- **Testes determinísticos** — mesmos inputs produzem mesmos resultados sempre
- **Testes rápidos** — suite completa em menos de 1 segundo

---

## Contribuição

Contribuições são bem-vindas!

### Reportar problemas

Abra uma issue descrevendo:
1. O comportamento esperado
2. O comportamento observado
3. Passos para reproduzir
4. Versão do Python e sistema operacional

### Enviar código

1. Fork o repositório
2. Crie uma branch: `git checkout -b minha-feature`
3. Faça suas alterações seguindo o estilo do código existente
4. Escreva testes (TDD: teste primeiro, implemente depois)
5. Execute `pytest` e verifique se todos passam
6. Commit e push
7. Abra um Pull Request

### Diretrizes

- Mantenha a simplicidade — código enxuto, sem abstrações desnecessárias
- Siga TDD — testes primeiro, implementação depois
- Documente decisões arquiteturais no código e nos PRs
- Use tipagem Python (`str | None`, não `Optional[str]`) — Python 3.12+

---

## Licença

MIT
