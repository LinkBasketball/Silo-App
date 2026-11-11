import { lazy, Suspense } from 'react'
import { Route, Routes } from 'react-router-dom'
import { MotionConfig } from 'framer-motion'
import Layout from './components/Layout'
import { ContextWidgetProvider } from './context/ContextWidgetContext'
import { LoadingBlock } from './components/ui'
import NewsPage from './pages/NewsPage'

const ArticlePage = lazy(() => import('./pages/ArticlePage'))
const AnalyzePage = lazy(() => import('./pages/AnalyzePage'))
const CandidatesPage = lazy(() => import('./pages/CandidatesPage'))
const FinancePage = lazy(() => import('./pages/FinancePage'))
const GeopoliticsPage = lazy(() => import('./pages/GeopoliticsPage'))
const MethodologyPage = lazy(() => import('./pages/MethodologyPage'))
const NotFound = lazy(() => import('./pages/NotFound'))

export default function App() {
  return (
    <MotionConfig reducedMotion="user">
      <ContextWidgetProvider>
        <Suspense fallback={<div className="p-10"><LoadingBlock lines={5} /></div>}>
          <Routes>
            <Route element={<Layout />}>
              <Route index element={<NewsPage />} />
              <Route path="news/:id" element={<ArticlePage />} />
              <Route path="analyze" element={<AnalyzePage />} />
              <Route path="candidates" element={<CandidatesPage />} />
              <Route path="finance" element={<FinancePage />} />
              <Route path="finance/rhetoric" element={<FinancePage tab="rhetoric" />} />
              <Route path="geopolitics" element={<GeopoliticsPage />} />
              <Route path="geopolitics/:slug" element={<GeopoliticsPage />} />
              <Route path="methodology" element={<MethodologyPage />} />
              <Route path="*" element={<NotFound />} />
            </Route>
          </Routes>
        </Suspense>
      </ContextWidgetProvider>
    </MotionConfig>
  )
}
