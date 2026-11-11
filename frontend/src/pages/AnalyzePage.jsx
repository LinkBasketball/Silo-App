import { useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { Link2, Loader2, ScanSearch, Type } from 'lucide-react'
import { api } from '../services/api'
import { useContextWidget } from '../context/ContextWidgetContext'
import AnalysisPanels from '../components/AnalysisPanels'
import CoverageGauge from '../components/CoverageGauge'
import { ErrorState, PageHeader, Stat, Tabs } from '../components/ui'

export const SAMPLES = [
  { label: 'Campaign speech', voice: 'speech', text: 'Make no mistake: this administration has been a disaster for working families. Under their watch, grocery prices rose 18 percent. Experts say our plan is the best in the nation. We will cut taxes for every family by next year, and we should never apologize for fighting for you. “This is the most important election of our lifetime,” said the candidate to a cheering crowd.' },
  { label: 'News report', voice: 'text', text: 'The city council voted 7 to 2 on Tuesday to approve a $14 million bond for road repairs. The measure will appear on the November 2026 ballot. Council member Rivera said the plan was overdue. Opponents said property taxes would rise, though the city budget office estimated the increase at $38 a year for a median home.' },
  { label: 'Opinion column', voice: 'opinion', text: 'Our schools are failing, and everyone knows it. I believe the reckless spending of the past decade has bought nothing. Lawmakers must stop the bleeding now. Some say more money is the answer, but clearly it is not. The next budget will decide whether our children get the education they deserve.' },
]

export default function AnalyzePage() {
  const [mode, setMode] = useState('text')
  const [text, setText] = useState('')
  const [url, setUrl] = useState('')
  const [voice, setVoice] = useState('text')
  const [state, setState] = useState({ loading: false, error: null, result: null, submitted: '' })
  const { setSource, setOpen, setTab } = useContextWidget()
  const resultsRef = useRef(null)

  useEffect(() => {
    if (state.result) {
      setSource({ kind: 'analysis', payload: state.result.context })
      resultsRef.current?.focus()
    }
  }, [state.result, setSource])

  const submit = async (e) => {
    e.preventDefault()
    const body = mode === 'text' ? { text, voice } : { url, voice }
    setState((s) => ({ ...s, loading: true, error: null }))
    try {
      const result = await api.analyze(body)
      setState({ loading: false, error: null, result, submitted: mode === 'text' ? text : (result.input.text || '') })
    } catch (error) {
      setState((s) => ({ ...s, loading: false, error }))
    }
  }
  const r = state.result
  const valid = mode === 'text' ? text.trim().length >= 20 : /^https?:\/\//.test(url.trim())

  return (
    <div>
      <PageHeader eyebrow="News Intelligence" title="Analyze any article or speech">
        Paste text you are allowed to read, or a public article link. SILO extracts checkable claims, looks for related records, and maps persuasive language. Your text is processed in memory; only an anonymous hash and counts are logged.
      </PageHeader>
      <form onSubmit={submit} className="card p-5 sm:p-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <Tabs label="Input type" value={mode} onChange={setMode} tabs={[{ id: 'text', label: 'Paste text', icon: Type }, { id: 'url', label: 'Article link', icon: Link2 }]} />
          <label className="flex items-center gap-2 text-sm text-ink-600">Treat as
            <select className="input w-auto py-1.5" value={voice} onChange={(e) => setVoice(e.target.value)}>
              <option value="text">News text</option><option value="speech">Speech</option><option value="opinion">Opinion piece</option>
            </select>
          </label>
        </div>
        <div className="mt-4" role="tabpanel" id={`panel-${mode}`} aria-labelledby={`tab-${mode}`}>
          {mode === 'text' ? (
            <>
              <label htmlFor="analyze-text" className="sr-only">Text to analyze</label>
              <textarea id="analyze-text" rows={8} className="input font-serif text-[15px] leading-relaxed" placeholder="Paste an article, speech or statement (at least 20 characters)…" value={text} onChange={(e) => setText(e.target.value)} maxLength={20000} />
              <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-ink-500">
                <span>Try a sample:</span>
                {SAMPLES.map((s) => <button key={s.label} type="button" className="rounded-full border border-ink-200 bg-white px-2.5 py-1 font-semibold text-ink-600 hover:border-teal-400 hover:text-teal-700" onClick={() => { setText(s.text); setVoice(s.voice) }}>{s.label}</button>)}
                <span className="ml-auto tabular-nums">{text.length.toLocaleString()} / 20,000</span>
              </div>
            </>
          ) : (
            <>
              <label htmlFor="analyze-url" className="text-sm font-medium text-navy">Public article URL</label>
              <input id="analyze-url" type="url" className="input mt-1.5" placeholder="https://…" value={url} onChange={(e) => setUrl(e.target.value)} />
              <p className="mt-2 text-xs text-ink-500">SILO respects robots.txt, does not bypass paywalls or logins, and blocks private-network addresses. If a site refuses, paste the text instead.</p>
            </>
          )}
        </div>
        <div className="mt-5 flex justify-end">
          <button type="submit" className="btn-primary min-w-[140px]" disabled={!valid || state.loading}>
            {state.loading ? <><Loader2 size={16} className="animate-spin" aria-hidden="true" />Analyzing…</> : <><ScanSearch size={16} aria-hidden="true" />Analyze</>}
          </button>
        </div>
      </form>

      {state.error && <div className="mt-6"><ErrorState error={state.error} title="Analysis could not be completed" /></div>}

      {r && (
        <motion.section ref={resultsRef} tabIndex={-1} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="mt-10 outline-none" aria-labelledby="results-title">
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <p className="eyebrow">Results · {r.duration_ms} ms · {r.analysis.engine}</p>
              <h2 id="results-title" className="mt-1 font-serif text-2xl font-semibold">{r.input.title}</h2>
            </div>
            <button type="button" className="btn-primary" onClick={() => { setTab('evidence'); setOpen(true) }}><ScanSearch size={16} aria-hidden="true" />Open in SILO context</button>
          </div>
          <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
            <div className="card flex items-center justify-center p-3 sm:row-span-2 lg:row-span-1"><CoverageGauge coverage={r.context.coverage} size={128} /></div>
            <Stat label="Checkable claims" value={r.analysis.claims.length} hint={`of ${r.analysis.sentences.length} sentences`} />
            <Stat label="Context gaps" value={r.context.gaps.length} hint="questions to ask" />
            <Stat label="Language flags" value={r.analysis.language_audit.length} hint="loaded or vague wording" />
            <Stat label="Related records" value={r.context.sources.length} hint="not yet assessed" tip="For pasted text, SILO only links records that name the same entity and share key terms. It never decides automatically whether they support or contradict the claim." />
          </div>
          {r.context.coverage.state !== 'scored' && (
            <p className="mt-4 rounded-xl border border-ink-200 bg-white px-4 py-3 text-[13px] leading-relaxed text-ink-600">
              <strong className="text-navy">Why no score?</strong> {r.context.coverage.reason} In demonstration mode SILO’s record library only covers fictional State X, so most real-world text will show “insufficient evidence”. That is the honest result, not an error.
            </p>
          )}
          <div className="mt-8"><AnalysisPanels analysis={r.analysis} text={state.submitted} /></div>
        </motion.section>
      )}
    </div>
  )
}
