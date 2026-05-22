from dataclasses import dataclass
from pathlib import Path
import re

from app.agents.gap_reasoning_agent import GapReasoningAgent
from app.scanners.auth_detector import detect_auth_mechanisms
from app.scanners.backend_route_extractor import extract_backend_routes
from app.scanners.dependency_extractor import extract_dependency_reality
from app.scanners.deployment_config_extractor import extract_deployment_config
from app.scanners.documentation_claim_extractor import extract_documentation_claims
from app.scanners.environment_extractor import extract_environment_usage
from app.scanners.frontend_api_call_extractor import extract_frontend_api_calls
from app.scanners.types import (
    ApiCall,
    ApiRoute,
    AuthReport,
    DependencyReport,
    DeploymentReport,
    DocumentationClaim,
    EnvReport,
    EnvUsage,
    GapDraft,
)


COMMON_ENV_VARS = {"NODE_ENV", "PYTHONPATH", "PATH", "HOME", "PWD", "PORT"}
DATABASE_TECHNOLOGIES = {"postgresql", "mongodb", "mysql", "sqlite"}


@dataclass
class RepositoryAnalysis:
    gaps: list[GapDraft]
    reality_score: int
    category_counts: dict[str, int]
    analysis: dict


def analyze_repository(repo_path: Path) -> RepositoryAnalysis:
    doc_claims = extract_documentation_claims(repo_path)
    backend_routes = extract_backend_routes(repo_path)
    frontend_calls = extract_frontend_api_calls(repo_path)
    env_report = extract_environment_usage(repo_path)
    deployment = extract_deployment_config(repo_path)
    dependencies = extract_dependency_reality(repo_path)
    auth = detect_auth_mechanisms(repo_path, dependencies)

    gaps = []
    gaps.extend(_detect_api_gaps(frontend_calls, backend_routes))
    gaps.extend(_detect_doc_api_gaps(doc_claims, backend_routes))
    gaps.extend(_detect_env_gaps(env_report))
    gaps.extend(_detect_deployment_gaps(doc_claims, deployment))
    gaps.extend(_detect_dependency_gaps(doc_claims, dependencies, env_report))
    gaps.extend(_detect_auth_gaps(doc_claims, auth))

    gaps = GapReasoningAgent().enrich(_dedupe_gaps(gaps))
    category_counts = _category_counts(gaps)
    score = calculate_reality_score(gaps)

    return RepositoryAnalysis(
        gaps=gaps,
        reality_score=score,
        category_counts=category_counts,
        analysis=_serialize_analysis(
            doc_claims=doc_claims,
            backend_routes=backend_routes,
            frontend_calls=frontend_calls,
            env_report=env_report,
            deployment=deployment,
            dependencies=dependencies,
            auth=auth,
        ),
    )


def calculate_reality_score(gaps: list[GapDraft]) -> int:
    penalties = {"High": 10, "Medium": 5, "Low": 2}
    score = 100 - sum(penalties.get(gap.severity, 0) for gap in gaps)
    return max(0, score)


def _detect_api_gaps(frontend_calls: list[ApiCall], backend_routes: list[ApiRoute]) -> list[GapDraft]:
    gaps: list[GapDraft] = []
    route_by_path = {_contract(route.path): route for route in backend_routes}
    route_contracts = {(_contract(route.path), route.method): route for route in backend_routes}

    for call in frontend_calls:
        call_path = _contract(call.endpoint)
        exact = route_contracts.get((call_path, call.method))
        if exact:
            continue

        same_path = route_by_path.get(call_path)
        if same_path:
            gaps.append(
                GapDraft(
                    category="API",
                    severity="High",
                    claim_text=f"Frontend calls {call.method} {call.endpoint}.",
                    reality_text=f"Backend exposes {same_path.method} {same_path.path} for that path, not {call.method}.",
                    source_file=call.source_file,
                    affected_file=same_path.source_file,
                )
            )
            continue

        version_match = _find_version_match(call_path, backend_routes)
        if version_match:
            gaps.append(
                GapDraft(
                    category="API",
                    severity="High",
                    claim_text=f"Frontend calls {call.method} {call.endpoint}.",
                    reality_text=f"Backend route appears versioned as {version_match.method} {version_match.path}.",
                    source_file=call.source_file,
                    affected_file=version_match.source_file,
                )
            )
            continue

        gaps.append(
            GapDraft(
                category="API",
                severity="High",
                claim_text=f"Frontend calls {call.method} {call.endpoint}.",
                reality_text="No matching backend route was detected.",
                source_file=call.source_file,
                affected_file=None,
            )
        )

    return gaps


def _detect_doc_api_gaps(claims: list[DocumentationClaim], routes: list[ApiRoute]) -> list[GapDraft]:
    gaps: list[GapDraft] = []
    route_contracts = {(_contract(route.path), route.method): route for route in routes}
    for claim in [claim for claim in claims if claim.category == "api_endpoint"]:
        parsed = _parse_method_path(claim.value)
        if not parsed:
            continue
        method, path = parsed
        if (_contract(path), method) in route_contracts:
            continue
        gaps.append(
            GapDraft(
                category="API",
                severity="Medium",
                claim_text=f"Documentation claims endpoint {method} {path}.",
                reality_text="No matching backend route was detected.",
                source_file=_source(claim),
            )
        )
    return gaps


