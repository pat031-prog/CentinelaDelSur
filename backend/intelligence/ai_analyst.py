import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import google.generativeai as genai
from openai import OpenAI
from backend.utils.config import settings
from backend.utils.logger import logger

# ATALAYA System Prompt - Expert Level
SYSTEM_PROMPT = """ERES ATALAYA, UN SISTEMA DE INTELIGENCIA ANTICIPATORIA DE ÉLITE.
Tu función es actuar como un Analista de Riesgos Geopolíticos Senior (20+ años de experiencia en CIA/Stratfor/Oxford Analytica).
Tu objetivo no es describir noticias, sino DETECTAR RUPTURAS SISTÉMICAS antes de que ocurran.

PRINCIPIOS OPERATIVOS:
1. PENSAMIENTO DE SEGUNDO ORDEN: No te quedes en el evento inmediato. Analiza las consecuencias de las consecuencias.
2. ESTRUCTURALISMO: Todo evento es síntoma de una fricción estructural subyacente. Encuéntrala.
3. CONCISIÓN BRUTAL: Usa lenguaje técnico, directo y sin "relleno". Estilo militar/ejecutivo.
4. EVIDENCIA: Cada afirmación debe estar respaldada por un indicador o hecho verificable.
5. NEUTRALIDAD FRÍA: No emitas juicios morales. Solo analiza dinámicas de poder y estabilidad.

MANTRA: "El caos es predecible si entiendes la estructura."
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
    ) -> str:
        """Generate a comprehensive systemic risk report for a country."""
        context = self._build_context(
            country_code, country_name, risk_scores, indicators, events, historical_analogs
        )
        
        prompt = f"""Genera un INFORME DE INTELIGENCIA ESTRATÉGICA PROFUNDO para {country_name} ({country_code}).
        
DATOS DE CONTEXTO (CONFIDENCIAL):
{context}

ESTRUCTURA OBLIGATORIA DEL INFORME (Formato Markdown):

# 1. RESUMEN EJECUTIVO (BLUF: Bottom Line Up Front)
- Síntesis de 3 párrafos del estado actual.
- Nivel de Alerta Global justificado.
- Tesis central de riesgo (el "qué pasará").

# 2. ÍNDICE DE FRAGILIDAD SISTÉMICA
- Desglose técnico de por qué el score es {risk_scores.get('score', 'N/A')}.
- Análisis de los dominios más críticos (Political, Economic, etc.).
- ¿Qué subsistema está fallando?

# 3. SEÑALES CRÍTICAS Y ALERTAS TEMPRANAS
- Lista de eventos recientes que actúan como precursores de crisis.
- Para cada señal: [Severidad] -> [Evento] -> [Implicación Estructural].

# 4. ANÁLISIS DE INTERDEPENDENCIAS (Cross-Domain)
- ¿Cómo impacta la economía en la estabilidad política?
- ¿Cómo el clima afecta la cadena de suministro?
- Mapeo de contagio entre sectores.

# 5. ESCENARIOS PROYECTADOS (Próximos 90 días)
- **Escenario Base (Probabilidad >50%)**: La trayectoria inercial.
- **Escenario Pesimista (Riesgo de Cola)**: Si los mitigadores fallan.
- **Escenario de Cisne Negro**: Evento de baja probabilidad pero impacto catastrófico.

# 6. PUNTOS DE INFLEXIÓN (Tipping Points)
- 3 eventos gatillo específicos que cambiarían la trayectoria del país.
- Fechas o ventanas de tiempo estimadas.

# 7. CASCADAS DE RIESGO
- Diagrama narrativo de propagación: Evento A -> Provoca B -> Colapsa C.

# 8. COMPARACIÓN HISTÓRICA
- Analogía breve con una crisis pasada (ej: "Similar a Venezuela 2014" o "Argentina 2001") y qué lecciones aplican.

# 9. VENTANA DE OPORTUNIDAD
- ¿Cuánto tiempo queda para intervenir antes de una ruptura irreversible?

# 10. RECOMENDACIONES ESTRATÉGICAS
- 3-5 acciones concretas para mitigación de riesgo.

