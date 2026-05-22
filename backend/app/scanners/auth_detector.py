import re
from pathlib import Path

from app.scanners.repository_reader import iter_text_files, line_number, read_text, relative_path
from app.scanners.types import AuthReport, DependencyReport, Evidence


AUTH_PATTERNS = {
    "jwt": re.compile(r"\b(jwt|jsonwebtoken|jwt\.decode|jwt\.encode|pyjwt|jose)\b", re.IGNORECASE),
    "sessions": re.compile(r"\b(session|express-session|SessionMiddleware)\b", re.IGNORECASE),
    "cookies": re.compile(r"\b(cookie|set_cookie|httponly)\b", re.IGNORECASE),
    "bearer": re.compile(r"\bBearer\s+[A-Za-z0-9_.-]*|authorization\s*[:=]", re.IGNORECASE),
}


def detect_auth_mechanisms(repo_path: Path, dependencies: DependencyReport) -> AuthReport:
    report = AuthReport()

    for technology in ("jwt", "sessions"):
        if dependencies.technologies.get(technology):
            report.mechanisms.add(technology)
            report.evidence.setdefault(technology, []).extend(
                dependencies.evidence.get(technology, [])
            )

    for file_path in iter_text_files(repo_path):
        if file_path.suffix.lower() not in {".py", ".js", ".jsx", ".ts", ".tsx"}:
            continue
        text = read_text(file_path)
        relative = relative_path(repo_path, file_path)

        for mechanism, pattern in AUTH_PATTERNS.items():
            for match in pattern.finditer(text):
                report.mechanisms.add(mechanism)
                report.evidence.setdefault(mechanism, []).append(
                    Evidence(match.group(0), relative, line_number(text, match.start()), match.group(0))
                )

    return report
