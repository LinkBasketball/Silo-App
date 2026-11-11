import { useEffect, useId, useRef, useState } from 'react'
import { AlertTriangle, FlaskConical, Info, Radio, RefreshCw, Database, CircleSlash, User } from 'lucide-react'

export function cx(...c) { return c.filter(Boolean).join(' ') }

const STATUS = {
  live: { label: 'Live record', icon: Radio, cls: 'bg-teal-50 text-teal-700 border-teal-200', tip: 'Fetched from an official source during this request.' },
  cached: { label: 'Cached record', icon: Database, cls: 'bg-navy-50 text-navy-600 border-navy-100', tip: 'A real record SILO fetched earlier and stored.' },
  demo: { label: 'Demo data', icon: FlaskConical, cls: 'bg-amber-50 text-amber-700 border-amber-200 demo-stripe', tip: 'Fictional, illustrative record used to demonstrate SILO. Not a real government record.' },
  unavailable: { label: 'Unavailable', icon: CircleSlash, cls: 'bg-ink-50 text-ink-600 border-ink-200', tip: 'SILO could not obtain this information.' },
  user_submitted: { label: 'Your text', icon: User, cls: 'bg-white text-ink-700 border-ink-200', tip: 'Text you provided. SILO has not verified where it came from.' },
}

export function DataStatusBadge({ status = 'demo', className, compact }) {
  const s = STATUS[status] || STATUS.unavailable
  const Icon = s.icon
  return (
    <span title={s.tip} className={cx('inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[11px] font-semibold whitespace-nowrap', s.cls, className)}>
      <Icon size={11} aria-hidden="true" />
      {compact ? null : s.label}
      <span className="sr-only">{compact ? s.label : ''}: {s.tip}</span>
    </span>
  )
}

export const RELATIONSHIP = {
  supports: { label: 'Supports', short: 'Supported', dot: 'bg-teal-500', chip: 'bg-teal-50 text-teal-700 border-teal-200', mark: 'bg-teal-100/70 decoration-teal-500' },
  partially_supports: { label: 'Partially supports', short: 'Partly supported', dot: 'bg-teal-300', chip: 'bg-teal-50/60 text-teal-700 border-teal-200 border-dashed', mark: 'bg-teal-50 decoration-teal-300' },
  contradicts: { label: 'Contradicts', short: 'Conflicting record', dot: 'bg-amber-400', chip: 'bg-amber-50 text-amber-700 border-amber-200', mark: 'bg-amber-100/80 decoration-amber-500' },
  provides_context: { label: 'Provides context', short: 'Context only', dot: 'bg-ink-400', chip: 'bg-ink-50 text-ink-700 border-ink-200', mark: 'bg-ink-100/70 decoration-ink-400' },
  insufficient_evidence: { label: 'Insufficient evidence', short: 'No record', dot: 'bg-white border border-ink-300', chip: 'bg-white text-ink-500 border-ink-200 border-dashed', mark: 'bg-transparent decoration-ink-300 decoration-dashed' },
}

export function RelationshipBadge({ rel, short }) {
  const r = RELATIONSHIP[rel] || RELATIONSHIP.insufficient_evidence
  return (
    <span className={cx('inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-[11px] font-semibold whitespace-nowrap', r.chip)}>
      <span className={cx('h-1.5 w-1.5 rounded-full', r.dot)} aria-hidden="true" />
      {short ? r.short : r.label}
    </span>
  )
}

export function InfoTip({ label = 'More information', children, side = 'top' }) {
  const [open, setOpen] = useState(false)
  const id = useId()
  return (
    <span className="relative inline-flex align-middle" onMouseEnter={() => setOpen(true)} onMouseLeave={() => setOpen(false)}>
      <button type="button" aria-label={label} aria-describedby={open ? id : undefined} onFocus={() => setOpen(true)} onBlur={() => setOpen(false)}
        onClick={() => setOpen((o) => !o)} onKeyDown={(e) => e.key === 'Escape' && setOpen(false)}
        className="rounded-full p-0.5 text-ink-400 hover:text-teal-600">
        <Info size={14} aria-hidden="true" />
      </button>
      {open && (
        <span role="tooltip" id={id} className={cx('absolute z-50 w-64 rounded-xl bg-navy px-3 py-2 text-xs font-normal normal-case tracking-normal leading-relaxed text-white shadow-lift',
          side === 'top' ? 'bottom-full mb-2 left-1/2 -translate-x-1/2' : 'top-full mt-2 left-1/2 -translate-x-1/2')}>
          {children}
        </span>
      )}
    </span>
  )
}

export function Skeleton({ className }) { return <div className={cx('animate-pulse rounded-lg bg-ink-100', className)} aria-hidden="true" /> }

export function LoadingBlock({ lines = 3, label = 'Loading' }) {
  return (
    <div role="status" aria-label={label} className="space-y-3">
      {Array.from({ length: lines }).map((_, i) => <Skeleton key={i} className={cx('h-4', i % 3 === 2 ? 'w-2/3' : 'w-full')} />)}
    </div>
  )
}

