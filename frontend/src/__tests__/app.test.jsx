import { act, render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { useEffect } from 'react'
import Layout from '../components/Layout'
import { ContextWidgetProvider, useContextWidget } from '../context/ContextWidgetContext'
import CandidatesPage from '../pages/CandidatesPage'
import CoverageGauge from '../components/CoverageGauge'
import { DataStatusBadge } from '../components/ui'
import { clearApiCache } from '../hooks/useApi'
import { candidates, compare, context, mockFetch } from '../test/fixtures'

function SetArticle() {
  const { setSource } = useContextWidget()
  useEffect(() => { setSource({ kind: 'article', id: 1 }) }, [setSource])
  return <h1>Article page</h1>
}

function renderApp(path = '/', page = <SetArticle />) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <ContextWidgetProvider>
        <Routes><Route element={<Layout />}><Route path="*" element={page} /></Route></Routes>
      </ContextWidgetProvider>
    </MemoryRouter>,
  )
}

beforeEach(() => {
  clearApiCache()
  globalThis.fetch = mockFetch({ '/health': { status: 'ok', nlp_engine: 'spacy', live_data_enabled: false }, '/context-widget/1': context, '/candidates/compare': compare, '/candidates': candidates })
})

test('primary navigation lists all five modules', () => {
  renderApp()
  const nav = screen.getAllByRole('navigation', { name: 'Primary' })[0]
  for (const label of ['News Intelligence', 'Candidate Comparison', 'Financial Transparency', 'Geopolitical Context', 'Methodology & Sources']) {
    expect(within(nav).getByText(label)).toBeInTheDocument()
  }
})

test('demonstration banner is always shown', () => {
  renderApp()
  expect(screen.getByText(/Demonstration mode\./)).toBeInTheDocument()
})

test('context widget opens, shows coverage, switches tabs and closes with Escape', async () => {
  const user = userEvent.setup()
  renderApp()
  const fab = await screen.findByRole('button', { name: /SILO context/ })
  await user.click(fab)
  const panel = await screen.findByRole('dialog', { name: 'Test article' })
  expect(within(panel).getByText('Broad coverage')).toBeInTheDocument()
  expect(within(panel).getByText(/Not a probability that it is true/)).toBeInTheDocument()
  await user.click(within(panel).getByRole('tab', { name: /Evidence/ }))
  expect(within(panel).getByText('Labor survey')).toBeInTheDocument()
  expect(within(panel).getByText(/Curated demonstration annotation/)).toBeInTheDocument()
  await user.click(within(panel).getByRole('tab', { name: /Context gaps/ }))
  expect(within(panel).getByText('Who said this?')).toBeInTheDocument()
  await user.keyboard('{Escape}')
  await waitFor(() => expect(screen.queryByRole('dialog', { name: 'Test article' })).not.toBeInTheDocument())
})

test('source dialog opens from evidence and shows the record text', async () => {
  const user = userEvent.setup()
  renderApp()
  await user.click(await screen.findByRole('button', { name: /SILO context/ }))
  const panel = await screen.findByRole('dialog', { name: 'Test article' })
  await user.click(within(panel).getByRole('tab', { name: /Evidence/ }))
  await user.click(within(panel).getByRole('button', { name: /Inspect record/ }))
  const dlg = await screen.findByRole('dialog', { name: 'Labor survey' })
  expect(within(dlg).getByText(/No external link — demonstration record/)).toBeInTheDocument()
})

test('widget shows an empty state when nothing is selected', async () => {
  const user = userEvent.setup()
  renderApp('/', <h1>Nothing</h1>)
  await user.click(screen.getByRole('button', { name: /SILO context/ }))
  expect(await screen.findByText('Nothing selected yet')).toBeInTheDocument()
})

test('widget shows an error state with retry when the API fails', async () => {
  globalThis.fetch = mockFetch({ '/health': {}, '/context-widget/1': new Error('Server exploded') })
  const user = userEvent.setup()
  renderApp()
  await user.click(screen.getByRole('button', { name: /SILO context/ }))
  expect(await screen.findByText('Server exploded')).toBeInTheDocument()
  expect(screen.getByRole('button', { name: /Try again/ })).toBeInTheDocument()
})

test('gauge renders insufficient evidence instead of a number', () => {
  render(<CoverageGauge coverage={{ state: 'insufficient_evidence', score: null }} />)
  expect(screen.getByRole('img', { name: /insufficient evidence/i })).toBeInTheDocument()
  expect(screen.queryByText('0')).not.toBeInTheDocument()
})

test('data status badges describe the data', () => {
  render(<DataStatusBadge status="demo" />)
  expect(screen.getByText('Demo data')).toBeInTheDocument()
  expect(screen.getByText(/Not a real government record/)).toBeInTheDocument()
})

test('candidate columns are rendered with identical field order', async () => {
  renderApp('/candidates', <CandidatesPage />)
  const grid = await screen.findByTestId('compare-grid')
  const cols = within(grid).getAllByRole('article')
  expect(cols).toHaveLength(2)
  const terms = (el) => within(el).getAllByRole('term').map((t) => t.textContent)
  const headings = (el) => within(el).getAllByRole('heading', { level: 3 }).map((h) => h.textContent)
  expect(terms(cols[0])).toEqual(terms(cols[1]))
  expect(headings(cols[0])).toEqual(headings(cols[1]))
  expect(within(cols[0]).getAllByText(/Insufficient evidence/).length).toBe(within(cols[1]).getAllByText(/Insufficient evidence/).length)
})

test('mobile menu toggles', async () => {
  const user = userEvent.setup()
  renderApp()
  const btn = screen.getByRole('button', { name: 'Open menu' })
  await user.click(btn)
  expect(document.getElementById('mobile-nav')).toBeInTheDocument()
  await act(async () => { await user.click(screen.getByRole('button', { name: 'Close menu' })) })
  expect(document.getElementById('mobile-nav')).not.toBeInTheDocument()
})
