import re
from pathlib import Path

from app.scanners.repository_reader import line_number, read_text, relative_path
from app.scanners.types import ApiCall


JS_EXTENSIONS = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}


def extract_frontend_api_calls(repo_path: Path) -> list[ApiCall]:
    calls: list[ApiCall] = []

    for file_path in repo_path.rglob("*"):
        if not file_path.is_file() or file_path.suffix.lower() not in JS_EXTENSIONS:
            continue
        if _skip_path(repo_path, file_path):
            continue
        text = read_text(file_path)
        relative = relative_path(repo_path, file_path)
        calls.extend(_extract_fetch_calls(text, relative))
        calls.extend(_extract_method_calls(text, relative))
        calls.extend(_extract_object_axios_calls(text, relative))

    return _dedupe_calls(calls)


def _extract_fetch_calls(text: str, source_file: str) -> list[ApiCall]:
    calls: list[ApiCall] = []
    fetch_pattern = re.compile(r"fetch\(\s*([`'\"])(?P<url>.*?)(?:\1)", re.DOTALL)
    method_pattern = re.compile(r"method\s*:\s*['\"](?P<method>[A-Za-z]+)['\"]")

    for match in fetch_pattern.finditer(text):
        endpoint = _normalize_endpoint(match.group("url"))
        if not endpoint:
            continue
        nearby = text[match.end() : match.end() + 220]
        method_match = method_pattern.search(nearby)
        calls.append(
            ApiCall(
                method=method_match.group("method").upper() if method_match else "GET",
                endpoint=endpoint,
                source_file=source_file,
                line=line_number(text, match.start()),
                caller="fetch",
            )
        )
    return calls


def _extract_method_calls(text: str, source_file: str) -> list[ApiCall]:
    calls: list[ApiCall] = []
    method_pattern = re.compile(
        r"(?:axios|api|client|http)\.(?P<method>get|post|put|patch|delete)\(\s*([`'\"])(?P<url>.*?)(?:\2)",
        re.IGNORECASE | re.DOTALL,
    )

    for match in method_pattern.finditer(text):
        endpoint = _normalize_endpoint(match.group("url"))
        if not endpoint:
            continue
        calls.append(
            ApiCall(
                method=match.group("method").upper(),
                endpoint=endpoint,
                source_file=source_file,
                line=line_number(text, match.start()),
                caller="axios",
            )
        )
    return calls


def _extract_object_axios_calls(text: str, source_file: str) -> list[ApiCall]:
    calls: list[ApiCall] = []
    call_pattern = re.compile(r"axios\(\s*\{(?P<body>.*?)\}\s*\)", re.DOTALL)
    method_pattern = re.compile(r"method\s*:\s*['\"](?P<method>[A-Za-z]+)['\"]", re.IGNORECASE)
    url_pattern = re.compile(r"url\s*:\s*([`'\"])(?P<url>.*?)(?:\1)", re.DOTALL)

    for match in call_pattern.finditer(text):
        body = match.group("body")
        method_match = method_pattern.search(body)
        url_match = url_pattern.search(body)
        if not url_match:
            continue
        endpoint = _normalize_endpoint(url_match.group("url"))
        if not endpoint:
            continue
        calls.append(
            ApiCall(
                method=method_match.group("method").upper() if method_match else "GET",
                endpoint=endpoint,
                source_file=source_file,
                line=line_number(text, match.start()),
                caller="axios",
            )
        )
    return calls


def _normalize_endpoint(raw_url: str) -> str | None:
    clean = raw_url.strip()
    if not clean:
        return None
    api_index = clean.find("/api")
    if api_index == -1:
        return None
    clean = clean[api_index:]
    clean = clean.split("?")[0].split("#")[0]
    clean = re.sub(r"\$\{[^}]+\}", "", clean)
    clean = re.sub(r"/+", "/", clean)
    return clean.rstrip("/") or "/"


def _skip_path(repo_path: Path, file_path: Path) -> bool:
    parts = set(file_path.relative_to(repo_path).parts)
    return bool(parts.intersection({".git", "node_modules", ".venv", "venv", "dist", "build"}))


def _dedupe_calls(calls: list[ApiCall]) -> list[ApiCall]:
    seen: set[tuple[str, str, str]] = set()
    deduped: list[ApiCall] = []
    for call in calls:
        key = (call.method, call.endpoint, call.source_file)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(call)
    return deduped
