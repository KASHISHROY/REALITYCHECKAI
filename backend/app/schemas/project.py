from typing import Any

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    repo_url: str = Field(..., min_length=12, max_length=500)


class ProjectResponse(BaseModel):
    id: int
    repo_url: str
    repo_owner: str
    repo_name: str
    status: str
    error_message: str | None = None

    model_config = {"from_attributes": True}


class ScanSummary(BaseModel):
    scan_id: int = 0
    project_id: int
    repo_name: str
    repo_owner: str
    status: str
    total_files: int
    total_folders: int
    frontend_detected: bool
    backend_detected: bool
    docs_detected: bool
    docker_detected: bool
    docker_compose_detected: bool
    env_detected: bool
    package_json_detected: bool
    requirements_detected: bool
    config_detected: bool
    important_files: list[str]
    reality_score: int = 100
    total_gaps: int = 0
    high_gaps: int = 0
    medium_gaps: int = 0
    low_gaps: int = 0
    category_counts: dict[str, int] = Field(default_factory=dict)
    gaps: list["GapResponse"] = Field(default_factory=list)
    analysis: dict[str, Any] = Field(default_factory=dict)


class GapResponse(BaseModel):
    id: int
    category: str
    severity: str
    claim_text: str
    reality_text: str
    source_file: str | None = None
    affected_file: str | None = None
    explanation: str
    suggested_fix: str

    model_config = {"from_attributes": True}
