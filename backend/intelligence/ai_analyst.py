import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import google.generativeai as genai
from openai import OpenAI
from backend.utils.config import settings
from backend.utils.logger import logger

# ATALAYA System Prompt - Magazine/Editorial Style
SYSTEM_PROMPT = """Eres ATALAYA, una plataforma de inteligencia geopolítica especializada en América Latina.
Tu rol es el de un equipo editorial de análisis estratégico — piensa en The Economist, Foreign Affairs, o eklipX Intelligence, pero enfocado exclusivamente en riesgo soberano latinoamericano.

ESTILO DE ESCRITURA:
- Escribe como un ARTÍCULO DE REVISTA de inteligencia: párrafos completos, narrativa fluida, análisis profundo.
- NO uses formato de lista/bullet points como estructura principal. Usa PROSA EDITORIAL.
- Cada sección debe tener al menos 2-3 párrafos sustanciales.
- Usa subtítulos editoriales atractivos (no genéricos como "Sección 1").
- Incluye datos específicos, cifras, porcentajes y nombres de actores clave.
- Cita fuentes cuando sea posible: [Fuente: Reuters, Feb 2026] o similar.
- Tono: Profesional, analítico, accesible pero nunca simplista. Como un artículo que leerías en una revista especializada.
- Idioma: ESPAÑOL LATINOAMERICANO (no español peninsular).

PRINCIPIOS EDITORIALES:
1. CONTEXTO PRIMERO: Antes de analizar, contextualiza. El lector necesita entender el panorama.
2. NARRATIVA: Los datos solos no cuentan la historia. Construye una narrativa clara.
3. PROFUNDIDAD: No te quedes en la superficie. Explica el "por qué" detrás de cada tendencia.
4. PROSPECTIVA: Siempre mira hacia adelante. ¿Qué viene? ¿Qué vigilar?
5. FUENTES: Menciona medios, instituciones, y reportes como base de tus afirmaciones.
"""

