import sys
import tempfile
from pathlib import Path
from typing import Optional
from importlib.metadata import version, PackageNotFoundError
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
from src.models.documentation import load_doc_metadata, save_doc_metadata
from src.analyzers.structure import compute_module_hashes
from src.cli.output import info, success, error, warn, print_json

try:
    __version__ = version("redator-tecnico")
except PackageNotFoundError:
    __version__ = "0.1.0"

app = typer.Typer(
    name="doc-rebuild",
    help="Auto-generate and maintain technical documentation from GitHub/GitLab repositories.",
    no_args_is_help=True,
)


def _version_callback(value: bool) -> None:
    if value:
        success(f"doc-rebuild v{__version__}")
        raise typer.Exit()


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


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        help="Show version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
):
    pass


@app.command()
def init(
    repo_url: str = typer.Argument(..., help="Repository URL (e.g. https://github.com/owner/repo)"),
    branch: str = typer.Option("main", "--branch", "-b", help="Target branch to analyze"),
    token: Optional[str] = typer.Option(
        None, "--token", "-t", help="Access token (omit to be prompted securely)"
    ),
):
    """Initialize a repository for documentation generation.

    Stores encrypted credentials and config for later use by 'generate', 'check', and 'update' commands.
    """
    try:
        provider = _detect_provider(repo_url)
    except typer.BadParameter as e:
        error(str(e))

    if token is None:
        token = typer.prompt("Access token", hide_input=True)

    if not token:
        error("Token cannot be empty.")

    config = load_config()

    existing = [r for r in config.repositories if r.url == repo_url]
    if existing:
        error(f"Repository already configured: {repo_url}")

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

    success(f"Initialized repo: {repo_url} (branch: {branch})")


@app.command()
def generate(
    repo_url: str = typer.Argument(..., help="Repository URL to generate docs for"),
    output: str = typer.Option("./docs", "--output", "-o", help="Output directory for generated docs"),
    api_key: Optional[str] = typer.Option(
        None, "--api-key", envvar="GROQ_API_KEY", help="Groq API key (or set GROQ_API_KEY env var)"
    ),
    include_prs: bool = typer.Option(
        True, "--include-prs/--no-include-prs", help="Include PR analysis in generated docs"
    ),
    include_history: bool = typer.Option(
        True, "--include-history/--no-include-history", help="Include git commit history in docs"
    ),
):
    """Generate complete documentation for a repository.

    Analyzes code structure, git history, and pull requests to produce Markdown documentation.
    Requires the repository to be initialized via the 'init' command first.
    """
    config = load_config()
    repo_cfg = next((r for r in config.repositories if r.url == repo_url), None)
    if repo_cfg is None:
        error(f"Repository '{repo_url}' not configured. Run 'init' first.")

    creds_dir = Path.home() / ".config" / "doc-rebuild" / "credentials"
    cred_file = creds_dir / f"{repo_cfg.credentials_ref}.cred"
    if not cred_file.exists():
        error("Credentials not found. Re-run 'init'.")

    token = decrypt_token(cred_file.read_bytes())

    if not api_key:
        error("Groq API key required. Set GROQ_API_KEY or pass --api-key.")

    conn = RepositoryConnection(
        url=repo_url,
        provider=_detect_provider(repo_url),
        branch=repo_cfg.branch,
        credentials_ref=repo_cfg.credentials_ref,
    )

    connector = _build_connector(conn)
    llm = GroqClient(api_key=api_key)
    orchestrator = DocOrchestrator(llm)

    info(f"Cloning repository: {repo_url}")
    with tempfile.TemporaryDirectory(prefix="doc-rebuild-") as tmp:
        repo_dir = Path(tmp) / "repo"
        try:
            connector.clone_repo(repo_dir, token)
        except Exception as e:
            error(f"Error cloning repository: {e}")

        info("Analyzing code structure...")
        analyzer = StructureAnalyzer(repo_dir)
        analysis = analyzer.analyze()
        info(f"Found {analysis.total_files} files in {len(analysis.languages)} language(s).")

        if analysis.total_files == 0:
            warn("No supported source files found.")

        if include_history:
            info("Analyzing git history...")
            try:
                git_analyzer = GitHistoryAnalyzer(repo_dir)
                commits = git_analyzer.analyze(max_depth=1000)
                analysis.commit_timeline = commits
                info(f"Found {len(commits)} commits.")
            except Exception as e:
                warn(f"Git history analysis failed: {e}")

        if include_prs:
            info("Analyzing pull requests...")
            try:
                pr_analyzer = PRAnalyzer(connector)
                insights = pr_analyzer.analyze(token)
                analysis.pr_insights = insights
                info(f"Found {len(insights)} PRs/MRs.")
            except Exception as e:
                warn(f"PR analysis failed: {e}")

        info("Generating documentation...")
        doc = orchestrator.generate(analysis, repo_url, include_history=include_history, include_prs=include_prs)

        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)

        doc_file = output_path / f"{connector.get_repo_name().replace('/', '_')}.md"
        full_content = f"# {connector.get_repo_name()}\n\n"
        for section in doc.sections:
            full_content += f"{'#' * section.level} {section.title}\n\n{section.content}\n\n"
        doc_file.write_text(full_content)

        current_hashes = compute_module_hashes(repo_dir)
        save_doc_metadata(doc, output_path, module_content_hashes=current_hashes)

        success(f"Documentation generated: {doc_file}")