def _detect_env_gaps(env_report: EnvReport) -> list[GapDraft]:
    gaps: list[GapDraft] = []
    for usage in env_report.used:
        if usage.name in COMMON_ENV_VARS or usage.name in env_report.example_vars:
            continue
        gaps.append(
            GapDraft(
                category="Env",
                severity="High",
                claim_text=f"Code reads environment variable {usage.name}.",
                reality_text=".env.example does not define it.",
                source_file=_env_source(usage),
                affected_file=", ".join(env_report.example_files) if env_report.example_files else ".env.example",
            )
        )
    return gaps


def _detect_deployment_gaps(
    claims: list[DocumentationClaim],
    deployment: DeploymentReport,
) -> list[GapDraft]:
    gaps: list[GapDraft] = []
    backend_ports = {item.value for item in deployment.backend_ports}
    frontend_ports = {item.value for item in deployment.frontend_ports}

    for claim in claims:
        if claim.category == "backend_port" and backend_ports and claim.value not in backend_ports:
            gaps.append(
                GapDraft(
                    category="Deployment",
                    severity="High",
                    claim_text=f"Documentation says backend port {claim.value}.",
                    reality_text=f"Deployment/config files indicate backend port(s): {', '.join(sorted(backend_ports))}.",
                    source_file=_source(claim),
                    affected_file=_first_source(deployment.backend_ports),
                )
            )
        if claim.category == "frontend_port" and frontend_ports and claim.value not in frontend_ports:
            gaps.append(
                GapDraft(
                    category="Deployment",
                    severity="High",
                    claim_text=f"Documentation says frontend port {claim.value}.",
                    reality_text=f"Frontend config/scripts indicate port(s): {', '.join(sorted(frontend_ports))}.",
                    source_file=_source(claim),
                    affected_file=_first_source(deployment.frontend_ports),
                )
            )
        if claim.category == "docker" and not deployment.dockerfiles and not deployment.compose_files:
            gaps.append(
                GapDraft(
                    category="Deployment",
                    severity="Medium",
                    claim_text=claim.claim_text,
                    reality_text="No Dockerfile or docker-compose file was detected.",
                    source_file=_source(claim),
                )
            )

    return gaps


def _detect_dependency_gaps(
    claims: list[DocumentationClaim],
    dependencies: DependencyReport,
    env_report: EnvReport,
) -> list[GapDraft]:
    gaps: list[GapDraft] = []
    detected_databases = {
        technology
        for technology in DATABASE_TECHNOLOGIES
        if dependencies.technologies.get(technology)
    }

    for claim in claims:
        if claim.category == "database":
            claimed_database = _normalize_database(claim.value)
            if claimed_database not in detected_databases:
                reality = (
                    f"Dependency files suggest {', '.join(sorted(detected_databases))}."
                    if detected_databases
                    else "No matching database dependency was detected."
                )
                gaps.append(
                    GapDraft(
                        category="Dependencies",
                        severity="Medium",
                        claim_text=f"Documentation claims {claimed_database} as the database.",
                        reality_text=reality,
                        source_file=_source(claim),
                        affected_file=_technology_source(dependencies, detected_databases),
                    )
                )

        if claim.category == "redis" and not dependencies.technologies.get("redis"):
            redis_used = any(usage.name == "REDIS_URL" for usage in env_report.used)
            if not redis_used:
                gaps.append(
                    GapDraft(
                        category="Dependencies",
                        severity="Medium",
                        claim_text=claim.claim_text,
                        reality_text="No Redis dependency or Redis environment usage was detected.",
                        source_file=_source(claim),
                    )
                )

        if claim.category == "rabbitmq" and not dependencies.technologies.get("rabbitmq"):
            gaps.append(
                GapDraft(
                    category="Dependencies",
                    severity="Medium",
                    claim_text=claim.claim_text,
                    reality_text="No RabbitMQ dependency was detected in package or Python dependency files.",
                    source_file=_source(claim),
                    affected_file=", ".join(dependencies.package_files + dependencies.requirement_files + dependencies.pyproject_files) or None,
                )
            )

    return gaps


def _detect_auth_gaps(claims: list[DocumentationClaim], auth: AuthReport) -> list[GapDraft]:
    gaps: list[GapDraft] = []
    mechanisms = set(auth.mechanisms)

    for claim in [claim for claim in claims if claim.category == "auth"]:
        claimed = "sessions" if claim.value.lower() in {"session", "sessions"} else claim.value.lower()
        if claimed in mechanisms:
            continue
        reality = (
            f"Code/dependencies indicate {', '.join(sorted(mechanisms))}."
            if mechanisms
            else "No matching authentication mechanism was detected."
        )
        gaps.append(
            GapDraft(
                category="Auth",
                severity="High",
                claim_text=f"Documentation claims {claimed} authentication.",
                reality_text=reality,
                source_file=_source(claim),
                affected_file=_auth_source(auth),
            )
        )
    return gaps


