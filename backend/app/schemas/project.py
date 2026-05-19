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

