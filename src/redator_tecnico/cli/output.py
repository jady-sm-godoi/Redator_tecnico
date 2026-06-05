import sys
from typing import Any


def info(msg: str) -> None:
    """Print status/info message to stderr (status channel)."""
    print(msg, file=sys.stderr)


def success(msg: str) -> None:
    """Print success output to stdout (data channel)."""
    print(msg)


def error(msg: str, exit_code: int = 1) -> None:
    """Print error message to stderr and exit."""
    print(f"Error: {msg}", file=sys.stderr)
    raise SystemExit(exit_code)


def warn(msg: str) -> None:
    """Print warning to stderr."""
    print(f"Warning: {msg}", file=sys.stderr)


def print_json(data: Any) -> None:
    """Print data as JSON to stdout."""
    import json
    json.dump(data, sys.stdout, indent=2, default=str)
    sys.stdout.write("\n")
