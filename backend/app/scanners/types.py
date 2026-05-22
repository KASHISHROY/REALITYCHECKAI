from dataclasses import dataclass, field


@dataclass(frozen=True)
class Evidence:
    value: str
    source_file: str
    line: int | None = None
    raw: str | None = None


@dataclass(frozen=True)
class DocumentationClaim:
    category: str
    value: str
    claim_text: str
    source_file: str
    line: int | None = None


@dataclass(frozen=True)
class ApiRoute:
    method: str
    path: str
    source_file: str
    line: int | None = None
    framework: str = "unknown"


@dataclass(frozen=True)
class ApiCall:
    method: str
    endpoint: str
    source_file: str
    line: int | None = None
    caller: str = "unknown"


@dataclass(frozen=True)
class EnvUsage:
    name: str
    source_file: str
    line: int | None = None


@dataclass
class EnvReport:
    used: list[EnvUsage] = field(default_factory=list)
    example_vars: set[str] = field(default_factory=set)
    example_files: list[str] = field(default_factory=list)


@dataclass
class DeploymentReport:
    dockerfiles: list[str] = field(default_factory=list)
    compose_files: list[str] = field(default_factory=list)
    render_files: list[str] = field(default_factory=list)
    vercel_files: list[str] = field(default_factory=list)
    backend_ports: list[Evidence] = field(default_factory=list)
    frontend_ports: list[Evidence] = field(default_factory=list)
    compose_ports: list[Evidence] = field(default_factory=list)
    commands: list[Evidence] = field(default_factory=list)


@dataclass
class DependencyReport:
    package_files: list[str] = field(default_factory=list)
    requirement_files: list[str] = field(default_factory=list)
    pyproject_files: list[str] = field(default_factory=list)
    technologies: dict[str, bool] = field(default_factory=dict)
    evidence: dict[str, list[Evidence]] = field(default_factory=dict)


@dataclass
class AuthReport:
    mechanisms: set[str] = field(default_factory=set)
    evidence: dict[str, list[Evidence]] = field(default_factory=dict)


@dataclass
class GapDraft:
    category: str
    severity: str
    claim_text: str
    reality_text: str
    source_file: str | None = None
    affected_file: str | None = None
    explanation: str = ""
    suggested_fix: str = ""
