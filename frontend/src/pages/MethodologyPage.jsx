import { useState } from 'react'
import { CheckCircle2, ExternalLink, Loader2, RefreshCw } from 'lucide-react'
import { api } from '../services/api'
import { useApi } from '../hooks/useApi'
import { cx, DataStatusBadge, ErrorState, LoadingBlock, PageHeader } from '../components/ui'

function Block({ id, title, children }) {
  return (
    <section id={id} aria-labelledby={`${id}-h`} className="card scroll-mt-6 p-5 sm:p-6">
      <h2 id={`${id}-h`} className="font-serif text-xl font-semibold">{title}</h2>
      <div className="mt-3 text-[14px] leading-relaxed text-ink-700">{children}</div>
    </section>
  )
}

function WeightTable({ rows, head }) {
  return (
    <table className="mt-2 w-full text-sm">
      <thead><tr className="text-left text-xs text-ink-500">{head.map((h) => <th key={h} scope="col" className="py-1.5 font-semibold">{h}</th>)}</tr></thead>
      <tbody className="divide-y divide-ink-100">{rows.map(([k, v]) => <tr key={k}><td className="py-1.5 capitalize">{k.replaceAll('_', ' ')}</td><td className="py-1.5 text-right font-mono tabular-nums">{v}</td></tr>)}</tbody>
    </table>
  )
}

