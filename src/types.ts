export type Language = 'en' | 'hi'
export type LocationType = 'rural' | 'town' | 'city' | 'unknown'
export type IncomeBand = 'under15' | '15to3' | '3to5' | 'above5' | 'unknown'
export type DocumentId = 'identity' | 'address' | 'income' | 'education' | 'land' | 'bank' | 'enrollment' | 'referral' | 'businessPlan'
export type Situation = 'student' | 'jobseeker' | 'employed' | 'farmer' | 'selfEmployed' | 'homemaker' | 'retired' | 'other'
export type MatchLevel = 'strong' | 'possible' | 'moreInfo' | 'explore'

export interface Profile {
  age?: number
  region?: string
  language: Language
  householdSize?: number
  incomeBand: IncomeBand
  location: LocationType
  cleanCooking: 'yes' | 'no' | 'unknown'
  situations: Situation[]
  educationStage?: 'higher' | 'school' | 'other' | 'unknown'
  enrolled?: 'yes' | 'no' | 'unknown'
  landholding?: 'none' | 'marginal' | 'small' | 'large' | 'unknown'
  trainingArea?: string
  planningBusiness?: 'yes' | 'no' | 'unknown'
  documents: DocumentId[]
}

export interface Rule {
  field: string
  operator: 'ageBetween' | 'incomeAtMost' | 'includes' | 'equals' | 'oneOf'
  value: string | number | string[]
  label: string
}

export interface Scheme {
  id: string
  name: string
  icon: string
  category: string
  summary: string
  whoItMayHelp: string
  support: string
  rules: Rule[]
  requiredDocuments: DocumentId[]
  optionalDocuments?: DocumentId[]
  preparationTime: string
  nextSteps: string[]
  availability: string
  privacyNote: string
}

export interface MatchResult {
  scheme: Scheme
  level: MatchLevel
  reasons: string[]
  missingInfo: string[]
  missingDocuments: DocumentId[]
  failedRules: string[]
}

export interface PlanTask {
  id: string
  title: string
  description: string
  status: 'available' | 'needed' | 'optional'
  done: boolean
}
