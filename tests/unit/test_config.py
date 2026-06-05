import tempfile
from pathlib import Path
from redator_tecnico.config.settings import (
    AppConfig,
    RepoConfig,
    GenerationConfig,
    save_config,
    load_config,
    resolve_repo_config,
)


class TestConfigManagement:
    def test_save_and_load_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_dir = Path(tmp) / "doc-rebuild"
            config = AppConfig(
                repositories=[
                    RepoConfig(
                        url="https://github.com/test/repo",
                        credentials_ref="001",
                    )
                ]
            )
            save_config(config, config_dir)
            loaded = load_config(config_dir)
            assert len(loaded.repositories) == 1
            assert loaded.repositories[0].url == "https://github.com/test/repo"
            assert loaded.repositories[0].credentials_ref == "001"

    def test_load_config_empty_when_no_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_dir = Path(tmp) / "doc-rebuild"
            config = load_config(config_dir)
            assert len(config.repositories) == 0

    def test_resolve_repo_config_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_dir = Path(tmp) / "doc-rebuild"
            config = AppConfig(
                repositories=[
                    RepoConfig(url="https://github.com/foo/bar", credentials_ref="abc"),
                ]
            )
            save_config(config, config_dir)
            found = resolve_repo_config("https://github.com/foo/bar", config_dir)
            assert found is not None
            assert found.credentials_ref == "abc"

    def test_resolve_repo_config_not_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_dir = Path(tmp) / "doc-rebuild"
            config = AppConfig(
                repositories=[
                    RepoConfig(url="https://github.com/foo/bar", credentials_ref="abc"),
                ]
            )
            save_config(config, config_dir)
            found = resolve_repo_config("https://github.com/other/repo", config_dir)
            assert found is None

    def test_save_preserves_generation_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_dir = Path(tmp) / "doc-rebuild"
            config = AppConfig(
                generation=GenerationConfig(
                    output_dir="./my-docs",
                    include_history=False,
                )
            )
            save_config(config, config_dir)
            loaded = load_config(config_dir)
            assert loaded.generation.output_dir == "./my-docs"
            assert loaded.generation.include_history is False
