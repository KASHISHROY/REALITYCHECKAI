import json
import re

from app.agents.llm_client import OptionalLlmClient
from app.scanners.types import GapDraft


class GapReasoningAgent:
    def __init__(self) -> None:
        self.client = OptionalLlmClient()

    def enrich(self, gaps: list[GapDraft]) -> list[GapDraft]:
        for gap in gaps:
            if self.client.enabled:
                llm_payload = self._ask_llm(gap)
                if llm_payload:
                    gap.explanation = llm_payload.get("explanation", "") or self._fallback_explanation(gap)
                    gap.suggested_fix = llm_payload.get("suggested_fix", "") or self._fallback_fix(gap)
                    continue
            gap.explanation = self._fallback_explanation(gap)
            gap.suggested_fix = self._fallback_fix(gap)
        return gaps

    def _ask_llm(self, gap: GapDraft) -> dict[str, str] | None:
        result = self.client.complete(
            system_prompt=(
                "You are a senior full-stack engineering reviewer. Explain repository reality gaps "
                "briefly and provide practical fixes. Return only JSON with explanation and suggested_fix."
            ),
            user_prompt=(
                f"Category: {gap.category}\n"
                f"Severity: {gap.severity}\n"
                f"Claim: {gap.claim_text}\n"
                f"Reality: {gap.reality_text}\n"
                f"Source: {gap.source_file}\n"
                f"Affected: {gap.affected_file}"
            ),
        )
        if not result:
            return None
        try:
            return _parse_json(result.text)
        except json.JSONDecodeError:
            return None

    def _fallback_explanation(self, gap: GapDraft) -> str:
        category = gap.category.lower()
        if category == "api":
            return "The frontend is calling an API contract that the backend scan did not find. This can create broken user flows at runtime."
        if category == "env":
            return "The code reads an environment variable that is missing from the example environment file, so new deployments may start with incomplete configuration."
        if category == "auth":
            return "The documented authentication model does not match the implementation signals found in code and dependencies. That can confuse client integration and security reviews."
        if category == "deployment":
            return "The documented runtime or deployment configuration differs from the files that actually drive containers or hosting."
        if category == "dependencies":
            return "The documentation claims one technology, but dependency files point to a different implementation reality."
        return "The repository contains a claim that does not line up with the implementation evidence found by the scanner."

    def _fallback_fix(self, gap: GapDraft) -> str:
        category = gap.category.lower()
        if category == "api":
            return "Align the frontend request path and HTTP method with the backend route, or add the missing backend route intentionally."
        if category == "env":
            return "Add the variable to .env.example with a safe placeholder, or remove the unused environment lookup from code."
        if category == "auth":
            return "Update the docs to describe the implemented auth mechanism, or migrate the code to the documented mechanism and add tests around login/logout."
        if category == "deployment":
            return "Update the README and deployment config to agree on ports, commands, and hosting assumptions."
        if category == "dependencies":
            return "Either update docs to match the installed dependency stack or change dependencies/configuration to match the documented architecture."
        return "Pick one source of truth, update the stale side, and add a lightweight check so the mismatch does not return."


def _parse_json(text: str) -> dict[str, str]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()
    first = cleaned.find("{")
    last = cleaned.rfind("}")
    if first >= 0 and last >= first:
        cleaned = cleaned[first : last + 1]
    payload = json.loads(cleaned)
    return {
        "explanation": str(payload.get("explanation", "")),
        "suggested_fix": str(payload.get("suggested_fix", "")),
    }
