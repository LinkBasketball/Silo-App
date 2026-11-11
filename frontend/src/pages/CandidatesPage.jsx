import { useEffect, useState } from 'react'
import { ArrowLeftRight, Info, Landmark, Quote, Vote } from 'lucide-react'
import { api } from '../services/api'
import { useApi } from '../hooks/useApi'
import { cx, DataStatusBadge, EmptyState, ErrorState, InfoTip, LoadingBlock, PageHeader } from '../components/ui'
import { fmtDate, fmtUSD } from '../components/format'

// Neutral encoding: no party colours. Classifications use shape + text, not red/green judgement.
const CLASS = {
  consistent: { cls: 'bg-teal-50 text-teal-800 ring-teal-200', mark: '●' },
  potentially_inconsistent: { cls: 'bg-amber-50 text-amber-800 ring-amber-200', mark: '◆' },
  mixed: { cls: 'bg-navy-50 text-navy-700 ring-navy-100', mark: '◐' },
  not_directly_comparable: { cls: 'bg-white text-ink-600 ring-ink-200', mark: '○' },
  insufficient_evidence: { cls: 'bg-white text-ink-500 ring-ink-200', mark: '·' },
}
const POSITION = { yea: 'Yea', nay: 'Nay', present: 'Present', not_voting: 'Not voting', no_record: 'No record' }

function Section({ title, icon: Icon, children, note }) {
  return (
    <section className="border-t border-ink-100 px-5 py-5">
      <h3 className="eyebrow mb-3 flex items-center gap-1.5">{Icon && <Icon size={12} aria-hidden="true" />}{title}</h3>
      {children}
      {note && <p className="mt-2 text-[11px] text-ink-400">{note}</p>}
    </section>
  )
}

