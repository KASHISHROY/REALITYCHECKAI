import json
import re
from pathlib import Path

from app.scanners.repository_reader import line_number, read_text, relative_path
from app.scanners.types import DeploymentReport, Evidence


def extract_deployment_config(repo_path: Path) -> DeploymentReport:
    report = DeploymentReport()

    for file_path in repo_path.rglob("*"):
        if not file_path.is_file() or _skip_path(repo_path, file_path):
            continue
        name = file_path.name
        lower_name = name.lower()
        relative = relative_path(repo_path, file_path)

        if name == "Dockerfile" or lower_name.endswith(".dockerfile"):
            report.dockerfiles.append(relative)
            _read_dockerfile(report, file_path, relative)
        elif lower_name in {"docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"}:
            report.compose_files.append(relative)
            _read_compose(report, file_path, relative)
        elif lower_name == "render.yaml":
            report.render_files.append(relative)
            _read_commands(report, file_path, relative)
        elif lower_name == "vercel.json":
            report.vercel_files.append(relative)
            _read_vercel(report, file_path, relative)
        elif lower_name in {"vite.config.ts", "vite.config.js", "vite.config.mts", "vite.config.mjs"}:
            _read_vite_config(report, file_path, relative)
        elif lower_name == "package.json":
            _read_package_scripts(report, file_path, relative)

    report.backend_ports = _dedupe_evidence(report.backend_ports)
    report.frontend_ports = _dedupe_evidence(report.frontend_ports)
    report.compose_ports = _dedupe_evidence(report.compose_ports)
    report.commands = _dedupe_evidence(report.commands)
    return report


def _read_dockerfile(report: DeploymentReport, file_path: Path, relative: str) -> None:
    text = read_text(file_path)
    for match in re.finditer(r"^\s*EXPOSE\s+([0-9 ]+)", text, re.IGNORECASE | re.MULTILINE):
        for port in re.findall(r"\d{2,5}", match.group(1)):
            report.backend_ports.append(
                Evidence(port, relative, line_number(text, match.start()), match.group(0).strip())
            )

    for match in re.finditer(r"^\s*(CMD|ENTRYPOINT)\s+(.+)$", text, re.IGNORECASE | re.MULTILINE):
        report.commands.append(
            Evidence(match.group(2).strip(), relative, line_number(text, match.start()), match.group(0).strip())
        )


def _read_compose(report: DeploymentReport, file_path: Path, relative: str) -> None:
    text = read_text(file_path)
    for match in re.finditer(r"['\"]?(\d{2,5})\s*:\s*(\d{2,5})['\"]?", text):
        host_port, container_port = match.group(1), match.group(2)
        raw = match.group(0).strip().strip('"').strip("'")
        report.compose_ports.append(
            Evidence(raw, relative, line_number(text, match.start()), raw)
        )
        if container_port in {"3000", "5173", "4173"} or host_port in {"3000", "5173", "4173"}:
            report.frontend_ports.append(
                Evidence(container_port, relative, line_number(text, match.start()), raw)
            )
        else:
            report.backend_ports.append(
                Evidence(container_port, relative, line_number(text, match.start()), raw)
            )
    _read_commands(report, file_path, relative)


def _read_vercel(report: DeploymentReport, file_path: Path, relative: str) -> None:
    text = read_text(file_path)
    report.commands.append(Evidence("vercel config", relative, None, "vercel.json"))
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return
    dev_command = payload.get("devCommand") or payload.get("buildCommand")
    if dev_command:
        report.commands.append(Evidence(str(dev_command), relative, None, str(dev_command)))


def _read_vite_config(report: DeploymentReport, file_path: Path, relative: str) -> None:
    text = read_text(file_path)
    for match in re.finditer(r"port\s*:\s*(\d{2,5})", text):
        report.frontend_ports.append(
            Evidence(match.group(1), relative, line_number(text, match.start()), match.group(0))
        )


def _read_package_scripts(report: DeploymentReport, file_path: Path, relative: str) -> None:
    try:
        package = json.loads(read_text(file_path))
    except json.JSONDecodeError:
        return

    scripts = package.get("scripts", {})
    if not isinstance(scripts, dict):
        return

    for script_name, command in scripts.items():
        command_text = str(command)
        if any(token in command_text for token in ("vite", "next", "react-scripts")):
            port_match = re.search(r"--port\s+(\d{2,5})", command_text)
            port = port_match.group(1) if port_match else "5173" if "vite" in command_text else "3000"
            report.frontend_ports.append(
                Evidence(port, relative, None, f"{script_name}: {command_text}")
            )
        if any(token in command_text for token in ("uvicorn", "fastapi", "node", "express")):
            report.commands.append(
                Evidence(command_text, relative, None, f"{script_name}: {command_text}")
            )


def _read_commands(report: DeploymentReport, file_path: Path, relative: str) -> None:
    text = read_text(file_path)
    for match in re.finditer(r"(uvicorn|gunicorn|npm run|docker compose|node\s+\S+|python\s+\S+).*$", text, re.IGNORECASE | re.MULTILINE):
        report.commands.append(
            Evidence(match.group(0).strip(), relative, line_number(text, match.start()), match.group(0).strip())
        )


def _skip_path(repo_path: Path, file_path: Path) -> bool:
    parts = set(file_path.relative_to(repo_path).parts)
    return bool(parts.intersection({".git", "node_modules", ".venv", "venv", "dist", "build"}))


def _dedupe_evidence(items: list[Evidence]) -> list[Evidence]:
    seen: set[tuple[str, str, str | None]] = set()
    deduped: list[Evidence] = []
    for item in items:
        key = (item.value, item.source_file, item.raw)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped
