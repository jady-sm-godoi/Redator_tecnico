import sys
import tempfile
from pathlib import Path
from typing import Optional
import typer
from src.config.settings import load_config, save_config, AppConfig, RepoConfig
from src.config.crypto import encrypt_token, decrypt_token
from src.connectors.github import GitHubConnector
from src.connectors.gitlab import GitLabConnector
from src.models.repo import RepositoryConnection, Provider
from src.analyzers.structure import StructureAnalyzer
from src.analyzers.git_history import GitHistoryAnalyzer
from src.analyzers.pr_analyzer import PRAnalyzer
from src.generators.llm_client import GroqClient
from src.generators.orchestrator import DocOrchestrator

app = typer.Typer()


def _detect_provider(url: str) -> Provider:
    if "github.com" in url:
        return Provider.github
    if "gitlab.com" in url:
        return Provider.gitlab
    raise typer.BadParameter(f"Unsupported provider in URL: {url}")


def _build_connector(conn: RepositoryConnection):
    if conn.provider == Provider.github:
        return GitHubConnector(conn)
    elif conn.provider == Provider.gitlab:
        return GitLabConnector(conn)
    raise ValueError(f"Unknown provider: {conn.provider}")


@app.command()
def init(
    repo_url: str = typer.Argument(..., help="Repository URL"),
    branch: str = typer.Option("main", "--branch", "-b", help="Target branch"),
    token: Optional[str] = typer.Option(None, "--token", "-t", help="Access token (omit to prompt)"),
):
    """Initialize configuration for a new repository."""
    try:
        provider = _detect_provider(repo_url)
    except typer.BadParameter as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

    if token is None:
        token = typer.prompt("Access token", hide_input=True)

    if not token:
        typer.echo("Error: Token cannot be empty.", err=True)
        raise typer.Exit(1)

    config = load_config()

    existing = [r for r in config.repositories if r.url == repo_url]
    if existing:
        typer.echo(f"Repository already configured: {repo_url}", err=True)
        raise typer.Exit(1)

    conn = RepositoryConnection(url=repo_url, provider=provider, branch=branch)
    encrypted = encrypt_token(token)

    config.repositories.append(
        RepoConfig(
            url=repo_url,
            branch=branch,
            provider=provider.value,
            credentials_ref=str(conn.id),
        )
    )
    save_config(config)

    creds_dir = Path.home() / ".config" / "doc-rebuild" / "credentials"
    creds_dir.mkdir(parents=True, exist_ok=True)
    (creds_dir / f"{conn.id}.cred").write_bytes(encrypted)

    typer.echo(f"Initialized repo: {repo_url} (branch: {branch})")


@app.command()
def generate(
    repo_url: str = typer.Argument(..., help="Repository URL"),
    output: str = typer.Option("./docs", "--output", "-o", help="Output directory"),
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="GROQ_API_KEY", help="Groq API key"),
    include_prs: bool = typer.Option(True, "--include-prs/--no-include-prs", help="Include PR analysis in docs"),
    include_history: bool = typer.Option(True, "--include-history/--no-include-history", help="Include git history in docs"),
):
    """Generate documentation for a repository."""
    config = load_config()
    repo_cfg = next((r for r in config.repositories if r.url == repo_url), None)
    if repo_cfg is None:
        typer.echo(
            f"Error: Repository '{repo_url}' not configured. Run 'init' first.",
            err=True,
        )
        raise typer.Exit(1)

    creds_dir = Path.home() / ".config" / "doc-rebuild" / "credentials"
    cred_file = creds_dir / f"{repo_cfg.credentials_ref}.cred"
    if not cred_file.exists():
        typer.echo("Error: Credentials not found. Re-run 'init'.", err=True)
        raise typer.Exit(1)

    token = decrypt_token(cred_file.read_bytes())

    if not api_key:
        typer.echo("Error: Groq API key required. Set GROQ_API_KEY or pass --api-key.", err=True)
        raise typer.Exit(1)

    conn = RepositoryConnection(
        url=repo_url,
        provider=_detect_provider(repo_url),
        branch=repo_cfg.branch,
        credentials_ref=repo_cfg.credentials_ref,
    )

    connector = _build_connector(conn)
    llm = GroqClient(api_key=api_key)
    orchestrator = DocOrchestrator(llm)

    typer.echo(f"Cloning repository: {repo_url}", err=True)
    with tempfile.TemporaryDirectory(prefix="doc-rebuild-") as tmp:
        repo_dir = Path(tmp) / "repo"
        try:
            connector.clone_repo(repo_dir, token)
        except Exception as e:
            typer.echo(f"Error cloning repository: {e}", err=True)
            raise typer.Exit(1)

        typer.echo("Analyzing code structure...", err=True)
        analyzer = StructureAnalyzer(repo_dir)
        analysis = analyzer.analyze()
        typer.echo(f"Found {analysis.total_files} files in {len(analysis.languages)} language(s).", err=True)

        if analysis.total_files == 0:
            typer.echo("Warning: No supported source files found.", err=True)

        if include_history:
            typer.echo("Analyzing git history...", err=True)
            try:
                git_analyzer = GitHistoryAnalyzer(repo_dir)
                commits = git_analyzer.analyze(max_depth=repo_cfg.branch if hasattr(repo_cfg, 'max_commit_depth') else 1000)
                analysis.commit_timeline = commits
                typer.echo(f"Found {len(commits)} commits.", err=True)
            except Exception as e:
                typer.echo(f"Warning: Git history analysis failed: {e}", err=True)

        if include_prs:
            typer.echo("Analyzing pull requests...", err=True)
            try:
                pr_analyzer = PRAnalyzer(connector)
                insights = pr_analyzer.analyze(token)
                analysis.pr_insights = insights
                typer.echo(f"Found {len(insights)} PRs/MRs.", err=True)
            except Exception as e:
                typer.echo(f"Warning: PR analysis failed: {e}", err=True)

        typer.echo("Generating documentation...", err=True)
        doc = orchestrator.generate(analysis, repo_url, include_history=include_history, include_prs=include_prs)

        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)

        doc_file = output_path / f"{connector.get_repo_name().replace('/', '_')}.md"
        full_content = f"# {connector.get_repo_name()}\n\n"
        for section in doc.sections:
            full_content += f"{'#' * section.level} {section.title}\n\n{section.content}\n\n"
        doc_file.write_text(full_content)

        typer.echo(f"Documentation generated: {doc_file}")


@app.command("list")
def list_repos():
    """List configured repositories."""
    config = load_config()
    if not config.repositories:
        typer.echo("No repositories configured.")
        return
    for r in config.repositories:
        typer.echo(f"  {r.url} (branch: {r.branch})")


@app.command()
def check(
    repo_url: str = typer.Argument(..., help="Repository URL"),
):
    """Check if documentation is stale."""
    typer.echo(f"Staleness check not yet implemented for: {repo_url}", err=True)


@app.command()
def update(
    repo_url: str = typer.Argument(..., help="Repository URL"),
):
    """Update stale documentation sections."""
    typer.echo(f"Update not yet implemented for: {repo_url}", err=True)


@app.command()
def config_view():
    """View configuration."""
    config = load_config()
    typer.echo(f"Repositories: {len(config.repositories)}")
    typer.echo(f"Output dir: {config.generation.output_dir}")
    typer.echo(f"LLM model: {config.generation.llm.model}")


if __name__ == "__main__":
    app()
