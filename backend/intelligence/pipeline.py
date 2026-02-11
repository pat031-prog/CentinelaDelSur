"""
Pipeline de 4 Etapas para CENTINELA DEL SUR / ATALAYA Intelligence.

Extracción → Análisis Estructural → Cuantificación → Síntesis

Cada etapa usa un modelo optimizado con fallback automático.
"""

import json
import asyncio
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from backend.utils.config import settings
from backend.intelligence.model_config import STAGE_CONFIGS, ModelSpec
from backend.intelligence.prompts import (
    PROMPT_EXTRACTION_SYSTEM, PROMPT_EXTRACTION_USER,
    PROMPT_ANALYSIS_SYSTEM, PROMPT_ANALYSIS_USER,
    PROMPT_QUANTIFICATION_SYSTEM, PROMPT_QUANTIFICATION_USER,
    PROMPT_SYNTHESIS_SYSTEM, PROMPT_SYNTHESIS_USER,
    PROMPT_QA_SYSTEM, PROMPT_QA_USER,
)
from backend.data.historical_crises import calculate_empirical_multiplier

log = logging.getLogger("atalaya.pipeline")


# ============================================================================
# Low-level: Call a specific model
# ============================================================================

async def _call_model(spec: ModelSpec, system_prompt: str, user_prompt: str) -> str:
    """Call a single model with the given prompts. Handles retries for 429."""

    if spec.provider == "gemini":
        return await _call_gemini(spec, system_prompt, user_prompt)
    elif spec.provider == "deepinfra":
        return await _call_deepinfra(spec, system_prompt, user_prompt)
    else:
        raise ValueError(f"Unknown provider: {spec.provider}")


async def _call_gemini(spec: ModelSpec, system_prompt: str, user_prompt: str) -> str:
    """Call Gemini model with 429 retry logic."""
    import google.generativeai as genai
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY not configured")

    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel(spec.model)
    full_prompt = f"{system_prompt}\n\n{user_prompt}"

    max_retries = 3
    for attempt in range(max_retries + 1):
        try:
            response = model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=spec.temperature,
                    max_output_tokens=spec.max_tokens,
                ),
            )
            return response.text
        except Exception as e:
            error_str = str(e)
            is_rate_limit = any(x in error_str for x in ["429", "ResourceExhausted", "quota"])

            if is_rate_limit and attempt < max_retries:
                wait_time = 2 ** (attempt + 1)
                log.warning(f"Gemini 429 (attempt {attempt+1}/{max_retries}), waiting {wait_time}s...")
                await asyncio.sleep(wait_time)
                continue

            raise


async def _call_deepinfra(spec: ModelSpec, system_prompt: str, user_prompt: str) -> str:
    """Call DeepInfra model (OpenAI-compatible API)."""
    from openai import OpenAI
    if not settings.deepinfra_api_key:
        raise ValueError("DEEPINFRA_API_KEY not configured")

    client = OpenAI(
        api_key=settings.deepinfra_api_key,
        base_url="https://api.deepinfra.com/v1/openai",
    )

    response = client.chat.completions.create(
        model=spec.model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=spec.max_tokens,
        temperature=spec.temperature,
    )
    return response.choices[0].message.content


# ============================================================================
# Mid-level: Call a stage (primary → fallback)
# ============================================================================

async def _call_stage(
    stage_name: str,
    system_prompt: str,
    user_prompt: str,
) -> Tuple[str, str]:
    """
    Execute a pipeline stage with automatic fallback.
    Returns (result_text, provider_used).
    """
    config = STAGE_CONFIGS[stage_name]
    t0 = time.time()

    # Try primary
    try:
        log.info(f"[{stage_name.upper()}] Trying primary: {config.primary.model}")
        result = await _call_model(config.primary, system_prompt, user_prompt)
        elapsed = time.time() - t0
        log.info(f"[{stage_name.upper()}] ✓ Primary succeeded ({len(result)} chars, {elapsed:.1f}s)")
        return result, f"{config.primary.provider}/{config.primary.model}"
    except Exception as e:
        log.warning(f"[{stage_name.upper()}] ✗ Primary failed: {type(e).__name__}: {str(e)[:200]}")

    # Try fallback
    try:
        log.info(f"[{stage_name.upper()}] Trying fallback: {config.fallback.model}")
        result = await _call_model(config.fallback, system_prompt, user_prompt)
        elapsed = time.time() - t0
        log.info(f"[{stage_name.upper()}] ✓ Fallback succeeded ({len(result)} chars, {elapsed:.1f}s)")
        return result, f"{config.fallback.provider}/{config.fallback.model}"
    except Exception as e:
        log.error(f"[{stage_name.upper()}] ✗ Fallback also failed: {type(e).__name__}: {str(e)[:200]}")
        raise