function CandidateColumn({ c, side }) {
  const idx = c.alignment
  return (
    <article className="card flex flex-col overflow-hidden" aria-label={`${c.name} profile`}>
      <header className="px-5 pb-5 pt-5">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3">
            <span className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-navy font-serif text-2xl font-semibold text-white" aria-hidden="true">{c.name.split(' ').pop()}</span>
            <div>
              <h2 className="font-serif text-xl font-semibold">{c.name}</h2>
              <p className="text-xs text-ink-500">Column {side}</p>
            </div>
          </div>
          <DataStatusBadge status={c.data_status} />
        </div>
        <dl className="mt-4 grid grid-cols-1 gap-2 text-sm">
          {[['Office sought', c.office_sought], ['Office held', c.office_held || 'None'], ['Party', c.party], ['Jurisdiction', c.jurisdiction]].map(([k, v]) => (
            <div key={k} className="flex justify-between gap-3 border-b border-dashed border-ink-100 pb-1.5"><dt className="text-ink-500">{k}</dt><dd className="text-right font-medium text-navy">{v}</dd></div>
          ))}
        </dl>
        <p className="mt-3 text-[13px] leading-relaxed text-ink-600">{c.biography}</p>
      </header>

      <Section title="Statement–vote consistency" icon={ArrowLeftRight} note={`Comparable pairs: ${idx.comparable} · excluded: ${idx.excluded} · minimum required: ${idx.minimum}`}>
        {idx.state === 'scored' ? (
          <div className="flex items-end gap-3">
            <span className="text-4xl font-semibold tabular-nums">{idx.value}</span>
            <span className="pb-1 text-xs leading-snug text-ink-500">out of 100, from {idx.comparable} reviewed pairs.<br />Describes consistency, not honesty.</span>
          </div>
        ) : <p className="rounded-xl border border-dashed border-ink-200 px-3 py-2.5 text-[13px] text-ink-600"><strong className="text-navy">Insufficient evidence.</strong> {idx.reason}</p>}
      </Section>

      <Section title="Speech vs. vote" icon={Quote}>
        {c.speech_vs_vote.length === 0 ? <p className="text-sm text-ink-500">No statement can be compared with a recorded vote.</p> : (
          <ul className="space-y-3">
            {c.speech_vs_vote.map((x, i) => (
              <li key={i} className="rounded-xl bg-paper p-3.5 ring-1 ring-ink-100">
                <blockquote className="font-serif text-[14.5px] leading-snug text-navy">“{x.quote}”</blockquote>
                <p className="mt-1 text-[11px] text-ink-500">{x.venue} · {fmtDate(x.quote_date)}</p>
                <div className="mt-2.5 rounded-lg bg-white p-2.5 text-[12.5px] ring-1 ring-ink-100">
                  <p className="font-semibold text-navy">{x.bill.bill_number} · {x.bill.title}</p>
                  <p className="text-ink-600">{x.question} · {fmtDate(x.vote_date)} · <span className="font-mono">{x.roll_call_id}</span>{x.is_procedural && <span className="ml-1 rounded bg-ink-100 px-1 text-[10px] font-semibold">procedural</span>}</p>
                  <p className="mt-1">Recorded vote: <strong>{POSITION[x.position]}</strong></p>
                </div>
                <p className={cx('mt-2.5 inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[11px] font-semibold ring-1', CLASS[x.classification].cls)}>
                  <span aria-hidden="true">{CLASS[x.classification].mark}</span>{x.classification_label}
                </p>
                <p className="mt-1.5 text-[12.5px] leading-relaxed text-ink-700">{x.rationale}</p>
              </li>
            ))}
          </ul>
        )}
      </Section>

      <Section title="Public statements" icon={Quote} note={`Showing ${c.statements.length} of ${c.statement_total}`}>
        <ul className="space-y-2.5">
          {c.statements.map((s, i) => (
            <li key={i} className="text-[13px]">
              <p className="font-serif leading-snug text-navy">“{s.quote}”</p>
              <p className="mt-0.5 text-[11px] text-ink-500">{s.topic} · {fmtDate(s.date)} · {s.source_label}</p>
            </li>
          ))}
        </ul>
      </Section>

      <Section title="Voting record" icon={Vote} note={c.vote_total ? `Showing ${c.voting_record.length} of ${c.vote_total}` : null}>
        {c.voting_record.length === 0 ? <p className="rounded-xl border border-dashed border-ink-200 px-3 py-2.5 text-[13px] text-ink-600">{c.voting_record_note}</p> : (
          <ul className="divide-y divide-ink-100">
            {c.voting_record.map((v) => (
              <li key={v.roll_call_id} className="flex items-start justify-between gap-3 py-2 text-[13px]">
                <span><span className="font-semibold text-navy">{v.bill.title}</span><span className="block text-[11px] text-ink-500">{v.question} · {fmtDate(v.vote_date)}{v.is_procedural && ' · procedural'}</span></span>
                <span className="shrink-0 rounded-md bg-ink-50 px-2 py-0.5 text-xs font-semibold text-navy">{POSITION[v.position]}</span>
              </li>
            ))}
          </ul>
        )}
      </Section>

      <Section title="Campaign finance (demo filings)" icon={Landmark}>
        <dl className="space-y-1.5 text-[13px]">
          <div className="flex justify-between"><dt className="text-ink-600">Received by campaign</dt><dd className="font-semibold tabular-nums">{fmtUSD(c.finance.direct_receipts_cents)}</dd></div>
          <div className="flex justify-between"><dt className="flex items-center gap-1 text-ink-600">Outside spending supporting<InfoTip label="About outside spending">Independent expenditures by groups the campaign does not control. Not money given to the candidate.</InfoTip></dt><dd className="font-semibold tabular-nums">{fmtUSD(c.finance.outside_support_cents)}</dd></div>
          <div className="flex justify-between"><dt className="text-ink-600">Outside spending opposing</dt><dd className="font-semibold tabular-nums">{fmtUSD(c.finance.outside_opposition_cents)}</dd></div>
        </dl>
      </Section>

      <Section title="Sources">
        <ul className="list-disc space-y-1 pl-4 text-[11.5px] text-ink-500">{c.sources.slice(0, 6).map((s) => <li key={s}>{s}</li>)}</ul>
      </Section>
    </article>
  )
}

