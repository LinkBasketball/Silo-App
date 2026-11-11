import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { Flag, Handshake, History, Landmark, Scale, Users, Zap } from 'lucide-react'
import { api } from '../services/api'
import { useApi } from '../hooks/useApi'
import { cx, DataStatusBadge, ErrorState, InfoTip, LoadingBlock, PageHeader } from '../components/ui'
import { fmtDate, fmtNum } from '../components/format'

const EVENT_ICON = { agreement: Handshake, resolution: Landmark, escalation: Zap, diplomacy: Flag, humanitarian: Users }

function Timeline({ events }) {
  const years = events.map((e) => Number(e.event_date.slice(0, 4)))
  const [min, max] = [Math.min(...years), Math.max(...years)]
  const [asOf, setAsOf] = useState(max)
  useEffect(() => setAsOf(max), [max])
  const visible = events.filter((e) => Number(e.event_date.slice(0, 4)) <= asOf)
  const latest = visible[visible.length - 1]
  return (
    <section className="card p-5 sm:p-6" aria-labelledby="timeline">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div><h2 id="timeline" className="flex items-center gap-2 font-serif text-xl font-semibold"><History size={18} className="text-teal-600" aria-hidden="true" />Verified timeline</h2>
          <p className="text-xs text-ink-500">Move the slider to see what was on the record at any point in time.</p></div>
        <div className="w-full sm:w-72">
          <label htmlFor="asof" className="flex justify-between text-xs font-semibold text-ink-600"><span>Record as of</span><span className="tabular-nums text-navy">{asOf}</span></label>
          <input id="asof" type="range" min={min} max={max} value={asOf} onChange={(e) => setAsOf(Number(e.target.value))} className="mt-1.5 w-full accent-teal-600" aria-valuetext={`Year ${asOf}`} />
        </div>
      </div>
      {latest && <p className="mt-4 rounded-xl bg-paper px-4 py-3 text-[13px] text-ink-700" aria-live="polite"><strong className="text-navy">As of {asOf}:</strong> {visible.length} documented event{visible.length === 1 ? '' : 's'}; most recent — {latest.title} ({fmtDate(latest.event_date)}).</p>}
      <ol className="relative mt-6 space-y-5 border-l-2 border-ink-100 pl-6">
        {events.map((e) => {
          const Icon = EVENT_ICON[e.event_type] || Flag
          const shown = Number(e.event_date.slice(0, 4)) <= asOf
          const contested = e.evidence_category === 'contested_interpretation'
          return (
            <li key={e.id} className={cx('relative transition-opacity', !shown && 'opacity-30')} aria-hidden={!shown || undefined}>
              <span className={cx('absolute -left-[37px] flex h-6 w-6 items-center justify-center rounded-full ring-4 ring-white', contested ? 'bg-amber-100 text-amber-700' : 'bg-navy text-white')}><Icon size={12} aria-hidden="true" /></span>
              <div className="flex flex-wrap items-center gap-2">
                <time dateTime={e.event_date} className="text-xs font-semibold tabular-nums text-ink-500">{fmtDate(e.event_date)}</time>
                <span className={cx('rounded-full px-2 py-0.5 text-[10.5px] font-semibold', contested ? 'bg-amber-50 text-amber-800 ring-1 ring-amber-200' : 'bg-teal-50 text-teal-800')}>{contested ? 'Contested interpretation' : 'Documented record'}</span>
                <span className="text-[11px] capitalize text-ink-400">{e.event_type}</span>
              </div>
              <h3 className="mt-1 font-semibold">{e.title}</h3>
              <p className="mt-0.5 text-[13.5px] leading-relaxed text-ink-700">{e.description}</p>
              <p className="mt-1 text-[11px] text-ink-500">Source: {e.source_label}</p>
            </li>
          )
        })}
      </ol>
    </section>
  )
}

