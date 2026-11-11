export const context = {
  article_id: 1, title: 'Test article', subtitle: 'Pub · Oct 1, 2026', data_status: 'demo', last_verified_at: '2026-11-01T12:00:00Z', engine: 'spacy',
  coverage: { state: 'scored', score: 80, band: 'Broad coverage', reason: null, version: 'coverage-v1', claims_total: 2, claims_supported: 1, claims_conflicting: 1, claims_context_only: 0, claims_lacking_evidence: 0 },
  evidence: [{ sentence_index: 0, claim_text: 'Jobs rose 4 percent in 2026.', claim_type: 'statistical', sentence_class: 'checkable_fact', topic: 'Economy & labor', status: 'supports',
    items: [{ relationship: 'supports', relationship_label: 'Supports', excerpt: 'Jobs rose 4.0 percent.', explanation: 'Matches the survey.', assessment_method: 'curated_demo_annotation', retrieved_at: '2026-11-01T12:00:00Z',
      source: { id: 9, record_key: 'DEMO-1', title: 'Labor survey', organization: 'Dept of Labor', source_type: 'official_statistic', source_type_label: 'Official statistic', record_date: '2026-10-01', url: null, content: 'Jobs rose 4.0 percent.', data_status: 'demo' } }] }],
  gaps: [{ type: 'unnamed_source', label: 'Unnamed source', question: 'Who said this?', sentence_index: 1, sentence: 'Experts say so.' }],
  topics: { distribution: [{ topic: 'Economy & labor', share: 1, sentence_count: 2 }], sentences: [], note: 'Topic share. It is not a measure of political bias or accuracy.' },
  publisher: null, sources: [], methodology: { coverage: 'Coverage explanation.', version: 'coverage-v1' },
}

const profile = (name, party, votes = true) => ({
  id: name.length, slug: name.toLowerCase().replace(' ', '-'), name, office_sought: 'Governor of State X', office_held: votes ? 'State Senator' : null,
  jurisdiction: 'State X', party, biography: 'Fictional.', data_status: 'demo', statements: [], statement_total: 0,
  voting_record: [], vote_total: 0, voting_record_note: votes ? null : 'No roll-call voting record.', speech_vs_vote: [],
  alignment: { state: 'insufficient_evidence', value: null, comparable: 0, excluded: 0, minimum: 4, reason: 'Not enough pairs.' },
  finance: { direct_receipts_cents: 100, outside_support_cents: 0, outside_opposition_cents: 0, committees: [] }, sources: [],
})
export const compare = { candidates: [profile('Candidate A', 'Harbor Party'), profile('Candidate B', 'Summit Party')], shared_votes: [], limits: { statements: 6, votes: 8, comparisons: 8 },
  methodology: { classification: 'c', index: 'i', symmetry: 's' } }
export const candidates = { items: [{ id: 1, slug: 'candidate-a', name: 'Candidate A', party: 'Harbor Party' }, { id: 2, slug: 'candidate-b', name: 'Candidate B', party: 'Summit Party' }] }

export function mockFetch(routes) {
  return vi.fn(async (url) => {
    const path = url.replace(/^.*\/api/, '').split('?')[0]
    const hit = Object.entries(routes).find(([k]) => path === k || path.startsWith(k))
    if (!hit) return { ok: false, status: 404, json: async () => ({ error: { code: 'not_found', message: 'Not found' } }) }
    const v = hit[1]
    if (v instanceof Error) return { ok: false, status: 500, json: async () => ({ error: { code: 'internal_error', message: v.message } }) }
    return { ok: true, status: 200, json: async () => v }
  })
}
