from sqlalchemy.orm import Session

from app.models import Project, Scan
from app.scanners.file_tree_scanner import scan_repository_tree
from app.services.repository_service import RepositoryCloneError, clone_or_fetch_repository


def run_project_scan(db: Session, project: Project) -> Scan:
    try:
        project.status = "cloning"
        project.error_message = None
        db.commit()

        repo_path = clone_or_fetch_repository(project)
        project.local_path = str(repo_path)
        project.status = "scanning"
        db.commit()

        summary = scan_repository_tree(
            repo_path=repo_path,
            project_id=project.id,
            repo_owner=project.repo_owner,
            repo_name=project.repo_name,
        )

        scan = Scan(
            project_id=project.id,
            status=summary.status,
            total_files=summary.total_files,
            total_folders=summary.total_folders,
            frontend_detected=summary.frontend_detected,
            backend_detected=summary.backend_detected,
            docs_detected=summary.docs_detected,
            docker_detected=summary.docker_detected,
            docker_compose_detected=summary.docker_compose_detected,
            env_detected=summary.env_detected,
            package_json_detected=summary.package_json_detected,
            requirements_detected=summary.requirements_detected,
            config_detected=summary.config_detected,
            important_files=summary.important_files,
        )
        project.status = "scanned"
        project.error_message = None
        db.add(scan)
        db.commit()
        db.refresh(scan)
        return scan
    except RepositoryCloneError as exc:
        project.status = "failed"
        project.error_message = str(exc)
        db.commit()
        raise


def scan_to_summary(project: Project, scan: Scan) -> dict:
    return {
        "project_id": project.id,
        "repo_owner": project.repo_owner,
        "repo_name": project.repo_name,
        "status": project.status,
        "total_files": scan.total_files,
        "total_folders": scan.total_folders,
        "frontend_detected": scan.frontend_detected,
        "backend_detected": scan.backend_detected,
        "docs_detected": scan.docs_detected,
        "docker_detected": scan.docker_detected,
        "docker_compose_detected": scan.docker_compose_detected,
        "env_detected": scan.env_detected,
        "package_json_detected": scan.package_json_detected,
        "requirements_detected": scan.requirements_detected,
        "config_detected": scan.config_detected,
        "important_files": scan.important_files,
    }

