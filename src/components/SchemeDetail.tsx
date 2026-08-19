import { documentName } from '../lib/eligibility'
import { fitExplanation } from '../lib/explanations'
import type { Language, MatchResult, Profile } from '../types'
import { BackButton, Badge, Button, Disclaimer, MatchBadge, Page } from './ui'

export function SchemeDetail({ match, profile, language, onBack, onPlan, onCompare }: {
  match: MatchResult; profile: Profile; language: Language; onBack: () => void; onPlan: () => void; onCompare: () => void
}) {
  const available = match.scheme.requiredDocuments.filter((doc) => profile.documents.includes(doc))
  const stillNeeded = match.scheme.requiredDocuments.filter((doc) => !profile.documents.includes(doc))
  return <Page className="detail-page">
    <BackButton onClick={onBack} label="All results" />
    <div className="scheme-intro"><div className="scheme-intro-icon" aria-hidden="true">{match.scheme.icon}</div><div><Badge tone="indigo">Demo scheme</Badge><h1>{match.scheme.name}</h1><p>{match.scheme.summary}</p><div className="detail-meta"><MatchBadge level={match.level} /><span>◷ {match.scheme.preparationTime}</span></div></div></div>
    <div className="support-strip"><span>Estimated demo support</span><b>{match.scheme.support.replace('Estimated demo support: ', '')}</b><small>◌ {match.scheme.availability}</small></div>
    <section className="detail-section fit-section"><div className="section-icon">✦</div><div><h2>Why this may fit you</h2><p>{fitExplanation(match)}</p></div></section>
    <section className="detail-section"><h2>Who this may help</h2><p>{match.scheme.whoItMayHelp}</p><div className="rule-chips">{match.scheme.rules.map((rule) => <span key={rule.label}>{rule.label}</span>)}</div></section>
    <section className="detail-section"><h2>Before you start</h2><p className="muted">These are example preparation items for the demo, not a live official checklist.</p><div className="document-statuses">
      <DocumentGroup title="Already marked available" icon="✓" tone="available" items={available.map(documentName)} empty="None marked yet" />
      <DocumentGroup title="Still needed" icon="!" tone="needed" items={stillNeeded.map(documentName)} empty="Nothing else marked as required" />
      <DocumentGroup title="Needs confirmation" icon="?" tone="confirm" items={[...match.missingInfo, ...(match.scheme.optionalDocuments ?? []).map(documentName)]} empty="Confirm current terms with the provider" />
    </div></section>
    <section className="detail-section next-section"><h2>What happens next</h2><ol>{['Gather documents', 'Confirm eligibility with the official provider', 'Submit through the official channel', 'Save the acknowledgement/reference number'].map((step, index) => <li key={step}><span>{index + 1}</span><div><b>{step}</b><p>{match.scheme.nextSteps[index]}</p></div></li>)}</ol></section>
    <section className="do-not-section"><span>⌾</span><div><h2>What we do not do</h2><p>Sahaayak does not submit any application, access official records, or collect document uploads. This is a readiness guide only.</p></div></section>
    <div className="detail-actions"><Button onClick={onPlan}>Create my preparation plan <span>→</span></Button><Button variant="secondary" onClick={onCompare}>Compare with another scheme</Button></div>
    <p className="privacy-inline">Privacy note: {match.scheme.privacyNote}</p>
    <Disclaimer language={language} compact />
  </Page>
}

function DocumentGroup({ title, icon, tone, items, empty }: { title: string; icon: string; tone: string; items: string[]; empty: string }) {
  return <div className={`doc-group ${tone}`}><h3><span>{icon}</span>{title}</h3>{items.length ? <ul>{items.map((item) => <li key={item}>{item}</li>)}</ul> : <p>{empty}</p>}</div>
}
