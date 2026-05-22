import re
from pathlib import Path

from app.scanners.repository_reader import line_number, read_text, relative_path
from app.scanners.types import ApiRoute


HTTP_METHODS = ("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD")


def extract_backend_routes(repo_path: Path) -> list[ApiRoute]:
    routes: list[ApiRoute] = []
    routes.extend(_extract_fastapi_routes(repo_path))
    routes.extend(_extract_express_routes(repo_path))
    return _dedupe_routes(routes)


def _extract_fastapi_routes(repo_path: Path) -> list[ApiRoute]:
    routes: list[ApiRoute] = []
    decorator_pattern = re.compile(
        r"@(?P<target>[A-Za-z_][A-Za-z0-9_]*)\.(?P<method>get|post|put|patch|delete|options|head)\(\s*['\"](?P<path>[^'\"]+)['\"]",
        re.IGNORECASE,
    )

    for file_path in repo_path.rglob("*.py"):
        if _skip_path(repo_path, file_path):
            continue
        text = read_text(file_path)
        relative = relative_path(repo_path, file_path)
        router_prefixes = _fastapi_router_prefixes(text)

        for match in decorator_pattern.finditer(text):
            target = match.group("target")
            prefix = router_prefixes.get(target, "")
            route_path = _join_paths(prefix, match.group("path"))
            routes.append(
                ApiRoute(
                    method=match.group("method").upper(),
                    path=route_path,
                    source_file=relative,
                    line=line_number(text, match.start()),
                    framework="fastapi",
                )
            )

    return routes


def _fastapi_router_prefixes(text: str) -> dict[str, str]:
    prefixes: dict[str, str] = {"app": ""}
    assignment_pattern = re.compile(
        r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?:APIRouter|FastAPI)\((?P<body>[^)]*)\)",
        re.DOTALL,
    )
    prefix_pattern = re.compile(r"prefix\s*=\s*['\"]([^'\"]+)['\"]")

    for match in assignment_pattern.finditer(text):
        body = match.group("body")
        prefix_match = prefix_pattern.search(body)
        prefixes[match.group("name")] = prefix_match.group(1) if prefix_match else ""

    return prefixes


def _extract_express_routes(repo_path: Path) -> list[ApiRoute]:
    routes: list[ApiRoute] = []
    js_extensions = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}
    direct_route_pattern = re.compile(
        r"(?P<target>app|router|apiRouter|routes)\.(?P<method>get|post|put|patch|delete|options|head)\(\s*['\"`](?P<path>[^'\"`]+)['\"`]",
        re.IGNORECASE,
    )
    chained_route_pattern = re.compile(
        r"\.route\(\s*['\"`](?P<path>[^'\"`]+)['\"`]\s*\)(?P<chain>(?:\s*\.\s*(?:get|post|put|patch|delete|options|head)\s*\()+)",
        re.IGNORECASE,
    )
    chained_method_pattern = re.compile(r"\.\s*(get|post|put|patch|delete|options|head)\s*\(", re.IGNORECASE)

    for file_path in repo_path.rglob("*"):
        if not file_path.is_file() or file_path.suffix.lower() not in js_extensions:
            continue
        if _skip_path(repo_path, file_path):
            continue

        text = read_text(file_path)
        relative = relative_path(repo_path, file_path)
        for match in direct_route_pattern.finditer(text):
            routes.append(
                ApiRoute(
                    method=match.group("method").upper(),
                    path=_normalize_path(match.group("path")),
                    source_file=relative,
                    line=line_number(text, match.start()),
                    framework="express",
                )
            )

        for match in chained_route_pattern.finditer(text):
            for method_match in chained_method_pattern.finditer(match.group("chain")):
                routes.append(
                    ApiRoute(
                        method=method_match.group(1).upper(),
                        path=_normalize_path(match.group("path")),
                        source_file=relative,
                        line=line_number(text, match.start()),
                        framework="express",
                    )
                )

    return routes


def _join_paths(prefix: str, path: str) -> str:
    return _normalize_path(f"{prefix.rstrip('/')}/{path.lstrip('/')}")


def _normalize_path(path: str) -> str:
    clean = path.strip()
    if not clean.startswith("/"):
        clean = f"/{clean}"
    clean = re.sub(r"/+", "/", clean)
    return clean.rstrip("/") or "/"


def _skip_path(repo_path: Path, file_path: Path) -> bool:
    parts = set(file_path.relative_to(repo_path).parts)
    return bool(parts.intersection({".git", "node_modules", ".venv", "venv", "dist", "build"}))


def _dedupe_routes(routes: list[ApiRoute]) -> list[ApiRoute]:
    seen: set[tuple[str, str, str]] = set()
    deduped: list[ApiRoute] = []
    for route in routes:
        key = (route.method, route.path, route.source_file)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(route)
    return deduped