# ============================================================================
# Helper: format domain scores as text
# ============================================================================

DOMAIN_NAMES_ES = {
    "political": "Político",
    "economic": "Económico",
    "supply_chain": "Cadena de Suministro",
    "technology": "Tecnológico",
    "climate": "Climático",
    "geopolitical": "Geopolítico",
}

DOMAIN_WEIGHTS = {
    "political": 0.20,
    "economic": 0.25,
    "supply_chain": 0.15,
    "technology": 0.10,
    "climate": 0.10,
    "geopolitical": 0.20,
}

RATING_THRESHOLDS = [
    (85, "NEGRO"), (70, "ROJO"), (55, "NARANJA"), (40, "AMARILLO"), (0, "VERDE"),
]


def _score_to_rating(score: float) -> str:
    for threshold, rating in RATING_THRESHOLDS:
        if score >= threshold:
            return rating
    return "VERDE"


def _format_domain_scores(domain_scores: Dict[str, float]) -> str:
    lines = []
    for domain, score in domain_scores.items():
        name = DOMAIN_NAMES_ES.get(domain, domain)
        weight = DOMAIN_WEIGHTS.get(domain, 0.1)
        lines.append(f"- {name}: {score:.0f}/100 (peso: {weight*100:.0f}%)")
    return "\n".join(lines)