export default function CandidatesPage() {
  const list = useApi((o) => api.candidates(o), [], { key: 'candidates' })
  const [a, setA] = useState('candidate-a')
  const [b, setB] = useState('candidate-b')
  const cmp = useApi((o) => api.compare(a, b, o), [a, b], { key: `cmp-${a}-${b}`, enabled: a !== b })
  useEffect(() => { if (a === b) setB(list.data?.items.find((c) => c.slug !== a)?.slug || b) }, [a, b, list.data])
  const opts = list.data?.items || []

  return (
    <div>
      <PageHeader eyebrow="Candidate comparison" title="Statements and votes, side by side">
        Both columns use identical fields, order, limits and treatment of missing data. SILO does not rank candidates or tell you who to support.
      </PageHeader>
      <div className="card mb-6 grid gap-3 p-4 sm:grid-cols-[1fr_auto_1fr] sm:items-end">
        <label className="text-sm font-medium text-navy">Column A
          <select className="input mt-1.5" value={a} onChange={(e) => setA(e.target.value)}>{opts.map((c) => <option key={c.slug} value={c.slug}>{c.name} — {c.party}</option>)}</select>
        </label>
        <button type="button" className="btn-ghost justify-self-center" onClick={() => { setA(b); setB(a) }} aria-label="Swap columns"><ArrowLeftRight size={16} aria-hidden="true" />Swap</button>
        <label className="text-sm font-medium text-navy">Column B
          <select className="input mt-1.5" value={b} onChange={(e) => setB(e.target.value)}>{opts.filter((c) => c.slug !== a).map((c) => <option key={c.slug} value={c.slug}>{c.name} — {c.party}</option>)}</select>
        </label>
      </div>
      {list.error && <ErrorState error={list.error} onRetry={list.reload} />}
      {cmp.error && <ErrorState error={cmp.error} onRetry={cmp.reload} />}
      {cmp.loading && !cmp.data && <div className="grid gap-5 md:grid-cols-2"><LoadingBlock lines={10} /><LoadingBlock lines={10} /></div>}
      {cmp.data && (
        <>
          <div className="grid items-start gap-5 md:grid-cols-2" data-testid="compare-grid">
            {cmp.data.candidates.map((c, i) => <CandidateColumn key={c.slug} c={c} side={i === 0 ? 'A' : 'B'} />)}
          </div>
          <section className="card mt-6 overflow-hidden" aria-labelledby="shared">
            <h2 id="shared" className="px-5 pt-5 font-serif text-xl font-semibold">Votes cast by both</h2>
            <p className="px-5 pb-3 text-sm text-ink-500">Same roll call, both recorded positions.</p>
            {cmp.data.shared_votes.length === 0 ? <div className="p-5"><EmptyState icon={Info} title="No shared votes">At least one of these candidates has no roll-call record in the same chamber.</EmptyState></div> : (
              <div className="overflow-x-auto">
                <table className="w-full min-w-[560px] text-sm">
                  <thead className="bg-paper text-left text-xs text-ink-500"><tr><th scope="col" className="px-5 py-2 font-semibold">Bill & question</th><th scope="col" className="px-3 py-2 font-semibold">Roll call</th><th scope="col" className="px-3 py-2 font-semibold">{cmp.data.candidates[0].name}</th><th scope="col" className="px-5 py-2 font-semibold">{cmp.data.candidates[1].name}</th></tr></thead>
                  <tbody className="divide-y divide-ink-100">
                    {cmp.data.shared_votes.map((v) => (
                      <tr key={v.roll_call_id}>
                        <td className="px-5 py-2.5"><span className="font-semibold">{v.bill.title}</span><span className="block text-xs text-ink-500">{v.question}{v.is_procedural ? ' · procedural' : ''}</span></td>
                        <td className="px-3 py-2.5 font-mono text-xs">{v.roll_call_id}</td>
                        {v.positions.map((p, i) => <td key={i} className={cx('py-2.5', i ? 'px-5' : 'px-3')}><span className="rounded-md bg-ink-50 px-2 py-0.5 text-xs font-semibold">{POSITION[p]}</span></td>)}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
          <section className="mt-6 rounded-2xl bg-navy-50 p-5 text-[13px] leading-relaxed text-navy-700">
            <h2 className="mb-2 font-semibold">How comparisons are made</h2>
            <ul className="list-disc space-y-1 pl-5">
              <li>{cmp.data.methodology.classification}</li><li>{cmp.data.methodology.index}</li><li>{cmp.data.methodology.symmetry}</li>
            </ul>
          </section>
        </>
      )}
    </div>
  )
}
