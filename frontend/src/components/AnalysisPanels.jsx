import { useMemo, useState } from 'react'
import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { CheckCircle2, ShieldCheck } from 'lucide-react'
import { cx, InfoTip, Tabs } from './ui'
import { fmtNum } from './format'

export const CLASS_STYLE = {
  checkable_fact: { label: 'Checkable fact', color: '#317F86', cls: 'border-teal-500 bg-teal-50/50' },
  opinion: { label: 'Opinion', color: '#D6A34A', cls: 'border-amber-400 bg-amber-50/50' },
  prediction: { label: 'Prediction / commitment', color: '#7F95B3', cls: 'border-navy-300 bg-navy-50/60' },
  normative: { label: 'Policy preference', color: '#14263D', cls: 'border-navy bg-navy-50/40' },
  mixed: { label: 'Mixed', color: '#536579', cls: 'border-ink-400 bg-ink-50' },
  ambiguous: { label: 'Ambiguous', color: '#A3AFBD', cls: 'border-ink-200 bg-white' },
}
const AUDIT = {
  loaded_language: { label: 'Loaded language', cls: 'bg-amber-100 decoration-amber-500' },
  unsupported_certainty: { label: 'Unsupported certainty', cls: 'bg-navy-100 decoration-navy-400' },
  vague_attribution: { label: 'Vague attribution', cls: 'bg-ink-100 decoration-ink-500' },
  unattributed_allegation: { label: 'Unattributed allegation', cls: 'bg-amber-200 decoration-amber-700' },
}

