import re
from dataclasses import dataclass
from urllib.parse import urlparse

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Project


GITHUB_OWNER_PATTERN = re.compile(r"^[A-Za-z0-9-]+$")
GITHUB_REPO_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")
DEMO_REPO_URL = "demo://realitycheck-demo-app"


@dataclass(frozen=True)
class ParsedGitHubRepo:
    owner: str
    name: str
    normalized_url: str


def parse_github_repo_url(repo_url: str) -> ParsedGitHubRepo:
    raw_url = repo_url.strip()
    if raw_url.startswith("git@github.com:"):
        path = raw_url.removeprefix("git@github.com:")
        return _parse_repo_path(path)

    if raw_url.startswith("github.com/"):
        raw_url = f"https://{raw_url}"

    parsed = urlparse(raw_url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Use a public GitHub URL that starts with https://github.com/.")

    if parsed.netloc.lower() not in {"github.com", "www.github.com"}:
        raise ValueError("Only GitHub repository URLs are supported on Day 1.")

    return _parse_repo_path(parsed.path)


def _parse_repo_path(path: str) -> ParsedGitHubRepo:
    clean_path = path.strip().strip("/")
    if clean_path.endswith(".git"):
        clean_path = clean_path[:-4]

    parts = [part for part in clean_path.split("/") if part]
    if len(parts) != 2:
        raise ValueError("GitHub URL must look like https://github.com/owner/repo.")

    owner, name = parts
    if not GITHUB_OWNER_PATTERN.fullmatch(owner):
        raise ValueError("GitHub owner contains invalid characters.")
    if not GITHUB_REPO_PATTERN.fullmatch(name):
        raise ValueError("GitHub repo name contains invalid characters.")

    return ParsedGitHubRepo(
        owner=owner,
        name=name,
        normalized_url=f"https://github.com/{owner}/{name}",
    )


def create_or_get_project(db: Session, repo_url: str) -> Project:
    parsed_repo = parse_github_repo_url(repo_url)
    existing = db.scalar(
        select(Project).where(Project.repo_url == parsed_repo.normalized_url)
    )
    if existing:
        return existing

    project = Project(
        repo_url=parsed_repo.normalized_url,
        repo_owner=parsed_repo.owner,
        repo_name=parsed_repo.name,
        status="created",
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def create_or_get_demo_project(db: Session) -> Project:
    existing = db.scalar(select(Project).where(Project.repo_url == DEMO_REPO_URL))
    if existing:
        return existing

    project = Project(
        repo_url=DEMO_REPO_URL,
        repo_owner="local",
        repo_name="realitycheck-demo-app",
        status="created",
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project
