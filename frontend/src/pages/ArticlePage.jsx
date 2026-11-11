import { useEffect, useMemo } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, ScanSearch } from 'lucide-react'
import { api } from '../services/api'
import { useApi } from '../hooks/useApi'
import { useContextWidget } from '../context/ContextWidgetContext'
import AnalysisPanels from '../components/AnalysisPanels'
import CoverageGauge from '../components/CoverageGauge'
import { cx, DataStatusBadge, ErrorState, LoadingBlock, RELATIONSHIP, RelationshipBadge, Skeleton } from '../components/ui'
import { fmtDate } from '../components/format'

/** Split the body into paragraphs while keeping absolute character offsets for claim highlighting. */
function paragraphs(body) {
  const out = []
  const re = /\n\s*\n/g
  let start = 0, m
  while ((m = re.exec(body)) !== null) { out.push([start, m.index]); start = m.index + m[0].length }
  out.push([start, body.length])
  return out
}

function ArticleBody({ body, claims, onClaim }) {
  const paras = useMemo(() => paragraphs(body), [body])
  return (
    <div className="prose-article">
      {paras.map(([ps, pe]) => {
        const inPara = claims.filter((c) => c.start >= ps && c.start < pe).sort((a, b) => a.start - b.start)
        const parts = []
        let pos = ps
        inPara.forEach((c) => {
          if (c.start > pos) parts.push(<span key={`t${pos}`}>{body.slice(pos, c.start)}</span>)
          const r = RELATIONSHIP[c.status]
          parts.push(
            <button key={`c${c.id}`} type="button" onClick={() => onClaim(c.sentence_index)}
              className={cx('rounded-[3px] px-0.5 text-left underline decoration-2 underline-offset-[5px] transition hover:brightness-95 focus-visible:ring-offset-0', r.mark)}
              aria-label={`Claim: ${c.text}. Evidence status: ${r.label}. Open evidence.`}>
              {body.slice(c.start, c.end)}
            </button>,
          )
          pos = c.end
        })
        if (pos < pe) parts.push(<span key={`t${pos}`}>{body.slice(pos, pe)}</span>)
        return <p key={ps}>{parts}</p>
      })}
    </div>
  )
}

export default function ArticlePage() {
  const { id } = useParams()
  const { setSource, showClaim, setOpen, setTab } = useContextWidget()
  const art = useApi((o) => api.article(id, o), [id], { key: `article-${id}` })
  const ctx = useApi((o) => api.context(id, o), [id], { key: `ctx-${id}` })
  const analysis = useApi((o) => api.analyze({ article_id: Number(id) }, o), [id], { key: `analysis-${id}` })

  useEffect(() => { setSource({ kind: 'article', id: Number(id) }) }, [id, setSource])

  if (art.error) return <ErrorState error={art.error} title={art.error.status === 404 ? 'Article not found' : 'Article could not be loaded'} onRetry={art.reload} />
  if (!art.data) return <div className="max-w-3xl space-y-4"><Skeleton className="h-6 w-40" /><Skeleton className="h-12 w-full" /><LoadingBlock lines={8} /></div>
  const a = art.data
  const legend = ['supports', 'partially_supports', 'contradicts', 'provides_context', 'insufficient_evidence']
  const statusCounts = a.claims.reduce((acc, c) => ({ ...acc, [c.status]: (acc[c.status] || 0) + 1 }), {})

  return (
    <div>
      <Link to="/" className="inline-flex items-center gap-1.5 text-sm font-semibold text-ink-600 hover:text-navy"><ArrowLeft size={15} aria-hidden="true" />All articles</Link>
      <div className="mt-6 grid gap-10 lg:grid-cols-[minmax(0,1fr)_300px]">
        <article>
          <div className="flex flex-wrap items-center gap-2 text-sm text-ink-500">
            <span className="font-semibold text-navy">{a.publisher.name}</span><span aria-hidden="true">·</span>
            <time dateTime={a.published_at}>{fmtDate(a.published_at, { month: 'long', day: 'numeric', year: 'numeric' })}</time>
            {a.author && <><span aria-hidden="true">·</span><span>{a.author}</span></>}
            {a.article_type === 'opinion' && <span className="rounded-full bg-navy-50 px-2 py-0.5 text-xs font-semibold text-navy-600">Opinion</span>}
            <DataStatusBadge status={a.data_status} />
          </div>
          <h1 className="mt-4 font-serif text-3xl font-semibold leading-[1.15] tracking-tight md:text-[2.5rem]">{a.title}</h1>
          {a.dek && <p className="mt-4 text-lg leading-relaxed text-ink-600">{a.dek}</p>}
          <div className="my-8 h-px bg-ink-100" />
          <p className="mb-5 rounded-xl bg-white px-4 py-3 text-[13px] text-ink-600 ring-1 ring-ink-100">
            <ScanSearch size={14} className="mr-1.5 inline -translate-y-px text-teal-600" aria-hidden="true" />
            Underlined passages are <strong className="text-navy">checkable claims</strong>. Select one to see the record behind it.
          </p>
          <ArticleBody body={a.body} claims={a.claims} onClaim={showClaim} />
        </article>

        <aside className="space-y-5 lg:sticky lg:top-8 lg:self-start" aria-label="Evidence summary">
          <div className="card p-5">
            <p className="eyebrow">Evidence at a glance</p>
            <div className="mt-3 flex justify-center">{ctx.data ? <CoverageGauge coverage={ctx.data.coverage} /> : <Skeleton className="h-24 w-36" />}</div>
            <ul className="mt-4 space-y-1.5">
              {legend.map((k) => (
                <li key={k} className="flex items-center justify-between text-sm">
                  <RelationshipBadge rel={k} short />
                  <span className="font-semibold tabular-nums">{statusCounts[k] || 0}</span>
                </li>
              ))}
            </ul>
            <button type="button" className="btn-primary mt-5 w-full" onClick={() => { setTab('overview'); setOpen(true) }}>
              <ScanSearch size={16} aria-hidden="true" />Open SILO context
            </button>
          </div>
          {a.claims.length === 0 && (
            <div className="rounded-2xl border border-dashed border-ink-200 p-4 text-[13px] leading-relaxed text-ink-600">
              This piece is mostly opinion and policy argument. SILO found no statements specific enough to check against a record, so it does not assign a coverage score.
            </div>
          )}
        </aside>
      </div>

      <section className="mt-16" aria-labelledby="lang">
        <p className="eyebrow">Language analysis</p>
        <h2 id="lang" className="mt-1 font-serif text-2xl font-semibold">How this text is written</h2>
        <p className="mb-5 mt-1 max-w-2xl text-sm text-ink-600">Sentence types, persuasive wording and a neutral restatement. These describe the language. They do not judge accuracy.</p>
        {analysis.error && <ErrorState error={analysis.error} onRetry={analysis.reload} />}
        {!analysis.data && !analysis.error && <LoadingBlock lines={5} />}
        {analysis.data && <AnalysisPanels analysis={analysis.data.analysis} text={a.body} />}
      </section>
    </div>
  )
}
