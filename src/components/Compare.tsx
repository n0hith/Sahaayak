import { useState } from 'react'
import { documentName } from '../lib/eligibility'
import type { Language, MatchResult } from '../types'
import { BackButton, Badge, Button, Disclaimer, MatchBadge, Page, SectionHeading } from './ui'

export function Compare({ selected, matches, language, onBack, onChoose, onPlan }: {
  selected: MatchResult; matches: MatchResult[]; language: Language; onBack: () => void; onChoose: (match: MatchResult) => void; onPlan: () => void
}) {
  const firstOther = matches.find((match) => match.scheme.id !== selected.scheme.id && match.level !== 'explore') ?? matches.find((match) => match.scheme.id !== selected.scheme.id)
  const [otherId, setOtherId] = useState(firstOther?.scheme.id ?? '')
  const other = matches.find((match) => match.scheme.id === otherId) ?? firstOther
  return <Page className="compare-page"><BackButton onClick={onBack} label="Scheme details" /><SectionHeading eyebrow="Compare options" title="Choose your next helpful step" body="Compare fictional preparation requirements before you decide what to work on first." />
    <div className="compare-pick"><label>Compare with</label><select value={other?.scheme.id ?? ''} onChange={(event) => setOtherId(event.target.value)}><option value="">Choose another demo scheme</option>{matches.filter((match) => match.scheme.id !== selected.scheme.id).map((match) => <option value={match.scheme.id} key={match.scheme.id}>{match.scheme.name}</option>)}</select></div>
    {other && <div className="comparison-grid"><ComparisonCard match={selected} chosen onPlan={onPlan} /><ComparisonCard match={other} onPlan={() => onChoose(other)} /></div>}
    <div className="compare-tip"><span>✦</span><p><b>A simple way to choose:</b> start with the option that matters most to you and has the fewest still-needed preparation items.</p></div><Disclaimer language={language} compact />
  </Page>
}

function ComparisonCard({ match, chosen, onPlan }: { match: MatchResult; chosen?: boolean; onPlan: () => void }) {
  return <article className={`comparison-card ${chosen ? 'chosen' : ''}`}>{chosen && <Badge tone="indigo">Currently viewing</Badge>}<span className="scheme-icon">{match.scheme.icon}</span><MatchBadge level={match.level} /><h2>{match.scheme.name}</h2><p>{match.scheme.summary}</p><dl><div><dt>Demo support</dt><dd>{match.scheme.support.replace('Estimated demo support: ', '')}</dd></div><div><dt>Preparation time</dt><dd>{match.scheme.preparationTime}</dd></div><div><dt>Still needed</dt><dd>{match.missingDocuments.length ? match.missingDocuments.map(documentName).join(', ') : match.missingInfo.length ? match.missingInfo.join(', ') : 'No gaps shown'}</dd></div></dl><Button variant={chosen ? 'primary' : 'secondary'} onClick={onPlan}>{chosen ? 'Make my plan' : 'View this scheme'} <span>→</span></Button></article>
}
