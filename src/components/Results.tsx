import { useMemo, useState } from 'react'
import { documentName } from '../lib/eligibility'
import { simpleTerms } from '../lib/explanations'
import type { Language, MatchLevel, MatchResult, Profile } from '../types'
import { BackButton, Badge, Button, Disclaimer, MatchBadge, Page, SectionHeading } from './ui'

type Filter = 'strong' | 'possible' | 'explore'

export function Results({ profile, matches, language, onBack, onDetails, onRestart }: {
  profile: Profile; matches: MatchResult[]; language: Language; onBack: () => void; onDetails: (match: MatchResult) => void; onRestart: () => void
}) {
  const [filter, setFilter] = useState<Filter>(() => matches.some((match) => match.level === 'strong') ? 'strong' : 'possible')
  const recommended = matches.find((match) => match.level === 'strong') ?? matches.find((match) => match.level === 'possible') ?? matches.find((match) => match.level === 'moreInfo')
  const visible = useMemo(() => matches.filter((match) => {
    if (filter === 'strong') return match.level === 'strong'
    if (filter === 'possible') return match.level === 'possible' || match.level === 'moreInfo'
    return match.level === 'explore'
  }), [matches, filter])
  const counts = {
    strong: matches.filter((match) => match.level === 'strong').length,
    possible: matches.filter((match) => match.level === 'possible' || match.level === 'moreInfo').length,
    explore: matches.filter((match) => match.level === 'explore').length,
  }
  return <Page className="results-page">
    <BackButton onClick={onBack} label="Edit answers" />
    <SectionHeading eyebrow="Your guidance" title="Here are benefits that may fit you" body="These are fictional demo results for guidance, not approval. Always confirm current requirements with the official provider." />
    <div className="simple-terms"><div className="ai-spark" aria-hidden="true">✦</div><div><div className="card-heading"><Badge tone="indigo">Demo assistant</Badge><h2>In simple terms</h2></div><p>{simpleTerms(profile, matches)}</p><small>Generated from your selected answers using local, deterministic templates.</small></div></div>
    {recommended && <button className="recommendation" onClick={() => onDetails(recommended)}><span className="recommendation-icon">★</span><span><small>START WITH THIS ONE</small><b>{recommended.scheme.name}</b><em>{recommended.level === 'strong' ? 'You have the key demo information and documents marked.' : 'It looks promising; start by clearing the highlighted gaps.'}</em></span><span className="arrow">→</span></button>}
    <div className="filters" role="tablist" aria-label="Filter schemes">
      <FilterButton active={filter === 'strong'} onClick={() => setFilter('strong')} label="Strong match" count={counts.strong} />
      <FilterButton active={filter === 'possible'} onClick={() => setFilter('possible')} label="Possible match" count={counts.possible} />
      <FilterButton active={filter === 'explore'} onClick={() => setFilter('explore')} label="Explore more" count={counts.explore} />
    </div>
    <div className="results-list">
      {visible.length ? visible.map((match) => <ResultCard key={match.scheme.id} match={match} onDetails={() => onDetails(match)} />) : <div className="empty-state"><span>✦</span><h2>No {filter === 'strong' ? 'strong' : filter === 'possible' ? 'possible' : ''} matches yet</h2><p>{filter === 'strong' ? 'A possible match may just need a document or detail confirmed.' : 'Try editing your answers or explore the demo options.'}</p>{filter !== 'explore' && <Button variant="secondary" onClick={() => setFilter('possible')}>See possible matches</Button>}</div>}
    </div>
    <button className="text-link restart-link" onClick={onRestart}>Start a new questionnaire</button>
    <Disclaimer language={language} compact />
  </Page>
}

function FilterButton({ active, label, count, onClick }: { active: boolean; label: string; count: number; onClick: () => void }) {
  return <button className={`filter-button ${active ? 'active' : ''}`} onClick={onClick} role="tab" aria-selected={active}>{label}<span>{count}</span></button>
}

function ResultCard({ match, onDetails }: { match: MatchResult; onDetails: () => void }) {
  const missing = match.missingDocuments.length ? `Still needed: ${match.missingDocuments.map(documentName).join(', ')}` : match.missingInfo.length ? `Confirm: ${match.missingInfo.join(', ')}` : null
  return <article className="result-card"><div className="scheme-card-top"><span className="scheme-icon" aria-hidden="true">{match.scheme.icon}</span><div><MatchBadge level={match.level} /><h2>{match.scheme.name}</h2></div></div><p className="scheme-summary">{match.scheme.summary}</p><div className="fit-line"><span aria-hidden="true">⌁</span><p><b>Why it may fit:</b> {match.reasons.length ? match.reasons.slice(0, 2).join(' · ') : match.level === 'explore' ? 'This demo scheme is available to explore.' : 'A few details could clarify this.'}</p></div>{missing && <div className="missing-line"><span aria-hidden="true">!</span><p>{missing}</p></div>}<div className="card-footer"><span>◷ {match.scheme.preparationTime}</span><Button variant="secondary" onClick={onDetails}>See details <span>→</span></Button></div></article>
}
