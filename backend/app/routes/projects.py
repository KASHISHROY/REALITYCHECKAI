from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Project
from app.schemas.project import ProjectCreate, ProjectResponse, ScanSummary
from app.services.report_service import build_markdown_report
from app.services.project_service import create_or_get_project
from app.services.repository_service import RepositoryCloneError
from app.services.scan_service import get_scan_or_latest, run_demo_scan, run_project_scan, scan_to_summary

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(payload: ProjectCreate, db: Session = Depends(get_db)) -> Project:
    try:
        return create_or_get_project(db, payload.repo_url)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.post("/demo/scan", response_model=ScanSummary)
async def scan_demo_project(db: Session = Depends(get_db)) -> dict:
    try:
        scan = run_demo_scan(db)
    except RepositoryCloneError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    db.refresh(scan.project)
    return scan_to_summary(scan.project, scan, getattr(scan, "_analysis_payload", None))


@router.post("/{project_id}/scan", response_model=ScanSummary)
async def scan_project(project_id: int, db: Session = Depends(get_db)) -> dict:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    try:
        scan = run_project_scan(db, project)
    except RepositoryCloneError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    db.refresh(project)
    return scan_to_summary(project, scan, getattr(scan, "_analysis_payload", None))


@router.get("/{project_id}/scans/{scan_id}/report")
async def export_scan_report(project_id: int, scan_id: int, db: Session = Depends(get_db)) -> Response:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    scan = get_scan_or_latest(db, project_id=project_id, scan_id=scan_id)
    if scan is None or scan.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found.")

    markdown = build_markdown_report(project, scan)
    filename = f"{project.repo_name}-realitycheck-report.md"
    return Response(
        content=markdown,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
