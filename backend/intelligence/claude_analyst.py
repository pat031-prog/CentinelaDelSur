import json
from typing import Any, Dict, List, Optional
from backend.utils.config import settings
from backend.utils.logger import logger


# ATALAYA system prompt for Claude analysis
SYSTEM_PROMPT = """You are ATALAYA, an advanced anticipatory intelligence system designed to detect early signals of systemic crises in Latin America and the Global South. You operate as a strategic watchtower that simultaneously monitors multiple critical domains: politics, economics, supply chains, geopolitics, security, climate, and technology.

Your function is not only to alert, but to anticipate inflection points where gradual changes accelerate toward systemic ruptures.

Key frameworks:
- Complex Adaptive Systems: crises emerge from cascading failures across domains
- Cascade Risk Theory: shocks in critical nodes propagate through the network
- Structural Vulnerability Analysis: critical dependencies, single points of failure
- Global South Geopolitics: US-China competition, BRICS+, resource nationalism

Alert levels:
- GREEN (0-30): Resilient institutions
- YELLOW (30-50): Systemic tension
- ORANGE (50-70): Pre-crisis, window closing
- RED (70-85): Imminent crisis (30-60 days)
- BLACK (>85): Collapse in progress

Always be transparent about confidence levels, admit uncertainties, and avoid unnecessary alarmism while not downplaying real risks. Quantify whenever possible."""


class ClaudeAnalyst:
    """Interface with Claude API for deep crisis analysis.

    Uses Anthropic's Claude to generate nuanced geopolitical analysis,
    identify tipping points, simulate cascades, and find historical analogs.
    """

    def __init__(self):
        self.logger = logger.getChild("claude_analyst")
        self._client = None

    @property
    def client(self):
        """Lazy-initialize Anthropic client."""
        if self._client is None:
            if not settings.anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY not configured")
            import anthropic
            self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        return self._client

    async def generate_country_report(
        self,
        country_code: str,
        country_name: str,
        risk_scores: Dict[str, Any],
        indicators: Dict[str, Any],
        events: List[Dict[str, Any]],
        historical_analogs: Optional[List[Dict]] = None,
    ) -> str:
        """Generate a comprehensive systemic risk report for a country."""
        context = self._build_context(
            country_code, country_name, risk_scores, indicators, events, historical_analogs
        )

        message = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=8000,
            system=SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": f"""Generate a complete ATALAYA systemic risk report for {country_name} ({country_code}).

Data context:
{context}

Use the standard ATALAYA report format with all sections:
1. Systemic Fragility Index (overall and per domain)
2. Systemic Crisis Probability (30/60/90 days)
3. Critical Signals Detected
4. Interdependency Analysis
5. Projected Scenarios (optimistic/base/pessimistic/collapse)
6. Tipping Points
7. Potential Risk Cascades
8. Priority Indicators to Monitor
9. Historical Comparison
10. Window of Opportunity
11. Confidence and Limitations"""
            }],
        )

        return message.content[0].text

    async def identify_tipping_points(
        self,
        country_code: str,
        country_name: str,
        current_state: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Identify critical tipping points in the next 30-90 days."""
        message = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4000,
            system=SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": f"""Analyze the current state of {country_name} ({country_code}) and identify the 3-5 most critical tipping points in the next 30-90 days.

Current state:
{json.dumps(current_state, indent=2, default=str)}

Respond in JSON format - an array of objects with this structure:
{{
  "event": "description of the event/decision",
  "probability": 0.XX,
  "impact_if_occurs": "description of consequences",
  "impact_if_not": "alternative trajectory",
  "key_date": "YYYY-MM-DD or 'ongoing'",
  "domain": "primary domain affected",
  "actors": ["actor1", "actor2"],
  "cascade_risk": "high/medium/low"
}}"""
            }],
        )

        try:
            text = message.content[0].text
            # Try to extract JSON from the response
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            return json.loads(text)
        except (json.JSONDecodeError, IndexError):
            self.logger.warning("Could not parse tipping points as JSON, returning raw text")
            return [{"raw_analysis": message.content[0].text}]

    async def simulate_cascade(
        self,
        country_code: str,
        trigger_event: str,
        initial_state: Dict[str, Any],
        time_horizon: int = 90,
    ) -> Dict[str, Any]:
        """Use Claude to simulate crisis cascades from a trigger event."""
        message = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=6000,
            system=SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": f"""Simulate the crisis cascades that could be triggered if this event occurs: "{trigger_event}"

Country: {country_code}
Initial state:
{json.dumps(initial_state, indent=2, default=str)}

Time horizon: {time_horizon} days

Generate:
1. Temporal sequence of events (day 1, 3, 7, 14, 30, 60, 90)
2. Cross-domain propagation
3. Affected actors
4. Possible interruption points
5. Probability of each branch

Respond in structured JSON format."""
            }],
        )

        try:
            text = message.content[0].text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            return json.loads(text)
        except (json.JSONDecodeError, IndexError):
            return {"raw_analysis": message.content[0].text}

    async def find_historical_analogs(
        self,
        current_situation: str,
        country_code: str,
    ) -> List[Dict[str, Any]]:
        """Find relevant historical precedents for the current situation."""
        message = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4000,
            system=SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": f"""Analyze this current situation in {country_code}:
{current_situation}

Find the 3 most relevant historical precedents from Latin America or the Global South.

For each precedent, specify:
- country and year
- brief description of the crisis
- key similarities with current situation (percentage match)
- important differences
- outcome of the historical case
- applicable lessons

Respond in JSON array format."""
            }],
        )

        try:
            text = message.content[0].text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            return json.loads(text)
        except (json.JSONDecodeError, IndexError):
            return [{"raw_analysis": message.content[0].text}]

    async def regional_scan(
        self,
        country_scores: Dict[str, Dict[str, Any]],
    ) -> str:
        """Generate a regional overview scanning all Latin American countries."""
        message = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=6000,
            system=SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": f"""Run a regional scan of Latin America. Here are the current risk profiles:

{json.dumps(country_scores, indent=2, default=str)}

Generate:
1. Top 5 countries by risk level with brief analysis
2. Regional risk patterns and trends
3. Cross-border contagion risks
4. Key regional events in next 30 days
5. Overall regional stability assessment"""
            }],
        )

        return message.content[0].text

    def _build_context(
        self,
        country_code: str,
        country_name: str,
        risk_scores: Dict,
        indicators: Dict,
        events: List[Dict],
        analogs: Optional[List[Dict]],
    ) -> str:
        """Build structured context for Claude analysis."""
        context_parts = [
            f"COUNTRY: {country_name} ({country_code})",
            f"\nRISK SCORES:\n{json.dumps(risk_scores, indent=2, default=str)}",
            f"\nKEY INDICATORS:\n{json.dumps(indicators, indent=2, default=str)}",
        ]

        if events:
            context_parts.append(
                f"\nRECENT EVENTS (last 7 days):\n{json.dumps(events[:20], indent=2, default=str)}"
            )

        if analogs:
            context_parts.append(
                f"\nHISTORICAL ANALOGS:\n{json.dumps(analogs, indent=2, default=str)}"
            )

        return "\n".join(context_parts)