@app.command("list")
def list_repos(
    json_format: bool = typer.Option(False, "--json", help="Output in JSON format for machine parsing"),
):
    """List all configured repositories.

    Shows registered repos, their branches, and providers.
    Use --json for machine-readable output.
    """
    config = load_config()
    if json_format:
        repos_data = [
            {"url": r.url, "branch": r.branch, "provider": r.provider}
            for r in config.repositories
        ]
        print_json({"repositories": repos_data, "count": len(config.repositories)})
        return
    if not config.repositories:
        info("No repositories configured.")
        return
    for r in config.repositories:
        success(f"  {r.url} (branch: {r.branch})")


@app.command()
def check(
    repo_url: str = typer.Argument(..., help="Repository URL to check"),
    output: str = typer.Option("./docs", "--output", "-o", help="Directory containing generated docs"),
    json_format: bool = typer.Option(False, "--json", help="Output in JSON format for machine parsing"),
):
    """Check if documentation is stale.

    Compares current repository state against stored module hashes
    and reports which documentation sections need updating.
    """
    meta = load_doc_metadata(Path(output))
    if meta is None:
        error("No documentation metadata found. Run 'generate' first.")

    config = load_config()
    repo_cfg = next((r for r in config.repositories if r.url == repo_url), None)
    if repo_cfg is None:
        error(f"Repository '{repo_url}' not configured. Run 'init' first.")

    creds_dir = Path.home() / ".config" / "doc-rebuild" / "credentials"
    cred_file = creds_dir / f"{repo_cfg.credentials_ref}.cred"
    if not cred_file.exists():
        error("Credentials not found. Re-run 'init'.")

    token = decrypt_token(cred_file.read_bytes())
    conn = RepositoryConnection(
        url=repo_url,
        provider=_detect_provider(repo_url),
        branch=repo_cfg.branch,
    )
    connector = _build_connector(conn)

    info("Cloning repository to check for changes...")
    with tempfile.TemporaryDirectory(prefix="doc-rebuild-check-") as tmp:
        repo_dir = Path(tmp) / "repo"
        try:
            connector.clone_repo(repo_dir, token)
        except Exception as e:
            error(f"Error cloning repository: {e}")

        info("Computing current module hashes...")
        current_hashes = compute_module_hashes(repo_dir)

        analyzer = StructureAnalyzer(repo_dir)
        analysis = analyzer.analyze()

        stale_sections, _ = DocOrchestrator.detect_static_stale(
            Path(output), current_hashes, analysis
        )

    if not stale_sections:
        info("No metadata found. Run with full 'generate' first.")
        return

    stale_any = False
    sections_data = []
    for title, is_stale in stale_sections:
        if is_stale:
            stale_any = True
        sections_data.append({"title": title, "status": "stale" if is_stale else "fresh"})

    if json_format:
        print_json({
            "sections": sections_data,
            "stale_count": sum(1 for s in sections_data if s["status"] == "stale"),
            "is_stale": stale_any,
        })
        return

    for title, is_stale in stale_sections:
        if is_stale:
            info(f"  [STALE]  {title}")
        else:
            info(f"  [FRESH]  {title}")

    if stale_any:
        info("\nDocumentation is stale. Run 'update' to regenerate sections.")
    else:
        info("\nAll documentation sections are up to date.")


