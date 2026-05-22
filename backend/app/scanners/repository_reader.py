import os
from pathlib import Path
from collections.abc import Iterable


SKIPPED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "dist",
    "build",
    ".next",
    ".turbo",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
}

TEXT_EXTENSIONS = {
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".py",
    ".md",
    ".txt",
    ".json",
    ".toml",
    ".yml",
    ".yaml",
    ".env",
    ".example",
    ".dockerfile",
}


def iter_files(
    repo_path: Path,
    extensions: Iterable[str] | None = None,
    names: Iterable[str] | None = None,
) -> Iterable[Path]:
    extension_set = {extension.lower() for extension in extensions or []}
    name_set = {name.lower() for name in names or []}

    for current_root_name, dirs, files in os.walk(repo_path):
        dirs[:] = [directory for directory in dirs if directory not in SKIPPED_DIRS]
        current_root = Path(current_root_name)

        for file_name in files:
            file_path = current_root / file_name
            lower_name = file_name.lower()
            suffix = file_path.suffix.lower()
            if extension_set and suffix not in extension_set:
                continue
            if name_set and lower_name not in name_set:
                continue
            yield file_path


def iter_text_files(repo_path: Path) -> Iterable[Path]:
    for file_path in iter_files(repo_path):
        if file_path.suffix.lower() in TEXT_EXTENSIONS or file_path.name in {
            "Dockerfile",
            ".env.example",
            ".env.sample",
        }:
            yield file_path


def read_text(file_path: Path) -> str:
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return file_path.read_text(encoding="latin-1", errors="ignore")


def relative_path(repo_path: Path, file_path: Path) -> str:
    return file_path.relative_to(repo_path).as_posix()


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1
