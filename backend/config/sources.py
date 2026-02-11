"""
Trusted Sources Configuration for ATALAYA Intelligence.
Defines the "Ground Truth" whitelist for different countries.
"""

from typing import Dict, List

TRUSTED_SOURCES: Dict[str, Dict[str, List[str]]] = {
    "ARG": {
        "official": [
            "boletinoficial.gob.ar",
            "indec.gob.ar",
            "bcra.gob.ar",
            "argentina.gob.ar",
            "senado.gob.ar",
            "diputados.gob.ar"
        ],
        "tier1_media": [
            "lanacion.com.ar",
            "clarin.com",
            "infobae.com",
            "ambitofinanciero.com",
            "cronista.com",
            "perfil.com"
        ],
        "financial": [
            "bolsar.com",
            "rava.com"
        ]
    },
    "BRA": {
        "official": [
            "gov.br",
            "bcb.gov.br",
            "ibge.gov.br",
            "camara.leg.br",
            "senado.leg.br"
        ],
        "tier1_media": [
            "uol.com.br",
            "globo.com",
            "estadao.com.br",
            "folha.uol.com.br",
            "valor.globo.com"
        ],
        "financial": [
            "b3.com.br"
        ]
    },
    "CHL": {
        "official": [
            "gob.cl",
            "bcentral.cl",
            "ine.gob.cl",
            "senado.cl",
            "camara.cl"
        ],
        "tier1_media": [
            "emol.com",
            "latercera.com",
            "biobiochile.cl",
            "df.cl"
        ],
        "financial": [
            "bolsadesantiago.com"
        ]
    },
    "COL": {
        "official": [
            "gov.co",
            "banrep.gov.co",
            "dane.gov.co",
            "senado.gov.co",
            "camara.gov.co"
        ],
        "tier1_media": [
            "eltiempo.com",
            "elespectador.com",
            "semana.com",
            "portafolio.co"
        ],
        "financial": [
            "bvc.com.co"
        ]
    },
    "MEX": {
        "official": [
            "gob.mx",
            "banxico.org.mx",
            "inegi.org.mx",
            "senado.gob.mx",
            "diputados.gob.mx"
        ],
        "tier1_media": [
            "eluniversal.com.mx",
            "reforma.com",
            "milenio.com",
            "elfinanciero.com.mx",
            "eleconomista.com.mx"
        ],
        "financial": [
            "bmv.com.mx"
        ]
    }
}

def get_search_query_modifiers(country_code: str) -> str:
    """
    Returns a search query modifier string to restrict results to trusted sources.
    Example: 'site:gov.ar OR site:lanacion.com.ar OR ...'
    """
    code = country_code.upper()
    if code not in TRUSTED_SOURCES:
        return ""
    
    sources = TRUSTED_SOURCES[code]
    all_domains = []
    
    # Prioritize official and tier1 media
    if "official" in sources:
        all_domains.extend(sources["official"])
    if "tier1_media" in sources:
        all_domains.extend(sources["tier1_media"])
        
    if not all_domains:
        return ""
        
    # Construct the OR query
    # "site:domain1 OR site:domain2 ..."
    # Google Search API has limits on query length/complexity, so we might need to be careful.
    # We will take top 10 most relevant to keep query valid.
    top_domains = all_domains[:15] 
    
    modifiers = " OR ".join([f"site:{d}" for d in top_domains])
    return f"({modifiers})"
