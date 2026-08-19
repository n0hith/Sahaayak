import { useState } from 'react'
import heroImage from '../assets/sahaayak-hero.png'
import communityImage from '../assets/community-support.png'
import { schemes } from '../data/schemes'
import type { Language } from '../types'
import { Badge, Button, Disclaimer, Page, Sheet } from './ui'

const categoryCards = [
  { icon: '✦', label: 'Education & skills', detail: 'Scholarship and training pathways', tone: 'indigo' },
  { icon: '⌂', label: 'Home & family', detail: 'Care and clean-cooking support', tone: 'teal' },
  { icon: '↗', label: 'Work & farming', detail: 'Business and seasonal inputs', tone: 'amber' },
]

export function Welcome({ language, lowData, onStart, onExplore }: { language: Language; lowData: boolean; onStart: () => void; onExplore: () => void }) {
  const [showHow, setShowHow] = useState(false)
  const hindi = language === 'hi'
  return <Page className="welcome-page">
    <section className={`portal-hero ${lowData ? 'no-media' : ''}`}>
      <div className="portal-hero-copy">
        <Badge tone="green"><span className="status-dot" />Free independent readiness guide</Badge>
        <p className="eyebrow">{hindi ? 'आपकी तैयारी का साथी' : 'A calmer way to prepare'}</p>
        <h1>{hindi ? 'आपके लिए सही सहायता खोजें।' : 'Find your next helpful step.'}</h1>
        <p>{hindi ? 'कुछ सरल प्रश्नों के साथ, काल्पनिक योजनाओं में से आपके लिए उपयोगी विकल्प खोजें।' : 'Understand fictional support pathways, what might fit your household, and what to prepare before you use an official channel.'}</p>
        <div className="hero-actions"><Button onClick={onStart}>{hindi ? 'मेरे लिए क्या सही है' : 'Check what may fit me'} <span>→</span></Button><Button variant="secondary" onClick={onExplore}>{hindi ? 'डेमो योजनाएँ देखें' : 'Explore demo schemes'}</Button></div>
        <button className="text-link how-link" onClick={() => setShowHow(true)}>◌ {hindi ? 'यह कैसे काम करता है' : 'How this works'}</button>
      </div>
      {!lowData && <div className="portal-hero-media"><img src={heroImage} alt="A fictional family reviewing information together at home" /><div className="hero-photo-note"><span>⌾</span><div><b>Private by design</b><small>No identity numbers or uploads</small></div></div></div>}
    </section>
    <section className="quick-actions" aria-label="Quick ways to begin">
      <div><span className="quick-icon indigo">◷</span><p><b>About 4 minutes</b><small>Short household questionnaire</small></p></div>
      <div><span className="quick-icon teal">✦</span><p><b>{schemes.length} demo pathways</b><small>Education, work, home & more</small></p></div>
      <div><span className="quick-icon amber">⌁</span><p><b>Saved on this device</b><small>No account or sign-in needed</small></p></div>
    </section>
    <section className="welcome-section start-section">
      <div className="section-title-row"><div><p className="eyebrow">Start here</p><h2>Simple guidance for the steps before you apply</h2></div><span className="section-mark">01</span></div>
      <div className="value-points rich"><div><i>1</i><span><b>Tell us the basics</b><small>Broad household details only—never your Aadhaar, OTP, or bank account.</small></span></div><div><i>2</i><span><b>See what may fit</b><small>We explain matches, gaps, and uncertainty in everyday language.</small></span></div><div><i>3</i><span><b>Make a preparation plan</b><small>Use a practical list before you visit an official channel.</small></span></div></div>
    </section>
    <section className="welcome-section pathways-section">
      <div className="section-title-row"><div><p className="eyebrow">Explore by need</p><h2>Support pathways, made easier to scan</h2><p>These fictional examples show the kinds of preparation a person may need.</p></div><button className="text-link" onClick={onExplore}>View all {schemes.length} →</button></div>
      <div className="category-grid">{categoryCards.map((card) => <button onClick={onExplore} key={card.label} className={`category-card ${card.tone}`}><span className="category-icon">{card.icon}</span><div><b>{card.label}</b><small>{card.detail}</small></div><i>→</i></button>)}</div>
      <div className="featured-scheme"><div className="featured-icon">◎</div><div><Badge tone="indigo">Featured demo pathway</Badge><h3>Kaushal Nayi Raah Training Voucher</h3><p>For people preparing for work, study, or a career change.</p></div><Button variant="secondary" onClick={onExplore}>Explore skills</Button></div>
    </section>
    <section className="welcome-section safety-panel"><div className="safety-copy"><p className="eyebrow">Your information</p><h2>Share less. Understand more.</h2><p>Sahaayak asks only what helps explain mock eligibility. We do not ask for Aadhaar, bank details, passwords, OTPs, or document uploads.</p><div className="safety-links"><span>✓ No sign-in</span><span>✓ Local device storage</span><span>✓ Clear uncertainty</span></div></div><div className="safety-visual" aria-hidden="true"><div className="shield">⌾</div><div className="safe-lines"><i /><i /><i /></div></div></section>
    <section className={`community-feature ${lowData ? 'no-media' : ''}`}>
      {!lowData && <div className="community-media"><img src={communityImage} alt="Fictional community learning session with a facilitator showing a digital checklist" /></div>}
      <div className="community-copy"><Badge tone="green">Friendly, not formal</Badge><h2>Build confidence before the official process begins</h2><p>Use Sahaayak at home, with a trusted helper, or before visiting a support centre. The tool gives you a clear place to start—not a promise or a submission.</p><ul><li><span>⌁</span> See what you already have</li><li><span>!</span> Spot what may still be needed</li><li><span>→</span> Choose a next step that feels manageable</li></ul><Button variant="secondary" onClick={onStart}>Start my checklist</Button></div>
    </section>
    <section className="welcome-section help-grid"><div><p className="eyebrow">Before you begin</p><h2>Good to know</h2></div><div className="help-cards"><article><span>ⓘ</span><h3>This is not an official portal</h3><p>We use fictional data and do not submit applications.</p></article><article><span>?</span><h3>Not sure about an answer?</h3><p>You can skip non-essential questions and see what would clarify a match.</p></article><article><span>▣</span><h3>Need a paper copy?</h3><p>Your preparation plan includes a simple print view.</p></article></div></section>
    <Disclaimer language={language} />
    {showHow && <Sheet title={hindi ? 'यह कैसे काम करता है' : 'How this works'} onClose={() => setShowHow(false)}><ol className="how-list"><li><b>Share only the basics.</b> We use a small household questionnaire; no identity numbers or uploads.</li><li><b>See guidance, not decisions.</b> Local fictional rules create transparent demo matches.</li><li><b>Prepare with confidence.</b> Build a checklist, then verify current requirements with the official provider.</li></ol><p className="muted">The Hindi option translates core navigation and demo actions; some explanatory content remains in English for this prototype.</p><Button onClick={() => { setShowHow(false); onStart() }}>Start the demo</Button></Sheet>}
  </Page>
}