class BaseAnalyst(ABC):
    """Abstract base class for AI analysts."""
    
    def __init__(self):
        self.logger = logger.getChild(self.__class__.__name__)

    @abstractmethod
    async def generate_content(self, system_prompt: str, user_prompt: str, max_tokens: int = 12000) -> str:
        pass

    async def generate_country_report(
        self,
        country_code: str,
        country_name: str,
        risk_scores: Dict[str, Any],
        indicators: Dict[str, Any],
        events: List[Dict[str, Any]],
        historical_analogs: Optional[List[Dict]] = None,
        news_context: Optional[str] = None,
    ) -> str:
        """Generate a magazine-style intelligence article for a country."""
        context = self._build_context(
            country_code, country_name, risk_scores, indicators, events, historical_analogs
        )
        
        news_section = ""
        if news_context:
            news_section = f"""
NOTICIAS RECIENTES (usar como base para el artículo, citar las fuentes):
{news_context}
"""
        
        prompt = f"""Escribe un ARTÍCULO DE INTELIGENCIA EDITORIAL completo sobre {country_name} ({country_code}).
        
DATOS ANALÍTICOS:
{context}
{news_section}

ESTRUCTURA DEL ARTÍCULO (en Markdown):

# {country_name}: [Titular editorial impactante que capture la situación actual]

*Por ATALAYA Intelligence | {self._get_date()} | Análisis de Riesgo Soberano*

## Resumen Ejecutivo

[3-4 párrafos que sinteticen la situación actual, el nivel de riesgo, y la tesis central. 
Debe leerse como la entrada de un artículo de The Economist — enganchando al lector con 
la urgencia y relevancia del tema.]

## El Panorama Actual

[Descripción detallada del contexto político, económico y social actual. 
Menciona actores clave (presidentes, ministros, líderes de oposición), 
cifras económicas (inflación, PIB, deuda), y eventos recientes.
Mínimo 3-4 párrafos sustanciales. Cita fuentes.]

## Anatomía del Riesgo

[Análisis técnico profundo del Índice de Fragilidad. Explica qué dominios están 
más comprometidos y por qué. Usa los datos de risk_scores para fundamentar.
Conecta los dominios entre sí: cómo la crisis política alimenta la económica, etc.]

## Señales de Alerta

[¿Qué indicadores tempranos están encendiéndose? Describe eventos específicos 
recientes que actúan como precursores. Para cada señal, explica su significado 
estructural — no solo qué pasó, sino qué implica para el futuro.]

## Escenarios a 90 Días

### Escenario Base: [Nombre descriptivo]
[2-3 párrafos describiendo la trayectoria más probable]

### Escenario de Riesgo: [Nombre descriptivo]  
[2-3 párrafos describiendo qué pasa si los factores de riesgo se materializan]

### Cisne Negro: [Nombre descriptivo]
[1-2 párrafos sobre el evento improbable pero catastrófico]

## Precedentes Históricos

[Comparación con crisis pasadas en la región. ¿Qué patrones se repiten? 
¿Qué lecciones aplican? Sé específico con fechas y resultados.]

## Recomendaciones para Observadores

[Para analistas, inversores, y tomadores de decisiones: ¿qué vigilar? 
¿Qué acciones tomar? ¿Cuáles son las fechas clave próximas?]

---

*Las opiniones expresadas representan el análisis de ATALAYA Intelligence y no constituyen asesoramiento financiero o político. Fuentes consultadas incluyen reportes de organismos internacionales, medios especializados y bases de datos propietarias.*

REGLAS:
- El artículo debe ser LARGO y SUSTANCIAL (mínimo 2000 palabras).
- Cada sección debe tener PÁRRAFOS COMPLETOS, no listas.
- Incluye cifras, datos y nombres específicos.
- Cita fuentes entre corchetes: [Fuente: nombre, fecha].
- El titular debe ser periodístico y provocador.
- USA ESPAÑOL LATINOAMERICANO.
- NO empieces con "A continuación..." o "En este informe...". Entra DIRECTO al contenido."""

        return await self.generate_content(SYSTEM_PROMPT, prompt, max_tokens=12000)

    async def identify_tipping_points(
        self,
        country_code: str,
        country_name: str,
        current_state: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Identify critical tipping points in the next 30-90 days."""
        prompt = f"""Analiza el estado actual de {country_name} ({country_code}) e identifica los 3-5 PUNTOS DE INFLEXIÓN más críticos para los próximos 30-90 días.
        
Estado actual:
{json.dumps(current_state, indent=2, default=str)}

Responde en formato JSON (array de objetos):
{{
  "event": "Descripción del evento gatillo",
  "probability": 0.XX,
  "impact_if_occurs": "Consecuencias si ocurre",
  "impact_if_not": "Trayectoria alternativa",
  "key_date": "Fecha estimada (YYYY-MM-DD)",
  "domain": "Dominio afectado",
  "actors": ["Actor 1", "Actor 2"],
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
        prompt = f"""Simula una CASCADA DE CRISIS iniciada por: "{trigger_event}"

País: {country_code}
Estado inicial:
{json.dumps(initial_state, indent=2, default=str)}
Horizonte: {time_horizon} días

Genera un análisis JSON con secuencia temporal, propagación entre dominios, 
actores afectados, puntos de interrupción y probabilidades."""

        response_text = await self.generate_content(SYSTEM_PROMPT, prompt, max_tokens=6000)
        return self._parse_json(response_text, return_dict=True)

    async def find_historical_analogs(
        self,
        current_situation: str,
        country_code: str,
        country_name: str = "",
    ) -> List[Dict[str, Any]]:
        """Find relevant historical precedents."""
        prompt = f"""Analiza la situación actual en {country_code}:
{current_situation}

Encuentra los 3 PRECEDENTES HISTÓRICOS más relevantes en Latinoamérica.

Para cada precedente, responde en JSON:
- country_year: "País Año"
- description: Descripción de la crisis
- similarity_score: Porcentaje de similitud (0-100)
- key_similarities: Lista de patrones similares
- key_differences: Diferencias clave
- outcome: Resultado final
- lesson: Lección aplicable hoy

Responde solo con el array JSON."""

        response_text = await self.generate_content(SYSTEM_PROMPT, prompt, max_tokens=4000)
        return self._parse_json(response_text)

    async def regional_scan(
        self,
        country_scores: Dict[str, Dict[str, Any]],
    ) -> str:
        """Generate a regional editorial overview."""
        prompt = f"""Escribe un ARTÍCULO EDITORIAL DE INTELIGENCIA REGIONAL sobre Latinoamérica.
        
Perfiles de riesgo actuales:
{json.dumps(country_scores, indent=2, default=str)}

Estructura del artículo (Markdown, prosa editorial, en español):

# Radar Hemisférico: [Titular sobre la situación regional]

*Por ATALAYA Intelligence | Análisis Regional*

## Panorama General
[Contexto regional en 2-3 párrafos]

## Focos de Tensión
[Top 5 países más críticos con análisis de cada uno]

## Dinámicas Transfronterizas
[Migración, crimen organizado, contagio económico, cadenas de suministro]

## Perspectiva a 30 Días
[Eventos a monitorear y proyecciones]

## Evaluación de Estabilidad Hemisférica
[Conclusión editorial]

Mínimo 1500 palabras. Prosa editorial, no listas."""

        return await self.generate_content(SYSTEM_PROMPT, prompt, max_tokens=8000)

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
            f"PAÍS: {country_name} ({country_code})",
            f"\nÍNDICES DE RIESGO:\n{json.dumps(risk_scores, indent=2, default=str)}",
            f"\nINDICADORES CLAVE:\n{json.dumps(indicators, indent=2, default=str)}",
        ]

        if events:
            context_parts.append(
                f"\nEVENTOS RECIENTES:\n{json.dumps(events[:20], indent=2, default=str)}"
            )

        if analogs:
            context_parts.append(
                f"\nANÁLOGOS HISTÓRICOS:\n{json.dumps(analogs, indent=2, default=str)}"
            )

        return "\n".join(context_parts)

    def _get_date(self) -> str:
        """Get current date string."""
        from datetime import datetime
        months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        now = datetime.now()
        return f"{now.day} de {months[now.month - 1]} {now.year}"

    def _parse_json(self, text: str, return_dict: bool = False) -> Any:
        try:
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            return json.loads(text)
        except (json.JSONDecodeError, IndexError) as e:
            self.logger.warning(f"Could not parse JSON: {e}. Returning raw text wrapper.")
            return {"raw_analysis": text} if return_dict else [{"raw_analysis": text}]


class GeminiAnalyst(BaseAnalyst):
    """Google Gemini implementation with Google Search Grounding & JSON Mode."""
    
    def __init__(self):
        super().__init__()
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not configured")
        
        genai.configure(api_key=settings.gemini_api_key)
        
        # Configure Google Search Tool
        self.tools = [
            {"google_search_retrieval": {
                "dynamic_retrieval_config": {
                    "mode": "dynamic",
                    "dynamic_threshold": 0.6
                }
            }}
        ]
        
        # Use best available model: gemini-2.5-flash
        self.model = genai.GenerativeModel('gemini-2.5-flash', tools=self.tools)
        self.json_model = genai.GenerativeModel('gemini-2.5-flash') # No tools for JSON tasks to avoid conflicts
        self.provider_name = "Gemini 2.5 Flash (Grounded)"

    async def generate_content(self, system_prompt: str, user_prompt: str, max_tokens: int = 12000) -> str:
        # Default generation (uses Search if dynamic threshold is met)
        return await self._generate(self.model, system_prompt, user_prompt, max_tokens, temperature=0.3)

    async def research_topic(self, query: str, search_modifiers: str = "") -> str:
        """
        Conduct grounded research using Google Search.
        Low temperature for factual accuracy.
        """
        system_prompt = "You are a research librarian. Gather factual information from credible sources."
        user_prompt = f"""RESEARCH QUERY: {query}
        
        CONTEXT MODIFIERS: {search_modifiers}
        
        TASK:
        1. Search for the most relevant, up-to-date information from the specified sources.
        2. Provide a detailed summary of facts, numbers, dates, and direct quotes.
        3. MANDATORY: Cite authoritative URLs for every key fact.
        4. Focus on official statements, economic data, and major political events.
        """
        
        # Force low temp for facts
        return await self._generate(self.model, system_prompt, user_prompt, max_tokens=8000, temperature=0.1)

    async def identify_tipping_points(self, country_code: str, country_name: str, current_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Use JSON mode model
        prompt = f"""Analiza el estado actual de {country_name} ({country_code}) e identifica los 3-5 PUNTOS DE INFLEXIÓN más críticos.
        Estado actual: {json.dumps(current_state, indent=2, default=str)}
        
        Return a JSON array of objects with keys: event, probability, impact_if_occurs, impact_if_not, key_date, domain, actors, cascade_risk."""
        
        try:
            response = await self._generate(
                self.json_model, 
                SYSTEM_PROMPT, 
                prompt, 
                max_tokens=4000, 
                temperature=0.4,
                mime_type="application/json"
            )
            return json.loads(response)
        except Exception as e:
            self.logger.error(f"JSON parsing/generation failed: {e}")
            return []

    async def _generate(self, model, system, user, max_tokens, temperature, mime_type=None):
        import asyncio
        full_prompt = f"{system}\n\n{user}"
        max_retries = 3
        
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            response_mime_type=mime_type
        )

        for attempt in range(max_retries + 1):
            try:
                response = model.generate_content(full_prompt, generation_config=generation_config)
                return response.text
            except Exception as e:
                error_str = str(e)
                if ("429" in error_str or "ResourceExhausted" in error_str) and attempt < max_retries:
                    wait_time = 2 ** (attempt + 1)
                    await asyncio.sleep(wait_time)
                    continue
                raise


class DeepInfraQwenAnalyst(BaseAnalyst):
    """DeepInfra Qwen3 implementation."""
    
    def __init__(self):
        super().__init__()
        if not settings.deepinfra_api_key:
            raise ValueError("DEEPINFRA_API_KEY not configured")
            
        self.client = OpenAI(
            api_key=settings.deepinfra_api_key,
            base_url="https://api.deepinfra.com/v1/openai"
        )
        self.model_name = "Qwen/Qwen3-235B-A22B"
        self.provider_name = "DeepInfra Qwen3-235B"

    async def generate_content(self, system_prompt: str, user_prompt: str, max_tokens: int = 12000) -> str:
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
            self.logger.error(f"DeepInfra Qwen API error: {str(e)}")
            raise


class DeepInfraDeepSeekAnalyst(BaseAnalyst):
    """DeepInfra DeepSeek V3 implementation."""
    
    def __init__(self):
        super().__init__()
        if not settings.deepinfra_api_key:
            raise ValueError("DEEPINFRA_API_KEY not configured")
            
        self.client = OpenAI(
            api_key=settings.deepinfra_api_key,
            base_url="https://api.deepinfra.com/v1/openai"
        )
        self.model_name = "deepseek-ai/DeepSeek-V3"
        self.provider_name = "DeepInfra DeepSeek V3"

    async def generate_content(self, system_prompt: str, user_prompt: str, max_tokens: int = 12000) -> str:
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
            self.logger.error(f"DeepInfra DeepSeek API error: {str(e)}")
            raise


# Keep backward compat alias
DeepInfraAnalyst = DeepInfraQwenAnalyst


class CascadingAnalyst(BaseAnalyst):
    """Multi-provider analyst that tries providers in cascade order.
    
    Order: Gemini 2.5 Flash → DeepInfra Qwen3 → DeepInfra DeepSeek V3
    If all fail, raises the last error so the template fallback can be used.
    """

    def __init__(self):
        super().__init__()
        self.providers: list[tuple[str, BaseAnalyst]] = []
        self.provider_name = "Cascade"
        self._active_provider = None
        
        # Build provider cascade
        if settings.gemini_api_key:
            try:
                self.providers.append(("Gemini 2.5 Flash", GeminiAnalyst()))
            except Exception as e:
                self.logger.warning(f"Gemini init failed: {e}")
        
        if settings.deepinfra_api_key:
            try:
                self.providers.append(("Qwen3-235B", DeepInfraQwenAnalyst()))
            except Exception as e:
                self.logger.warning(f"DeepInfra Qwen init failed: {e}")
            try:
                self.providers.append(("DeepSeek V3", DeepInfraDeepSeekAnalyst()))
            except Exception as e:
                self.logger.warning(f"DeepInfra DeepSeek init failed: {e}")
        
        if not self.providers:
            raise ValueError("No AI providers configured. Set GEMINI_API_KEY or DEEPINFRA_API_KEY.")
        
        self.logger.info(f"Cascade initialized with {len(self.providers)} providers: {[p[0] for p in self.providers]}")

    async def generate_content(self, system_prompt: str, user_prompt: str, max_tokens: int = 12000) -> str:
        last_error = None
        
        for name, provider in self.providers:
            try:
                self.logger.info(f"Trying provider: {name}")
                result = await provider.generate_content(system_prompt, user_prompt, max_tokens)
                self._active_provider = name
                self.provider_name = name
                self.logger.info(f"✓ Provider {name} succeeded ({len(result)} chars)")
                return result
            except Exception as e:
                last_error = e
                self.logger.warning(f"✗ Provider {name} failed: {type(e).__name__}: {str(e)[:200]}")
                continue
        
        # All providers failed
        raise last_error or ValueError("All AI providers failed")


# Factory
def get_analyst() -> BaseAnalyst:
    """Get an AI analyst instance.
    
    If ai_provider is 'auto' (default), returns CascadingAnalyst which tries
    all configured providers in order: Gemini → Qwen3 → DeepSeek.
    
    Otherwise returns a specific provider by name.
    """
    provider = settings.ai_provider.lower()
    
    if provider == "auto":
        return CascadingAnalyst()
    elif provider == "gemini":
        return GeminiAnalyst()
    elif provider == "deepinfra":
        return DeepInfraQwenAnalyst()
    elif provider == "deepseek":
        return DeepInfraDeepSeekAnalyst()
    else:
        # Default to cascade
        return CascadingAnalyst()

