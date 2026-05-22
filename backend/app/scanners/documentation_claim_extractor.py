import json
import re
from pathlib import Path
from typing import Any

from app.agents.llm_client import OptionalLlmClient
from app.scanners.repository_reader import line_number, read_text, relative_path
from app.scanners.types import DocumentationClaim


DOC_EXTENSIONS = {".md", ".mdx", ".txt", ".rst"}
CLAIM_CATEGORIES = {
    "backend_port",
    "frontend_port",
    "database",
    "auth",
    "redis",
    "rabbitmq",
    "docker",
    "deployment_command",
    "api_endpoint",
}


def extract_documentation_claims(repo_path: Path) -> list[DocumentationClaim]:
    docs = list(_iter_doc_files(repo_path))
    llm_claims = _extract_with_llm(repo_path, docs)
    if llm_claims:
        return _dedupe_claims(llm_claims + _extract_with_regex(repo_path, docs))
    return _dedupe_claims(_extract_with_regex(repo_path, docs))


def _iter_doc_files(repo_path: Path) -> list[Path]:
    doc_files: list[Path] = []
    for file_path in repo_path.rglob("*"):
        if not file_path.is_file():
            continue
        parts = set(file_path.relative_to(repo_path).parts)
        if parts.intersection({".git", "node_modules", ".venv", "venv", "dist", "build"}):
            continue
        if file_path.name.lower().startswith("readme") or "docs" in parts:
            if file_path.suffix.lower() in DOC_EXTENSIONS or file_path.name.lower().startswith("readme"):
                doc_files.append(file_path)
    return doc_files


def _extract_with_llm(repo_path: Path, docs: list[Path]) -> list[DocumentationClaim]:
    client = OptionalLlmClient()
    if not client.enabled or not docs:
        return []

    excerpts: list[str] = []
    for file_path in docs[:6]:
        text = read_text(file_path)
        excerpts.append(
            f"FILE: {relative_path(repo_path, file_path)}\n{text[:3500]}"
        )

    result = client.complete(
        system_prompt=(
            "You extract precise engineering claims from repository documentation. "
            "Return only JSON with a top-level claims array. Each claim must include "
            "category, value, claim_text, source_file. Categories: "
            + ", ".join(sorted(CLAIM_CATEGORIES))
            + "."
        ),
        user_prompt="\n\n".join(excerpts),
    )
    if not result:
        return []

    try:
        payload = _parse_json_object(result.text)
        raw_claims = payload.get("claims", [])
    except (json.JSONDecodeError, AttributeError):
        return []

    claims: list[DocumentationClaim] = []
    for raw_claim in raw_claims:
        if not isinstance(raw_claim, dict):
            continue
        category = str(raw_claim.get("category", "")).strip()
        source_file = str(raw_claim.get("source_file", "")).strip()
        value = str(raw_claim.get("value", "")).strip()
        claim_text = str(raw_claim.get("claim_text", "")).strip()
        if category in CLAIM_CATEGORIES and source_file and value and claim_text:
            claims.append(
                DocumentationClaim(
                    category=category,
                    value=value,
                    claim_text=claim_text,
                    source_file=source_file,
                )
            )
    return claims


def _parse_json_object(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()
    first = cleaned.find("{")
    last = cleaned.rfind("}")
    if first >= 0 and last >= first:
        cleaned = cleaned[first : last + 1]
    return json.loads(cleaned)


def _extract_with_regex(repo_path: Path, docs: list[Path]) -> list[DocumentationClaim]:
    claims: list[DocumentationClaim] = []
    endpoint_pattern = re.compile(
        r"(?:(GET|POST|PUT|PATCH|DELETE)\s+)?(`?)(/[A-Za-z0-9_./:{}-]*api[A-Za-z0-9_./:{}-]*)\2",
        re.IGNORECASE,
    )

    for file_path in docs:
        text = read_text(file_path)
        relative = relative_path(repo_path, file_path)
        lines = text.splitlines()

        for index, line in enumerate(lines, start=1):
            lower = line.lower()
            clean_line = line.strip().strip("-* ")
            if not clean_line:
                continue

            if "backend" in lower and "port" in lower:
                for port in re.findall(r"\b(\d{3,5})\b", line):
                    claims.append(_claim("backend_port", port, clean_line, relative, index))

            if "frontend" in lower and "port" in lower:
                for port in re.findall(r"\b(\d{3,5})\b", line):
                    claims.append(_claim("frontend_port", port, clean_line, relative, index))

            if "localhost:" in lower:
                for port in re.findall(r"localhost:(\d{3,5})", line, flags=re.IGNORECASE):
                    category = "frontend_port" if "frontend" in lower or "vite" in lower else "backend_port"
                    claims.append(_claim(category, port, clean_line, relative, index))

            for database in ("postgresql", "postgres", "mongodb", "mongo", "mysql", "sqlite"):
                if database in lower:
                    value = "postgresql" if database == "postgres" else "mongodb" if database == "mongo" else database
                    claims.append(_claim("database", value, clean_line, relative, index))

            if "jwt" in lower or "json web token" in lower:
                claims.append(_claim("auth", "jwt", clean_line, relative, index))
            if "session" in lower:
                claims.append(_claim("auth", "sessions", clean_line, relative, index))
            if "bearer" in lower:
                claims.append(_claim("auth", "bearer", clean_line, relative, index))
            if "cookie" in lower:
                claims.append(_claim("auth", "cookies", clean_line, relative, index))

            if "redis" in lower:
                claims.append(_claim("redis", "redis", clean_line, relative, index))
            if "rabbitmq" in lower or "rabbit mq" in lower:
                claims.append(_claim("rabbitmq", "rabbitmq", clean_line, relative, index))
            if "docker" in lower:
                claims.append(_claim("docker", "docker", clean_line, relative, index))

            if any(command in lower for command in ("npm run", "uvicorn", "docker compose", "vercel", "render")):
                claims.append(_claim("deployment_command", clean_line, clean_line, relative, index))

            for match in endpoint_pattern.finditer(line):
                method = (match.group(1) or "GET").upper()
                endpoint = match.group(3)
                claims.append(
                    _claim(
                        "api_endpoint",
                        f"{method} {endpoint}",
                        clean_line,
                        relative,
                        line_number(text, match.start()),
                    )
                )

    return claims


def _claim(
    category: str,
    value: str,
    claim_text: str,
    source_file: str,
    line: int | None,
) -> DocumentationClaim:
    return DocumentationClaim(
        category=category,
        value=value.strip(),
        claim_text=claim_text[:500],
        source_file=source_file,
        line=line,
    )


def _dedupe_claims(claims: list[DocumentationClaim]) -> list[DocumentationClaim]:
    seen: set[tuple[str, str, str]] = set()
    deduped: list[DocumentationClaim] = []
    for claim in claims:
        key = (claim.category, claim.value.lower(), claim.source_file)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(claim)
    return deduped
