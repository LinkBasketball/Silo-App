"""Documented, versioned lexicons. Every list here is shown on the Methodology page.

These are deliberately small, transparent and symmetric: terms of praise and terms of
criticism are both included, so the same rules apply regardless of who is described.
"""
LEXICON_VERSION = "2026.11-a"

# Emotionally loaded / evaluative vocabulary, grouped by the emotion or appeal it signals.
EMOTIONAL_TERMS: dict[str, set[str]] = {
    "fear": {
        "alarming", "catastrophe", "catastrophic", "crisis", "danger", "dangerous", "devastate",
        "devastated", "devastating", "dire", "disaster", "disastrous", "doom", "dread", "fear",
        "frightening", "menace", "nightmare", "panic", "peril", "terrifying", "threat", "threaten",
        "collapse", "chaos", "chaotic",
    },
    "anger": {
        "outrage", "outrageous", "furious", "betray", "betrayal", "scandal", "scandalous", "shameful",
        "disgrace", "disgraceful", "corrupt", "corruption", "reckless", "rigged", "assault", "attack",
        "war", "destroy", "destroyed", "ruin", "ruined", "slam", "slammed", "blast", "blasted",
    },
    "contempt": {
        "absurd", "pathetic", "ridiculous", "incompetent", "clueless", "radical", "extreme",
        "extremist", "fringe", "elitist", "failed", "failing", "sham", "spree", "joke",
    },
    "praise": {
        "heroic", "hero", "brave", "courageous", "historic", "landmark", "visionary", "champion",
        "brilliant", "tremendous", "incredible", "amazing", "triumph", "lifeline", "bold",
        "extraordinary", "unprecedented", "fearless", "patriot", "patriotic",
    },
    "urgency": {
        "urgent", "emergency", "desperate", "unacceptable",
    },
}
EMOTIONAL_INDEX: dict[str, str] = {w: cat for cat, ws in EMOTIONAL_TERMS.items() for w in ws}

# Evaluative words that, when describing a subject, carry a direction of judgement.
NEGATIVE_EVALUATIVE = (
    EMOTIONAL_TERMS["fear"] | EMOTIONAL_TERMS["anger"] | EMOTIONAL_TERMS["contempt"]
) - {"war", "threat", "attack"}
POSITIVE_EVALUATIVE = EMOTIONAL_TERMS["praise"]

CERTAINTY_MARKERS = [
    "clearly", "undeniably", "undoubtedly", "obviously", "without a doubt", "everyone knows",
    "no one can deny", "there is no question", "beyond question", "always", "never", "100 percent",
    "100%", "definitely", "certainly", "proven", "the fact is", "make no mistake",
]
VAGUE_ATTRIBUTION = [
    "experts say", "experts agree", "studies show", "research shows", "many people", "some say",
    "people are saying", "critics say", "sources say", "it is said", "reportedly", "observers note",
    "many believe", "it is widely believed", "officials say", "analysts say",
]
HEDGES = ["may", "might", "could", "possibly", "perhaps", "appears", "suggests", "estimated", "roughly"]

OPINION_MARKERS = [
    "i think", "i believe", "i feel", "in my view", "in my opinion", "we believe", "seems",
    "frankly", "honestly", "to me", "it is clear that",
]
NORMATIVE_MARKERS = [
    "should", "ought", "must", "need to", "needs to", "have to", "has to", "it is time to",
    "we cannot", "we can't", "deserve", "deserves",
]
PREDICTION_MARKERS = [
    "will", "is expected to", "are expected to", "is likely to", "are likely to", "is projected to",
    "are projected to", "forecast", "projected", "is set to", "going to", "next year", "by 20",
]
FACT_VERBS = {
    "voted", "passed", "signed", "approved", "rejected", "vetoed", "enacted", "increased",
    "decreased", "rose", "fell", "grew", "declined", "dropped", "reported", "recorded", "closed",
    "opened", "spent", "allocated", "received", "raised", "filed", "announced", "introduced",
    "doubled", "tripled", "halved", "reached", "totaled", "cut", "added", "lost", "awarded",
}
ATTRIBUTION_VERBS = {"said", "says", "stated", "told", "wrote", "argued", "claimed", "added", "noted", "according"}

# Topic lexicon used by the narrative-focus visualisation. Topic frequency is NOT bias.
TOPIC_KEYWORDS: dict[str, set[str]] = {
    "Fiscal policy": {
        "budget", "tax", "taxes", "taxpayer", "deficit", "surplus", "spending", "revenue", "debt",
        "appropriation", "fiscal", "reserve", "comptroller", "dollar", "dollars", "funding", "fund",
    },
    "Economy & labor": {
        "jobs", "job", "unemployment", "jobless", "wages", "wage", "employment", "workers",
        "economy", "economic", "factory", "manufacturing", "labor", "business", "businesses", "inflation",
        "housing", "rent", "permits", "homes",
    },
    "Environment": {
        "river", "rivers", "pollution", "climate", "emissions", "water", "environmental", "cleanup",
        "phosphorus", "wetlands", "conservation", "energy", "watershed",
    },
    "Healthcare": {
        "clinic", "clinics", "hospital", "hospitals", "health", "patients", "medical", "care",
        "medicaid", "insurance", "doctors", "nurses",
    },
    "Immigration": {
        "immigration", "immigrants", "border", "asylum", "visa", "visas", "migrants", "citizenship",
        "deportation", "refugee", "refugees",
    },
    "Foreign affairs": {
        "trade", "tariff", "tariffs", "treaty", "diplomatic", "foreign", "strait", "shipping",
        "sanctions", "embassy", "negotiations", "ports", "port", "accord", "international",
    },
    "Elections & governance": {
        "election", "elections", "vote", "voters", "ballot", "campaign", "senate", "legislature",
        "governor", "senator", "candidate", "bill", "law", "committee", "roll-call",
    },
    "Education": {"school", "schools", "teachers", "students", "education", "university", "tuition"},
    "Public safety": {"police", "crime", "safety", "court", "courts", "prison", "emergency", "fire"},
}
