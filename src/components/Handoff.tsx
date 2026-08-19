import { useState } from 'react'
import type { Language, PlanTask, Scheme } from '../types'
import { BackButton, Badge, Button, Disclaimer, Page, SectionHeading } from './ui'

type Route = 'online' | 'centre' | 'helper'
const routes: Array<{ id: Route; title: string; description: string; icon: string }> = [
  { id: 'online', title: 'Apply online myself', description: 'I will find and use a verified official website.', icon: '⌁' },
  { id: 'centre', title: 'Visit a support centre', description: 'I would like in-person help from an official support point.', icon: '⌂' },
  { id: 'helper', title: 'Ask a trusted family member/helper', description: 'I will get help from someone I trust.', icon: '♡' },
]

export function Handoff({ scheme, tasks, language, onBack, onCreated }: { scheme: Scheme; tasks: PlanTask[]; language: Language; onBack: () => void; onCreated: (route: Route) => void }) {
  const [route, setRoute] = useState<Route>('online')
  const complete = tasks.filter((task) => task.done).length
  return <Page className="handoff-page"><BackButton onClick={onBack} label="My preparation plan" /><SectionHeading eyebrow="Final demo step" title="Ready for the official application channel?" body="Sahaayak does not submit applications. Please verify the current requirements and use the relevant official channel yourself." />
    <div className="handoff-scheme"><span>{scheme.icon}</span><div><Badge tone="indigo">Demo scheme</Badge><b>{scheme.name}</b><small>{complete} of {tasks.length} preparation steps complete</small></div></div>
    <section className="route-section"><h2>How would you prefer to continue?</h2><p>Choose a fictional preferred route for your saved plan.</p><div className="route-choices">{routes.map((item) => <button key={item.id} className={route === item.id ? 'active' : ''} onClick={() => setRoute(item.id)} aria-pressed={route === item.id}><span>{item.icon}</span><span><b>{item.title}</b><small>{item.description}</small></span><i>{route === item.id ? '✓' : ''}</i></button>)}</div></section>
    <div className="handoff-warning"><span>ⓘ</span><p>Never share OTPs, passwords, or bank details with helpers. Use only a channel you have independently verified.</p></div>
    <Button className="full-button" onClick={() => onCreated(route)}>Create my readiness reference <span>→</span></Button><Disclaimer language={language} compact />
  </Page>
}

export function Success({ scheme, tasks, reference, route, language, onPlan, onHome }: { scheme: Scheme; tasks: PlanTask[]; reference: string; route: Route; language: Language; onPlan: () => void; onHome: () => void }) {
  const completed = tasks.filter((task) => task.done).length
  const routeLabel = routes.find((item) => item.id === route)?.title ?? 'your chosen route'
  return <Page className="success-page"><div className="success-mark">✓</div><Badge tone="green">Saved locally</Badge><h1>Your preparation plan is saved on this device</h1><p className="success-lead">You have not submitted an application. Your next step is to use a verified official channel when you are ready.</p><div className="success-summary"><div><small>CHOSEN DEMO SCHEME</small><b>{scheme.name}</b></div><div><small>PREPARATION</small><b>{completed} completed · {tasks.length - completed} pending</b></div><div><small>NEXT ACTION</small><b>{routeLabel}</b></div><div className="reference"><small>SYNTHETIC READINESS REFERENCE</small><b>{reference}</b><em>For this demo only — not an official reference number.</em></div></div><div className="success-actions"><Button onClick={onPlan}>Return to my plan</Button><Button variant="secondary" onClick={onHome}>Back to home</Button></div><Disclaimer language={language} /></Page>
}
