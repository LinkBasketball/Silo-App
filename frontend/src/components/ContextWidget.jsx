import { useEffect, useMemo, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import {
  Building2, ChevronDown, CircleHelp, Clock, FileSearch, Gauge, Layers, Library, Network, ScanSearch, X,
} from 'lucide-react'
import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { useContextWidget } from '../context/ContextWidgetContext'
import { api } from '../services/api'
import { useApi } from '../hooks/useApi'
import CoverageGauge from './CoverageGauge'
import SourceDialog from './SourceDialog'
import { cx, DataStatusBadge, EmptyState, ErrorState, InfoTip, LoadingBlock, RELATIONSHIP, RelationshipBadge, Tabs } from './ui'
import { fmtDate, fmtDateTime, fmtPct, fmtUSD } from './format'

const TABS = [
  { id: 'overview', label: 'Coverage', icon: Gauge },
  { id: 'evidence', label: 'Evidence', icon: FileSearch },
  { id: 'gaps', label: 'Context gaps', icon: CircleHelp },
  { id: 'topics', label: 'Focus', icon: Layers },
  { id: 'publisher', label: 'Publisher', icon: Building2 },
  { id: 'sources', label: 'Sources', icon: Library },
]
const METHOD_LABEL = {
  curated_demo_annotation: 'Curated demonstration annotation',
  automatic_related_record: 'Automatic match — relationship not assessed',
}
const CLAIM_TYPE = { statistical: 'Statistic', legislative_action: 'Legislative action', attributed_quote: 'Attributed quote', event: 'Event' }

export function useWidgetData() {
  const { source } = useContextWidget()
  const isArticle = source?.kind === 'article'
  const q = useApi((o) => api.context(source.id, o), [source?.id], { key: isArticle ? `ctx-${source?.id}` : undefined, enabled: isArticle })
  if (!source) return { data: null, loading: false, error: null }
  if (source.kind === 'analysis') return { data: source.payload, loading: false, error: null }
  return q
}

export default function ContextWidget() {
  const { open, setOpen, tab, setTab, source } = useContextWidget()
  const { data, loading, error, reload } = useWidgetData()
  const fabRef = useRef(null)
  const panelRef = useRef(null)
  const [dialog, setDialog] = useState(null)

  useEffect(() => {
    if (!open) return undefined
    const t = setTimeout(() => panelRef.current?.focus(), 30)
    const onKey = (e) => { if (e.key === 'Escape' && !dialog) { setOpen(false); fabRef.current?.focus() } }
    document.addEventListener('keydown', onKey)
    return () => { clearTimeout(t); document.removeEventListener('keydown', onKey) }
  }, [open, dialog, setOpen])

  const close = () => { setOpen(false); fabRef.current?.focus() }
  const counts = data ? { evidence: data.evidence.length, gaps: data.gaps.length, sources: data.sources.length } : {}

  return (
    <>
      <AnimatePresence>
        {open && (
          <motion.section
            ref={panelRef} tabIndex={-1} role="dialog" aria-modal="false" aria-labelledby="ctx-title" id="silo-context-panel"
            initial={{ opacity: 0, y: 16, scale: 0.98 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: 12, scale: 0.98 }}
            transition={{ duration: 0.18, ease: 'easeOut' }}
            className="fixed inset-0 z-[60] flex flex-col bg-paper outline-none sm:inset-auto sm:bottom-24 sm:right-6 sm:h-[min(760px,calc(100vh-8rem))] sm:w-[460px] sm:rounded-2xl sm:border sm:border-ink-100 sm:shadow-lift"
          >
            <header className="flex items-start justify-between gap-3 border-b border-ink-100 bg-white px-5 pb-3 pt-4 sm:rounded-t-2xl">
              <div className="min-w-0">
                <p className="eyebrow flex items-center gap-1.5"><ScanSearch size={12} aria-hidden="true" />SILO context</p>
                <h2 id="ctx-title" className="mt-1 line-clamp-2 font-serif text-[17px] font-semibold leading-snug">{data?.title || 'Evidence context'}</h2>
                {data && <div className="mt-1.5 flex flex-wrap items-center gap-2 text-xs text-ink-500"><DataStatusBadge status={data.data_status} />{data.subtitle && <span className="truncate">{data.subtitle}</span>}</div>}
              </div>
              <button type="button" onClick={close} className="rounded-lg p-1.5 text-ink-500 hover:bg-ink-50 hover:text-navy" aria-label="Close context panel"><X size={18} /></button>
            </header>
            {data && (
              <div className="border-b border-ink-100 bg-white px-3 py-2">
                <Tabs size="sm" label="Context sections" value={tab} onChange={setTab}
                  tabs={TABS.map((t) => ({ ...t, count: counts[t.id] }))} />
              </div>
            )}
            <div key={tab} className="flex-1 overflow-y-auto px-5 py-4" id={`panel-${tab}`} role="tabpanel" aria-labelledby={`tab-${tab}`}>
              {!source && <NoSource />}
              {source && loading && <LoadingBlock lines={6} label="Loading context" />}
              {source && error && <ErrorState error={error} onRetry={reload} title="Context could not be loaded" />}
              {data && tab === 'overview' && <Overview data={data} onTab={setTab} />}
              {data && tab === 'evidence' && <Evidence data={data} onOpen={setDialog} />}
              {data && tab === 'gaps' && <Gaps data={data} />}
              {data && tab === 'topics' && <Topics data={data} />}
              {data && tab === 'publisher' && <Publisher data={data} />}
              {data && tab === 'sources' && <Sources data={data} onOpen={setDialog} />}
            </div>
            <footer className="border-t border-ink-100 bg-white px-5 py-2.5 text-[11px] text-ink-500 sm:rounded-b-2xl">
              SILO shows evidence, not verdicts. <Link to="/methodology" onClick={() => setOpen(false)} className="font-semibold text-teal-700 hover:underline">How this works</Link>
            </footer>
          </motion.section>
        )}
      </AnimatePresence>

      <button ref={fabRef} type="button" onClick={() => (open ? close() : setOpen(true))} aria-expanded={open} aria-controls="silo-context-panel"
        className={cx('fixed bottom-5 right-5 z-[61] flex items-center gap-2.5 rounded-full bg-navy py-2.5 pl-3 pr-4 text-sm font-semibold text-white shadow-lift transition hover:bg-navy-600 sm:bottom-6 sm:right-6',
          open && 'max-sm:hidden')}>
        <span className="relative flex h-8 w-8 items-center justify-center rounded-full bg-white/10">
          {open ? <X size={16} aria-hidden="true" /> : <ScanSearch size={16} aria-hidden="true" />}
          {!open && data && <span className="absolute -right-0.5 -top-0.5 h-2.5 w-2.5 rounded-full bg-amber-400 ring-2 ring-navy" aria-hidden="true" />}
        </span>
        <span>{open ? 'Close context' : 'SILO context'}</span>
        {!open && data && (
          <span className="rounded-full bg-white/15 px-2 py-0.5 text-xs tabular-nums">
            {data.coverage.state === 'scored' ? `${data.coverage.score}` : 'n/a'}<span className="sr-only"> evidence coverage</span>
          </span>
        )}
      </button>
      <SourceDialog source={dialog?.source} highlight={dialog?.highlight} onClose={() => setDialog(null)} />
    </>
  )
}

function NoSource() {
  return (
    <EmptyState icon={ScanSearch} title="Nothing selected yet"
      action={<div className="flex flex-wrap justify-center gap-2"><Link to="/" className="btn-primary">Browse articles</Link><Link to="/analyze" className="btn-secondary">Analyze text</Link></div>}>
      Open an article or analyze your own text. This panel will show the claims it makes, the records connected to them, and what context may be missing.
    </EmptyState>
  )
}

function Overview({ data, onTab }) {
  const c = data.coverage
  const rows = [
    { label: 'Checkable claims', value: c.claims_total, rel: null },
    { label: 'Supported or partly supported', value: c.claims_supported, rel: 'supports' },
    { label: 'Conflicting record found', value: c.claims_conflicting, rel: 'contradicts' },
    { label: 'Context only', value: c.claims_context_only, rel: 'provides_context' },
    { label: 'No connected record', value: c.claims_lacking_evidence, rel: 'insufficient_evidence' },
  ]
  return (
    <div className="space-y-5">
      <div className="card flex items-center gap-5 p-4">
        <CoverageGauge coverage={c} size={132} />
        <div className="min-w-0 text-sm">
          <p className="flex items-center gap-1 font-semibold text-navy">Evidence coverage
            <InfoTip label="About evidence coverage">{data.methodology.coverage} Contradicting records count toward coverage, because they make a claim checkable.</InfoTip>
          </p>
          <p className="mt-1 text-[13px] leading-relaxed text-ink-600">
            {c.state === 'scored'
              ? 'How much of this text’s checkable content is connected to records you can inspect. Not a probability that it is true.'
              : c.reason}
          </p>
        </div>
      </div>
      <ul className="divide-y divide-ink-100 rounded-2xl border border-ink-100 bg-white">
        {rows.map((r) => (
          <li key={r.label} className="flex items-center justify-between px-4 py-2.5 text-sm">
            <span className="flex items-center gap-2.5 text-ink-700">{r.rel && <span className={cx('h-2.5 w-2.5 rounded-full', RELATIONSHIP[r.rel].dot)} aria-hidden="true" />}{r.label}</span>
            <span className="font-semibold tabular-nums">{r.value}</span>
          </li>
        ))}
      </ul>
      {c.claims_conflicting > 0 && (
        <button type="button" onClick={() => onTab('evidence')} className="w-full rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-left text-sm text-amber-800 hover:bg-amber-100/60">
          <strong>{c.claims_conflicting} claim{c.claims_conflicting > 1 ? 's' : ''}</strong> {c.claims_conflicting > 1 ? 'have' : 'has'} a record that conflicts with what is stated. Review the evidence →
        </button>
      )}
      <dl className="grid grid-cols-2 gap-3 text-xs">
        <div className="rounded-xl bg-white p-3 ring-1 ring-ink-100"><dt className="flex items-center gap-1 text-ink-500"><Clock size={12} aria-hidden="true" />Last verified</dt><dd className="mt-1 font-semibold text-navy">{fmtDateTime(data.last_verified_at)}</dd></div>
        <div className="rounded-xl bg-white p-3 ring-1 ring-ink-100"><dt className="text-ink-500">Method</dt><dd className="mt-1 font-semibold text-navy">{data.methodology.version} · {data.engine}</dd></div>
      </dl>
    </div>
  )
}

function Evidence({ data, onOpen }) {
  const { focusClaim, setFocusClaim } = useContextWidget()
  const [openIdx, setOpenIdx] = useState(() => new Set(focusClaim !== null ? [focusClaim] : data.evidence.slice(0, 1).map((g) => g.sentence_index)))
  const refs = useRef({})
  useEffect(() => {
    if (focusClaim === null) return
    setOpenIdx((s) => new Set([...s, focusClaim]))
    const el = refs.current[focusClaim]
    if (el) setTimeout(() => el.scrollIntoView({ block: 'start', behavior: 'smooth' }), 60)
  }, [focusClaim])
  if (!data.evidence.length) {
    return <EmptyState icon={FileSearch} title="No checkable claims found">SILO did not find statements in this text that could be checked against a record — for example numbers, dates, votes or attributed quotes.</EmptyState>
  }
  const toggle = (i) => { setFocusClaim(null); setOpenIdx((s) => { const n = new Set(s); n.has(i) ? n.delete(i) : n.add(i); return n }) }
  return (
    <ol className="space-y-3">
      {data.evidence.map((g, n) => {
        const isOpen = openIdx.has(g.sentence_index)
        return (
          <li key={g.sentence_index} ref={(el) => { refs.current[g.sentence_index] = el }}
            className={cx('card scroll-mt-2 overflow-hidden transition-shadow', focusClaim === g.sentence_index && 'ring-2 ring-teal-400')}>
            <button type="button" onClick={() => toggle(g.sentence_index)} aria-expanded={isOpen} className="flex w-full items-start gap-3 px-4 py-3 text-left">
              <span className="mt-0.5 text-xs font-semibold tabular-nums text-ink-400">{String(n + 1).padStart(2, '0')}</span>
              <span className="min-w-0 flex-1">
                <span className="block font-serif text-[14.5px] leading-snug text-navy">{g.claim_text}</span>
                <span className="mt-2 flex flex-wrap items-center gap-1.5">
                  <RelationshipBadge rel={g.status} short />
                  <span className="rounded-full bg-ink-50 px-2 py-0.5 text-[11px] font-medium text-ink-600">{CLAIM_TYPE[g.claim_type] || 'Claim'}</span>
                  <span className="text-[11px] text-ink-400">{g.items.length} record{g.items.length === 1 ? '' : 's'}</span>
                </span>
              </span>
              <ChevronDown size={16} className={cx('mt-1 shrink-0 text-ink-400 transition-transform', isOpen && 'rotate-180')} aria-hidden="true" />
            </button>
            {isOpen && (
              <div className="space-y-3 border-t border-ink-100 bg-paper/60 px-4 py-3">
                {g.items.length === 0 && (
                  <p className="text-[13px] leading-relaxed text-ink-600"><strong className="text-navy">No connected record.</strong> This does not mean the claim is false — SILO has no record to compare it with. Look for the original data, filing or transcript.</p>
                )}
                {g.items.map((it, k) => (
                  <article key={k} className="rounded-xl bg-white p-3.5 ring-1 ring-ink-100">
                    <div className="flex flex-wrap items-center gap-2"><RelationshipBadge rel={it.relationship} /><DataStatusBadge status={it.source.data_status} /></div>
                    <h4 className="mt-2 text-[13px] font-semibold leading-snug text-navy">{it.source.title}</h4>
                    <p className="text-xs text-ink-500">{it.source.organization} · {it.source.source_type_label} · {fmtDate(it.source.record_date)}</p>
                    <blockquote className="mt-2 border-l-2 border-teal-400 pl-3 font-serif text-[13.5px] italic leading-relaxed text-navy-600">“{it.excerpt}”</blockquote>
                    <p className="mt-2 text-[13px] leading-relaxed text-ink-700"><span className="font-semibold text-navy">How SILO reached this: </span>{it.explanation}</p>
                    <div className="mt-2.5 flex flex-wrap items-center justify-between gap-2">
                      <span className="text-[11px] text-ink-400">{METHOD_LABEL[it.assessment_method] || it.assessment_method} · retrieved {fmtDate(it.retrieved_at)}</span>
                      <button type="button" className="text-xs font-semibold text-teal-700 hover:underline" onClick={() => onOpen({ source: it.source, highlight: it.excerpt })}>Inspect record →</button>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </li>
        )
      })}
    </ol>
  )
}

const GAP_ICON = { no_record: '∅', missing_time_period: '⏱', missing_baseline: '⇵', incomplete_comparison: '≈', missing_denominator: '÷', unnamed_source: '?', unattributed_quote: '“', unsupported_certainty: '!' }

function Gaps({ data }) {
  if (!data.gaps.length) return <EmptyState icon={CircleHelp} title="No context gaps detected">SILO’s rules found no missing time periods, baselines, comparisons or unnamed sources. That is not a guarantee the text is complete.</EmptyState>
  return (
    <div className="space-y-3">
      <p className="text-[13px] leading-relaxed text-ink-600">Questions worth asking before relying on this text. Each is triggered by a specific feature of the wording — not a judgement that anything was deliberately left out.</p>
      <ul className="space-y-2.5">
        {data.gaps.map((g, i) => (
          <li key={i} className="rounded-xl bg-white p-3.5 ring-1 ring-ink-100">
            <div className="flex items-center gap-2">
              <span className="flex h-6 w-6 items-center justify-center rounded-md bg-amber-50 text-xs font-bold text-amber-700" aria-hidden="true">{GAP_ICON[g.type] || '?'}</span>
              <span className="text-[13px] font-semibold text-navy">{g.label}</span>
            </div>
            <p className="mt-1.5 text-[13px] text-ink-700">{g.question}</p>
            {g.sentence && <p className="mt-1.5 line-clamp-2 font-serif text-xs italic text-ink-500">“{g.sentence}”</p>}
          </li>
        ))}
      </ul>
    </div>
  )
}

export const TOPIC_COLORS = ['#14263D', '#317F86', '#D6A34A', '#536579', '#4A979D', '#7F95B3', '#B98A34', '#A3AFBD', '#205358', '#C9D1DB']

function Topics({ data }) {
  const dist = data.topics.distribution
  const [sel, setSel] = useState(dist[0]?.topic)
  const sentences = useMemo(() => data.topics.sentences.filter((s) => s.topic === sel), [data, sel])
  const chart = dist.map((d) => ({ ...d, pct: Math.round(d.share * 1000) / 10 }))
  return (
    <div className="space-y-4">
      <p className="rounded-xl bg-navy-50 px-3.5 py-2.5 text-[12.5px] leading-relaxed text-navy-600"><strong>Narrative focus</strong> shows how much of the text discusses each subject. {data.topics.note.split('. ')[1]}</p>
      <div className="h-[220px]" aria-label="Topic share chart" role="img">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chart} layout="vertical" margin={{ left: 0, right: 24, top: 4, bottom: 4 }}>
            <XAxis type="number" domain={[0, 100]} tickFormatter={(v) => `${v}%`} tick={{ fontSize: 11, fill: '#536579' }} axisLine={false} tickLine={false} />
            <YAxis type="category" dataKey="topic" width={128} tick={{ fontSize: 11.5, fill: '#14263D' }} axisLine={false} tickLine={false} />
            <Tooltip cursor={{ fill: '#EEF2F7' }} formatter={(v) => [`${v}% of words`, 'Share']} contentStyle={{ borderRadius: 12, border: '1px solid #E4E8EE', fontSize: 12 }} />
            <Bar dataKey="pct" radius={[0, 6, 6, 0]} onClick={(d) => setSel(d.topic)} cursor="pointer" barSize={18}>
              {chart.map((d, i) => <Cell key={d.topic} fill={TOPIC_COLORS[i % TOPIC_COLORS.length]} opacity={sel && sel !== d.topic ? 0.45 : 1} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div>
        <label htmlFor="topic-pick" className="eyebrow">Inspect classifications</label>
        <select id="topic-pick" className="input mt-1.5" value={sel} onChange={(e) => setSel(e.target.value)}>
          {dist.map((d) => <option key={d.topic} value={d.topic}>{d.topic} — {fmtPct(d.share)} ({d.sentence_count} sentence{d.sentence_count > 1 ? 's' : ''})</option>)}
        </select>
        <ul className="mt-3 space-y-2">
          {sentences.map((s) => (
            <li key={s.sentence_index} className="rounded-xl bg-white p-3 text-[13px] ring-1 ring-ink-100">
              <p className="font-serif leading-relaxed text-navy-700">{s.text}</p>
              <p className="mt-1.5 text-[11px] text-ink-500">Matched keywords: {s.matched_keywords.length ? s.matched_keywords.join(', ') : 'none (assigned to Other)'}</p>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

const REL_TYPE = { owner: 'Owner', parent: 'Parent organization', political_spending: 'Political spending', editorial_control: 'Editorial control', grant: 'Grant', funder: 'Funding', board: 'Governance' }

function Publisher({ data }) {
  const p = data.publisher
  if (!p) {
    return <EmptyState icon={Building2} title="Publisher not identified">This text was submitted directly, so SILO cannot link it to a publisher, owner or funding record.</EmptyState>
  }
  const chain = [p.name, p.legal_entity, p.parent_organization].filter(Boolean)
  return (
    <div className="space-y-4">
      <div className="card p-4">
        <div className="flex items-center justify-between gap-2"><h3 className="font-semibold">{p.name}</h3><DataStatusBadge status={p.data_status} /></div>
        <p className="mt-1 text-[13px] text-ink-600">{p.description}</p>
        <p className="mt-2 inline-flex rounded-full bg-ink-50 px-2.5 py-0.5 text-xs font-semibold capitalize text-ink-700">{p.ownership_type}</p>
      </div>
      <div>
        <p className="eyebrow mb-2 flex items-center gap-1.5"><Network size={12} aria-hidden="true" />Ownership lineage</p>
        <ol className="flex flex-col gap-1.5">
          {chain.map((c, i) => (
            <li key={c} className="flex items-center gap-2 text-[13px]">
              <span className={cx('flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-[11px] font-bold', i === 0 ? 'bg-navy text-white' : 'bg-ink-100 text-ink-600')}>{i + 1}</span>
              <span className="font-medium text-navy">{c}</span>
              {i > 0 && <span className="text-[11px] text-ink-400">{i === 1 ? 'legal entity' : 'parent'}</span>}
            </li>
          ))}
        </ol>
      </div>
      <div>
        <p className="eyebrow mb-2">Documented relationships</p>
        <ul className="space-y-2.5">
          {p.relationships.map((r) => (
            <li key={r.id} className={cx('rounded-xl p-3.5 ring-1', r.established ? 'bg-white ring-ink-100' : 'border border-dashed border-ink-200 bg-paper ring-transparent')}>
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span className="text-[13px] font-semibold text-navy">{r.related_entity}</span>
                <span className={cx('rounded-full px-2 py-0.5 text-[11px] font-semibold', r.established ? 'bg-ink-50 text-ink-700' : 'bg-white text-ink-500 ring-1 ring-ink-200')}>
                  {r.established ? REL_TYPE[r.relationship_type] || r.relationship_type : 'Not established'}
                </span>
              </div>
              <p className="mt-1 text-[13px] leading-relaxed text-ink-700">{r.description}</p>
              <p className="mt-1.5 text-[11px] text-ink-500">
                {r.amount_usd ? <>{fmtUSD(r.amount_usd * 100)} · </> : null}
                {r.start_date ? <>{fmtDate(r.start_date)}{r.end_date ? ` – ${fmtDate(r.end_date)}` : ' – present'} · </> : null}
                Source: {r.source_label}
              </p>
            </li>
          ))}
        </ul>
      </div>
      <p className="rounded-xl bg-navy-50 px-3.5 py-2.5 text-[12.5px] leading-relaxed text-navy-600">{p.note}</p>
    </div>
  )
}

function Sources({ data, onOpen }) {
  if (!data.sources.length) return <EmptyState icon={Library} title="No records connected">No records were connected to this text.</EmptyState>
  return (
    <ul className="space-y-2.5">
      {data.sources.map((s) => (
        <li key={s.id}>
          <button type="button" onClick={() => onOpen({ source: s })} className="w-full rounded-xl bg-white p-3.5 text-left ring-1 ring-ink-100 transition hover:ring-teal-300">
            <div className="flex items-start justify-between gap-2">
              <span className="text-[13px] font-semibold leading-snug text-navy">{s.title}</span>
              <DataStatusBadge status={s.data_status} compact />
            </div>
            <p className="mt-1 text-xs text-ink-500">{s.organization} · {s.source_type_label} · {fmtDate(s.record_date)}</p>
            <p className="mt-1 font-mono text-[11px] text-ink-400">{s.record_key}</p>
          </button>
        </li>
      ))}
    </ul>
  )
}