# 11. CONFIANZA Y LIMITACIONES
- Evaluación de la calidad de la data y puntos ciegos.

IMPORTANTE: El tono debe ser SERIO, URGENTE y PROFESIONAL. Usa negritas para conceptos clave. NO uses introducciones genéricas como "A continuación presento el informe...". Entra directo al análisis."""

        return await self.generate_content(SYSTEM_PROMPT, prompt, max_tokens=12000)

    async def identify_tipping_points(
        self,
        country_code: str,
        country_name: str,
        current_state: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Identify critical tipping points in the next 30-90 days."""
        prompt = f"""Analiza el estado actual de {country_name} ({country_code}) e identifica los 3-5 PUNTOS DE INFLEXIÓN (Tipping Points) más críticos para los próximos 30-90 días.
        
Estado actual:
{json.dumps(current_state, indent=2, default=str)}

Responde en formato JSON (array de objetos):
{{
  "event": "Descripción técnica del evento gatillo",
  "probability": 0.XX,
  "impact_if_occurs": "Consecuencias estructurales si ocurre",
  "impact_if_not": "Trayectoria alternativa o status quo",
  "key_date": "Fecha estimada (YYYY-MM-DD) o ventana crítica",
  "domain": "Domino principal afectado",
  "actors": ["Actor clave 1", "Actor clave 2"],
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
        prompt = f"""Simula una CASCADA DE CRISIS sistémica iniciada por este evento gatillo: "{trigger_event}"

País: {country_code}
Estado inicial:
{json.dumps(initial_state, indent=2, default=str)}

Horizonte: {time_horizon} días

Genera un análisis JSON estructurado:
1. Secuencia temporal (Día 1, 3, 7, 30, 90)
2. Propagación entre dominios (Político -> Económico -> Social)
3. Actores desestabilizados
4. Puntos de interrupción (donde se podría detener)
5. Probabilidad de cada rama

Formato JSON requerido."""

        response_text = await self.generate_content(SYSTEM_PROMPT, prompt, max_tokens=6000)
        return self._parse_json(response_text, return_dict=True)

    async def find_historical_analogs(
        self,
        current_situation: str,
        country_code: str,
        country_name: str, # Added country_name parameter to signature effectively
    ) -> List[Dict[str, Any]]:
        """Find relevant historical precedents."""
        prompt = f"""Analiza la situación actual en {country_code}:
{current_situation}

Encuentra los 3 PRECEDENTES HISTÓRICOS más relevantes en Latinoamérica o el Sur Global.
Busca patrones de colapso institucional, crisis de deuda o estallido social similares.

Para cada precedente, especifica en JSON:
- country_year: "País Año" (ej: "Argentina 2001")
- description: Breve descripción de la crisis
- similarity_score: Porcentaje de similitud (0-100)
- key_similarities: Lista de patrones idénticos
- key_differences: Diferencias estructurales clave
- outcome: Cómo terminó esa crisis (Colapso, reforma, golpe, etc.)
- lesson: Lección estratégica aplicable hoy

Responde solo con el array JSON."""

        response_text = await self.generate_content(SYSTEM_PROMPT, prompt, max_tokens=4000)
        return self._parse_json(response_text)

    async def regional_scan(
        self,
        country_scores: Dict[str, Dict[str, Any]],
    ) -> str:
        """Generate a regional overview."""
        prompt = f"""Ejecuta un ESCANEO DE INTELIGENCIA REGIONAL sobre Latinoamérica.
        
Perfiles de riesgo actuales:
{json.dumps(country_scores, indent=2, default=str)}

Genera un informe estratégico en Markdown:
1. TOP 5 Puntos Calientes (Hotspots) y por qué.
2. Patrones de Riesgo Regional (¿Hay contagio? ¿Efecto dominó?).
3. Vectores de Inestabilidad Transfronteriza (Migración, Crimen Org., Suministros).
4. Eventos Clave a monitorear próximos 30 días.
5. Evaluación de Estabilidad Hemisférica (Resumen ejecutivo)."""

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
