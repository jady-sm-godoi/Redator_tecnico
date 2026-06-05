from src.models.analysis import PRInsight
from src.connectors.base import BaseConnector


class PRAnalyzer:
    def __init__(self, connector: BaseConnector):
        self.connector = connector

    def analyze(self, token: str, state: str = "all") -> list[PRInsight]:
        from src.connectors.github import GitHubConnector
        from src.connectors.gitlab import GitLabConnector

        if isinstance(self.connector, GitHubConnector):
            raw_prs = self.connector.fetch_prs(token, state=state)
        elif isinstance(self.connector, GitLabConnector):
            raw_prs = self.connector.fetch_merge_requests(token, state=state)
        else:
            return []

        insights: list[PRInsight] = []
        for raw in raw_prs:
            decision, rationale = self._extract_decision(raw.get("description", ""))
            insights.append(
                PRInsight(
                    pr_number=raw["number"],
                    title=raw["title"],
                    description=raw.get("description", ""),
                    decision=decision,
                    rationale=rationale,
                    date=raw.get("date"),
                )
            )
        return insights

    def _extract_decision(self, description: str) -> tuple[str | None, str | None]:
        if not description:
            return None, None
        lines = description.split("\n")
        decision = None
        rationale = None
        for line in lines:
            lower = line.lower().strip()
            if lower.startswith("decision:") or lower.startswith("**decision:**"):
                decision = line.split(":", 1)[-1].strip().strip("*").strip()
            if lower.startswith("rationale:") or lower.startswith("**rationale:**"):
                rationale = line.split(":", 1)[-1].strip().strip("*").strip()
            if lower.startswith("why:") or lower.startswith("**why:**"):
                rationale = line.split(":", 1)[-1].strip().strip("*").strip()
        return decision, rationale
