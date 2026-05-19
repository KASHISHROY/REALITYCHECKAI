from pathlib import Path

from git import GitCommandError, InvalidGitRepositoryError, Repo

from app.config import get_settings
from app.models import Project


class RepositoryCloneError(RuntimeError):
    pass


def clone_or_fetch_repository(project: Project) -> Path:
    settings = get_settings()
    storage_root = Path(settings.repo_storage_path)
    target_path = storage_root / str(project.id)
    storage_root.mkdir(parents=True, exist_ok=True)

    if target_path.exists():
        try:
            repo = Repo(target_path)
        except InvalidGitRepositoryError as exc:
            raise RepositoryCloneError(
                f"Storage path already exists but is not a Git repository: {target_path}"
            ) from exc

        try:
            repo.remotes.origin.fetch(prune=True)
        except GitCommandError as exc:
            raise RepositoryCloneError(
                f"Repository exists locally, but fetching updates failed: {exc.stderr}"
            ) from exc
        return target_path

    try:
        Repo.clone_from(project.repo_url, target_path, depth=1)
    except GitCommandError as exc:
        raise RepositoryCloneError(
            "Could not clone the repository. Make sure it is public and the URL is correct."
        ) from exc

    return target_path