def _parse_json_from_text(text: str) -> Optional[dict]:
    """Extract JSON from a text response that may contain markdown fences."""
    import re
    # Try direct parse first
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        pass

    # Try extracting from markdown code block
    patterns = [
        r"```json\s*\n(.*?)\n```",
        r"```\s*\n(.*?)\n```",
        r"\{[\s\S]*\}",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                candidate = match.group(1) if match.lastindex else match.group(0)
                return json.loads(candidate)
            except (json.JSONDecodeError, IndexError):
                continue

    return None


# ============================================================================
# HIGH LEVEL: The 4-Stage Pipeline
# ============================================================================

async def run_pipeline(
    country_code: str,
    country_name: str,
    domain_scores: Dict[str, float],
    news_context: str = "",
) -> Dict[str, Any]:
    """
    Execute the full 4-stage ATALAYA Intelligence pipeline.

    Stages:
      1. EXTRACTION — Extract structured data from news (Gemini Flash)
      2. ANALYSIS — Structural analysis of power dynamics (DeepSeek V3)
      3. QUANTIFICATION — Numeric scoring & scenarios (DeepSeek V3)
      4. SYNTHESIS — Editorial report in Spanish (Gemini Flash)
      + QA pass (DeepSeek V3)

    Returns dict with: report_text, ai_scores, scenarios, stages_log, multiplier.
    """
    pipeline_start = time.time()
    stages_log: List[Dict] = []
    date_str = datetime.utcnow().strftime("%d de %B de %Y")
    domain_scores_text = _format_domain_scores(domain_scores)

    log.info(f"{'='*60}")
    log.info(f"[PIPELINE] Starting 4-stage analysis for {country_name} ({country_code})")
    log.info(f"{'='*60}")

    # ------------------------------------------------------------------
    # STAGE 1: RESEARCH & EXTRACTION (The Librarian)
    # ------------------------------------------------------------------
    from backend.config.sources import get_search_query_modifiers
    from backend.intelligence.ai_analyst import GeminiAnalyst
    
    extraction_prompt = "" 
    extracted_data = ""
    ext_provider = "Unknown"

    try:
        # Research Phase using Gemini (Librarian)
        search_modifiers = get_search_query_modifiers(country_code)
        log.info(f"[EXTRACTION] Starting Research Phase with modifiers: {search_modifiers}")
        
        # Instantiate Librarian
        librarian = GeminiAnalyst()
        research_query = f"Latest official political and economic events in {country_name} ({country_code}) {date_str}. Key risk indicators, government decrees, central bank decisions."
        
        extracted_data = await librarian.research_topic(research_query, search_modifiers)
        ext_provider = "Gemini 2.5 Flash (Research)"
        stages_log.append({"stage": "extraction", "status": "ok", "provider": ext_provider, "chars": len(extracted_data)})
        
    except Exception as e:
        log.warning(f"[EXTRACTION] Research mode failed: {e}. Falling back to standard generation.")
        
        # Fallback: Standard Prompt Extraction
        extraction_prompt = PROMPT_EXTRACTION_USER.format(
            country_name=country_name,
            country_code=country_code,
            date=date_str,
            news_context=news_context or "Sin noticias recientes disponibles. Usa tu conocimiento general actualizado.",
            domain_scores_text=domain_scores_text,
        )
    
    if not extracted_data:
        try:
            if not extraction_prompt: # Should have been set in except block above, but double check
                 extraction_prompt = PROMPT_EXTRACTION_USER.format(
                    country_name=country_name,
                    country_code=country_code,
                    date=date_str,
                    news_context=news_context or "Sin noticias recientes disponibles. Usa tu conocimiento general actualizado.",
                    domain_scores_text=domain_scores_text,
                )
            log.info(f"[EXTRACTION] Running Standard Extraction (Fallback)")
            extracted_data, ext_provider = await _call_stage(
                "extraction", PROMPT_EXTRACTION_SYSTEM, extraction_prompt
            )
            stages_log.append({"stage": "extraction", "status": "ok", "provider": ext_provider, "chars": len(extracted_data)})
        except Exception as e:
            extracted_data = f"Extracción falló: {e}. Usando scores base del sistema."
            stages_log.append({"stage": "extraction", "status": "failed", "error": str(e)[:200]})
            log.warning(f"[EXTRACTION] Failed, continuing with base data")

    # ------------------------------------------------------------------
    # STAGE 2: STRUCTURAL ANALYSIS
    # ------------------------------------------------------------------
    analysis_prompt = PROMPT_ANALYSIS_USER.format(
        country_name=country_name,
        country_code=country_code,
        extracted_data=extracted_data[:8000],  # Cap context to avoid token overflow
        domain_scores_text=domain_scores_text,
    )
    try:
        structural_analysis, ana_provider = await _call_stage(
            "analysis", PROMPT_ANALYSIS_SYSTEM, analysis_prompt
        )
        stages_log.append({"stage": "analysis", "status": "ok", "provider": ana_provider, "chars": len(structural_analysis)})
    except Exception as e:
        structural_analysis = f"Análisis estructural no disponible. Scores base: {domain_scores_text}"
        stages_log.append({"stage": "analysis", "status": "failed", "error": str(e)[:200]})
        log.warning(f"[ANALYSIS] Failed, continuing with base scores")

    # ------------------------------------------------------------------
    # STAGE 3: QUANTIFICATION
    # ------------------------------------------------------------------
    quant_prompt = PROMPT_QUANTIFICATION_USER.format(
        country_name=country_name,
        country_code=country_code,
        structural_analysis=structural_analysis[:6000],
        domain_scores_text=domain_scores_text,
    )
    ai_scores = None
    ai_scenarios = []
    try:
        quant_result, quant_provider = await _call_stage(
            "quantification", PROMPT_QUANTIFICATION_SYSTEM, quant_prompt
        )
        stages_log.append({"stage": "quantification", "status": "ok", "provider": quant_provider, "chars": len(quant_result)})

        # Parse JSON scores from quantification
        parsed = _parse_json_from_text(quant_result)
        if parsed and "scores" in parsed:
            ai_scores = {}
            for domain_key, val in parsed["scores"].items():
                if isinstance(val, dict) and "total" in val:
                    ai_scores[domain_key] = val["total"]
                elif isinstance(val, (int, float)):
                    ai_scores[domain_key] = val
            log.info(f"[QUANT] AI scores parsed: {ai_scores}")

            if "scenarios" in parsed:
                ai_scenarios = parsed["scenarios"]
    except Exception as e:
        stages_log.append({"stage": "quantification", "status": "failed", "error": str(e)[:200]})
        log.warning(f"[QUANTIFICATION] Failed, using original scores")

    # Determine final scores (AI scores override system scores if available)
    final_domain_scores = {**domain_scores}
    if ai_scores:
        for key, val in ai_scores.items():
            if isinstance(val, (int, float)) and 0 <= val <= 100:
                final_domain_scores[key] = val

    # Calculate empirical interaction multiplier
    multiplier = calculate_empirical_multiplier(final_domain_scores)

    # Calculate final composite
    weighted_sum = sum(
        final_domain_scores.get(d, 30) * w
        for d, w in DOMAIN_WEIGHTS.items()
    )
    base_score = weighted_sum / sum(DOMAIN_WEIGHTS.values())
    final_score = min(100, round(base_score * multiplier, 1))
    rating = _score_to_rating(final_score)

    log.info(f"[PIPELINE] Base={base_score:.1f} × Multiplier={multiplier} = Final={final_score} ({rating})")

    # ------------------------------------------------------------------
    # STAGE 4: SYNTHESIS
    # ------------------------------------------------------------------
    scenarios_text = ""
    if ai_scenarios:
        for s in ai_scenarios:
            scenarios_text += f"- {s.get('type', '?')}: {s.get('title', '')} (prob {s.get('probability', '?')}%)\n  {s.get('description', '')}\n\n"
    else:
        scenarios_text = "Escenarios no disponibles — generar basándose en el análisis."

    synthesis_prompt = PROMPT_SYNTHESIS_USER.format(
        country_name=country_name,
        country_code=country_code,
        final_score=final_score,
        rating=rating,
        interaction_multiplier=multiplier,
        domain_scores_text=_format_domain_scores(final_domain_scores),
        structural_analysis=structural_analysis[:5000],
        extracted_data=extracted_data[:3000],
        scenarios_text=scenarios_text,
        news_context=(news_context[:2000] if news_context else "Sin fuentes de noticias adicionales."),
        date=date_str,
    )
    try:
        report_text, syn_provider = await _call_stage(
            "synthesis", PROMPT_SYNTHESIS_SYSTEM, synthesis_prompt
        )
        stages_log.append({"stage": "synthesis", "status": "ok", "provider": syn_provider, "chars": len(report_text)})
    except Exception as e:
        stages_log.append({"stage": "synthesis", "status": "failed", "error": str(e)[:200]})
        raise  # Synthesis is critical — let caller handle fallback

    # ------------------------------------------------------------------
    # QA PASS (non-blocking)
    # ------------------------------------------------------------------
    qa_result = {"passed": True, "confidence": 0.0, "issues": []}
    try:
        qa_prompt = PROMPT_QA_USER.format(
            report=report_text[:4000],
            final_score=final_score,
            domain_scores_text=_format_domain_scores(final_domain_scores),
        )
        qa_text, qa_provider = await _call_stage("qa", PROMPT_QA_SYSTEM, qa_prompt)
        stages_log.append({"stage": "qa", "status": "ok", "provider": qa_provider})

        qa_parsed = _parse_json_from_text(qa_text)
        if qa_parsed:
            qa_result = qa_parsed
            if not qa_result.get("passed", True):
                log.warning(f"[QA] Issues found: {qa_result.get('issues', [])}")
    except Exception as e:
        log.warning(f"[QA] Skipped: {e}")
        stages_log.append({"stage": "qa", "status": "skipped", "error": str(e)[:100]})

    # ------------------------------------------------------------------
    # RESULT
    # ------------------------------------------------------------------
    elapsed = time.time() - pipeline_start
    log.info(f"[PIPELINE] Complete for {country_code} in {elapsed:.1f}s — Score: {final_score} ({rating})")

    return {
        "report_text": report_text,
        "final_score": final_score,
        "rating": rating,
        "interaction_multiplier": multiplier,
        "ai_domain_scores": final_domain_scores,
        "ai_scenarios": ai_scenarios,
        "qa": qa_result,
        "stages": stages_log,
        "elapsed_seconds": round(elapsed, 1),
    }
