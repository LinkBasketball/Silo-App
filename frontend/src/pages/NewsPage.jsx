import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowRight, FileText, ScanSearch, Search, SquareMousePointer, Newspaper } from 'lucide-react'
import { api } from '../services/api'
import { useApi } from '../hooks/useApi'
import { cx, DataStatusBadge, EmptyState, ErrorState, Skeleton } from '../components/ui'
import { fmtDate } from '../components/format'

const TOPICS = ['Economy & labor', 'Environment', 'Healthcare', 'Foreign affairs']

function CoverageMeter({ item }) {
  if (item.coverage_state !== 'scored') {
    return <span className="text-xs font-semibold text-ink-500" title="Too few checkable claims, or none connected to an assessed record">Insufficient evidence</span>
  }
  return (
    <span className="flex items-center gap-2 text-xs font-semibold text-navy" title="Evidence coverage — not a truth score">
      <span className="h-1.5 w-16 overflow-hidden rounded-full bg-ink-100" aria-hidden="true"><span className="block h-full rounded-full bg-teal-500" style={{ width: `${item.coverage_score}%` }} /></span>
      {item.coverage_score}<span className="font-normal text-ink-500">coverage</span>
    </span>
  )
}

function ArticleCard({ item, featured }) {
  return (
    <motion.article layout initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
      className={cx('card group relative flex flex-col p-5 transition hover:border-ink-200 hover:shadow-lift', featured && 'md:col-span-2 md:p-7')}>
      <div className="flex flex-wrap items-center gap-2 text-xs text-ink-500">
        <span className="font-semibold text-navy">{item.publisher.name}</span><span aria-hidden="true">·</span>
        <time dateTime={item.published_at}>{fmtDate(item.published_at)}</time>
        {item.article_type === 'opinion' && <span className="rounded-full bg-navy-50 px-2 py-0.5 font-semibold text-navy-600">Opinion</span>}
        <DataStatusBadge status={item.data_status} className="ml-auto" />
      </div>
      <h3 className={cx('mt-3 font-serif font-semibold leading-snug tracking-tight', featured ? 'text-2xl md:text-[1.75rem]' : 'text-lg')}>
        <Link to={`/news/${item.id}`} className="after:absolute after:inset-0 focus:outline-none">{item.title}</Link>
      </h3>
      {item.dek && <p className={cx('mt-2 text-ink-600', featured ? 'text-[15px]' : 'line-clamp-2 text-sm')}>{item.dek}</p>}
      <div className="mt-auto flex flex-wrap items-center justify-between gap-3 pt-5">
        <span className="rounded-full bg-paper-2 px-2.5 py-1 text-[11px] font-semibold text-ink-600">{item.primary_topic}</span>
        <span className="flex items-center gap-4"><span className="text-xs text-ink-500">{item.claim_count} claims</span><CoverageMeter item={item} /></span>
      </div>
    </motion.article>
  )
}

const STEPS = [
  { icon: FileText, title: 'Read a claim', body: 'Open an article or paste any text. SILO pulls out the statements that can be checked.' },
  { icon: ScanSearch, title: 'Open SILO', body: 'The context panel shows which claims connect to records, which conflict, and what is missing.' },
  { icon: SquareMousePointer, title: 'Inspect the source', body: 'Every conclusion links to the record behind it, with an explanation you can check yourself.' },
]