export function ErrorState({ error, onRetry, title = 'Something went wrong' }) {
  return (
    <div role="alert" className="card flex flex-col items-start gap-3 p-6 border-amber-200 bg-amber-50/40">
      <div className="flex items-center gap-2 font-semibold text-navy"><AlertTriangle size={18} className="text-amber-500" aria-hidden="true" />{title}</div>
      <p className="text-sm text-ink-600">{error?.message || 'An unexpected error occurred.'}</p>
      {onRetry && <button type="button" className="btn-secondary" onClick={onRetry}><RefreshCw size={14} aria-hidden="true" />Try again</button>}
    </div>
  )
}

export function EmptyState({ icon: Icon = Info, title, children, action }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-ink-200 bg-white/60 px-6 py-10 text-center">
      <Icon size={22} className="text-ink-400" aria-hidden="true" />
      <p className="mt-3 font-semibold text-navy">{title}</p>
      {children && <div className="mt-1 max-w-md text-sm text-ink-500">{children}</div>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  )
}

export function PageHeader({ eyebrow, title, children, actions }) {
  return (
    <header className="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
      <div className="max-w-3xl">
        {eyebrow && <p className="eyebrow mb-2">{eyebrow}</p>}
        <h1 className="font-serif text-3xl font-semibold tracking-tight md:text-[2.4rem] md:leading-tight">{title}</h1>
        {children && <div className="mt-3 text-[15px] leading-relaxed text-ink-600">{children}</div>}
      </div>
      {actions && <div className="flex shrink-0 flex-wrap gap-2">{actions}</div>}
    </header>
  )
}

export function Stat({ label, value, hint, tip }) {
  return (
    <div className="rounded-xl border border-ink-100 bg-white px-4 py-3">
      <div className="flex items-center gap-1 text-xs font-medium text-ink-500">{label}{tip && <InfoTip label={`About ${label}`}>{tip}</InfoTip>}</div>
      <div className="mt-1 text-2xl font-semibold tabular-nums text-navy">{value}</div>
      {hint && <div className="mt-0.5 text-xs text-ink-500">{hint}</div>}
    </div>
  )
}

export function Tabs({ tabs, value, onChange, label, size = 'md' }) {
  const refs = useRef({})
  const onKey = (e, i) => {
    const dir = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0
    if (!dir) return
    e.preventDefault()
    const next = tabs[(i + dir + tabs.length) % tabs.length]
    onChange(next.id)
    refs.current[next.id]?.focus()
  }
  return (
    <div role="tablist" aria-label={label} className="flex gap-1 overflow-x-auto rounded-xl bg-ink-50 p-1 [scrollbar-width:none]">
      {tabs.map((t, i) => {
        const active = t.id === value
        return (
          <button key={t.id} ref={(el) => { refs.current[t.id] = el }} role="tab" type="button" id={`tab-${t.id}`} aria-selected={active}
            aria-controls={`panel-${t.id}`} tabIndex={active ? 0 : -1} onClick={() => onChange(t.id)} onKeyDown={(e) => onKey(e, i)}
            className={cx('flex shrink-0 items-center gap-1.5 rounded-lg font-semibold transition-colors', size === 'sm' ? 'px-2.5 py-1.5 text-xs' : 'px-3.5 py-2 text-sm',
              active ? 'bg-white text-navy shadow-card' : 'text-ink-500 hover:text-navy')}>
            {t.icon && <t.icon size={size === 'sm' ? 13 : 15} aria-hidden="true" />}{t.label}
            {t.count !== undefined && <span className={cx('rounded-full px-1.5 text-[10px] tabular-nums', active ? 'bg-navy text-white' : 'bg-ink-200 text-ink-600')}>{t.count}</span>}
          </button>
        )
      })}
    </div>
  )
}

/** Accessible modal dialog: focus moves in, Escape closes, focus returns to the opener. */
export function Dialog({ open, onClose, title, children, wide }) {
  const ref = useRef(null)
  const id = useId()
  useEffect(() => {
    if (!open) return undefined
    const prev = document.activeElement
    ref.current?.focus()
    const onKey = (e) => {
      if (e.key === 'Escape') { e.stopPropagation(); onClose() }
      if (e.key === 'Tab' && ref.current) {
        const f = ref.current.querySelectorAll('a[href],button:not([disabled]),[tabindex]:not([tabindex="-1"])')
        if (!f.length) return
        const first = f[0], last = f[f.length - 1]
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus() }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus() }
      }
    }
    document.addEventListener('keydown', onKey, true)
    return () => { document.removeEventListener('keydown', onKey, true); prev?.focus?.() }
  }, [open, onClose])
  if (!open) return null
  return (
    <div className="fixed inset-0 z-[70] flex items-end justify-center bg-navy-900/40 p-0 backdrop-blur-[2px] sm:items-center sm:p-6" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <div ref={ref} role="dialog" aria-modal="true" aria-labelledby={id} tabIndex={-1}
        className={cx('max-h-[92vh] w-full overflow-y-auto rounded-t-2xl bg-white shadow-lift outline-none sm:rounded-2xl', wide ? 'sm:max-w-3xl' : 'sm:max-w-xl')}>
        <div className="sticky top-0 z-10 flex items-start justify-between gap-4 border-b border-ink-100 bg-white px-6 py-4">
          <h2 id={id} className="font-serif text-lg font-semibold leading-snug">{title}</h2>
          <button type="button" onClick={onClose} className="btn-ghost -mr-2 px-2 py-1" aria-label="Close dialog">Close</button>
        </div>
        <div className="px-6 py-5">{children}</div>
      </div>
    </div>
  )
}
