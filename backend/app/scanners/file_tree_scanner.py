import os
from pathlib import Path

from app.schemas.project import ScanSummary


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
}

IMPORTANT_FILENAMES = {
    "README",
    "README.md",
    "README.txt",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml",
    ".env.example",
    "package.json",
    "requirements.txt",
    "pyproject.toml",
    "vite.config.ts",
    "vite.config.js",
    "vite.config.mjs",
    "vite.config.mts",
    "next.config.js",
    "next.config.mjs",
    "main.py",
    "app.py",
}


def scan_repository_tree(
    repo_path: Path,
    project_id: int,
    repo_owner: str,
    repo_name: str,
) -> ScanSummary:
    total_files = 0
    total_folders = 0
    important_files: list[str] = []
    all_paths: set[str] = set()

    for current_root_name, dirs, files in os.walk(repo_path):
        current_root = Path(current_root_name)
        dirs[:] = [directory for directory in dirs if directory not in SKIPPED_DIRS]
        relative_root = _relative_path(repo_path, current_root)

        if relative_root != ".":
            total_folders += 1
            all_paths.add(relative_root)

        for file_name in files:
            total_files += 1
            file_path = current_root / file_name
            relative_file = _relative_path(repo_path, file_path)
            all_paths.add(relative_file)

            if _is_important_file(relative_file, file_name):
                important_files.append(relative_file)

    package_json_detected = any(path.endswith("package.json") for path in all_paths)
    requirements_detected = any(path.endswith("requirements.txt") for path in all_paths)
    docker_detected = any(path.endswith("Dockerfile") for path in all_paths)
    docker_compose_detected = any(
        Path(path).name in {"docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"}
        for path in all_paths
    )
    env_detected = any(
        Path(path).name in {".env.example", ".env.sample"} or path.endswith(".env.example")
        for path in all_paths
    )
    docs_detected = any(_is_doc_path(path) for path in all_paths)

    frontend_detected = package_json_detected or any(
        Path(path).name
        in {
            "vite.config.ts",
            "vite.config.js",
            "vite.config.mjs",
            "vite.config.mts",
            "next.config.js",
            "next.config.mjs",
        }
        or path.startswith("frontend/")
        for path in all_paths
    )
    backend_detected = requirements_detected or any(
        Path(path).name in {"main.py", "app.py", "pyproject.toml"}
        or path.startswith("backend/")
        for path in all_paths
    )
    config_detected = any(
        [
            docker_detected,
            docker_compose_detected,
            env_detected,
            package_json_detected,
            requirements_detected,
        ]
    )

    return ScanSummary(
        project_id=project_id,
        repo_owner=repo_owner,
        repo_name=repo_name,
        status="completed",
        total_files=total_files,
        total_folders=total_folders,
        frontend_detected=frontend_detected,
        backend_detected=backend_detected,
        docs_detected=docs_detected,
        docker_detected=docker_detected,
        docker_compose_detected=docker_compose_detected,
        env_detected=env_detected,
        package_json_detected=package_json_detected,
        requirements_detected=requirements_detected,
        config_detected=config_detected,
        important_files=sorted(set(important_files))[:60],
    )


def _relative_path(repo_path: Path, path: Path) -> str:
    relative = path.relative_to(repo_path).as_posix()
    return relative or "."


def _is_important_file(relative_file: str, file_name: str) -> bool:
    if file_name in IMPORTANT_FILENAMES:
        return True
    normalized_name = file_name.lower()
    if normalized_name.startswith("readme"):
        return True
    if normalized_name.endswith(".md") and (
        relative_file.upper() == "README.MD" or relative_file.startswith("docs/")
    ):
        return True
    return False


def _is_doc_path(path: str) -> bool:
    file_name = Path(path).name.lower()
    return file_name.startswith("readme") or path.startswith("docs/") or file_name.endswith(".md")