def _serialize_analysis(
    doc_claims: list[DocumentationClaim],
    backend_routes: list[ApiRoute],
    frontend_calls: list[ApiCall],
    env_report: EnvReport,
    deployment: DeploymentReport,
    dependencies: DependencyReport,
    auth: AuthReport,
) -> dict:
    missing_env = sorted(
        {
            usage.name
            for usage in env_report.used
            if usage.name not in COMMON_ENV_VARS and usage.name not in env_report.example_vars
        }
    )
    return {
        "doc_claims": [
            {
                "category": claim.category,
                "value": claim.value,
                "claim_text": claim.claim_text,
                "source_file": _source(claim),
            }
            for claim in doc_claims[:80]
        ],
        "backend_routes": [
            {
                "method": route.method,
                "path": route.path,
                "source_file": route.source_file,
                "framework": route.framework,
            }
            for route in backend_routes[:120]
        ],
        "frontend_calls": [
            {
                "method": call.method,
                "endpoint": call.endpoint,
                "source_file": call.source_file,
                "caller": call.caller,
            }
            for call in frontend_calls[:120]
        ],
        "environment": {
            "used": sorted({usage.name for usage in env_report.used}),
            "example_vars": sorted(env_report.example_vars),
            "missing": missing_env,
            "example_files": env_report.example_files,
        },
        "deployment": {
            "dockerfiles": deployment.dockerfiles,
            "compose_files": deployment.compose_files,
            "render_files": deployment.render_files,
            "vercel_files": deployment.vercel_files,
            "backend_ports": sorted({item.value for item in deployment.backend_ports}),
            "frontend_ports": sorted({item.value for item in deployment.frontend_ports}),
            "compose_ports": sorted({item.value for item in deployment.compose_ports}),
        },
        "technologies": dependencies.technologies,
        "auth": {
            "mechanisms": sorted(auth.mechanisms),
        },
    }


def _parse_method_path(value: str) -> tuple[str, str] | None:
    match = re.match(r"\s*(GET|POST|PUT|PATCH|DELETE|OPTIONS|HEAD)?\s*(/[^\s`]+)", value, re.IGNORECASE)
    if not match:
        return None
    return (match.group(1) or "GET").upper(), match.group(2)


def _contract(path: str) -> str:
    clean = path.split("?")[0].split("#")[0].strip().lower()
    if not clean.startswith("/"):
        clean = f"/{clean}"
    clean = re.sub(r"/+", "/", clean)
    clean = re.sub(r"\{[^/]+\}", "{param}", clean)
    clean = re.sub(r":[^/]+", "{param}", clean)
    clean = clean.rstrip("/") or "/"
    return clean


def _without_version(path: str) -> str:
    return re.sub(r"^/api/v\d+", "/api", path)


def _find_version_match(call_path: str, routes: list[ApiRoute]) -> ApiRoute | None:
    target = _without_version(call_path)
    for route in routes:
        if _without_version(_contract(route.path)) == target:
            return route
    return None


def _normalize_database(value: str) -> str:
    lower = value.lower()
    if lower in {"postgres", "postgresql"}:
        return "postgresql"
    if lower in {"mongo", "mongodb"}:
        return "mongodb"
    return lower


def _source(claim: DocumentationClaim) -> str:
    return f"{claim.source_file}:{claim.line}" if claim.line else claim.source_file


def _env_source(usage: EnvUsage) -> str:
    return f"{usage.source_file}:{usage.line}" if usage.line else usage.source_file


def _first_source(items) -> str | None:
    if not items:
        return None
    first = items[0]
    return f"{first.source_file}:{first.line}" if first.line else first.source_file


def _technology_source(dependencies: DependencyReport, technologies: set[str]) -> str | None:
    sources: list[str] = []
    for technology in sorted(technologies):
        sources.extend(item.source_file for item in dependencies.evidence.get(technology, []))
    return ", ".join(sorted(set(sources))) or None


def _auth_source(auth: AuthReport) -> str | None:
    sources: list[str] = []
    for items in auth.evidence.values():
        sources.extend(item.source_file for item in items)
    return ", ".join(sorted(set(sources))[:4]) or None


def _dedupe_gaps(gaps: list[GapDraft]) -> list[GapDraft]:
    seen: set[tuple[str, str, str, str, str | None, str | None]] = set()
    deduped: list[GapDraft] = []
    for gap in gaps:
        key = (
            gap.category,
            gap.severity,
            gap.claim_text,
            gap.reality_text,
            gap.source_file,
            gap.affected_file,
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(gap)
    return deduped


def _category_counts(gaps: list[GapDraft]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for gap in gaps:
        counts[gap.category] = counts.get(gap.category, 0) + 1
    return counts
