from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    repo_url: Mapped[str] = mapped_column(String(500), unique=True, index=True)
    repo_owner: Mapped[str] = mapped_column(String(120), index=True)
    repo_name: Mapped[str] = mapped_column(String(200), index=True)
    status: Mapped[str] = mapped_column(String(40), default="created", index=True)
    local_path: Mapped[str | None] = mapped_column(String(600), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    scans: Mapped[list["Scan"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )


class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    status: Mapped[str] = mapped_column(String(40), default="completed")
    total_files: Mapped[int] = mapped_column(Integer, default=0)
    total_folders: Mapped[int] = mapped_column(Integer, default=0)
    frontend_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    backend_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    docs_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    docker_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    docker_compose_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    env_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    package_json_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    requirements_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    config_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    important_files: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    project: Mapped[Project] = relationship(back_populates="scans")