@app.command()
def update(
    repo_url: str = typer.Argument(..., help="Repository URL to update docs for"),
    output: str = typer.Option("./docs", "--output", "-o", help="Directory containing generated docs"),
    api_key: str | None = typer.Option(
        None, "--api-key", envvar="GROQ_API_KEY", help="Groq API key (or set GROQ_API_KEY env var)"
    ),
):
    """Regenerate only stale documentation sections.

    Incremental update that detects changed modules and regenerates
    only the affected sections, preserving unchanged content.
    """
    meta = load_doc_metadata(Path(output))
    if meta is None:
        error("No documentation metadata found. Run 'generate' first.")

    output_path = Path(output)
    doc_file = next(output_path.glob("*.md"), None)
    if doc_file is None:
        error("No documentation file found. Run 'generate' first.")

    if not api_key:
        error("Groq API key required. Set GROQ_API_KEY or pass --api-key.")

    config = load_config()
    repo_cfg = next((r for r in config.repositories if r.url == repo_url), None)
    if repo_cfg is None:
        error(f"Repository '{repo_url}' not configured. Run 'init' first.")

    creds_dir = Path.home() / ".config" / "doc-rebuild" / "credentials"
    cred_file = creds_dir / f"{repo_cfg.credentials_ref}.cred"
    if not cred_file.exists():
        error("Credentials not found. Re-run 'init'.")

    token = decrypt_token(cred_file.read_bytes())
    conn = RepositoryConnection(
        url=repo_url,
        provider=_detect_provider(repo_url),
        branch=repo_cfg.branch,
    )
    connector = _build_connector(conn)
    llm = GroqClient(api_key=api_key)
    orch = DocOrchestrator(llm)

    from src.models.documentation import Documentation, DocSection
    existing_sections = [
        DocSection(title=s.title, level=s.level, source_modules=s.source_modules)
        for s in meta.sections
    ]
    existing_doc = Documentation(
        repo_url=repo_url,
        sections=existing_sections,
        source_hash=meta.source_hash,
    )

    info("Cloning repository...")
    with tempfile.TemporaryDirectory(prefix="doc-rebuild-update-") as tmp:
        repo_dir = Path(tmp) / "repo"
        try:
            connector.clone_repo(repo_dir, token)
        except Exception as e:
            error(f"Error cloning repository: {e}")

        info("Analyzing code structure...")
        analyzer = StructureAnalyzer(repo_dir)
        analysis = analyzer.analyze()

        info("Detecting stale sections...")
        current_hashes = compute_module_hashes(repo_dir)
        stale_sections, _ = DocOrchestrator.detect_static_stale(output_path, current_hashes, analysis)

        stale_titles = [t for t, s in stale_sections if s]
        if not stale_titles:
            info("No stale sections found. Documentation is up to date.")
            return

        info(f"Regenerating {len(stale_titles)} stale section(s): {', '.join(stale_titles)}")
        updated_doc = orch.update(analysis, output_path, existing_doc)

        full_content = f"# {connector.get_repo_name()}\n\n"
        for section in updated_doc.sections:
            full_content += f"{'#' * section.level} {section.title}\n\n{section.content}\n\n"
        doc_file.write_text(full_content)
        current_hashes = compute_module_hashes(repo_dir)
        save_doc_metadata(updated_doc, output_path, module_content_hashes=current_hashes)

        success(f"Documentation updated: {doc_file}")


@app.command()
def config_view():
    """View current configuration and settings.

    Displays all configured repositories, generation defaults,
    and LLM model settings from ~/.config/doc-rebuild/config.yml.
    """
    config = load_config()
    success(f"Repositories ({len(config.repositories)}):")
    for r in config.repositories:
        success(f"  - {r.url} (branch: {r.branch}, provider: {r.provider})")
    success("")
    info("Generation settings:")
    info(f"  Output dir:     {config.generation.output_dir}")
    info(f"  Include PRs:    {config.generation.include_prs}")
    info(f"  Include history: {config.generation.include_history}")
    info(f"  Max commits:    {config.generation.max_commit_depth}")
    info(f"  LLM model:      {config.generation.llm.model}")
    info(f"  Temperature:    {config.generation.llm.temperature}")


if __name__ == "__main__":
    app()
