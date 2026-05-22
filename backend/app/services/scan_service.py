from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Gap, Project, Scan
from app.scanners.file_tree_scanner import scan_repository_tree
from app.services.analysis_service import RepositoryAnalysis, analyze_repository, calculate_reality_score
from app.services.project_service import create_or_get_demo_project
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

        return _run_scan_for_path(db, project, repo_path)
    except RepositoryCloneError as exc:
        project.status = "failed"
        project.error_message = str(exc)
        db.commit()
        raise


def run_demo_scan(db: Session) -> Scan:
    project = create_or_get_demo_project(db)
    repo_root = Path(__file__).resolve().parents[3]
    demo_path = repo_root / "realitycheck-demo-app"
    if not demo_path.exists():
        raise RepositoryCloneError("Demo repository was not found at realitycheck-demo-app.")

    project.status = "scanning"
    project.local_path = str(demo_path)
    project.error_message = None
    db.commit()
    return _run_scan_for_path(db, project, demo_path)


def _run_scan_for_path(db: Session, project: Project, repo_path: Path) -> Scan:
    summary = scan_repository_tree(
        repo_path=repo_path,
        project_id=project.id,
        repo_owner=project.repo_owner,
        repo_name=project.repo_name,
    )
    analysis = analyze_repository(repo_path)

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
    db.flush()

    for gap in analysis.gaps:
        db.add(
            Gap(
                project_id=project.id,
                scan_id=scan.id,
                category=gap.category,
                severity=gap.severity,
                claim_text=gap.claim_text,
                reality_text=gap.reality_text,
                source_file=gap.source_file,
                affected_file=gap.affected_file,
                explanation=gap.explanation,
                suggested_fix=gap.suggested_fix,
            )
        )

    db.commit()
    db.refresh(scan)
    scan._analysis_payload = analysis
    return scan


def scan_to_summary(project: Project, scan: Scan, analysis: RepositoryAnalysis | None = None) -> dict:
    gaps = list(scan.gaps)
    severity_counts = _severity_counts(gaps)
    category_counts = _category_counts(gaps)
    reality_score = (
        analysis.reality_score
        if analysis
        else calculate_reality_score(
            [
                _gap_like(severity=gap.severity)
                for gap in gaps
            ]
        )
    )

    return {
        "scan_id": scan.id,
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
        "reality_score": reality_score,
        "total_gaps": len(gaps),
        "high_gaps": severity_counts["High"],
        "medium_gaps": severity_counts["Medium"],
        "low_gaps": severity_counts["Low"],
        "category_counts": category_counts,
        "gaps": [
            {
                "id": gap.id,
                "category": gap.category,
                "severity": gap.severity,
                "claim_text": gap.claim_text,
                "reality_text": gap.reality_text,
                "source_file": gap.source_file,
                "affected_file": gap.affected_file,
                "explanation": gap.explanation,
                "suggested_fix": gap.suggested_fix,
            }
            for gap in gaps
        ],
        "analysis": analysis.analysis if analysis else {},
    }


def get_scan_or_latest(db: Session, project_id: int, scan_id: int | None = None) -> Scan | None:
    if scan_id is not None:
        return db.get(Scan, scan_id)

    return db.scalar(
        select(Scan)
        .where(Scan.project_id == project_id)
        .order_by(Scan.created_at.desc(), Scan.id.desc())
        .limit(1)
    )


class _gap_like:
    def __init__(self, severity: str) -> None:
        self.severity = severity


def _severity_counts(gaps: list[Gap]) -> dict[str, int]:
    return {
        "High": sum(1 for gap in gaps if gap.severity == "High"),
        "Medium": sum(1 for gap in gaps if gap.severity == "Medium"),
        "Low": sum(1 for gap in gaps if gap.severity == "Low"),
    }


def _category_counts(gaps: list[Gap]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for gap in gaps:
        counts[gap.category] = counts.get(gap.category, 0) + 1
    return counts