function MetricCard({ m }) {
  const value = m.value_low != null ? `${fmtNum(m.value_low)}–${fmtNum(m.value_high)}` : `${m.value > 0 && m.unit === 'percent' ? '+' : ''}${fmtNum(m.value)}`
  return (
    <div className="rounded-2xl border border-ink-100 bg-white p-4">
      <p className="text-[13px] font-semibold leading-snug text-navy">{m.label}</p>
      <p className="mt-2 text-2xl font-semibold tabular-nums">{value}<span className="ml-1 text-sm font-medium text-ink-500">{m.unit === 'percent' ? '%' : m.unit}</span></p>
      {m.value_low != null && <p className="text-[11px] text-ink-500">Range reported by source; central estimate {fmtNum(m.value)}</p>}
      {m.series && (
        <div className="mt-2 h-20" role="img" aria-label={`${m.label} trend: ${m.series.map((s) => `${s.period} ${s.value}`).join(', ')}`}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={m.series} margin={{ top: 4, right: 4, left: 4, bottom: 0 }}>
              <CartesianGrid vertical={false} stroke="#EEF2F7" />
              <XAxis dataKey="period" tick={{ fontSize: 9, fill: '#7A889A' }} axisLine={false} tickLine={false} interval="preserveStartEnd" />
              <YAxis hide domain={['auto', 'auto']} />
              <Tooltip contentStyle={{ borderRadius: 10, fontSize: 11 }} formatter={(v) => fmtNum(v)} />
              <Line type="monotone" dataKey="value" stroke="#317F86" strokeWidth={2} dot={{ r: 2 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
      <dl className="mt-3 space-y-1 border-t border-dashed border-ink-100 pt-2 text-[11.5px] text-ink-600">
        <div><dt className="inline font-semibold text-ink-700">Period: </dt><dd className="inline">{m.period}</dd></div>
        <div><dt className="inline font-semibold text-ink-700">Scope: </dt><dd className="inline">{m.scope}</dd></div>
        <div><dt className="inline font-semibold text-ink-700">Method: </dt><dd className="inline">{m.methodology}</dd></div>
        <div><dt className="inline font-semibold text-ink-700">Source: </dt><dd className="inline">{m.source_label}</dd></div>
      </dl>
    </div>
  )
}

function Approaches({ approaches }) {
  return (
    <section aria-labelledby="approaches">
      <h2 id="approaches" className="flex items-center gap-2 font-serif text-xl font-semibold"><Scale size={18} className="text-teal-600" aria-hidden="true" />Competing policy approaches</h2>
      <p className="mb-4 mt-1 text-sm text-ink-500">Each approach is shown in the same format. Arguments are labelled as <strong>empirical</strong> (checkable against data) or <strong>value judgements</strong> (not resolvable by data).</p>
      <div className="grid gap-5 md:grid-cols-2">
        {approaches.map((ap) => (
          <article key={ap.approach} className="card overflow-hidden">
            <h3 className="border-b border-ink-100 bg-paper px-5 py-3 font-semibold">{ap.approach}</h3>
            {['for', 'against'].map((side) => (
              <div key={side} className="px-5 py-4">
                <p className="eyebrow mb-2">{side === 'for' ? 'Arguments in favor' : 'Arguments against'}</p>
                <ul className="space-y-3">
                  {ap[side].map((a, i) => (
                    <li key={i} className="text-[13.5px]">
                      <span className={cx('mr-1.5 rounded px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wide', a.argument_type === 'empirical' ? 'bg-teal-50 text-teal-800' : 'bg-navy-50 text-navy-600')}>{a.argument_type === 'empirical' ? 'Empirical' : 'Value judgement'}</span>
                      <span className="leading-relaxed text-navy-700">{a.argument}</span>
                      <span className="mt-0.5 block text-[11px] text-ink-500">{a.evidence_note}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </article>
        ))}
      </div>
    </section>
  )
}

export default function GeopoliticsPage() {
  const { slug } = useParams()
  const nav = useNavigate()
  const list = useApi((o) => api.conflicts(o), [], { key: 'conflicts' })
  const current = slug || list.data?.items[0]?.slug
  const detail = useApi((o) => api.conflict(current, o), [current], { key: `conflict-${current}`, enabled: !!current })
  const c = detail.data
  const groups = useMemo(() => (c ? ['humanitarian', 'economic'].map((g) => ({ g, items: c.metrics.filter((m) => m.metric_group === g) })).filter((x) => x.items.length) : []), [c])

  return (
    <div>
      <PageHeader eyebrow="Geopolitical context" title="Context before conclusions">
        Timelines built from documented events, metrics with their methods and limits, and competing approaches presented in parallel. Documented records are kept separate from contested interpretations.
      </PageHeader>
      {list.error && <ErrorState error={list.error} onRetry={list.reload} />}
      {list.data && (
        <div className="mb-8 grid gap-3 sm:grid-cols-2" role="list" aria-label="Conflicts">
          {list.data.items.map((it) => (
            <button key={it.slug} role="listitem" type="button" onClick={() => nav(`/geopolitics/${it.slug}`)} aria-current={it.slug === current ? 'true' : undefined}
              className={cx('rounded-2xl border p-4 text-left transition', it.slug === current ? 'border-navy bg-navy text-white' : 'border-ink-100 bg-white hover:border-ink-300')}>
              <span className="flex items-center justify-between gap-2"><span className="font-semibold">{it.name}</span><DataStatusBadge status={it.data_status} compact /></span>
              <span className={cx('mt-1 block text-xs', it.slug === current ? 'text-navy-200' : 'text-ink-500')}>{it.region} · {it.event_count} events</span>
            </button>
          ))}
        </div>
      )}
      {detail.error && <ErrorState error={detail.error} onRetry={detail.reload} />}
      {!c && !detail.error && <LoadingBlock lines={8} />}
      {c && (
        <div className="space-y-8">
          <section className="card p-5 sm:p-6">
            <div className="flex flex-wrap items-center gap-2"><DataStatusBadge status={c.data_status} /><span className="text-xs text-ink-500">{c.region}</span></div>
            <h2 className="mt-2 font-serif text-2xl font-semibold">{c.name}</h2>
            <p className="mt-2 max-w-3xl text-[15px] leading-relaxed text-ink-700">{c.summary}</p>
            <div className="mt-4 flex flex-wrap gap-2">{c.actors.map((a) => <span key={a} className="rounded-full bg-paper-2 px-3 py-1 text-xs font-semibold text-navy-600">{a}</span>)}</div>
            <p className="mt-4 rounded-xl border border-amber-200 bg-amber-50/60 px-4 py-3 text-[12.5px] text-amber-900"><strong>Data limitations: </strong>{c.limitations}</p>
          </section>
          <Timeline events={c.events} />
          {groups.map(({ g, items }) => (
            <section key={g} aria-labelledby={`m-${g}`}>
              <h2 id={`m-${g}`} className="mb-1 flex items-center gap-1.5 font-serif text-xl font-semibold capitalize">{g} indicators
                <InfoTip label="Why figures are not combined">Estimates from different sources use different definitions, periods and areas. SILO shows each separately instead of adding them into a misleading total.</InfoTip></h2>
              <p className="mb-4 text-sm text-ink-500">Each figure is shown with its period, scope and method. Estimates from different sources are never added together.</p>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">{items.map((m) => <MetricCard key={m.id} m={m} />)}</div>
            </section>
          ))}
          <Approaches approaches={c.approaches} />
        </div>
      )}
    </div>
  )
}
