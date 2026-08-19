import { documentName, profileAtAGlance } from './eligibility'
import type { MatchResult, PlanTask, Profile, Scheme } from '../types'

export function simpleTerms(profile: Profile, matches: MatchResult[]): string {
  const top = matches.filter((match) => match.level !== 'explore').slice(0, 3)
  if (!top.length) return 'We need a little more information before we can suggest a useful next step. You can still explore the demo schemes below.'
  const names = top.map((match) => match.scheme.name.replace(' Support', '').replace(' Voucher', '')).join(', ')
  const uncertainty = top.some((match) => match.level !== 'strong')
    ? ' A few items still need confirming, so these are guidance—not approval.'
    : ' These are strong demo matches based on the answers you shared.'
  return `You told us: ${profileAtAGlance(profile)}. The clearest places to start are ${names}.${uncertainty}`
}

export function fitExplanation(match: MatchResult): string {
  if (match.level === 'strong') return `Your answers match the main demo conditions: ${match.reasons.join(', ').toLowerCase()}. Please still confirm current requirements with the official provider.`
  if (match.level === 'possible') return `Your answers meet the main demo conditions. Before you continue, prepare or confirm ${match.missingDocuments.map(documentName).join(', ').toLowerCase()}.`
  if (match.level === 'moreInfo') return `This could be relevant, but we cannot tell yet because ${match.missingInfo.join(', ').toLowerCase()} needs confirmation.`
  return `This is not one of your current matches because ${match.failedRules.join(', ').toLowerCase()} does not match the demo conditions. You can still explore it and update your answers later.`
}

export function planTasks(scheme: Scheme, profile: Profile, existing: Record<string, boolean> = {}): PlanTask[] {
  const documents = scheme.requiredDocuments.map((doc) => {
    const available = profile.documents.includes(doc)
    return {
      id: `doc-${doc}`,
      title: available ? `${documentName(doc)} is marked available` : `Gather ${documentName(doc)}`,
      description: available ? 'Keep a current copy ready for the official provider.' : 'Check the latest official requirements before requesting or sharing this document.',
      status: available ? 'available' as const : 'needed' as const,
      done: existing[`doc-${doc}`] ?? available,
    }
  })
  return [
    ...documents,
    {
      id: 'official-instructions', title: 'Read the official application instructions',
      description: 'Check the official provider’s current eligibility, dates, fees, and process.', status: 'needed', done: existing['official-instructions'] ?? false,
    },
    {
      id: 'provider-check', title: 'Confirm eligibility with the official provider',
      description: 'Ask about anything that is unclear before submitting documents.', status: 'needed', done: existing['provider-check'] ?? false,
    },
    {
      id: 'secure-copy', title: 'Keep your acknowledgement safely',
      description: 'After using an official channel, save the reference number somewhere secure.', status: 'optional', done: existing['secure-copy'] ?? false,
    },
  ]
}

export function explainTask(task: PlanTask, question: 'why' | 'missing' | 'first'): string {
  if (question === 'why') return `${task.title} helps the official provider check the mock conditions. Sahaayak does not review or receive the document.`
  if (question === 'missing') return task.status === 'available'
    ? 'You have marked this as available. Make sure it is current, readable, and only share it through a verified official channel.'
    : 'Check the official provider’s current instructions. They can tell you whether an alternative document or a local support centre can help.'
  return task.status === 'needed'
    ? `Start with “${task.title}”. It is one of the items that could hold up preparation.`
    : 'Start by reading the official instructions, then complete the still-needed items one at a time.'
}
