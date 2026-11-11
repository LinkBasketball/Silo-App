"""NLP engine abstraction.

The analysis layer works on a small engine-neutral document structure so SILO stays usable
when the spaCy model is unavailable. The active engine is always reported to the user.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from functools import lru_cache

from app.core.config import get_settings

log = logging.getLogger("silo.nlp")


@dataclass(frozen=True)
class Token:
    text: str
    lower: str
    pos: str          # Universal POS tag: ADJ, NOUN, PROPN, VERB, NUM, ...
    is_alpha: bool
    idx: int          # char offset in the full text


@dataclass(frozen=True)
class Entity:
    text: str
    label: str        # spaCy labels: PERSON, ORG, GPE, DATE, PERCENT, MONEY, CARDINAL, ...


@dataclass
class Sentence:
    index: int
    text: str
    start: int
    end: int
    tokens: list[Token] = field(default_factory=list)
    entities: list[Entity] = field(default_factory=list)
    noun_chunks: list[str] = field(default_factory=list)


@dataclass
class ParsedDoc:
    text: str
    engine: str
    sentences: list[Sentence]

    @property
    def tokens(self) -> list[Token]:
        return [t for s in self.sentences for t in s.tokens]


class SpacyEngine:
    name = "spacy"

    def __init__(self, model: str):
        import spacy  # imported lazily so the rules engine works without it
        from spacy.language import Language

        if not Language.has_factory("silo_label_boundaries"):
            @Language.component("silo_label_boundaries")
            def _label_boundaries(doc):
                # "…said Candidate A. Experts say…" — spaCy reads "A." as an abbreviation.
                for i in range(1, len(doc) - 1):
                    t = doc[i]
                    if (re.fullmatch(r"[A-Z]\.", t.text) and doc[i - 1].text in _LABEL_WORDS
                            and doc[i + 1].text[:1].isupper()):
                        doc[i + 1].is_sent_start = True
                return doc

        self._nlp = spacy.load(model, disable=["lemmatizer"])
        self._nlp.add_pipe("silo_label_boundaries", before="parser")
        self.name = f"spacy:{model}"

    def parse(self, text: str) -> ParsedDoc:
        doc = self._nlp(text)
        sents = []
        for _i, s in enumerate(doc.sents):
            if not s.text.strip():
                continue
            sents.append(Sentence(
                index=len(sents), text=s.text.strip(), start=s.start_char,
                end=s.start_char + len(s.text.rstrip()),
                tokens=[Token(t.text, t.lower_, t.pos_, t.is_alpha, t.idx) for t in s if not t.is_space],
                entities=[Entity(e.text, e.label_) for e in s.ents],
                noun_chunks=[nc.text for nc in s.noun_chunks],
            ))
        return ParsedDoc(text=text, engine=self.name, sentences=sents)


_LABEL_WORDS = {"Candidate", "Option", "Plan", "Section", "Part", "Group", "State", "District"}
_SENT_RE = re.compile(r"[^.!?]+(?:[.!?]+[\"”’)]*|$)", re.S)
_TOKEN_RE = re.compile(r"\$?\d[\d,.]*%?|[A-Za-z][A-Za-z'’-]*|[^\sA-Za-z\d]")
_ADJ_SUFFIX = ("ous", "ful", "ive", "able", "ible", "al", "ic", "less", "ish", "ary")
_FUNCTION = set(
    "a an the and or but if of to in on at by for with from as is are was were be been being it its "
    "this that these those he she they we you i his her their our your my me him them us not no so "
    "than then there here who whom which what when where why how all any each some more most very "
    "has have had do does did will would can could should may might must shall also just only".split()
)


class RulesEngine:
    """Dependency-free fallback. Coarser POS tags; flagged as lower reliability in the UI."""
    name = "rules-fallback"

    def parse(self, text: str) -> ParsedDoc:
        from app.nlp.lexicons import ATTRIBUTION_VERBS, EMOTIONAL_INDEX, FACT_VERBS

        sents = []
        for m in _SENT_RE.finditer(text):
            raw = m.group(0)
            if not raw.strip():
                continue
            lead = len(raw) - len(raw.lstrip())
            start = m.start() + lead
            stext = raw.strip()
            toks = []
            for tm in _TOKEN_RE.finditer(stext):
                w = tm.group(0)
                lw = w.lower()
                if w[0].isdigit() or w[0] == "$":
                    pos = "NUM"
                elif not w[0].isalpha():
                    pos = "PUNCT"
                elif lw in _FUNCTION:
                    pos = "DET"
                elif lw in FACT_VERBS or lw in ATTRIBUTION_VERBS or lw.endswith("ed"):
                    pos = "VERB"
                elif lw in EMOTIONAL_INDEX and (lw.endswith(_ADJ_SUFFIX) or lw in {"bold", "brave", "dire"}):
                    pos = "ADJ"
                elif lw.endswith(_ADJ_SUFFIX) and len(lw) > 5:
                    pos = "ADJ"
                elif w[0].isupper() and tm.start() > 0:
                    pos = "PROPN"
                else:
                    pos = "NOUN"
                toks.append(Token(w, lw, pos, w.isalpha(), start + tm.start()))
            ents = [Entity(n, "CARDINAL") for n in re.findall(r"\d[\d,.]*", stext)]
            ents += [Entity(p, "PERCENT") for p in re.findall(r"\d[\d.]*\s?(?:%|percent)", stext)]
            ents += [Entity(d, "DATE") for d in re.findall(r"\b(?:19|20)\d{2}\b", stext)]
            sents.append(Sentence(len(sents), stext, start, start + len(stext), toks, ents, []))
        return ParsedDoc(text=text, engine=self.name, sentences=sents)


@lru_cache
def get_engine():
    """Load once per worker. 'auto' prefers spaCy and falls back to rules."""
    s = get_settings()
    if s.nlp_engine in ("auto", "spacy"):
        try:
            return SpacyEngine(s.spacy_model)
        except Exception as exc:  # model missing / import error
            if s.nlp_engine == "spacy":
                raise
            log.warning("spaCy unavailable (%s); using rules fallback", type(exc).__name__)
    return RulesEngine()


def parse(text: str) -> ParsedDoc:
    return get_engine().parse(text)
