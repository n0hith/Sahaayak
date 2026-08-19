import { useMemo, useState } from 'react'
import { documentLabels } from '../data/schemes'
import { demoProfile, profileAtAGlance } from '../lib/eligibility'
import type { DocumentId, Language, Profile, Situation } from '../types'
import { BackButton, Badge, Button, Disclaimer, Page, SectionHeading } from './ui'

const situations: Array<{ id: Situation; label: string; emoji: string }> = [
  { id: 'student', label: 'Student', emoji: '⌑' }, { id: 'jobseeker', label: 'Job seeker', emoji: '◌' }, { id: 'employed', label: 'Employed', emoji: '↗' }, { id: 'farmer', label: 'Farmer', emoji: '♧' }, { id: 'selfEmployed', label: 'Self-employed', emoji: '◇' }, { id: 'homemaker', label: 'Homemaker', emoji: '⌂' }, { id: 'retired', label: 'Retired', emoji: '☼' }, { id: 'other', label: 'Other', emoji: '·' },
]

const steps = ['About you', 'Household', 'Your situation', 'A few details', 'Documents & summary']

export function Questionnaire({ profile, language, onChange, onComplete, onBack }: {
  profile: Profile; language: Language; onChange: (profile: Profile) => void; onComplete: () => void; onBack: () => void
}) {
  const [step, setStep] = useState(0)
  const [saved, setSaved] = useState(false)
  const update = <K extends keyof Profile>(key: K, value: Profile[K]) => onChange({ ...profile, [key]: value })
  const toggleSituation = (id: Situation) => update('situations', profile.situations.includes(id) ? profile.situations.filter((item) => item !== id) : [...profile.situations, id])
  const toggleDoc = (id: DocumentId) => update('documents', profile.documents.includes(id) ? profile.documents.filter((item) => item !== id) : [...profile.documents, id])
  const usesStudent = profile.situations.includes('student')
  const usesFarmer = profile.situations.includes('farmer')
  const needsExtra = usesStudent || usesFarmer || profile.situations.includes('jobseeker') || profile.situations.includes('selfEmployed')
  const completion = useMemo(() => Math.round(((step + 1) / steps.length) * 100), [step])
  const useDemo = () => { onChange({ ...demoProfile, language }); setStep(4) }
  const save = () => { setSaved(true); window.setTimeout(() => setSaved(false), 2200) }

  return <Page className="wizard-page">
    <BackButton onClick={step === 0 ? onBack : () => setStep(step - 1)} />
    <div className="wizard-progress" aria-label={`Step ${step + 1} of ${steps.length}`}><div className="progress-copy"><span>Step {step + 1} of {steps.length}</span><span>{completion}%</span></div><div className="progress-track"><span style={{ width: `${completion}%` }} /></div><div className="step-labels">{steps.map((name, index) => <span className={index <= step ? 'current' : ''} key={name}>{name}</span>)}</div></div>
    {step === 0 && <section className="wizard-content">
      <SectionHeading eyebrow="A few basics" title="Let’s start with you" body="Choose what feels comfortable. You can skip anything non-essential; it may make a match less certain." />
      <div className="callout demo-callout"><div><Badge tone="indigo">Fast demo path</Badge><p><b>Try a realistic example profile</b><br />A 20-year-old undergraduate in a town, also seeking training.</p></div><Button variant="secondary" onClick={useDemo}>Use demo profile</Button></div>
      <Question label="Your age" helper="Age helps us avoid suggesting a demo scheme meant for a different life stage."><div className="choice-grid compact">{[18, 20, 24, 30, 40, 60].map((age) => <Choice key={age} active={profile.age === age} onClick={() => update('age', age)}>{age === 60 ? '60+' : `${age} years`}</Choice>)}</div></Question>
      <Question label="Your demo state or region"><select value={profile.region ?? ''} onChange={(e) => update('region', e.target.value)}><option value="">Choose a demo region (optional)</option><option>Sundar Pradesh (demo)</option><option>Nadi State (demo)</option><option>Udaan Territory (demo)</option></select></Question>
      <Question label="Preferred language"><div className="choice-grid two"><Choice active={profile.language === 'en'} onClick={() => update('language', 'en')}>English</Choice><Choice active={profile.language === 'hi'} onClick={() => update('language', 'hi')}>हिन्दी</Choice></div></Question>
    </section>}
    {step === 1 && <section className="wizard-content">
      <SectionHeading eyebrow="Your household" title="Tell us only what helps matching" body="Amounts are broad ranges, not exact figures." />
      <Question label="How many people are in your household?" helper="Some support is designed for a whole household."><div className="choice-grid compact">{[1, 2, 3, 4, 5, 6].map((size) => <Choice key={size} active={profile.householdSize === size} onClick={() => update('householdSize', size)}>{size === 6 ? '6+' : size}</Choice>)}</div></Question>
      <Question label="Approximate annual household income"><div className="choice-stack">{[['under15', 'Under ₹1.5 lakh'], ['15to3', '₹1.5–3 lakh'], ['3to5', '₹3–5 lakh'], ['above5', 'Above ₹5 lakh'], ['unknown', 'Prefer not to say']].map(([id, label]) => <Choice key={id} active={profile.incomeBand === id} onClick={() => update('incomeBand', id as Profile['incomeBand'])}>{label}</Choice>)}</div></Question>
      <Question label="Where do you live?"><div className="choice-grid three">{[['rural', 'Village'], ['town', 'Town'], ['city', 'City']].map(([id, label]) => <Choice key={id} active={profile.location === id} onClick={() => update('location', id as Profile['location'])}>{label}</Choice>)}</div></Question>
      <Question label="Does your household have a current clean-cooking connection?" helper="This only helps us show a fictional home-support pathway. We do not ask for account numbers."><div className="choice-grid three"><Choice active={profile.cleanCooking === 'yes'} onClick={() => update('cleanCooking', 'yes')}>Yes</Choice><Choice active={profile.cleanCooking === 'no'} onClick={() => update('cleanCooking', 'no')}>No</Choice><Choice active={profile.cleanCooking === 'unknown'} onClick={() => update('cleanCooking', 'unknown')}>Not sure</Choice></div></Question>
    </section>}
    {step === 2 && <section className="wizard-content">
      <SectionHeading eyebrow="Your situation" title="What best describes you right now?" body="Choose more than one if it helps. This is about your current situation, not your identity." />
      <div className="situation-grid">{situations.map((item) => <button key={item.id} className={`situation-choice ${profile.situations.includes(item.id) ? 'active' : ''}`} onClick={() => toggleSituation(item.id)}><span aria-hidden="true">{item.emoji}</span>{item.label}<i>{profile.situations.includes(item.id) ? '✓' : '+'}</i></button>)}</div>
      <p className="helper-line">You can leave this empty and explore schemes, but we will be less able to tailor guidance.</p>
    </section>}
    {step === 3 && <section className="wizard-content">
      <SectionHeading eyebrow="Only if relevant" title={needsExtra ? 'A few helpful details' : 'Nothing more needed'} body={needsExtra ? 'These answers help clarify the schemes connected to your situation. All are optional.' : 'You can skip to documents, or go back and choose a situation to unlock relevant questions.'} />
      {usesStudent && <div className="detail-block"><h3>For students</h3><Question label="What are you studying?"><div className="choice-grid three"><Choice active={profile.educationStage === 'higher'} onClick={() => update('educationStage', 'higher')}>Higher education</Choice><Choice active={profile.educationStage === 'school'} onClick={() => update('educationStage', 'school')}>School</Choice><Choice active={profile.educationStage === 'unknown'} onClick={() => update('educationStage', 'unknown')}>Not sure</Choice></div></Question><Question label="Are you currently enrolled?"><div className="choice-grid three"><Choice active={profile.enrolled === 'yes'} onClick={() => update('enrolled', 'yes')}>Yes</Choice><Choice active={profile.enrolled === 'no'} onClick={() => update('enrolled', 'no')}>No</Choice><Choice active={profile.enrolled === 'unknown'} onClick={() => update('enrolled', 'unknown')}>Not sure</Choice></div></Question></div>}
      {usesFarmer && <div className="detail-block"><h3>For farming households</h3><Question label="Landholding range" helper="This is a broad range, only for fictional matching. We never check land records."><div className="choice-grid two"><Choice active={profile.landholding === 'marginal'} onClick={() => update('landholding', 'marginal')}>Marginal</Choice><Choice active={profile.landholding === 'small'} onClick={() => update('landholding', 'small')}>Small</Choice><Choice active={profile.landholding === 'large'} onClick={() => update('landholding', 'large')}>Larger</Choice><Choice active={profile.landholding === 'unknown'} onClick={() => update('landholding', 'unknown')}>Not sure</Choice></div></Question></div>}
      {profile.situations.includes('jobseeker') && <div className="detail-block"><h3>For training</h3><Question label="What kind of training interests you?"><select value={profile.trainingArea ?? ''} onChange={(e) => update('trainingArea', e.target.value)}><option value="">Choose later (optional)</option><option>Digital services</option><option>Healthcare support</option><option>Repair and maintenance</option><option>Food and hospitality</option></select></Question></div>}
      {(profile.situations.includes('selfEmployed') || profile.situations.includes('jobseeker')) && <div className="detail-block"><h3>Business interest</h3><Question label="Are you planning to start a small business?"><div className="choice-grid three"><Choice active={profile.planningBusiness === 'yes'} onClick={() => update('planningBusiness', 'yes')}>Yes</Choice><Choice active={profile.planningBusiness === 'no'} onClick={() => update('planningBusiness', 'no')}>No</Choice><Choice active={profile.planningBusiness === 'unknown'} onClick={() => update('planningBusiness', 'unknown')}>Not sure</Choice></div></Question></div>}
    </section>}
    {step === 4 && <section className="wizard-content">
      <SectionHeading eyebrow="Almost there" title="What documents do you have on hand?" body="Choose only examples you are comfortable marking. Do not upload anything here." />
      <div className="document-picker">{(Object.keys(documentLabels) as DocumentId[]).slice(0, 6).map((id) => <button key={id} className={`document-choice ${profile.documents.includes(id) ? 'active' : ''}`} onClick={() => toggleDoc(id)}><span>{profile.documents.includes(id) ? '✓' : '+'}</span>{documentLabels[id]}</button>)}</div>
      <div className="profile-summary"><span className="summary-icon">◌</span><div><p className="eyebrow">Your quick profile</p><p>{profileAtAGlance(profile)}</p><small>{profile.documents.length ? `${profile.documents.length} example document${profile.documents.length === 1 ? '' : 's'} marked available` : 'No example documents marked yet'}</small></div></div>
      <div className="uncertainty-note"><span>ⓘ</span><p>Missing answers will be shown honestly as “possible” or “more information needed”—never as an approval.</p></div>
    </section>}
    <div className="wizard-footer"><button className="text-link" onClick={save}>⌁ Save & continue later</button>{saved && <span className="saved-message">Saved on this device</span>}<div>{step > 0 && <Button variant="ghost" onClick={() => setStep(step - 1)}>Back</Button>}{step < steps.length - 1 ? <Button onClick={() => setStep(step + 1)}>Continue <span>→</span></Button> : <Button onClick={onComplete}>Find my matches <span>→</span></Button>}</div></div>
    <Disclaimer language={language} compact />
  </Page>
}

function Question({ label, helper, children }: { label: string; helper?: string; children: React.ReactNode }) {
  return <div className="question"><div className="question-label"><label>{label}</label>{helper && <details><summary>Why do we ask this?</summary><p>{helper}</p></details>}</div>{children}</div>
}

function Choice({ children, active, onClick }: { children: React.ReactNode; active: boolean; onClick: () => void }) {
  return <button type="button" className={`choice ${active ? 'active' : ''}`} onClick={onClick} aria-pressed={active}><span className="choice-check" aria-hidden="true">{active ? '✓' : ''}</span>{children}</button>
}
