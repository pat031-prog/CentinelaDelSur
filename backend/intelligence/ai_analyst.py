import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import google.generativeai as genai
from openai import OpenAI
from backend.utils.config import settings
from backend.utils.logger import logger

# ATALAYA system prompt
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

class BaseAnalyst(ABC):
    """Abstract base class for AI analysts."""
    
    def __init__(self):
        self.logger = logger.getChild(self.__class__.__name__)

    @abstractmethod
    async def generate_content(self, system_prompt: str, user_prompt: str, max_tokens: int = 8000) -> str:
        pass

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
        
        prompt = f"""Generate a complete ATALAYA systemic risk report for {country_name} ({country_code}).

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

        return await self.generate_content(SYSTEM_PROMPT, prompt, max_tokens=8000)

    async def identify_tipping_points(
        self,
        country_code: str,
        country_name: str,
        current_state: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Identify critical tipping points in the next 30-90 days."""
        prompt = f"""Analyze the current state of {country_name} ({country_code}) and identify the 3-5 most critical tipping points in the next 30-90 days.

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
        
        response_text = await self.generate_content(SYSTEM_PROMPT, prompt, max_tokens=4000)
        return self._parse_json(response_text)

    async def simulate_cascade(
        self,
        country_code: str,
        trigger_event: str,
        initial_state: Dict[str, Any],
        time_horizon: int = 90,
    ) -> Dict[str, Any]:
        """Simulate crisis cascades from a trigger event."""
        prompt = f"""Simulate the crisis cascades that could be triggered if this event occurs: "{trigger_event}"

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

        response_text = await self.generate_content(SYSTEM_PROMPT, prompt, max_tokens=6000)
        return self._parse_json(response_text, return_dict=True)

    async def find_historical_analogs(
        self,
        current_situation: str,
        country_code: str,
    ) -> List[Dict[str, Any]]:
        """Find relevant historical precedents."""
        prompt = f"""Analyze this current situation in {country_code}:
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

        response_text = await self.generate_content(SYSTEM_PROMPT, prompt, max_tokens=4000)
        return self._parse_json(response_text)

    async def regional_scan(
        self,
        country_scores: Dict[str, Dict[str, Any]],
    ) -> str:
        """Generate a regional overview."""
        prompt = f"""Run a regional scan of Latin America. Here are the current risk profiles:

{json.dumps(country_scores, indent=2, default=str)}

Generate:
1. Top 5 countries by risk level with brief analysis
2. Regional risk patterns and trends
3. Cross-border contagion risks
4. Key regional events in next 30 days
5. Overall regional stability assessment"""

        return await self.generate_content(SYSTEM_PROMPT, prompt, max_tokens=6000)

    def _build_context(
        self,
        country_code: str,
        country_name: str,
        risk_scores: Dict,
        indicators: Dict,
        events: List[Dict],
        analogs: Optional[List[Dict]],
    ) -> str:
        """Build structured context for analysis."""
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

    def _parse_json(self, text: str, return_dict: bool = False) -> Any:
        try:
            # Clean up potential markdown code blocks
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            return json.loads(text)
        except (json.JSONDecodeError, IndexError) as e:
            self.logger.warning(f"Could not parse JSON: {e}. Returning raw text wrapper.")
            return {"raw_analysis": text} if return_dict else [{"raw_analysis": text}]


class GeminiAnalyst(BaseAnalyst):
    """Google Gemini implementation."""
    
    def __init__(self):
        super().__init__()
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not configured")
        
        genai.configure(api_key=settings.gemini_api_key)
        # Using auto-updated 2.5 model alias if available, falling back to exp/latest
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp') 

    async def generate_content(self, system_prompt: str, user_prompt: str, max_tokens: int = 8000) -> str:
        try:
            # Gemini supports system instructions in model config or combined with prompt
            # Here combining for simplicity and compatibility
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=max_tokens,
                )
            )
            return response.text
        except Exception as e:
            self.logger.error(f"Gemini API error: {str(e)}")
            raise

class DeepInfraAnalyst(BaseAnalyst):
    """DeepInfra implementation (OpenAI-compatible)."""
    
    def __init__(self):
        super().__init__()
        if not settings.deepinfra_api_key:
            raise ValueError("DEEPINFRA_API_KEY not configured")
            
        self.client = OpenAI(
            api_key=settings.deepinfra_api_key,
            base_url="https://api.deepinfra.com/v1/openai"
        )
        # Default high-performance model
        self.model_name = "Qwen/Qwen3-Next-80B-A3B-Instruct"

    async def generate_content(self, system_prompt: str, user_prompt: str, max_tokens: int = 8000) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"DeepInfra API error: {str(e)}")
            raise

# Factory to get the configured analyst
def get_analyst() -> BaseAnalyst:
    provider = settings.ai_provider.lower()
    
    if provider == "gemini":
        return GeminiAnalyst()
    elif provider == "deepinfra":
        return DeepInfraAnalyst()
    else:
        raise ValueError(f"Unknown AI provider: {provider}")
