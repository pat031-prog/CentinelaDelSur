import { useState, useEffect, useCallback } from 'react'
import { api } from '../services/api'

export function useRiskData<T>(fetcher: () => Promise<T>, deps: any[] = []) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await fetcher()
      setData(result)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }, deps)

  useEffect(() => {
    load()
  }, [load])

  return { data, loading, error, reload: load }
}

export function useCountries() {
  return useRiskData(() => api.getCountries(), [])
}

export function useCountry(code: string) {
  return useRiskData(() => api.getCountry(code), [code])
}

export function useRegionalOverview() {
  return useRiskData(() => api.getRegionalOverview(), [])
}

export function useAlerts(params?: { country_code?: string; level?: string }) {
  return useRiskData(
    () => api.getAlerts(params),
    [params?.country_code, params?.level]
  )
}
