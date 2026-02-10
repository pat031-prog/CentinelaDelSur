"""
Configuración de modelos por etapa del pipeline.
Cada etapa tiene un modelo primario y un fallback.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ModelSpec:
    """Specification for a single model."""
    provider: str         # "gemini" or "deepinfra"
    model: str            # model identifier
    temperature: float
    max_tokens: int


@dataclass(frozen=True)
class StageConfig:
    """Configuration for a pipeline stage."""
    primary: ModelSpec
    fallback: ModelSpec
    qa: Optional[ModelSpec] = None


# ============================================================================
# Stage-to-Model Mapping
# ============================================================================

STAGE_CONFIGS = {
    "extraction": StageConfig(
        primary=ModelSpec(
            provider="gemini",
            model="gemini-2.5-flash",
            temperature=0.1,
            max_tokens=8000,
        ),
        fallback=ModelSpec(
            provider="deepinfra",
            model="deepseek-ai/DeepSeek-V3",
            temperature=0.1,
            max_tokens=8000,
        ),
    ),
    "analysis": StageConfig(
        primary=ModelSpec(
            provider="deepinfra",
            model="deepseek-ai/DeepSeek-V3",
            temperature=0.3,
            max_tokens=12000,
        ),
        fallback=ModelSpec(
            provider="deepinfra",
            model="Qwen/Qwen2.5-72B-Instruct",
            temperature=0.3,
            max_tokens=12000,
        ),
    ),
    "quantification": StageConfig(
        primary=ModelSpec(
            provider="deepinfra",
            model="deepseek-ai/DeepSeek-V3",
            temperature=0.2,
            max_tokens=8000,
        ),
        fallback=ModelSpec(
            provider="deepinfra",
            model="Qwen/Qwen2.5-72B-Instruct",
            temperature=0.2,
            max_tokens=8000,
        ),
    ),
    "synthesis": StageConfig(
        primary=ModelSpec(
            provider="gemini",
            model="gemini-2.5-flash",
            temperature=0.4,
            max_tokens=16000,
        ),
        fallback=ModelSpec(
            provider="deepinfra",
            model="deepseek-ai/DeepSeek-V3",
            temperature=0.4,
            max_tokens=16000,
        ),
    ),
    "qa": StageConfig(
        primary=ModelSpec(
            provider="deepinfra",
            model="deepseek-ai/DeepSeek-V3",
            temperature=0.1,
            max_tokens=4000,
        ),
        fallback=ModelSpec(
            provider="gemini",
            model="gemini-2.5-flash",
            temperature=0.1,
            max_tokens=4000,
        ),
    ),
}
