import { documentLabels, schemes } from '../data/schemes'
import type { DocumentId, MatchLevel, MatchResult, Profile, Rule, Scheme } from '../types'

const incomeRank: Record<Profile['incomeBand'], number | undefined> = {
  under15: 1,
  '15to3': 2,
  '3to5': 3,
  above5: 4,
  unknown: undefined,
}

const incomeLabel: Record<Profile['incomeBand'], string> = {
  under15: 'under ₹1.5 lakh/year',
  '15to3': '₹1.5–3 lakh/year',
  '3to5': '₹3–5 lakh/year',
  above5: 'above ₹5 lakh/year',
  unknown: 'not shared',
}

type RuleState = 'met' | 'unmet' | 'unknown'

function checkRule(rule: Rule, profile: Profile): RuleState {
  const field = rule.field as keyof Profile
  const current = profile[field]

  if (current === undefined || current === 'unknown' || (Array.isArray(current) && current.length === 0)) return 'unknown'

  if (rule.operator === 'ageBetween') {
    const [min, max] = String(rule.value).split('-').map(Number)
    return typeof current === 'number' && current >= min && current <= max ? 'met' : 'unmet'
  }
  if (rule.operator === 'incomeAtMost') {
    const limit = incomeRank[String(rule.value) as Profile['incomeBand']]
    const value = incomeRank[current as Profile['incomeBand']]
    return value !== undefined && limit !== undefined && value <= limit ? 'met' : 'unmet'
  }
  if (rule.operator === 'equals') return current === rule.value ? 'met' : 'unmet'
  if (rule.operator === 'includes') return Array.isArray(current) && current.includes(rule.value as never) ? 'met' : 'unmet'
  if (rule.operator === 'oneOf') {
    const accepted = rule.value as string[]
    return Array.isArray(current)
      ? current.some((item) => accepted.includes(String(item))) ? 'met' : 'unmet'
      : accepted.includes(String(current)) ? 'met' : 'unmet'
  }
  return 'unknown'
}

function missingDocs(scheme: Scheme, profile: Profile): DocumentId[] {
  return scheme.requiredDocuments.filter((doc) => !profile.documents.includes(doc))
}

export function evaluateScheme(scheme: Scheme, profile: Profile): MatchResult {
  const states = scheme.rules.map((rule) => ({ rule, state: checkRule(rule, profile) }))
  const unmet = states.filter((item) => item.state === 'unmet').map((item) => item.rule.label)
  const unknown = states.filter((item) => item.state === 'unknown').map((item) => item.rule.label)
  const docs = missingDocs(scheme, profile)
  const reasons = states.filter((item) => item.state === 'met').map((item) => item.rule.label)

  let level: MatchLevel
  if (unmet.length) level = 'explore'
  else if (unknown.length) level = 'moreInfo'
  else if (docs.length) level = 'possible'
  else level = 'strong'

  return {
    scheme,
    level,
    reasons,
    missingInfo: unknown,
    missingDocuments: docs,
    failedRules: unmet,
  }
}

export function getMatches(profile: Profile): MatchResult[] {
  const order: Record<MatchLevel, number> = { strong: 0, possible: 1, moreInfo: 2, explore: 3 }
  return schemes.map((scheme) => evaluateScheme(scheme, profile)).sort((a, b) => order[a.level] - order[b.level])
}

export function ruleFriendlyText(rule: Rule): string {
  return rule.label
}

export function documentName(id: DocumentId): string {
  return documentLabels[id]
}

export function profileAtAGlance(profile: Profile): string {
  const place = profile.location === 'unknown' ? 'location not shared' : profile.location
  const income = incomeLabel[profile.incomeBand]
  const roles = profile.situations.length ? profile.situations.join(', ').replaceAll('jobseeker', 'job seeker') : 'situation not shared'
  return `${profile.age ? `age ${profile.age}` : 'age not shared'} · ${place} · ${income} · ${roles}`
}

export const demoProfile: Profile = {
  age: 20,
  region: 'Sundar Pradesh (demo)',
  language: 'en',
  householdSize: 4,
  incomeBand: '15to3',
  location: 'town',
  cleanCooking: 'unknown',
  situations: ['student', 'jobseeker'],
  educationStage: 'higher',
  enrolled: 'yes',
  trainingArea: 'Digital services',
  planningBusiness: 'unknown',
  documents: ['identity', 'education'],
}

export function initialProfile(language: Profile['language'] = 'en'): Profile {
  return {
    language,
    incomeBand: 'unknown',
    location: 'unknown',
    cleanCooking: 'unknown',
    situations: [],
    educationStage: 'unknown',
    enrolled: 'unknown',
    landholding: 'unknown',
    planningBusiness: 'unknown',
    documents: [],
  }
}

export function schemeById(id?: string): Scheme | undefined {
  return schemes.find((scheme) => scheme.id === id)
}
