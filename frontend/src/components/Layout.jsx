import { useEffect, useState } from 'react'
import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { BookOpenCheck, Coins, Globe2, Menu, Newspaper, Scale, X, FlaskConical } from 'lucide-react'
import ContextWidget from './ContextWidget'
import { api } from '../services/api'
import { useApi } from '../hooks/useApi'
import { cx } from './ui'

export const NAV = [
  { to: '/', label: 'News Intelligence', icon: Newspaper, hint: 'Claims, evidence and context', end: true },
  { to: '/candidates', label: 'Candidate Comparison', icon: Scale, hint: 'Statements and votes, side by side' },
  { to: '/finance', label: 'Financial Transparency', icon: Coins, hint: 'Campaign money and rhetoric' },
  { to: '/geopolitics', label: 'Geopolitical Context', icon: Globe2, hint: 'Timelines, metrics, approaches' },
  { to: '/methodology', label: 'Methodology & Sources', icon: BookOpenCheck, hint: 'How every number is made' },
]

export function Logo({ className }) {
  return (
    <span className={cx('flex items-center gap-2.5', className)}>
      <svg width="30" height="30" viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="8" fill="#14263D" /><rect x="8" y="17" width="4" height="8" rx="1" fill="#317F86" /><rect x="14" y="12" width="4" height="13" rx="1" fill="#F7F9FC" /><rect x="20" y="7" width="4" height="18" rx="1" fill="#D6A34A" /></svg>
      <span className="leading-none">
        <span className="block font-serif text-xl font-semibold tracking-tight text-navy">SILO</span>
        <span className="block text-[10px] font-medium uppercase tracking-[0.16em] text-ink-500">Civic intelligence</span>
      </span>
    </span>
  )
}

function NavItems({ onNavigate }) {
  return (
    <ul className="space-y-1">
      {NAV.map((n) => (
        <li key={n.to}>
          <NavLink to={n.to} end={n.end} onClick={onNavigate}
            className={({ isActive }) => cx('group flex items-start gap-3 rounded-xl px-3 py-2.5 transition-colors', isActive ? 'bg-navy text-white' : 'text-navy hover:bg-white')}>
            {({ isActive }) => (<>
              <n.icon size={18} className={cx('mt-0.5 shrink-0', isActive ? 'text-amber-300' : 'text-ink-500 group-hover:text-teal-600')} aria-hidden="true" />
              <span><span className="block text-sm font-semibold">{n.label}</span><span className={cx('block text-xs', isActive ? 'text-navy-200' : 'text-ink-500')}>{n.hint}</span></span>
            </>)}
          </NavLink>
        </li>
      ))}
    </ul>
  )
}

function SystemStatus() {
  const { data, error } = useApi((o) => api.health(o), [], { key: 'health' })
  return (
    <div className="rounded-xl border border-ink-100 bg-white p-3 text-xs" aria-live="polite">
      <div className="flex items-center gap-2 font-semibold text-navy">
        <span className={cx('h-2 w-2 rounded-full', error ? 'bg-amber-400' : data ? 'bg-teal-500' : 'bg-ink-300')} aria-hidden="true" />
        {error ? 'Server unreachable' : data ? 'System operational' : 'Connecting…'}
      </div>
      {data && <p className="mt-1 text-ink-500">NLP: {data.nlp_engine}<br />Live data: {data.live_data_enabled ? 'enabled' : 'off (demo mode)'}</p>}
    </div>
  )
}

export function DemoBanner() {
  return (
    <div className="demo-stripe border-b border-amber-200 bg-amber-50 px-4 py-2 text-center text-[12.5px] text-amber-800 sm:px-8">
      <FlaskConical size={13} className="mr-1.5 inline -translate-y-px" aria-hidden="true" />
      <strong>Demonstration mode.</strong> State X, its candidates, publishers, records and the conflicts shown are fictional and illustrative. Text you paste is analyzed for real.
    </div>
  )
}

export default function Layout() {
  const [menu, setMenu] = useState(false)
  const loc = useLocation()
  useEffect(() => { setMenu(false); window.scrollTo(0, 0) }, [loc.pathname])
  return (
    <div className="min-h-screen lg:flex">
      <a href="#main" className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[80] focus:rounded-lg focus:bg-white focus:px-4 focus:py-2 focus:shadow-lift">Skip to content</a>
      <aside className="hidden w-72 shrink-0 border-r border-ink-100 bg-paper-2/60 lg:block">
        <div className="sticky top-0 flex h-screen flex-col gap-6 px-4 py-6">
          <NavLink to="/" className="px-3" aria-label="SILO home"><Logo /></NavLink>
          <nav aria-label="Primary"><NavItems /></nav>
          <div className="mt-auto space-y-3 px-1">
            <p className="px-2 font-serif text-sm italic text-ink-500">Less persuasion. More evidence.</p>
            <SystemStatus />
          </div>
        </div>
      </aside>
      <div className="min-w-0 flex-1">
        <div className="sticky top-0 z-40 flex items-center justify-between border-b border-ink-100 bg-paper/90 px-4 py-3 backdrop-blur lg:hidden">
          <NavLink to="/" aria-label="SILO home"><Logo /></NavLink>
          <button type="button" className="rounded-lg p-2 text-navy hover:bg-ink-50" aria-expanded={menu} aria-controls="mobile-nav" aria-label={menu ? 'Close menu' : 'Open menu'} onClick={() => setMenu((m) => !m)}>
            {menu ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
        {menu && (
          <nav id="mobile-nav" aria-label="Primary" className="fixed inset-x-0 top-[61px] z-40 border-b border-ink-100 bg-paper px-4 pb-5 pt-2 shadow-lift lg:hidden">
            <NavItems onNavigate={() => setMenu(false)} />
          </nav>
        )}
        <DemoBanner />
        <main id="main" className="mx-auto max-w-6xl px-4 pb-32 pt-8 sm:px-8 lg:pt-10">
          <Outlet />
        </main>
      </div>
      <ContextWidget />
    </div>
  )
}
