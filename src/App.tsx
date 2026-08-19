import { useEffect, useMemo, useState } from 'react'
import { Compare } from './components/Compare'
import { Handoff, Success } from './components/Handoff'
import { PreparationPlan } from './components/PreparationPlan'
import { Questionnaire } from './components/Questionnaire'
import { Results } from './components/Results'
import { SchemeDetail } from './components/SchemeDetail'
import { Header } from './components/ui'
import { Welcome } from './components/Welcome'
import { getMatches, initialProfile } from './lib/eligibility'
import { planTasks } from './lib/explanations'
import type { Language, Profile } from './types'

type Screen = 'welcome' | 'questionnaire' | 'results' | 'detail' | 'compare' | 'plan' | 'handoff' | 'success'
type StoredTasks = Record<string, Record<string, boolean>>

function restore<T>(key: string, fallback: T): T {
  try { const saved = localStorage.getItem(key); return saved ? JSON.parse(saved) as T : fallback } catch { return fallback }
}

export default function App() {
  const [profile, setProfile] = useState<Profile>(() => restore('sahaayak-profile', initialProfile()))
  const [screen, setScreen] = useState<Screen>(() => restore('sahaayak-screen', 'welcome'))
  const [selectedId, setSelectedId] = useState<string>(() => restore('sahaayak-selected-scheme', 'kaushal-nayi-raah'))
  const [lowData, setLowData] = useState(() => restore('sahaayak-low-data', false))
  const [taskStates, setTaskStates] = useState<StoredTasks>(() => restore('sahaayak-plan-tasks', {}))
  const [reference, setReference] = useState(() => restore('sahaayak-reference', ''))
  const [route, setRoute] = useState<'online' | 'centre' | 'helper'>(() => restore('sahaayak-route', 'online'))
  const matches = useMemo(() => getMatches(profile), [profile])
  const selected = matches.find((match) => match.scheme.id === selectedId) ?? matches[0]
  const tasks = useMemo(() => selected ? planTasks(selected.scheme, profile, taskStates[selected.scheme.id]) : [], [selected, profile, taskStates])

  useEffect(() => { localStorage.setItem('sahaayak-profile', JSON.stringify(profile)) }, [profile])
  useEffect(() => { localStorage.setItem('sahaayak-screen', JSON.stringify(screen)) }, [screen])
  useEffect(() => { localStorage.setItem('sahaayak-selected-scheme', JSON.stringify(selectedId)) }, [selectedId])
  useEffect(() => { localStorage.setItem('sahaayak-low-data', JSON.stringify(lowData)) }, [lowData])
  useEffect(() => { localStorage.setItem('sahaayak-plan-tasks', JSON.stringify(taskStates)) }, [taskStates])
  useEffect(() => { localStorage.setItem('sahaayak-reference', JSON.stringify(reference)); localStorage.setItem('sahaayak-route', JSON.stringify(route)) }, [reference, route])

  const language: Language = profile.language || 'en'
  const choose = (id: string, next: Screen = 'detail') => { setSelectedId(id); setScreen(next); window.scrollTo(0, 0) }
  const move = (next: Screen) => { setScreen(next); window.scrollTo(0, 0) }
  const completeQuestionnaire = () => move('results')
  const startFresh = () => { setProfile(initialProfile(language)); setTaskStates({}); move('questionnaire') }
  const toggleTask = (taskId: string) => { if (!selected) return; setTaskStates((previous) => ({ ...previous, [selected.scheme.id]: { ...previous[selected.scheme.id], [taskId]: !tasks.find((task) => task.id === taskId)?.done } })) }
  const createReference = (selectedRoute: 'online' | 'centre' | 'helper') => { setRoute(selectedRoute); setReference(`SHY-2026-${Math.floor(10000 + Math.random() * 90000)}`); move('success') }
  const onHome = () => move('welcome')

  return <div className={`app-shell ${lowData ? 'low-data-mode' : ''}`}>
    <div className="prototype-strip"><span>●</span> Demo service guide — fictional schemes, private by design, no official applications.</div>
    <Header language={language} lowData={lowData} onLanguage={(next) => setProfile({ ...profile, language: next })} onLowData={() => setLowData(!lowData)} onHome={onHome} onExplore={() => move('results')} />
    {screen === 'welcome' && <Welcome language={language} lowData={lowData} onStart={() => move('questionnaire')} onExplore={() => move('results')} />}
    {screen === 'questionnaire' && <Questionnaire profile={profile} language={language} onChange={setProfile} onComplete={completeQuestionnaire} onBack={onHome} />}
    {screen === 'results' && <Results profile={profile} matches={matches} language={language} onBack={() => move('questionnaire')} onDetails={(match) => choose(match.scheme.id)} onRestart={startFresh} />}
    {screen === 'detail' && selected && <SchemeDetail match={selected} profile={profile} language={language} onBack={() => move('results')} onPlan={() => move('plan')} onCompare={() => move('compare')} />}
    {screen === 'compare' && selected && <Compare selected={selected} matches={matches} language={language} onBack={() => move('detail')} onChoose={(match) => choose(match.scheme.id)} onPlan={() => move('plan')} />}
    {screen === 'plan' && selected && <PreparationPlan scheme={selected.scheme} tasks={tasks} language={language} onBack={() => move('detail')} onToggle={toggleTask} onReady={() => move('handoff')} />}
    {screen === 'handoff' && selected && <Handoff scheme={selected.scheme} tasks={tasks} language={language} onBack={() => move('plan')} onCreated={createReference} />}
    {screen === 'success' && selected && <Success scheme={selected.scheme} tasks={tasks} reference={reference || 'SHY-2026-00000'} route={route} language={language} onPlan={() => move('plan')} onHome={onHome} />}
  </div>
}
