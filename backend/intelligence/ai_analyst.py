import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import google.generativeai as genai
from openai import OpenAI
from backend.utils.config import settings
from backend.utils.logger import logger
from backend.config.country_profiles import COUNTRY_VECTORS

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
    """Google Gemini implementation with Native Search Grounding."""
    
    def __init__(self):
        super().__init__()
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not configured")
        
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.provider_name = "Gemini 2.5 Flash (Search Enabled)"
        
        # Configuración de la herramienta de búsqueda
        self.tools = [
            {"google_search_retrieval": {
                "dynamic_retrieval_config": {
                    "mode": "dynamic",
                    "dynamic_threshold": 0.6
                }
            }}
        ]

    async def generate_deep_analysis(
        self,
        country_code: str,
        country_name: str,
    ) -> Dict[str, Any]:
        """
        Perform a Deep Dive Analysis using Country Vectors and Parallel Research.
        Returns a structured JSON object.
        """
        vectors = COUNTRY_VECTORS.get(country_code, COUNTRY_VECTORS.get("ARG")) # Default to ARG format if missing
        
        # 1. PARALLEL DEEP RESEARCH
        futures = []
        
        # Thread A: Real Economy & Commodities
        commodities_query = f"{country_name} statistics exports production: {', '.join(vectors['commodities'])} current status data"
        futures.append(self.perform_research(commodities_query))
        
        # Thread B: Power Dynamics & Risks
        risks_query = f"{country_name} political crisis institutional stability: {', '.join(vectors['risks'])} recent events"
        futures.append(self.perform_research(risks_query))
        
        # Thread C: Geopolitics & Alignment
        geo_query = f"{country_name} foreign diplomacy alignment USA China EU Russia: {', '.join(vectors['geopolitics'])}"
        futures.append(self.perform_research(geo_query))
        
        # Thread D: Future Tech & Science
        tech_query = f"{country_name} science technology startups innovation: {', '.join(vectors['tech'])}"
        futures.append(self.perform_research(tech_query))
        
        # Run all research threads in parallel
        results = await asyncio.gather(*futures)
        econ_ctx, risk_ctx, geo_ctx, tech_ctx = results
        
        # 2. SYNTHESIS & STRUCTURED OUTPUT
        prompt = f"""
        ACTÚA COMO: Estratega Geopolítico Principal de ATALAYA.
        TAREA: Producir un Informe de Inteligencia de 'Contexto Profundo' para {country_name} ({country_code}).
        
        DATOS DE ENTRADA (Hilos de Investigación):
        [ECONOMÍA]: {econ_ctx[:2000]}
        [POLÍTICA]: {risk_ctx[:2000]}
        [GEOPOLÍTICA]: {geo_ctx[:2000]}
        [TEC/FUTURO]: {tech_ctx[:2000]}
        
        FORMATO DE SALIDA: SOLO JSON ESTRICTO. Sin formato markdown.
        Esquema:
        {{
            "executive_summary": "Texto en Markdown. Síntesis de alto nivel de la situación. Máximo 300 palabras. Tono editorial, en ESPAÑOL.",
            "alignment_score": {{
                "usa_china_axis": <int -100 (USA) a +100 (China)>,
                "description": "Breve explicación de la posición de alineación en ESPAÑOL."
            }},
            "key_commodities": [
                {{ "name": "Nombre del Recurso", "status": "Crítico/Estable/En Auge", "trend": "Sube/Baja/Estable", "details": "Dato específico en ESPAÑOL" }}
            ],
            "tech_biotech_radar": {{
                "level": "Latente/Emergente/Avanzado",
                "highlights": ["Lista de 2-3 proyectos o startups clave encontrados en la investigación (en ESPAÑOL)"]
            }},
            "supply_chain_alert": "La amenaza logística o cuello de botella más crítico encontrado (en ESPAÑOL)."
        }}
        """
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.4, # Lower temp for strict JSON
                    response_mime_type="application/json" # Force JSON mode if available, or just guide model
                )
            )
            text = response.text
            # Clean possible markdown blocks
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            return json.loads(text)
            
        except Exception as e:
            self.logger.error(f"Deep Analysis failed: {e}")
            return {
                "executive_summary": "Deep analysis generation failed. System defaulted to basic mode.",
                "alignment_score": {"usa_china_axis": 0, "description": "Unknown"},
                "key_commodities": [],
                "tech_biotech_radar": {"level": "Unknown", "highlights": []},
                "supply_chain_alert": "System Error"
            }

    async def perform_research(self, query: str) -> str:
        """Método específico para investigar datos duros en tiempo real."""
        research_prompt = f"""
        OBJETIVO: Encontrar datos EXACTOS y RECIENTES sobre: {query}
        
        INSTRUCCIONES:
        1. Utiliza Google Search para encontrar fuentes oficiales (FMI, Bancos Centrales, Reuters, Bloomberg).
        2. Prioriza datos de las últimas 4 semanas.
        3. Extrae cifras exactas: fechas, porcentajes, montos en USD, nombres de empresas.
        4. Si no encuentras datos exactos, indica explicitamente "Sin datos recientes confiables".
        
        FORMATO DE SALIDA:
        - Resumen factual en Español.
        - Cita las fuentes entre paréntesis.
        """
        
        try:
            # Usamos temperatura baja para precisión y activamos TOOLS
            response = self.model.generate_content(
                research_prompt,
                tools=self.tools, # <--- CRITICAL: Use the search tool
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3
                )
            )
            return response.text
        except Exception as e:
            self.logger.error(f"Research failed: {e}")
            return "No se pudieron obtener datos recientes."

    async def generate_content(self, system_prompt: str, user_prompt: str, max_tokens: int = 12000) -> str:
        # Inyectamos una instrucción de grounding en el prompt
        grounding_instruction = "\nIMPORTANTE: Usa la herramienta de búsqueda integrada para verificar CADA dato reciente (tipo de cambio, inflación, conflictos) antes de escribir. No inventes que 'no hay datos'."
        
        full_prompt = f"{system_prompt}\n{grounding_instruction}\n\n{user_prompt}"
        
        # Lógica de reintento existente...
        import asyncio
        max_retries = 3
        for attempt in range(max_retries + 1):
            try:
                response = self.model.generate_content(
                    full_prompt,
                    tools=self.tools,  # <--- AQUÍ ACTIVAMOS LA BÚSQUEDA
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                        max_output_tokens=max_tokens,
                    )
                )
                
                # Verificar si la respuesta fue bloqueada o está vacía
                if not response.parts:
                    return "Error: La IA no generó contenido (posible bloqueo de seguridad)."
                    
                return response.text
            except Exception as e:
                self.logger.warning(f"Gemini error: {e}")
                if attempt < max_retries:
                    wait_time = 2 ** (attempt + 1)
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    self.logger.error(f"Gemini critical error after retries: {e}")
        
        return "Error crítico: Falló la generación después de varios intentos."

    # Mantenemos el método generate_country_report pero lo mejoramos
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
        
        # PASO 1: INVESTIGACIÓN ACTIVA (Nuevo)
        # Antes de escribir, mandamos a investigar los datos críticos
        print(f"🕵️  Investigando datos en tiempo real para {country_name}...")
        live_data = await self.perform_research(
            f"Situación actual {country_name} economía política crisis {self._get_date()}. Dolar blue, riesgo país, inflación último mes, protestas recientes."
        )
        
        # PASO 2: Construcción del contexto enriquecido
        context = self._build_context(
            country_code, country_name, risk_scores, indicators, events, historical_analogs
        )
        
        # Añadimos los datos "live" al prompt
        real_time_section = f"""
DATOS EN TIEMPO REAL (GOOGLE SEARCH):
{live_data}
"""
        
        prompt = f"""Escribe un ARTÍCULO DE INTELIGENCIA EDITORIAL completo sobre {country_name} ({country_code}).
        
DATOS ANALÍTICOS SISTÉMICOS:
{context}

INVESTIGACIÓN DE MERCADO EN TIEMPO REAL (USAR COMO FUENTE PRIMARIA):
{real_time_section}

{news_context if news_context else ""}

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

