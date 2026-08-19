import { useState } from 'react'
import { explainTask } from '../lib/explanations'
import type { Language, PlanTask, Scheme } from '../types'
import { BackButton, Badge, Button, Disclaimer, Page, SectionHeading, Sheet } from './ui'

export function PreparationPlan({ scheme, tasks, language, onBack, onToggle, onReady }: {
  scheme: Scheme; tasks: PlanTask[]; language: Language; onBack: () => void; onToggle: (id: string) => void; onReady: () => void
}) {
  const [explainOpen, setExplainOpen] = useState(false)
  const [activeTask, setActiveTask] = useState(tasks.find((task) => task.status === 'needed') ?? tasks[0])
  const [question, setQuestion] = useState<'why' | 'missing' | 'first'>('why')
  const completed = tasks.filter((task) => task.done).length
  const progress = Math.round((completed / tasks.length) * 100)
  return <Page className="plan-page"><BackButton onClick={onBack} label="Scheme details" />
    <SectionHeading eyebrow="For your chosen demo scheme" title="Your preparation plan" body="A simple, local checklist to help you prepare before using any official channel." />
    <div className="plan-overview"><div className="progress-ring" style={{ '--progress': `${progress * 3.6}deg` } as React.CSSProperties}><div><b>{progress}%</b><small>ready</small></div></div><div><Badge tone="indigo">{scheme.name}</Badge><h2>{completed} of {tasks.length} steps complete</h2><p>Take one step at a time. Preparation is not an application or approval.</p></div></div>
    <div className="task-legend"><span className="available">● Already available</span><span className="needed">● Still needed</span><span className="optional">● Optional</span></div>
    <div className="task-list">{tasks.map((task) => <label key={task.id} className={`task ${task.status} ${task.done ? 'done' : ''}`}><input type="checkbox" checked={task.done} onChange={() => onToggle(task.id)} /><span className="task-check" aria-hidden="true">{task.done ? '✓' : ''}</span><span className="task-copy"><span className="task-topline"><Badge tone={task.status === 'available' ? 'green' : task.status === 'needed' ? 'amber' : 'neutral'}>{task.status === 'available' ? 'Available' : task.status === 'needed' ? 'Still needed' : 'Optional'}</Badge><button type="button" className="mini-explain" onClick={(event) => { event.preventDefault(); setActiveTask(task); setExplainOpen(true) }}>Explain</button></span><b>{task.title}</b><small>{task.description}</small></span></label>)}</div>
    <div className="plan-actions"><Button variant="secondary" onClick={() => { setActiveTask(tasks.find((task) => task.status === 'needed') ?? tasks[0]); setExplainOpen(true) }}>✦ Ask Sahaayak to explain</Button><Button variant="ghost" onClick={() => window.print()}>▣ Download / print summary</Button></div>
    <div className="ready-card"><div><span className="ready-icon">→</span><div><h2>I’m ready to continue</h2><p>Make a synthetic readiness reference, then use a verified official channel yourself.</p></div></div><Button onClick={onReady}>Continue</Button></div>
    <Disclaimer language={language} compact />
    {explainOpen && <Sheet title="Ask Sahaayak to explain" onClose={() => setExplainOpen(false)}><div className="explain-task"><Badge tone={activeTask.status === 'needed' ? 'amber' : activeTask.status === 'available' ? 'green' : 'neutral'}>{activeTask.status}</Badge><h3>{activeTask.title}</h3></div><div className="ask-choices"><button className={question === 'why' ? 'active' : ''} onClick={() => setQuestion('why')}>Why do I need this?</button><button className={question === 'missing' ? 'active' : ''} onClick={() => setQuestion('missing')}>What if I don’t have it?</button><button className={question === 'first' ? 'active' : ''} onClick={() => setQuestion('first')}>What should I do first?</button></div><div className="assistant-answer"><span>✦</span><p>{explainTask(activeTask, question)}</p></div><p className="muted">This demo explanation uses a local template. It does not contact any provider or inspect your documents.</p></Sheet>}
  </Page>
}
