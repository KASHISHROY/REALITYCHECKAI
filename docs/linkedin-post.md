# LinkedIn Launch Post Draft

I built RealityCheck AI, a full-stack engineering tool that detects when a repository's documentation, APIs, configs, dependencies, and deployment reality no longer match.

The problem is familiar: the README says one thing, the frontend calls another thing, the backend exposes something else, and deployment files quietly disagree with all of it.

RealityCheck AI scans a repository and detects:

- documentation drift
- frontend/backend API mismatches
- missing environment variables
- auth documentation mismatches
- dependency inconsistencies
- Docker/deployment reality gaps

The architecture is intentionally not LLM-only.

It uses deterministic scanners for exact evidence: FastAPI/Express routes, frontend API calls, env vars, Docker/Compose config, dependencies, and auth signals. Then it uses optional GenAI reasoning through Groq/OpenAI for natural-language claim extraction, explanations, severity reasoning, and fix recommendations.

No API key? It still works with deterministic fallback explanations.

I also created an intentionally broken demo repo with 39 gaps so the product can show realistic drift immediately.

This was a great exercise in building practical AI engineering tooling: not a chatbot, not a wrapper, but a system that helps engineers understand whether the repo's claimed behavior matches reality.

Next up: deeper AST parsing, GitHub App integration, historical scan comparison, PR patch generation, and CI/CD checks.
