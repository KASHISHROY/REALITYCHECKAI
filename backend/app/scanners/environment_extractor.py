import re
from pathlib import Path

from app.scanners.repository_reader import iter_text_files, line_number, read_text, relative_path
from app.scanners.types import EnvReport, EnvUsage


ENV_NAME_PATTERN = r"[A-Z][A-Z0-9_]{1,}"


def extract_environment_usage(repo_path: Path) -> EnvReport:
    report = EnvReport()

    for file_path in iter_text_files(repo_path):
        relative = relative_path(repo_path, file_path)
        if file_path.name in {".env.example", ".env.sample"} or relative.endswith(".env.example"):
            report.example_files.append(relative)
            report.example_vars.update(_parse_env_example(read_text(file_path)))
            continue

        text = read_text(file_path)
        for usage in _extract_usages(text, relative):
            report.used.append(usage)

    report.used = _dedupe_usages(report.used)
    return report


def _parse_env_example(text: str) -> set[str]:
    env_vars: set[str] = set()
    for line in text.splitlines():
        clean = line.strip()
        if not clean or clean.startswith("#") or "=" not in clean:
            continue
        name = clean.split("=", 1)[0].strip()
        if re.fullmatch(ENV_NAME_PATTERN, name):
            env_vars.add(name)
    return env_vars


def _extract_usages(text: str, source_file: str) -> list[EnvUsage]:
    patterns = [
        re.compile(rf"process\.env\.({ENV_NAME_PATTERN})"),
        re.compile(rf"import\.meta\.env\.({ENV_NAME_PATTERN})"),
        re.compile(rf"os\.getenv\(\s*['\"]({ENV_NAME_PATTERN})['\"]"),
        re.compile(rf"os\.environ\[\s*['\"]({ENV_NAME_PATTERN})['\"]\s*\]"),
        re.compile(rf"os\.environ\.get\(\s*['\"]({ENV_NAME_PATTERN})['\"]"),
    ]

    usages: list[EnvUsage] = []
    for pattern in patterns:
        for match in pattern.finditer(text):
            usages.append(
                EnvUsage(
                    name=match.group(1),
                    source_file=source_file,
                    line=line_number(text, match.start()),
                )
            )
    return usages


def _dedupe_usages(usages: list[EnvUsage]) -> list[EnvUsage]:
    seen: set[tuple[str, str]] = set()
    deduped: list[EnvUsage] = []
    for usage in usages:
        key = (usage.name, usage.source_file)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(usage)
    return deduped
