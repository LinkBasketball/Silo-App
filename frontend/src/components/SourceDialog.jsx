import { ExternalLink, FileText } from 'lucide-react'
import { DataStatusBadge, Dialog } from './ui'
import { fmtDate } from './format'

/** Shows the full text of an evidence record so the reader can inspect it directly. */
export default function SourceDialog({ source, highlight, onClose }) {
  if (!source) return null
  const content = source.content || ''
  const idx = highlight ? content.indexOf(highlight) : -1
  return (
    <Dialog open={!!source} onClose={onClose} title={source.title} wide>
      <div className="flex flex-wrap items-center gap-2 text-xs text-ink-500">
        <DataStatusBadge status={source.data_status} />
        <span className="rounded-full bg-ink-50 px-2 py-0.5 font-semibold text-ink-600">{source.source_type_label}</span>
        <span>{source.organization}</span>
        <span aria-hidden="true">·</span>
        <span>Record date {fmtDate(source.record_date)}</span>
      </div>
      <dl className="mt-4 grid grid-cols-1 gap-3 rounded-xl bg-paper p-4 text-sm sm:grid-cols-2">
        <div><dt className="text-xs text-ink-500">Record identifier</dt><dd className="font-mono text-[13px]">{source.record_key}</dd></div>
        <div><dt className="text-xs text-ink-500">Original location</dt><dd>{source.url
          ? <a className="inline-flex items-center gap-1 font-semibold text-teal-700 underline-offset-2 hover:underline" href={source.url} target="_blank" rel="noreferrer">Open original <ExternalLink size={13} aria-hidden="true" /></a>
          : <span className="text-ink-600">No external link — demonstration record</span>}</dd></div>
      </dl>
      <figure className="mt-5">
        <figcaption className="eyebrow mb-2 flex items-center gap-1.5"><FileText size={12} aria-hidden="true" />Record text</figcaption>
        <blockquote className="rounded-xl border-l-4 border-teal-500 bg-white px-4 py-3 font-serif text-[15px] leading-relaxed text-navy-700 ring-1 ring-ink-100">
          {idx >= 0 ? (<>{content.slice(0, idx)}<mark className="rounded bg-teal-100 px-0.5 text-navy">{highlight}</mark>{content.slice(idx + highlight.length)}</>) : content}
        </blockquote>
      </figure>
      {source.data_status === 'demo' && (
        <p className="mt-4 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-xs leading-relaxed text-amber-800">
          This is a fictional record written to demonstrate how SILO connects claims to sources. It is not a real government document.
        </p>
      )}
    </Dialog>
  )
}
