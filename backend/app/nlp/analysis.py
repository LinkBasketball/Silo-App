"""Deterministic, explainable text analysis.

Every function returns the *reasons* behind its output so the UI can show its work.
Nothing here decides whether a statement is true. It describes what kind of statement it
is, what it would take to check it, and which language features are present.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

from app.nlp import lexicons as L
from app.nlp.engine import ParsedDoc, Sentence

SENTENCE_CLASSES = {
    "checkable_fact": "Checkable factual assertion",
    "opinion": "Subjective opinion",
    "prediction": "Prediction or commitment",
    "normative": "Normative / policy preference",
    "mixed": "Mixed or ambiguous",
    "ambiguous": "Mixed or ambiguous",
}
NUMERIC_LABELS = {"CARDINAL", "PERCENT", "MONEY", "QUANTITY"}
NAMED_LABELS = {"PERSON", "ORG", "GPE", "LAW", "NORP", "FAC", "EVENT"}
QUOTE_RE = re.compile(r"“([^”]{3,}?)”|\"([^\"]{3,}?)\"")
SPEAKER_BEFORE = re.compile(
    r"((?:[A-Z][\w.'’-]*)(?:\s+(?:[A-Z][\w.'’-]*|of|for))*)\s*,?\s+(?:said|says|stated|told|argued|wrote|added|declared)\b"
)
SPEAKER_AFTER = re.compile(
    r"(?:said|says|stated|argued|wrote|added|declared)\s+((?:[A-Z][\w.'’-]*)(?:\s+[A-Z][\w.'’-]*)*)"
)


def _has_phrase(lower: str, phrase: str) -> bool:
    return re.search(r"(?<![\w])" + re.escape(phrase) + r"(?![\w])", lower) is not None


def _phrases_in(lower: str, phrases) -> list[str]:
    return [p for p in phrases if _has_phrase(lower, p)]


def _emotional_terms(sent: Sentence) -> list[str]:
    out = []
    for t in sent.tokens:
        w = t.lower
        if w in L.EMOTIONAL_INDEX:
            out.append(w)
        elif w.endswith("s") and w[:-1] in L.EMOTIONAL_INDEX:
            out.append(w[:-1])
    return out


# ───────────────────────── Quotations ─────────────────────────
@dataclass
class Quote:
    text: str
    start: int  # offset in the full document
    end: int
    speaker: str | None
    sentence_index: int


def find_quotes(doc: ParsedDoc) -> list[Quote]:
    quotes = []
    for m in QUOTE_RE.finditer(doc.text):
        inner = (m.group(1) or m.group(2)).rstrip(", ")
        if len(inner.split()) < 3:
            continue
        sidx = next((s.index for s in doc.sentences if s.start <= m.start() < s.end),
                    next((s.index for s in doc.sentences if s.start <= m.start() + 1 < s.end + 1), 0))
        # Look for attribution in a window around the quote (same paragraph).
        window_before = doc.text[max(0, m.start() - 160): m.start()]
        window_after = doc.text[m.end(): m.end() + 120]
        speaker = None
        after = SPEAKER_AFTER.match(window_after.lstrip(" ,"))
        if after:
            speaker = after.group(1)
        else:
            sb = list(SPEAKER_BEFORE.finditer(window_before))
            if sb:
                speaker = sb[-1].group(1)
            else:
                sa = re.match(r"\s*,?\s*((?:[A-Z][\w.'’-]*)(?:\s+[A-Z][\w.'’-]*)*)\s+(?:said|says|argued|wrote)", window_after)
                if sa:
                    speaker = sa.group(1)
        if speaker:
            speaker = re.split(r"\.\s", speaker)[0].rstrip(".,")
        if speaker and speaker.split()[0] in {"The", "A", "An", "This", "That", "It"} and len(speaker.split()) == 1:
            speaker = None
        quotes.append(Quote(inner, m.start(), m.end(), speaker, sidx))
    return quotes


# ───────────────────────── Sentence classification ─────────────────────────
def classify_sentence(sent: Sentence, quotes_in_sentence: list[Quote] | None = None) -> dict:
    lower = sent.text.lower()
    reasons: list[str] = []
    labels = {e.label for e in sent.entities}
    has_number = bool(labels & NUMERIC_LABELS) or bool(re.search(r"\d", sent.text))
    has_date = "DATE" in labels or bool(re.search(r"\b(19|20)\d{2}\b", sent.text))
    named = bool(labels & NAMED_LABELS) or any(t.pos == "PROPN" for t in sent.tokens[1:])
    words = {t.lower for t in sent.tokens}
    verbs = {t.lower for t in sent.tokens if t.pos in ("VERB", "AUX")}
    # Only count action words used as verbs: "the tax cut" (noun) is not a reported action.
    fact_verbs = sorted(verbs & L.FACT_VERBS)
    attributed = bool(words & L.ATTRIBUTION_VERBS) or "according to" in lower
    opinion = _phrases_in(lower, L.OPINION_MARKERS)
    normative = _phrases_in(lower, L.NORMATIVE_MARKERS)
    prediction = _phrases_in(lower, L.PREDICTION_MARKERS)
    evaluative = _emotional_terms(sent)
    superlative_judgement = sorted(words & {"best", "worst", "greatest", "terrible", "great", "wonderful", "awful"})
    certainty = _phrases_in(lower, L.CERTAINTY_MARKERS)
    quotes_in_sentence = quotes_in_sentence or []

    if has_number:
        reasons.append("contains a number, amount or percentage")
    if has_date:
        reasons.append("contains a date or time reference")
    if fact_verbs:
        reasons.append(f"reports a verifiable action ({', '.join(fact_verbs)})")
    if opinion:
        reasons.append(f"opinion marker ({', '.join(opinion)})")
    if normative:
        reasons.append(f"normative marker ({', '.join(normative)})")
    if prediction:
        reasons.append(f"forward-looking marker ({', '.join(prediction)})")
    if evaluative:
        reasons.append(f"evaluative language ({', '.join(sorted(set(evaluative)))})")
    if superlative_judgement:
        reasons.append(f"judgement word ({', '.join(superlative_judgement)})")
    if certainty:
        reasons.append(f"certainty marker ({', '.join(certainty)})")

    fact_signal = has_number or (bool(fact_verbs) and (has_date or named))

    if sent.text.rstrip().endswith("?"):
        cls = "ambiguous"
        reasons.append("phrased as a question, not an assertion")
    elif quotes_in_sentence and attributed:
        cls = "checkable_fact"
        reasons.insert(0, "attributes a direct quotation to a speaker (whether it was said is checkable)")
    elif fact_signal and (opinion or normative or len(evaluative) >= 1):
        cls = "mixed"
    elif fact_signal:
        cls = "prediction" if prediction and not fact_verbs else "checkable_fact"
    elif normative:
        cls = "normative"
    elif prediction:
        cls = "prediction"
    elif opinion or evaluative or superlative_judgement or certainty:
        cls = "opinion"
    elif fact_verbs or (attributed and named):
        cls = "checkable_fact"
    else:
        cls = "ambiguous"
        if not reasons:
            reasons.append("no strong factual, opinion or forward-looking signal")

    claim_type = None
    if cls in ("checkable_fact", "mixed"):
        if quotes_in_sentence and attributed:
            claim_type = "attributed_quote"
        elif words & {"voted", "vote", "passed", "bill", "signed", "vetoed", "enacted", "senate", "legislature"}:
            claim_type = "legislative_action"
        elif has_number:
            claim_type = "statistical"
        else:
            claim_type = "event"
    return {
        "sentence_class": cls,
        "label": SENTENCE_CLASSES[cls],
        "claim_type": claim_type,
        "reasons": reasons,
        "evaluative_terms": sorted(set(evaluative)),
    }


# ───────────────────────── Topics ─────────────────────────
def topic_for_sentence(sent: Sentence) -> tuple[str, list[str]]:
    words = [t.lower for t in sent.tokens]
    best, best_hits = "Other", []
    for topic, kws in L.TOPIC_KEYWORDS.items():
        hits = [w for w in words if w in kws]
        if len(hits) > len(best_hits):
            best, best_hits = topic, hits
    return best, sorted(set(best_hits))


def topic_distribution(doc: ParsedDoc) -> dict:
    weights: Counter = Counter()
    counts: Counter = Counter()
    rows = []
    for s in doc.sentences:
        topic, hits = topic_for_sentence(s)
        n = max(1, sum(1 for t in s.tokens if t.is_alpha))
        weights[topic] += n
        counts[topic] += 1
        rows.append({"sentence_index": s.index, "text": s.text, "topic": topic, "matched_keywords": hits})
    total = sum(weights.values()) or 1
    dist = [
        {"topic": t, "share": round(w / total, 4), "sentence_count": counts[t]}
        for t, w in sorted(weights.items(), key=lambda kv: (-kv[1], kv[0]))
    ]
    return {
        "distribution": dist,
        "sentences": rows,
        "note": "Topic share measures how much of the text discusses each subject. "
                "It is not a measure of political bias or accuracy.",
    }


# ───────────────────────── Rhetoric ─────────────────────────
def rhetoric_metrics(doc: ParsedDoc, classifications: list[dict]) -> dict:
    toks = [t for t in doc.tokens if t.is_alpha]
    adj = sum(1 for t in toks if t.pos == "ADJ")
    nouns = sum(1 for t in toks if t.pos in ("NOUN", "PROPN"))
    matched: Counter = Counter()
    by_cat: Counter = Counter()
    for t in toks:
        w = t.lower if t.lower in L.EMOTIONAL_INDEX else (t.lower[:-1] if t.lower[:-1] in L.EMOTIONAL_INDEX else None)
        if w:
            matched[w] += 1
            by_cat[L.EMOTIONAL_INDEX[w]] += 1
    n = len(toks)
    dist: Counter = Counter(c["sentence_class"] for c in classifications)
    total_s = max(1, len(classifications))
    examples: dict[str, list[str]] = {}
    for s, c in zip(doc.sentences, classifications, strict=False):
        examples.setdefault(c["sentence_class"], [])
        if len(examples[c["sentence_class"]]) < 2:
            examples[c["sentence_class"]].append(s.text)
    return {
        "token_count": n,
        "sentence_count": len(classifications),
        "adjective_count": adj,
        "noun_count": nouns,
        "adjective_noun_ratio": round(adj / nouns, 3) if nouns else None,
        "emotional_term_count": sum(matched.values()),
        "emotional_density": round(sum(matched.values()) / n, 4) if n else None,
        "emotional_per_100_words": round(100 * sum(matched.values()) / n, 2) if n else None,
        "emotional_by_category": dict(sorted(by_cat.items())),
        "emotional_terms": [{"term": w, "count": c, "category": L.EMOTIONAL_INDEX[w]} for w, c in matched.most_common()],
        "sentence_distribution": [
            {"sentence_class": k, "label": SENTENCE_CLASSES[k], "count": dist.get(k, 0),
             "share": round(dist.get(k, 0) / total_s, 4), "examples": examples.get(k, [])}
            for k in ("checkable_fact", "opinion", "prediction", "normative", "mixed", "ambiguous")
        ],
        "engine": doc.engine,
    }


# ───────────────────────── Language audit (Module E) ─────────────────────────
ALLEGATION_TERMS = {"corrupt", "corruption", "fraud", "bribe", "bribery", "illegal", "lied", "lying", "rigged", "stole", "criminal", "crooked"}


def language_audit(doc: ParsedDoc, quotes: list[Quote]) -> list[dict]:
    findings = []

    def in_quote(pos: int) -> bool:
        return any(q.start <= pos < q.end for q in quotes)

    for s in doc.sentences:
        lower = s.text.lower()
        words = {t.lower for t in s.tokens}
        attributed = bool(words & L.ATTRIBUTION_VERBS) or "according to" in lower
        for t in s.tokens:
            w = t.lower if t.lower in L.EMOTIONAL_INDEX else (t.lower[:-1] if t.lower[:-1] in L.EMOTIONAL_INDEX else None)
            if not w:
                continue
            q = in_quote(t.idx)
            if w in ALLEGATION_TERMS and not attributed and not q:
                kind, expl = "unattributed_allegation", "An accusation appears without attribution to a named source or supporting record."
            else:
                kind = "loaded_language"
                expl = f"Emotionally loaded term ({L.EMOTIONAL_INDEX[w]}). Emotional language is not evidence of falsehood; it signals an appeal beyond the facts stated."
            findings.append({
                "type": kind, "term": t.text, "sentence_index": s.index, "start": t.idx,
                "end": t.idx + len(t.text), "in_quotation": q, "explanation": expl
                + (" This term is inside a direct quotation and is preserved verbatim." if q else ""),
            })
        for p in _phrases_in(lower, L.CERTAINTY_MARKERS):
            off = s.start + lower.find(p)
            findings.append({
                "type": "unsupported_certainty", "term": s.text[lower.find(p): lower.find(p) + len(p)],
                "sentence_index": s.index, "start": off, "end": off + len(p), "in_quotation": in_quote(off),
                "explanation": "Expresses certainty. Check whether the passage provides evidence proportional to that certainty.",
            })
        for p in _phrases_in(lower, L.VAGUE_ATTRIBUTION):
            off = s.start + lower.find(p)
            findings.append({
                "type": "vague_attribution", "term": s.text[lower.find(p): lower.find(p) + len(p)],
                "sentence_index": s.index, "start": off, "end": off + len(p), "in_quotation": in_quote(off),
                "explanation": "Attributes information to unnamed sources. The original source cannot be inspected from this passage.",
            })
    findings.sort(key=lambda f: f["start"])
    return findings


# ───────────────────────── Context gaps ─────────────────────────
COMPARATIVES = {"highest", "lowest", "best", "worst", "record", "fastest", "biggest", "largest", "smallest", "most", "least"}
CHANGE_WORDS = {"rose", "fell", "grew", "increased", "decreased", "declined", "dropped", "jumped", "surged", "plunged", "cut", "doubled", "tripled", "halved"}


def context_gaps(sent: Sentence, cls: dict, quotes: list[Quote]) -> list[dict]:
    gaps = []
    lower = sent.text.lower()
    words = {t.lower for t in sent.tokens}
    labels = {e.label for e in sent.entities}
    has_date = "DATE" in labels or bool(re.search(r"\b(19|20)\d{2}\b|\b(since|last year|this year|quarter|month)\b", lower))
    has_pct = "PERCENT" in labels or "%" in sent.text or "percent" in lower

    def add(kind, label, question, trigger):
        gaps.append({"type": kind, "label": label, "question": question, "trigger": trigger, "sentence_index": sent.index})

    verbs = {t.lower for t in sent.tokens if t.pos in ("VERB", "AUX")}
    change = sorted(verbs & CHANGE_WORDS)
    if change and not has_date:
        add("missing_time_period", "Missing time period", "Over what period did this change happen, and starting from when?", change[0])
    if words & {"doubled", "tripled", "halved"} and not re.search(r"\d", sent.text):
        add("missing_baseline", "Missing baseline", "What were the starting and ending values?", next(iter(words & {"doubled", "tripled", "halved"})))
    comp = sorted(words & COMPARATIVES)
    if comp and not re.search(r"\b(than|since|compared|among|in the state|in the nation|on record since)\b", lower):
        add("incomplete_comparison", "Incomplete comparison", "Compared with what — which places, periods or groups?", comp[0])
    if cls["claim_type"] == "statistical" and not has_pct and re.search(r"\b\d[\d,]{2,}\b", sent.text) and not re.search(r"\b(of|per|out of)\b\s+\d", lower):
        add("missing_denominator", "Possible missing denominator", "Out of how many? A count alone can be hard to interpret.", re.search(r"\b\d[\d,]{2,}\b", sent.text).group(0))
    for p in _phrases_in(lower, L.VAGUE_ATTRIBUTION):
        add("unnamed_source", "Unnamed source", "Who specifically said or found this, and where is it published?", p)
    for q in quotes:
        if q.sentence_index == sent.index and not q.speaker:
            add("unattributed_quote", "Quote without clear attribution", "Who said this, when, and where is the original recording or transcript?", q.text[:40])
    for p in _phrases_in(lower, L.CERTAINTY_MARKERS):
        add("unsupported_certainty", "Certainty without shown evidence", "What evidence supports this level of certainty?", p)
    return gaps


# ───────────────────────── Neutral summary ─────────────────────────
def _clean_loaded(sent: Sentence) -> tuple[str, list[str]]:
    """Remove loaded *modifiers* (adjectives/adverbs) only. Loaded verbs/nouns are kept, never paraphrased."""
    removed = []
    text = sent.text
    for t in sorted(sent.tokens, key=lambda t: -t.idx):
        if t.pos in ("ADJ", "ADV") and (t.lower in L.EMOTIONAL_INDEX):
            rel = t.idx - sent.start
            if 0 <= rel < len(text) and text[rel: rel + len(t.text)] == t.text:
                removed.append(t.text)
                text = (text[:rel] + text[rel + len(t.text):])
    text = re.sub(r"\s{2,}", " ", text).replace(" ,", ",").replace(" .", ".").strip()
    return text, list(reversed(removed))


def _lead_lower(text: str, sent: Sentence) -> str:
    if not text:
        return text
    first = sent.tokens[0] if sent.tokens else None
    if first and first.pos == "PROPN" or (len(text) > 1 and text[1].isupper()):
        return text
    return text[0].lower() + text[1:]


def _subject(sent: Sentence) -> str:
    for nc in sent.noun_chunks:
        words = [w for w in nc.split() if w.lower().strip(",.") not in L.EMOTIONAL_INDEX]
        content = [w for w in words if w.lower() not in {"a", "an", "the", "this", "that", "every", "our", "their", "its"}]
        if content and words[0].lower() not in {"i", "we", "you", "it", "they", "this"}:
            phrase = " ".join(words)
            return phrase[0].lower() + phrase[1:] if words[0] in {"The", "A", "An", "This", "That"} else phrase
    return "the subject under discussion"


def neutral_summary(doc: ParsedDoc, classifications: list[dict], quotes: list[Quote], voice: str = "text", max_items: int = 12) -> dict:
    who = {"speech": "The speaker", "opinion": "The author"}.get(voice, "The text")
    items = []
    for s, c in list(zip(doc.sentences, classifications, strict=False))[:max_items]:
        sq = [q for q in quotes if q.sentence_index == s.index]
        cleaned, removed = _clean_loaded(s)
        cleaned = cleaned.rstrip(".!") + "."
        neg = [w for w in c["evaluative_terms"] if w in L.NEGATIVE_EVALUATIVE]
        pos = [w for w in c["evaluative_terms"] if w in L.POSITIVE_EVALUATIVE]
        has_data = bool(re.search(r"\d", s.text))
        note = None
        if sq:
            q = sq[0]
            out = f"{q.speaker} is quoted: “{q.text}”" if q.speaker else f"{who} includes an unattributed quotation: “{q.text}”"
            if not out.endswith((".", "?", "!", "”")):
                out += "."
            note = "Quotation reproduced verbatim with attribution; wording inside quotation marks is unchanged."
        elif c["sentence_class"] == "checkable_fact":
            out = f"{who} states that {_lead_lower(cleaned, s)}"
            note = "Reported as an attributed statement" + (f"; removed evaluative modifiers: {', '.join(removed)}." if removed else ".")
        elif c["sentence_class"] == "mixed":
            out = f"{who} states that {_lead_lower(cleaned, s)}"
            if c["evaluative_terms"]:
                out += " It also uses evaluative language (" + ", ".join(f"“{w}”" for w in c["evaluative_terms"]) + ")."
            note = "Factual content kept as an attributed statement; evaluative language listed separately."
        elif c["sentence_class"] == "opinion" and (neg or pos):
            direction = "negatively" if len(neg) > len(pos) else "positively" if len(pos) > len(neg) else "in evaluative terms"
            terms = ", ".join(f"“{w}”" for w in c["evaluative_terms"])
            out = f"{who} characterizes {_subject(s)} {direction} ({terms})."
            if not has_data:
                out += " No supporting data is provided in this sentence."
            note = "Evaluative wording converted into an attributed characterization."
        elif c["sentence_class"] == "opinion":
            out = f"{who} expresses the view that {_lead_lower(cleaned, s)}"
            note = "Opinion kept as an attributed view."
        elif c["sentence_class"] == "normative":
            out = f"{who} argues that {_lead_lower(cleaned, s)}"
            note = "Policy preference kept as an attributed argument."
        elif c["sentence_class"] == "prediction":
            out = f"{who} predicts or commits that {_lead_lower(cleaned, s)}"
            note = "Forward-looking statement; cannot be verified until the predicted time."
        else:
            continue
        items.append({"sentence_index": s.index, "original": s.text, "neutral": out, "transformation": note,
                      "removed_modifiers": removed})
    summary_text = " ".join(i["neutral"] for i in items)
    return {
        "items": items,
        "text": summary_text,
        "voice": who,
        "integrity": verify_summary(doc.text, summary_text),
    }


ENDORSEMENT_PATTERNS = [r"\byou should vote\b", r"\bvote for\b", r"\bvote against\b", r"\bwe endorse\b", r"\bthe best candidate\b", r"\bthe right choice\b"]


def verify_summary(original: str, summary: str) -> dict:
    """Output guardrails: quoted text must be verbatim; no endorsement language may be introduced."""
    violations = []
    quoted = re.findall(r"“([^”]+)”", summary)
    for q in quoted:
        if q not in original and q.lower() not in original.lower():
            violations.append({"check": "quote_preservation", "detail": q[:80]})
    for pat in ENDORSEMENT_PATTERNS:
        if re.search(pat, summary, re.I) and not re.search(pat, original, re.I):
            violations.append({"check": "no_introduced_endorsement", "detail": pat})
    return {
        "quotes_checked": len(quoted),
        "quotes_preserved": not any(v["check"] == "quote_preservation" for v in violations),
        "endorsements_introduced": any(v["check"] == "no_introduced_endorsement" for v in violations),
        "passed": not violations,
        "violations": violations,
    }


# ───────────────────────── Orchestration ─────────────────────────
def analyze_text(doc: ParsedDoc, voice: str = "text") -> dict:
    quotes = find_quotes(doc)
    classifications = [classify_sentence(s, [q for q in quotes if q.sentence_index == s.index]) for s in doc.sentences]
    claims, gaps = [], []
    for s, c in zip(doc.sentences, classifications, strict=False):
        topic, _ = topic_for_sentence(s)
        g = context_gaps(s, c, quotes)
        gaps.extend(g)
        if c["sentence_class"] in ("checkable_fact", "mixed"):
            claims.append({
                "sentence_index": s.index, "text": s.text, "start": s.start, "end": s.end,
                "sentence_class": c["sentence_class"], "claim_type": c["claim_type"], "topic": topic,
                "reasons": c["reasons"],
            })
    return {
        "engine": doc.engine,
        "sentences": [
            {"index": s.index, "text": s.text, "start": s.start, "end": s.end, **c}
            for s, c in zip(doc.sentences, classifications, strict=False)
        ],
        "claims": claims,
        "quotes": [{"text": q.text, "speaker": q.speaker, "start": q.start, "end": q.end, "sentence_index": q.sentence_index} for q in quotes],
        "context_gaps": gaps,
        "topics": topic_distribution(doc),
        "rhetoric": rhetoric_metrics(doc, classifications),
        "language_audit": language_audit(doc, quotes),
        "neutral_summary": neutral_summary(doc, classifications, quotes, voice),
    }