export function RhetoricMetrics({ rhetoric }) {
  const r = rhetoric
  const fact = r.sentence_distribution.find((d) => d.sentence_class === 'checkable_fact')
  const chart = r.sentence_distribution.filter((d) => d.count > 0).map((d) => ({ ...d, name: CLASS_STYLE[d.sentence_class].label, pct: Math.round(d.share * 100) }))
  const cats = Object.entries(r.emotional_by_category)
  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        <Metric label="Adjective-to-noun ratio" value={r.adjective_noun_ratio ?? '—'} hint={`${r.adjective_count} adj. / ${r.noun_count} nouns`}
          tip="Adjectives ÷ (nouns + proper nouns), counted by the part-of-speech tagger. Higher values mean more descriptive modifiers per thing named. It does not measure accuracy." />
        <Metric label="Emotional language" value={r.emotional_per_100_words ?? '—'} hint="matches per 100 words"
          tip="Words matching SILO's published emotional-language lexicon (fear, anger, contempt, praise, urgency), per 100 words. Emotional language is not evidence of falsehood." />
        <Metric label="Checkable statements" value={fact ? `${Math.round(fact.share * 100)}%` : '—'} hint={`${fact?.count ?? 0} of ${r.sentence_count} sentences`}
          tip="Share of sentences containing something that could be checked against a record: a number, date, recorded action or attributed quote. Checkable does not mean correct." />
        <Metric label="Words analyzed" value={fmtNum(r.token_count)} hint={r.engine} tip="Alphabetic tokens counted by the active NLP engine." />
      </div>
      <div className="grid gap-5 md:grid-cols-5">
        <div className="md:col-span-3">
          <p className="eyebrow mb-2">Sentence types</p>
          <div className="h-[200px]" role="img" aria-label="Sentence type distribution">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chart} layout="vertical" margin={{ left: 0, right: 30 }}>
                <XAxis type="number" domain={[0, 100]} hide />
                <YAxis type="category" dataKey="name" width={150} tick={{ fontSize: 12, fill: '#14263D' }} axisLine={false} tickLine={false} />
                <Tooltip cursor={{ fill: '#EEF2F7' }} formatter={(v, _n, p) => [`${v}% (${p.payload.count})`, 'Sentences']} contentStyle={{ borderRadius: 12, fontSize: 12 }} />
                <Bar dataKey="pct" radius={[0, 6, 6, 0]} barSize={16} label={{ position: 'right', fontSize: 11, fill: '#536579', formatter: (v) => `${v}%` }}>
                  {chart.map((d) => <Cell key={d.sentence_class} fill={CLASS_STYLE[d.sentence_class].color} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="md:col-span-2">
          <p className="eyebrow mb-2">Emotional terms found</p>
          {r.emotional_terms.length === 0 ? <p className="text-sm text-ink-500">None from the lexicon.</p> : (
            <>
              <div className="mb-3 flex flex-wrap gap-1.5">{cats.map(([k, v]) => <span key={k} className="rounded-full bg-ink-50 px-2 py-0.5 text-[11px] font-semibold capitalize text-ink-600">{k} · {v}</span>)}</div>
              <ul className="flex flex-wrap gap-1.5">
                {r.emotional_terms.map((t) => <li key={t.term} className="rounded-lg bg-amber-50 px-2 py-1 text-xs text-amber-800 ring-1 ring-amber-200">{t.term}{t.count > 1 ? ` ×${t.count}` : ''}</li>)}
              </ul>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

function Metric({ label, value, hint, tip }) {
  return (
    <div className="rounded-xl border border-ink-100 bg-white px-4 py-3">
      <div className="flex items-center gap-1 text-xs font-medium text-ink-500">{label}<InfoTip label={`About ${label}`}>{tip}</InfoTip></div>
      <div className="mt-1 text-2xl font-semibold tabular-nums">{value}</div>
      <div className="mt-0.5 truncate text-[11px] text-ink-500">{hint}</div>
    </div>
  )
}

export function SentenceList({ sentences }) {
  const [filter, setFilter] = useState('all')
  const shown = filter === 'all' ? sentences : sentences.filter((s) => s.sentence_class === filter)
  const classes = [...new Set(sentences.map((s) => s.sentence_class))]
  return (
    <div>
      <div className="mb-3 flex flex-wrap gap-1.5" role="group" aria-label="Filter sentences by type">
        {['all', ...classes].map((c) => (
          <button key={c} type="button" aria-pressed={filter === c} onClick={() => setFilter(c)}
            className={cx('rounded-full border px-2.5 py-1 text-xs font-semibold', filter === c ? 'border-navy bg-navy text-white' : 'border-ink-200 bg-white text-ink-600 hover:border-ink-300')}>
            {c === 'all' ? `All (${sentences.length})` : `${CLASS_STYLE[c].label} (${sentences.filter((s) => s.sentence_class === c).length})`}
          </button>
        ))}
      </div>
      <ol className="space-y-2">
        {shown.map((s) => (
          <li key={s.index} className={cx('rounded-r-xl border-l-4 px-4 py-2.5', CLASS_STYLE[s.sentence_class].cls)}>
            <p className="font-serif text-[15px] leading-relaxed text-navy">{s.text}</p>
            <p className="mt-1 text-[11.5px] text-ink-600"><span className="font-semibold text-navy">{s.label}</span>{s.reasons.length > 0 && <> — {s.reasons.join('; ')}</>}</p>
          </li>
        ))}
      </ol>
    </div>
  )
}

export function AuditedText({ text, findings }) {
  const parts = useMemo(() => {
    const out = []
    let pos = 0
    ;[...findings].sort((a, b) => a.start - b.start).forEach((f, i) => {
      if (f.start < pos) return
      if (f.start > pos) out.push({ t: text.slice(pos, f.start) })
      out.push({ t: text.slice(f.start, f.end), f, i })
      pos = f.end
    })
    out.push({ t: text.slice(pos) })
    return out
  }, [text, findings])
  return (
    <p className="whitespace-pre-line font-serif text-[15.5px] leading-[1.9] text-navy-700">
      {parts.map((p, k) => p.f
        ? <mark key={k} title={`${AUDIT[p.f.type].label}: ${p.f.explanation}`} className={cx('rounded px-0.5 text-navy underline decoration-2 underline-offset-4', AUDIT[p.f.type].cls)}>{p.t}</mark>
        : <span key={k}>{p.t}</span>)}
    </p>
  )
}

export function LanguageAudit({ text, findings }) {
  const counts = findings.reduce((a, f) => ({ ...a, [f.type]: (a[f.type] || 0) + 1 }), {})
  return (
    <div className="grid gap-6 lg:grid-cols-5">
      <div className="lg:col-span-3">
        <div className="mb-3 flex flex-wrap gap-2 text-[11px]">
          {Object.entries(AUDIT).map(([k, v]) => <span key={k} className={cx('rounded px-1.5 py-0.5 font-semibold text-navy underline decoration-2 underline-offset-2', v.cls)}>{v.label} · {counts[k] || 0}</span>)}
        </div>
        <div className="rounded-2xl border border-ink-100 bg-white p-5"><AuditedText text={text} findings={findings} /></div>
        <p className="mt-2 text-xs text-ink-500">The original text is shown exactly as submitted. Highlights flag wording; they do not change it.</p>
      </div>
      <ul className="space-y-2 lg:col-span-2" aria-label="Language findings">
        {findings.length === 0 && <li className="text-sm text-ink-500">No loaded terms, certainty markers or vague attributions found.</li>}
        {findings.map((f, i) => (
          <li key={i} className="rounded-xl bg-white p-3 ring-1 ring-ink-100">
            <div className="flex items-center justify-between gap-2"><span className="text-[13px] font-semibold text-navy">“{f.term}”</span><span className="text-[11px] font-semibold text-ink-500">{AUDIT[f.type].label}</span></div>
            <p className="mt-1 text-xs leading-relaxed text-ink-600">{f.explanation}</p>
          </li>
        ))}
      </ul>
    </div>
  )
}

export function NeutralSummary({ summary }) {
  const ok = summary.integrity.passed
  return (
    <div className="space-y-4">
      <div className={cx('flex flex-wrap items-center gap-x-4 gap-y-1 rounded-xl px-4 py-3 text-[13px]', ok ? 'bg-teal-50 text-teal-800' : 'bg-amber-50 text-amber-800')}>
        <span className="flex items-center gap-1.5 font-semibold"><ShieldCheck size={15} aria-hidden="true" />Output guardrails {ok ? 'passed' : 'flagged an issue'}</span>
        <span className="flex items-center gap-1"><CheckCircle2 size={13} aria-hidden="true" />{summary.integrity.quotes_checked} quotation{summary.integrity.quotes_checked === 1 ? '' : 's'} verified verbatim</span>
        <span className="flex items-center gap-1"><CheckCircle2 size={13} aria-hidden="true" />No endorsement language introduced</span>
      </div>
      <div className="hidden grid-cols-2 gap-4 px-1 text-[11px] font-semibold uppercase tracking-wider text-ink-500 md:grid"><span>Original (unchanged)</span><span>Neutral restatement</span></div>
      <ol className="space-y-2.5">
        {summary.items.map((it) => (
          <li key={it.sentence_index} className="grid gap-2 rounded-2xl border border-ink-100 bg-white p-4 md:grid-cols-2 md:gap-5">
            <p className="font-serif text-[14.5px] leading-relaxed text-ink-700"><span className="mr-1 text-[10px] font-semibold uppercase text-ink-400 md:hidden">Original · </span>{it.original}</p>
            <div>
              <p className="text-[14.5px] leading-relaxed text-navy"><span className="mr-1 text-[10px] font-semibold uppercase text-ink-400 md:hidden">Neutral · </span>{it.neutral}</p>
              <p className="mt-1.5 text-[11px] text-ink-500">{it.transformation}</p>
            </div>
          </li>
        ))}
      </ol>
      {summary.items.length === 0 && <p className="text-sm text-ink-500">No sentences required restatement.</p>}
    </div>
  )
}

export default function AnalysisPanels({ analysis, text, initial = 'sentences' }) {
  const [tab, setTab] = useState(initial)
  const tabs = [
    { id: 'sentences', label: 'Statement types', count: analysis.sentences.length },
    { id: 'audit', label: 'Language audit', count: analysis.language_audit.length },
    { id: 'neutral', label: 'Neutral summary' },
    { id: 'rhetoric', label: 'Rhetoric metrics' },
  ]
  return (
    <div>
      <Tabs tabs={tabs} value={tab} onChange={setTab} label="Analysis views" />
      <div className="mt-5" role="tabpanel" id={`panel-${tab}`} aria-labelledby={`tab-${tab}`}>
        {tab === 'sentences' && <SentenceList sentences={analysis.sentences} />}
        {tab === 'audit' && <LanguageAudit text={text} findings={analysis.language_audit} />}
        {tab === 'neutral' && <NeutralSummary summary={analysis.neutral_summary} />}
        {tab === 'rhetoric' && <RhetoricMetrics rhetoric={analysis.rhetoric} />}
      </div>
    </div>
  )
}
