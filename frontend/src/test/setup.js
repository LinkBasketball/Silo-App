import '@testing-library/jest-dom/vitest'

// Recharts' ResponsiveContainer needs ResizeObserver in jsdom.
class RO { observe() {} unobserve() {} disconnect() {} }
globalThis.ResizeObserver = globalThis.ResizeObserver || RO
window.matchMedia = window.matchMedia || (() => ({ matches: false, addListener() {}, removeListener() {}, addEventListener() {}, removeEventListener() {} }))
window.scrollTo = window.scrollTo || (() => {})
Element.prototype.scrollIntoView = Element.prototype.scrollIntoView || (() => {})
