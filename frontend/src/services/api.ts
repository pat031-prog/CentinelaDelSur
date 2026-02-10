const API_URL = (window as any).ENV?.API_URL || import.meta.env.VITE_API_URL || 'https://atalaya-backend.onrender.com';
const API_BASE = `${API_URL}/api/v1`

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`)
  }
  return response.json()
}

export const api = {
  getCountries: (params?: { region?: string; min_risk?: number }) => {
    const searchParams = new URLSearchParams()
    if (params?.region) searchParams.set('region', params.region)
    if (params?.min_risk) searchParams.set('min_risk', String(params.min_risk))
    const qs = searchParams.toString()
    return fetchApi<any[]>(`/countries${qs ? `?${qs}` : ''}`)
  },

  getCountry: (code: string) =>
    fetchApi<any>(`/countries/${code}`),

  getCountryRisk: (code: string) =>
    fetchApi<any>(`/countries/${code}/risk`),

  analyzeCountry: (code: string, depth: string = 'standard') =>
    fetchApi<any>(`/countries/${code}/analyze`, {
      method: 'POST',
      body: JSON.stringify({ depth, domains: ['political', 'economic', 'supply_chain', 'geopolitical', 'climate', 'technology'] }),
    }),

  getRegionalOverview: () =>
    fetchApi<any>('/regional/latam'),

  getAlerts: (params?: { country_code?: string; level?: string }) => {
    const searchParams = new URLSearchParams()
    if (params?.country_code) searchParams.set('country_code', params.country_code)
    if (params?.level) searchParams.set('level', params.level)
    const qs = searchParams.toString()
    return fetchApi<any>(`/alerts${qs ? `?${qs}` : ''}`)
  },

  getAlertSummary: () =>
    fetchApi<any>('/alerts/summary'),

  getDomainAnalysis: (domain: string) =>
    fetchApi<any>(`/domains/${domain}`),

  simulateCascade: (countryCode: string, triggerEvent: string, shockMagnitude: number = 30) =>
    fetchApi<any>('/scenarios/simulate', {
      method: 'POST',
      body: JSON.stringify({
        country_code: countryCode,
        trigger_event: triggerEvent,
        parameters: { shock_magnitude: shockMagnitude },
        time_horizon_days: 90,
      }),
    }),

  getHistoricalCrises: (params?: { crisis_type?: string; country_code?: string }) => {
    const searchParams = new URLSearchParams()
    if (params?.crisis_type) searchParams.set('crisis_type', params.crisis_type)
    if (params?.country_code) searchParams.set('country_code', params.country_code)
    const qs = searchParams.toString()
    return fetchApi<any[]>(`/historical/crises${qs ? `?${qs}` : ''}`)
  },
}