export default function NewsPage() {
  const [topic, setTopic] = useState('')
  const [q, setQ] = useState('')
  const [query, setQuery] = useState('')
  const { data, loading, error, reload } = useApi((o) => api.news({ topic, q: query, page_size: 20 }, o), [topic, query], { key: `news-${topic}-${query}` })

  return (
    <div>
      <section className="relative overflow-hidden rounded-3xl bg-navy px-6 py-10 text-white sm:px-10 sm:py-12">
        <div className="pointer-events-none absolute -right-20 -top-24 h-72 w-72 rounded-full bg-teal-500/20 blur-3xl" aria-hidden="true" />
        <p className="eyebrow text-navy-200">News Intelligence</p>
        <h1 className="mt-3 max-w-2xl font-serif text-3xl font-semibold leading-tight tracking-tight text-white sm:text-[2.6rem]">See the evidence behind the headline.</h1>
        <p className="mt-4 max-w-2xl text-[15.5px] leading-relaxed text-navy-100">
          SILO connects political claims to records you can inspect, flags missing context, and shows its work. It never tells you what to conclude.
        </p>
        <ol className="mt-8 grid gap-3 sm:grid-cols-3">
          {STEPS.map((s, i) => (
            <li key={s.title} className="rounded-2xl bg-white/[0.06] p-4 ring-1 ring-white/10">
              <div className="flex items-center gap-2 text-sm font-semibold"><span className="flex h-6 w-6 items-center justify-center rounded-full bg-amber-400 text-xs font-bold text-navy">{i + 1}</span>{s.title}</div>
              <p className="mt-2 text-[13px] leading-relaxed text-navy-100">{s.body}</p>
            </li>
          ))}
        </ol>
        <div className="mt-8 flex flex-wrap gap-3">
          {data?.items?.[0] && <Link to={`/news/${data.items.find((i) => i.claim_count > 0)?.id || data.items[0].id}`} className="btn bg-amber-400 text-navy hover:bg-amber-300">Try the guided example <ArrowRight size={16} aria-hidden="true" /></Link>}
          <Link to="/analyze" className="btn bg-white/10 text-white ring-1 ring-white/20 hover:bg-white/15">Analyze your own text</Link>
        </div>
      </section>

      <section className="mt-12" aria-labelledby="latest">
        <div className="mb-5 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <h2 id="latest" className="font-serif text-2xl font-semibold">Articles to examine</h2>
            <p className="mt-1 text-sm text-ink-500">Fictional articles about State X, written to exercise each kind of evidence relationship.</p>
          </div>
          <form className="flex w-full gap-2 md:w-80" role="search" onSubmit={(e) => { e.preventDefault(); setQuery(q.trim()) }}>
            <label htmlFor="news-q" className="sr-only">Search articles</label>
            <div className="relative flex-1"><Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-ink-400" aria-hidden="true" />
              <input id="news-q" className="input pl-9" placeholder="Search articles" value={q} onChange={(e) => setQ(e.target.value)} /></div>
            <button type="submit" className="btn-secondary">Search</button>
          </form>
        </div>
        <div className="mb-6 flex flex-wrap gap-2" role="group" aria-label="Filter by topic">
          {['', ...TOPICS].map((t) => (
            <button key={t || 'all'} type="button" aria-pressed={topic === t} onClick={() => setTopic(t)}
              className={cx('rounded-full border px-3 py-1.5 text-xs font-semibold transition', topic === t ? 'border-navy bg-navy text-white' : 'border-ink-200 bg-white text-ink-600 hover:border-ink-300')}>
              {t || 'All topics'}
            </button>
          ))}
        </div>
        {error && <ErrorState error={error} onRetry={reload} title="Articles could not be loaded" />}
        {loading && !data && <div className="grid gap-5 md:grid-cols-2">{[0, 1, 2, 3].map((i) => <Skeleton key={i} className={cx('h-48', i === 0 && 'md:col-span-2')} />)}</div>}
        {data && data.items.length === 0 && <EmptyState icon={Newspaper} title="No articles match" action={<button type="button" className="btn-secondary" onClick={() => { setTopic(''); setQ(''); setQuery('') }}>Clear filters</button>}>Try a different topic or search term.</EmptyState>}
        {data && data.items.length > 0 && (
          <div className="grid gap-5 md:grid-cols-2">
            {data.items.map((it, i) => <ArticleCard key={it.id} item={it} featured={i === 0 && !topic && !query} />)}
          </div>
        )}
      </section>
    </div>
  )
}
