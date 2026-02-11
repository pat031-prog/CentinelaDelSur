export type AlertLevel = 'green' | 'yellow' | 'orange' | 'red' | 'black'

export type Domain = 'political' | 'economic' | 'supply_chain' | 'geopolitical' | 'climate' | 'technology'

export interface Country {
  code: string
  name: string
  name_es?: string
  region: string
  subregion: string
  capital: string
  population: number
  gdp_usd: number
  timezone?: string
  current_risk_score: number
  current_risk_level: AlertLevel
}

export interface DomainScore {
  domain: Domain
  score: number
  level: AlertLevel
  weight: number
}

export interface RiskAssessment {
  score: number
  level: AlertLevel
  base_score: number
  interaction_multiplier: number
  elevated_domains: number
  domains: Record<string, DomainScore>
  crisis_probability: {
    '30_days': ProbabilityEstimate
    '60_days': ProbabilityEstimate
    '90_days': ProbabilityEstimate
  }
  trend: string
}

export interface ProbabilityEstimate {
  probability: number
  margin: number
  lower_bound: number
  upper_bound: number
}

export interface Alert {
  id: number
  created_at: string
  country_code: string
  alert_level: AlertLevel
  domain?: string
  title: string
  description: string
  editorial?: string
  source_url?: string
  probability?: number
  is_active: boolean
}

export interface Scenario {
  country_code: string
  scenario_type: 'optimistic' | 'base' | 'pessimistic' | 'collapse'
  title: string
  description: string
  probability: number
  timeframe?: number
}
