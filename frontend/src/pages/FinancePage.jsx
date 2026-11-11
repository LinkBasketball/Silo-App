import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { ArrowRight, ChevronLeft, ChevronRight, Coins, Loader2, MessageSquareQuote, ScanSearch } from 'lucide-react'
import { api } from '../services/api'
import { useApi } from '../hooks/useApi'
import AnalysisPanels from '../components/AnalysisPanels'
import { cx, DataStatusBadge, ErrorState, InfoTip, LoadingBlock, PageHeader, Tabs } from '../components/ui'
import { fmtDate, fmtUSD } from '../components/format'
import { SAMPLES } from './AnalyzePage'

const SERIES = ['#14263D', '#317F86', '#A3AFBD']
const CAT_COLORS = { individual_itemized: '#14263D', individual_unitemized: '#4C6589', pac: '#317F86', party: '#D6A34A', candidate_self: '#A3AFBD' }

function MoneyTab() {
  const [period, setPeriod] = useState('')
  const [page, setPage] = useState(1)
  const { data, loading, error, reload } = useApi((o) => api.finance({ period, page, page_size: 15 }, o), [period, page], { key: `fin-${period}-${page}` })
  const byPeriod = useMemo(() => {
    if (!data) return []
    const periods = data.summaries[0]?.by_period.map((p) => p.period) || []
    return periods.map((p) => Object.fromEntries([['period', p], ...data.summaries.map((s) => [s.candidate.name, (s.by_period.find((x) => x.period === p)?.direct_cents || 0) / 100])]))
  }, [data])
  const outside = useMemo(() => (data ? data.summaries.map((s) => ({ name: s.candidate.name, Supporting: s.outside_support_cents / 100, Opposing: s.outside_oppose_cents / 100 })) : []), [data])
  const maxFlow = data ? Math.max(...data.relationships.map((r) => r.amount_cents), 1) : 1

  if (error) return <ErrorState error={error} onRetry={reload} title="Finance ledger could not be loaded" />
  if (!data) return <LoadingBlock lines={8} />
  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap gap-2" role="group" aria-label="Reporting period">
          {['', ...data.periods].map((p) => (
            <button key={p || 'all'} type="button" aria-pressed={period === p} onClick={() => { setPeriod(p); setPage(1) }}
              className={cx('rounded-full border px-3 py-1.5 text-xs font-semibold', period === p ? 'border-navy bg-navy text-white' : 'border-ink-200 bg-white text-ink-600 hover:border-ink-300')}>
              {p || 'All periods'}
            </button>
          ))}
        </div>
        <p className="flex items-center gap-2 text-xs text-ink-500"><DataStatusBadge status={data.data_status} />Filings as of {fmtDate(data.freshness.as_of)}{loading && <Loader2 size={13} className="animate-spin" aria-label="Updating" />}</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {data.summaries.map((s) => (
          <div key={s.candidate.id} className="card p-5">
            <div className="flex items-baseline justify-between"><h3 className="font-serif text-lg font-semibold">{s.candidate.name}</h3><span className="text-xs text-ink-500">{s.candidate.party}</span></div>
            <p className="mt-3 text-xs font-medium text-ink-500">Received by the campaign</p>
            <p className="text-2xl font-semibold tabular-nums">{fmtUSD(s.direct_receipts_cents)}</p>
            <div className="mt-3 flex h-2.5 overflow-hidden rounded-full bg-ink-100" role="img" aria-label={`Receipts by source: ${s.receipts_by_category.map((c) => `${c.label} ${fmtUSD(c.amount_cents)}`).join(', ')}`}>
              {s.receipts_by_category.map((c) => <span key={c.category} style={{ width: `${(100 * c.amount_cents) / (s.direct_receipts_cents || 1)}%`, background: CAT_COLORS[c.category] }} />)}
            </div>
            <ul className="mt-2.5 space-y-1 text-[12px]">
              {s.receipts_by_category.map((c) => <li key={c.category} className="flex items-center justify-between gap-2"><span className="flex items-center gap-1.5 text-ink-600"><span className="h-2 w-2 rounded-sm" style={{ background: CAT_COLORS[c.category] }} aria-hidden="true" />{c.label}</span><span className="tabular-nums">{fmtUSD(c.amount_cents, true)}</span></li>)}
            </ul>
            <div className="mt-4 border-t border-dashed border-ink-200 pt-3 text-[12px]">
              <p className="flex items-center gap-1 font-medium text-ink-500">Outside spending (not received by campaign)<InfoTip label="About outside spending">{data.definitions.independent_expenditure}</InfoTip></p>
              <div className="mt-1 flex justify-between"><span className="text-ink-600">Supporting</span><span className="font-semibold tabular-nums">{fmtUSD(s.outside_support_cents)}</span></div>
              <div className="flex justify-between"><span className="text-ink-600">Opposing</span><span className="font-semibold tabular-nums">{fmtUSD(s.outside_oppose_cents)}</span></div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <figure className="card p-5">
          <figcaption className="mb-3"><span className="font-semibold">Campaign receipts by reporting period</span><span className="block text-xs text-ink-500">Direct contributions and committee transfers only</span></figcaption>
          <div className="h-64"><ResponsiveContainer width="100%" height="100%">
            <BarChart data={byPeriod} margin={{ left: 8, right: 8 }}>
              <CartesianGrid vertical={false} stroke="#E4E8EE" />
              <XAxis dataKey="period" tick={{ fontSize: 12, fill: '#536579' }} axisLine={false} tickLine={false} />
              <YAxis tickFormatter={(v) => `$${v / 1000}k`} tick={{ fontSize: 11, fill: '#536579' }} axisLine={false} tickLine={false} width={56} />
              <Tooltip formatter={(v) => fmtUSD(v * 100)} contentStyle={{ borderRadius: 12, fontSize: 12 }} cursor={{ fill: '#EEF2F7' }} />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              {data.summaries.map((s, i) => <Bar key={s.candidate.id} dataKey={s.candidate.name} fill={SERIES[i % SERIES.length]} radius={[4, 4, 0, 0]} />)}
            </BarChart>
          </ResponsiveContainer></div>
        </figure>
        <figure className="card p-5">
          <figcaption className="mb-3"><span className="font-semibold">Outside spending by target</span><span className="block text-xs text-ink-500">Independent expenditures supporting or opposing each candidate</span></figcaption>
          <div className="h-64"><ResponsiveContainer width="100%" height="100%">
            <BarChart data={outside} layout="vertical" margin={{ left: 8, right: 16 }}>
              <CartesianGrid horizontal={false} stroke="#E4E8EE" />
              <XAxis type="number" tickFormatter={(v) => `$${v / 1000}k`} tick={{ fontSize: 11, fill: '#536579' }} axisLine={false} tickLine={false} />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 12, fill: '#14263D' }} width={88} axisLine={false} tickLine={false} />
              <Tooltip formatter={(v) => fmtUSD(v * 100)} contentStyle={{ borderRadius: 12, fontSize: 12 }} cursor={{ fill: '#EEF2F7' }} />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Bar dataKey="Supporting" fill="#317F86" radius={[0, 4, 4, 0]} />
              <Bar dataKey="Opposing" fill="#D6A34A" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer></div>
        </figure>
      </div>

      <section className="card p-5" aria-labelledby="flows">
        <h2 id="flows" className="font-semibold">Documented money flows</h2>
        <p className="text-xs text-ink-500">Each line is a reported transaction type between two named committees or candidates. {data.definitions.caution}</p>
        <ul className="mt-4 space-y-2.5">
          {data.relationships.map((r, i) => (
            <li key={i} className="grid items-center gap-2 text-[13px] sm:grid-cols-[1fr_auto_1fr_150px]">
              <span className="font-medium text-navy">{r.source}</span>
              <span className="flex items-center gap-1 text-[11px] font-semibold text-ink-500"><ArrowRight size={13} aria-hidden="true" />{r.label}</span>
              <span className="font-medium text-navy">{r.target}</span>
              <span className="flex items-center gap-2"><span className="h-1.5 flex-1 rounded-full bg-ink-100"><span className={cx('block h-full rounded-full', r.support_oppose === 'oppose' ? 'bg-amber-400' : 'bg-teal-500')} style={{ width: `${(100 * r.amount_cents) / maxFlow}%` }} /></span><span className="w-16 text-right text-xs tabular-nums">{fmtUSD(r.amount_cents, true)}</span></span>
            </li>
          ))}
        </ul>
      </section>

      <section className="card overflow-hidden" aria-labelledby="ledger">
        <div className="flex flex-wrap items-end justify-between gap-2 px-5 pt-5">
          <div><h2 id="ledger" className="font-semibold">Transaction ledger</h2><p className="text-xs text-ink-500">{data.total} transactions{period ? ` in ${period}` : ''}. Aggregated rows protect contributor privacy.</p></div>
          <div className="flex items-center gap-1 text-xs">
            <button type="button" className="btn-ghost px-2 py-1" disabled={page <= 1} onClick={() => setPage((p) => p - 1)} aria-label="Previous page"><ChevronLeft size={15} /></button>
            <span className="tabular-nums">Page {page} of {Math.max(1, Math.ceil(data.total / data.page_size))}</span>
            <button type="button" className="btn-ghost px-2 py-1" disabled={page * data.page_size >= data.total} onClick={() => setPage((p) => p + 1)} aria-label="Next page"><ChevronRight size={15} /></button>
          </div>
        </div>
        <div className="mt-3 overflow-x-auto">
          <table className="w-full min-w-[760px] text-[13px]">
            <thead className="bg-paper text-left text-xs text-ink-500"><tr>
              {['Date', 'Committee', 'Type', 'Counterparty / vendor', 'Amount', 'Filing'].map((h) => <th key={h} scope="col" className="px-4 py-2 font-semibold first:pl-5">{h}</th>)}
            </tr></thead>
            <tbody className="divide-y divide-ink-100">
              {data.transactions.map((t) => (
                <tr key={t.transaction_uid} className="align-top">
                  <td className="whitespace-nowrap py-2.5 pl-5 pr-4">{fmtDate(t.transaction_date)}<span className="block text-[11px] text-ink-500">{t.reporting_period}</span></td>
                  <td className="px-4 py-2.5"><span className="font-medium">{t.committee.name}</span><span className="block text-[11px] text-ink-500">{t.committee.type}</span></td>
                  <td className="px-4 py-2.5"><span className={cx('rounded-full px-2 py-0.5 text-[11px] font-semibold', t.transaction_type === 'independent_expenditure' ? 'bg-amber-50 text-amber-800' : 'bg-ink-50 text-ink-700')}>{t.transaction_type_label}</span>
                    {t.target_candidate && <span className="mt-1 block text-[11px] text-ink-500">{t.support_oppose === 'support' ? 'Supporting' : 'Opposing'} {t.target_candidate}</span>}</td>
                  <td className="px-4 py-2.5">{t.counterparty}<span className="block text-[11px] text-ink-500">{t.counterparty_category}</span></td>
                  <td className="px-4 py-2.5 text-right font-semibold tabular-nums">{fmtUSD(t.amount_cents)}</td>
                  <td className="px-4 py-2.5 font-mono text-[11px] text-ink-500">{t.filing_id}<span className="block font-sans">filed {fmtDate(t.filed_date)}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {['direct_contribution', 'committee_transfer', 'independent_expenditure'].map((k) => (
          <div key={k} className="rounded-2xl bg-navy-50 p-4 text-[13px] leading-relaxed text-navy-700">
            <h3 className="mb-1 font-semibold capitalize">{k.replaceAll('_', ' ')}</h3>{data.definitions[k]}
          </div>
        ))}
      </section>
    </div>
  )
}

function RhetoricTab() {
  const [text, setText] = useState(SAMPLES[0].text)
  const [voice, setVoice] = useState('speech')
  const [st, setSt] = useState({ loading: false, error: null, res: null, text: '' })
  const run = async (e) => {
    e?.preventDefault()
    setSt((s) => ({ ...s, loading: true, error: null }))
    try { const res = await api.rhetoric({ text, voice }); setSt({ loading: false, error: null, res, text }) } catch (error) { setSt((s) => ({ ...s, loading: false, error })) }
  }
  return (
    <div className="space-y-6">
      <form onSubmit={run} className="card p-5">
        <label htmlFor="rh-text" className="text-sm font-semibold text-navy">Speech, statement or article text</label>
        <textarea id="rh-text" rows={6} className="input mt-2 font-serif text-[15px] leading-relaxed" value={text} onChange={(e) => setText(e.target.value)} maxLength={20000} />
        <div className="mt-3 flex flex-wrap items-center gap-2 text-xs">
          {SAMPLES.map((s) => <button key={s.label} type="button" className="rounded-full border border-ink-200 bg-white px-2.5 py-1 font-semibold text-ink-600 hover:border-teal-400" onClick={() => { setText(s.text); setVoice(s.voice) }}>{s.label}</button>)}
          <select aria-label="Text type" className="input ml-auto w-auto py-1.5 text-xs" value={voice} onChange={(e) => setVoice(e.target.value)}><option value="text">News text</option><option value="speech">Speech</option><option value="opinion">Opinion</option></select>
          <button type="submit" className="btn-primary" disabled={text.trim().length < 20 || st.loading}>{st.loading ? <Loader2 size={15} className="animate-spin" aria-hidden="true" /> : <ScanSearch size={15} aria-hidden="true" />}Scan rhetoric</button>
        </div>
      </form>
      {st.error && <ErrorState error={st.error} />}
      {st.res && <AnalysisPanels analysis={st.res} text={st.text} initial="rhetoric" />}
      {!st.res && !st.error && <p className="text-sm text-ink-500">Run a scan to see adjective-to-noun ratio, emotional-language density, statement types, a language audit and a neutral restatement. These describe style; they never judge whether a statement is true.</p>}
    </div>
  )
}

export default function FinancePage({ tab = 'money' }) {
  const nav = useNavigate()
  return (
    <div>
      <PageHeader eyebrow="Financial transparency & rhetoric" title="Follow the money. Read the language.">
        Campaign-finance records separate money received by campaigns from outside spending they do not control. The rhetoric scanner measures how a text is written, and shows how each measure is calculated.
      </PageHeader>
      <div className="mb-6"><Tabs label="Financial transparency sections" value={tab} onChange={(t) => nav(t === 'money' ? '/finance' : '/finance/rhetoric')}
        tabs={[{ id: 'money', label: 'Campaign finance', icon: Coins }, { id: 'rhetoric', label: 'Rhetoric scanner', icon: MessageSquareQuote }]} /></div>
      <div role="tabpanel" id={`panel-${tab}`} aria-labelledby={`tab-${tab}`}>{tab === 'money' ? <MoneyTab /> : <RhetoricTab />}</div>
    </div>
  )
}
