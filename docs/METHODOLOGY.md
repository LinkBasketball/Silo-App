# Methodology

The live version of this page is served at `GET /api/methodology` and rendered in the app.

## Evidence Coverage Score (`coverage-v1`)
Question: *How much of this text's checkable content is connected to inspectable records?* It is **not** a probability of truth.

`score = round(100 × Σ best(relationship_weight × source_quality) ÷ checkable_claims)`

| Relationship | Weight | | Source type | Quality |
|---|---|---|---|---|
| supports / partially supports / contradicts | 1.0 | | primary record, official statistic | 1.0 |
| provides context | 0.5 | | official transcript | 0.9 |
| insufficient evidence | 0 | | secondary reporting | 0.6 |

**Insufficient Evidence** (no number shown) when there are fewer than 2 checkable claims, or no claim has an assessed record.
Contradicting records raise coverage because they make a claim checkable; they are counted and shown separately.

## Claim–evidence relationships
For demonstration articles, relationships are **curated annotations** with written explanations. For pasted text, SILO only
proposes related records that pass an entity gate (they must name the same entity) and share at least 3 key terms. These are
always labelled *provides context: relationship not assessed*. SILO never automatically declares support or contradiction.

## Sentence classes
Checkable factual assertion · subjective opinion · prediction or commitment · normative/policy preference · mixed or ambiguous.
Rules use part-of-speech-gated action verbs, numeric/date entities, and published marker lists. Each sentence carries the reasons it was classified that way.
An attributed quotation is "checkable": whether the person said it can be verified, separately from whether it is accurate.

## Rhetoric metrics
- **Adjective-to-noun ratio** = ADJ ÷ (NOUN + PROPN) from the active tagger.
- **Emotional density** = lexicon matches ÷ alphabetic tokens (also reported per 100 words, by category).
- Emotional language is not evidence of falsehood; neutral-sounding language is not evidence of truth.

## Neutral summary (Module E)
Three representations: **original** (never modified), **language audit** (flags with explanations), **neutral restatement**:
quotes reproduced verbatim with attribution; factual sentences reported as "The text states that…" with only loaded
*modifiers* removed (and listed); opinions turned into attributed characterizations ("The speaker characterizes the bill
negatively ('disastrous', 'devastated'). No supporting data is provided in this sentence."). `verify_summary` checks
that every quoted string appears in the original and that no endorsement language was introduced.

## Alignment index
`(consistent + 0.5 × mixed) ÷ comparable pairs × 100`, shown only with at least 4 comparable, non-procedural pairs. Categories:
consistent, potentially inconsistent, mixed/conditional, not directly comparable, insufficient evidence. Never computed by keyword similarity, and never a measure of honesty.

## Nonpartisanship testing
`backend/tests/test_nonpartisan.py` swaps actors, parties and positions in otherwise identical text and asserts identical
classifications, audits, gaps and scores. During development this caught a real asymmetry ("tax cut" was read as a reported
action while "spending bill" was not), which was fixed by POS-gating action verbs. These tests show the rules are symmetric
for the tested pairs. They cannot prove the lexicons or curated annotations are unbiased.
