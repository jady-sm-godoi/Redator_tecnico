from pathlib import Path
from redator_tecnico.analyzers.git_history import GitHistoryAnalyzer
from redator_tecnico.models.analysis import Significance


class TestGitHistoryAnalyzer:
    def test_analyze_empty_repo(self, tmp_path):
        tmp_path.joinpath(".git").mkdir()
        import git
        repo = git.Repo.init(tmp_path)
        repo.close()
        analyzer = GitHistoryAnalyzer(tmp_path)
        commits = analyzer.analyze(max_depth=100)
        assert len(commits) == 0

    def test_analyze_single_commit(self, tmp_path):
        repo = _init_repo_with_commit(tmp_path, "Initial commit", "README.md", "hello")
        analyzer = GitHistoryAnalyzer(tmp_path)
        commits = analyzer.analyze()
        assert len(commits) == 1
        assert commits[0].message == "Initial commit"
        assert len(commits[0].hash) == 8

    def test_analyze_multiple_commits(self, tmp_path):
        repo = _init_repo_with_commit(tmp_path, "First commit", "a.txt", "a")
        (tmp_path / "b.txt").write_text("b")
        repo.index.add(["b.txt"])
        repo.index.commit("Second commit")
        repo.close()

        analyzer = GitHistoryAnalyzer(tmp_path)
        commits = analyzer.analyze()
        assert len(commits) == 2

    def test_classify_breaking_as_major(self, tmp_path):
        repo = _init_repo_with_commit(tmp_path, "BREAKING: redesign API", "x.py", "x")
        analyzer = GitHistoryAnalyzer(tmp_path)
        assert analyzer.analyze()[0].significance == Significance.major

    def test_classify_fix_as_fix(self, tmp_path):
        repo = _init_repo_with_commit(tmp_path, "fix login bug", "x.py", "x")
        analyzer = GitHistoryAnalyzer(tmp_path)
        assert analyzer.analyze()[0].significance == Significance.fix

    def test_classify_refactor(self, tmp_path):
        repo = _init_repo_with_commit(tmp_path, "refactor auth module", "x.py", "x")
        analyzer = GitHistoryAnalyzer(tmp_path)
        assert analyzer.analyze()[0].significance == Significance.refactor

    def test_classify_docs(self, tmp_path):
        repo = _init_repo_with_commit(tmp_path, "update documentation", "README.md", "# docs")
        analyzer = GitHistoryAnalyzer(tmp_path)
        assert analyzer.analyze()[0].significance == Significance.docs

    def test_classify_minor_default(self, tmp_path):
        repo = _init_repo_with_commit(tmp_path, "tweak styling", "x.py", "x")
        analyzer = GitHistoryAnalyzer(tmp_path)
        assert analyzer.analyze()[0].significance == Significance.minor

    def test_max_depth_limit(self, tmp_path):
        repo = _init_repo_with_commit(tmp_path, "c0", "f0", "0")
        for i in range(1, 10):
            (tmp_path / f"f{i}").write_text(str(i))
            repo.index.add([f"f{i}"])
            repo.index.commit(f"c{i}")
        repo.close()
        analyzer = GitHistoryAnalyzer(tmp_path)
        commits = analyzer.analyze(max_depth=3)
        assert len(commits) == 3

    def test_files_changed_tracked(self, tmp_path):
        repo = _init_repo_with_commit(tmp_path, "add files", "main.py", "print(1)")
        (tmp_path / "utils.py").write_text("def f(): pass")
        repo.index.add(["utils.py"])
        repo.index.commit("add utils")
        repo.close()
        analyzer = GitHistoryAnalyzer(tmp_path)
        commits = analyzer.analyze()
        latest = commits[0]
        assert "utils.py" in latest.files_changed


def _init_repo_with_commit(tmp_path: Path, msg: str, filename: str, content: str):
    import git
    repo = git.Repo.init(tmp_path)
    (tmp_path / filename).write_text(content)
    repo.index.add([filename])
    repo.index.commit(msg)
    return repo