function SourceStatus() {
  const [probe, setProbe] = useState(false)
  const { data, error, loading, reload } = useApi((o) => api.sources({ probe }, o), [probe], { key: `sources-${probe}` })
  const badge = { available: 'bg-teal-50 text-teal-800', configured: 'bg-teal-50 text-teal-800', reachable: 'bg-teal-50 text-teal-800', disabled: 'bg-ink-50 text-ink-600', not_configured: 'bg-ink-50 text-ink-600', unreachable: 'bg-amber-50 text-amber-800' }
  return (
    <Block id="sources" title="Data sources and status">
      <p>SILO separates its data providers from its analysis. Live adapters for official sources are built in, with timeouts, bounded retries and provenance, and stay off until an operator supplies an API key.</p>
      {error && <div className="mt-3"><ErrorState error={error} onRetry={reload} /></div>}
      {!data && !error && <div className="mt-3"><LoadingBlock lines={3} /></div>}
      {data && (
        <div className="mt-4 overflow-x-auto">
          <table className="w-full min-w-[560px] text-sm">
            <thead className="text-left text-xs text-ink-500"><tr><th scope="col" className="py-2 font-semibold">Source</th><th scope="col" className="py-2 font-semibold">Type</th><th scope="col" className="py-2 font-semibold">Status</th><th scope="col" className="py-2 font-semibold">Data label</th></tr></thead>
            <tbody className="divide-y divide-ink-100">
              {data.sources.map((s) => (
                <tr key={s.name}>
                  <td className="py-2.5"><span className="font-semibold text-navy">{s.name}</span>{s.docs_url && <a href={s.docs_url} target="_blank" rel="noreferrer" className="ml-1.5 inline-flex items-center gap-0.5 text-xs text-teal-700 hover:underline">docs<ExternalLink size={11} aria-hidden="true" /></a>}{s.note && <span className="block text-[11px] text-ink-500">{s.note}</span>}</td>
                  <td className="py-2.5 text-ink-600">{s.kind === 'fixture' ? 'Fixture' : 'Live adapter'}</td>
                  <td className="py-2.5"><span className={cx('rounded-full px-2 py-0.5 text-[11px] font-semibold', badge[s.status] || 'bg-ink-50')}>{s.status.replace('_', ' ')}</span></td>
                  <td className="py-2.5"><DataStatusBadge status={s.data_status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
          <button type="button" className="btn-secondary mt-4" onClick={() => (probe ? reload() : setProbe(true))} disabled={loading}>
            {loading ? <Loader2 size={14} className="animate-spin" aria-hidden="true" /> : <RefreshCw size={14} aria-hidden="true" />}Check live connections
          </button>
        </div>
      )}
    </Block>
  )
}

export default function MethodologyPage() {
  const { data: m, error, reload } = useApi((o) => api.methodology(o), [], { key: 'methodology' })
  const toc = [['principles', 'Principles'], ['labels', 'Data labels'], ['coverage', 'Evidence coverage'], ['alignment', 'Alignment index'], ['language', 'Language analysis'], ['lexicon', 'Lexicons'], ['sources', 'Sources'], ['limits', 'Limitations']]
  return (
    <div>
      <PageHeader eyebrow="Methodology & sources" title="How every number is made">
        SILO’s analysis is deterministic and rule-based, so it can be inspected. The same rules, word lists and limits apply to every person and party.
      </PageHeader>
      {error && <ErrorState error={error} onRetry={reload} />}
      {!m && !error && <LoadingBlock lines={10} />}
      {m && (
        <div className="grid gap-8 lg:grid-cols-[200px_minmax(0,1fr)]">
          <nav aria-label="On this page" className="hidden lg:block"><ul className="sticky top-8 space-y-1 text-sm">{toc.map(([id, l]) => <li key={id}><a href={`#${id}`} className="block rounded-lg px-3 py-1.5 text-ink-600 hover:bg-white hover:text-navy">{l}</a></li>)}</ul></nav>
          <div className="space-y-5">
            <Block id="principles" title="Principles">
              <ul className="space-y-2">{m.principles.map((p) => <li key={p} className="flex gap-2"><CheckCircle2 size={16} className="mt-0.5 shrink-0 text-teal-600" aria-hidden="true" />{p}</li>)}</ul>
            </Block>
            <Block id="labels" title="Data labels">
              <dl className="grid gap-3 sm:grid-cols-2">{Object.entries(m.data_statuses).map(([k, v]) => <div key={k} className="rounded-xl bg-paper p-3"><dt><DataStatusBadge status={k} /></dt><dd className="mt-1.5 text-[13px]">{v}</dd></div>)}</dl>
            </Block>
            <Block id="coverage" title="Evidence coverage score">
              <p><strong className="text-navy">Question it answers:</strong> {m.coverage_score.question}</p>
              <pre className="mt-3 overflow-x-auto rounded-xl bg-navy p-4 text-[12.5px] text-navy-50"><code>{m.coverage_score.formula}</code></pre>
              <div className="mt-4 grid gap-6 sm:grid-cols-2">
                <div><p className="eyebrow">Relationship weight</p><WeightTable head={['Relationship', 'Weight']} rows={Object.entries(m.coverage_score.relationship_weights)} /></div>
                <div><p className="eyebrow">Source quality</p><WeightTable head={['Source type', 'Weight']} rows={Object.entries(m.coverage_score.source_quality)} /></div>
              </div>
              <p className="mt-4"><strong className="text-navy">Not scored when:</strong> {m.coverage_score.insufficient_when}.</p>
              <ul className="mt-2 list-disc space-y-1 pl-5">{m.coverage_score.notes.map((n) => <li key={n}>{n}</li>)}</ul>
              <p className="mt-2 text-xs text-ink-500">Version {m.coverage_score.version}. Bands: {Object.entries(m.coverage_score.bands).map(([k, v]) => `${k} ${v}`).join(' · ')}</p>
            </Block>
            <Block id="alignment" title="Statement–vote alignment index">
              <pre className="overflow-x-auto rounded-xl bg-navy p-4 text-[12.5px] text-navy-50"><code>{m.alignment_index.formula}</code></pre>
              <p className="mt-3">Shown only with at least <strong>{m.alignment_index.minimum_comparable_pairs}</strong> comparable pairs. Excluded: {m.alignment_index.excluded.join(', ')}.</p>
              <p className="mt-2 rounded-xl bg-amber-50 px-3 py-2 text-[13px] text-amber-900">{m.alignment_index.caution}</p>
            </Block>
            <Block id="language" title="Language analysis">
              <p className="eyebrow mb-2">Sentence types</p>
              <ul className="mb-4 flex flex-wrap gap-2">{Object.values(m.sentence_classes).map((v) => <li key={v} className="rounded-full bg-ink-50 px-2.5 py-1 text-xs font-semibold text-ink-700">{v}</li>)}</ul>
              <dl className="space-y-2">
                <div><dt className="font-semibold text-navy">Adjective-to-noun ratio</dt><dd>{m.rhetoric.adjective_noun_ratio}</dd></div>
                <div><dt className="font-semibold text-navy">Emotional language density</dt><dd>{m.rhetoric.emotional_density}</dd></div>
              </dl>
              <p className="mt-3 rounded-xl bg-amber-50 px-3 py-2 text-[13px] text-amber-900">{m.rhetoric.caution}</p>
              <p className="mt-3 text-xs text-ink-500">Active NLP engine: <span className="font-mono">{m.nlp_engine}</span></p>
            </Block>
            <Block id="lexicon" title={`Lexicons (version ${m.lexicon.version})`}>
              <p>Every word list SILO uses is published here. Praise and criticism are both included, so the same rules apply whoever is described.</p>
              <div className="mt-3 space-y-2">
                {Object.entries(m.lexicon.emotional_terms).map(([k, v]) => (
                  <details key={k} className="rounded-xl bg-paper px-4 py-2.5"><summary className="cursor-pointer text-sm font-semibold capitalize text-navy">{k} <span className="font-normal text-ink-500">({v.length} terms)</span></summary><p className="mt-2 text-[13px] text-ink-600">{v.join(', ')}</p></details>
                ))}
                <details className="rounded-xl bg-paper px-4 py-2.5"><summary className="cursor-pointer text-sm font-semibold text-navy">Certainty markers & vague attribution</summary><p className="mt-2 text-[13px] text-ink-600">{m.lexicon.certainty_markers.join(', ')}</p><p className="mt-2 text-[13px] text-ink-600">{m.lexicon.vague_attribution.join(', ')}</p></details>
                <details className="rounded-xl bg-paper px-4 py-2.5"><summary className="cursor-pointer text-sm font-semibold text-navy">Topic keywords</summary>{Object.entries(m.lexicon.topics).map(([t, w]) => <p key={t} className="mt-2 text-[13px] text-ink-600"><strong className="text-navy">{t}:</strong> {w.join(', ')}</p>)}</details>
              </div>
            </Block>
            <SourceStatus />
            <Block id="limits" title="Known limitations">
              <ul className="list-disc space-y-1.5 pl-5">{m.limitations.map((l) => <li key={l}>{l}</li>)}</ul>
            </Block>
          </div>
        </div>
      )}
    </div>
  )
}
