import type { ReactNode } from 'react'
import type { Language, MatchLevel } from '../types'

const copy = {
  en: { home: 'Home', settings: 'Settings', lowData: 'Low data', language: 'English', demo: 'Independent prototype using fictional data. This is not a government website and does not submit applications.' },
  hi: { home: 'होम', settings: 'सेटिंग्स', lowData: 'कम डेटा', language: 'हिन्दी', demo: 'काल्पनिक डेटा वाला स्वतंत्र प्रोटोटाइप। यह सरकारी वेबसाइट नहीं है और आवेदन जमा नहीं करता।' },
}

export function Header({ language, lowData, onLanguage, onLowData, onHome, onExplore }: {
  language: Language; lowData: boolean; onLanguage: (language: Language) => void; onLowData: () => void; onHome: () => void; onExplore: () => void
}) {
  const t = copy[language]
  return <header className="site-header">
    <button className="brand" onClick={onHome} aria-label="Sahaayak home">
      <span className="brand-mark" aria-hidden="true">S</span>
      <span><strong>Sahaayak</strong><small>Find support you may be eligible for.</small></span>
    </button>
    <div className="header-actions">
      <button className="browse-link" onClick={onExplore}><span aria-hidden="true">⌕</span> Browse</button>
      <label className="language-select"><span className="sr-only">Choose language</span>
        <select value={language} onChange={(event) => onLanguage(event.target.value as Language)} aria-label="Choose language">
          <option value="en">EN</option><option value="hi">हिं</option>
        </select>
      </label>
      <button className={`low-data ${lowData ? 'active' : ''}`} onClick={onLowData} aria-pressed={lowData} title="Toggle low-data mode">
        <span aria-hidden="true">◌</span><span>{t.lowData}</span>
      </button>
    </div>
  </header>
}

export function Disclaimer({ language = 'en', compact = false }: { language?: Language; compact?: boolean }) {
  return <div className={`disclaimer ${compact ? 'compact' : ''}`} role="note"><span aria-hidden="true">ⓘ</span>{copy[language].demo}</div>
}

export function Page({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <main className={`page ${className}`}>{children}</main>
}

export function Badge({ children, tone = 'neutral' }: { children: ReactNode; tone?: 'neutral' | 'green' | 'amber' | 'indigo' }) {
  return <span className={`badge ${tone}`}>{children}</span>
}

export function MatchBadge({ level }: { level: MatchLevel }) {
  const label: Record<MatchLevel, string> = { strong: 'Strong match', possible: 'Possible match', moreInfo: 'More information needed', explore: 'Explore more' }
  const tone: Record<MatchLevel, 'green' | 'amber' | 'neutral'> = { strong: 'green', possible: 'amber', moreInfo: 'amber', explore: 'neutral' }
  return <Badge tone={tone[level]}><span className="status-dot" />{label[level]}</Badge>
}

export function Button({ children, onClick, variant = 'primary', type = 'button', disabled = false, className = '' }: {
  children: ReactNode; onClick?: () => void; variant?: 'primary' | 'secondary' | 'ghost' | 'danger'; type?: 'button' | 'submit'; disabled?: boolean; className?: string
}) {
  return <button type={type} onClick={onClick} disabled={disabled} className={`button ${variant} ${className}`}>{children}</button>
}

export function BackButton({ onClick, label = 'Back' }: { onClick: () => void; label?: string }) {
  return <button className="back-button" onClick={onClick}><span aria-hidden="true">←</span>{label}</button>
}

export function SectionHeading({ eyebrow, title, body }: { eyebrow?: string; title: string; body?: string }) {
  return <div className="section-heading">{eyebrow && <p className="eyebrow">{eyebrow}</p>}<h1>{title}</h1>{body && <p>{body}</p>}</div>
}

export function Sheet({ title, children, onClose }: { title: string; children: ReactNode; onClose: () => void }) {
  return <div className="overlay" role="dialog" aria-modal="true" aria-labelledby="sheet-title">
    <div className="sheet"><div className="sheet-top"><h2 id="sheet-title">{title}</h2><button className="icon-button" onClick={onClose} aria-label="Close">×</button></div>{children}</div>
  </div>
}
