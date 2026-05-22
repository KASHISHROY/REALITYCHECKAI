import json
import re
from pathlib import Path

from app.scanners.repository_reader import read_text, relative_path
from app.scanners.types import DependencyReport, Evidence


TECH_DEPENDENCIES = {
    "postgresql": {"pg", "postgres", "postgresql", "psycopg2", "psycopg", "asyncpg"},
    "mongodb": {"mongodb", "mongoose", "pymongo", "motor"},
    "mysql": {"mysql", "mysql2", "pymysql", "mysqlclient"},
    "sqlite": {"sqlite3", "aiosqlite"},
    "redis": {"redis", "ioredis", "aioredis"},
    "rabbitmq": {"amqplib", "pika", "aio-pika", "kombu"},
    "jwt": {"jsonwebtoken", "jwt-decode", "pyjwt", "python-jose", "jose", "fastapi-jwt-auth"},
    "sessions": {"express-session", "cookie-session", "flask-session", "itsdangerous"},
    "fastapi": {"fastapi", "uvicorn"},
    "express": {"express"},
}


def extract_dependency_reality(repo_path: Path) -> DependencyReport:
    report = DependencyReport(
        technologies={technology: False for technology in TECH_DEPENDENCIES}
    )

    for file_path in repo_path.rglob("*"):
        if not file_path.is_file() or _skip_path(repo_path, file_path):
            continue
        relative = relative_path(repo_path, file_path)
        lower_name = file_path.name.lower()

        if lower_name == "package.json":
            report.package_files.append(relative)
            _read_package_json(report, file_path, relative)
        elif lower_name == "requirements.txt":
            report.requirement_files.append(relative)
            _read_dependency_text(report, read_text(file_path), relative)
        elif lower_name == "pyproject.toml":
            report.pyproject_files.append(relative)
            _read_dependency_text(report, read_text(file_path), relative)

    return report


def _read_package_json(report: DependencyReport, file_path: Path, relative: str) -> None:
    try:
        package = json.loads(read_text(file_path))
    except json.JSONDecodeError:
        return

    dependency_names: set[str] = set()
    for section in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        dependencies = package.get(section, {})
        if isinstance(dependencies, dict):
            dependency_names.update(str(name).lower() for name in dependencies)

    _mark_technologies(report, dependency_names, relative)


def _read_dependency_text(report: DependencyReport, text: str, relative: str) -> None:
    names: set[str] = set()
    for line in text.splitlines():
        clean = line.strip().lower()
        if not clean or clean.startswith("#"):
            continue
        match = re.match(r"([a-z0-9_.-]+)", clean)
        if match:
            names.add(match.group(1))
    _mark_technologies(report, names, relative)


def _mark_technologies(report: DependencyReport, dependency_names: set[str], source_file: str) -> None:
    for technology, markers in TECH_DEPENDENCIES.items():
        matches = sorted(marker for marker in markers if marker in dependency_names)
        if not matches:
            continue
        report.technologies[technology] = True
        report.evidence.setdefault(technology, [])
        for dependency in matches:
            report.evidence[technology].append(
                Evidence(dependency, source_file, None, dependency)
            )


def _skip_path(repo_path: Path, file_path: Path) -> bool:
    parts = set(file_path.relative_to(repo_path).parts)
    return bool(parts.intersection({".git", "node_modules", ".venv", "venv", "dist", "build"}))
