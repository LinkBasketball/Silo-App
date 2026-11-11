# Demo script (about 6 minutes, fully offline)

Start: `uvicorn app.main:app` (backend) + `npm run dev` (frontend) → http://localhost:5173

1. **Home.** Point out the demo banner and the three-step journey. "SILO shows evidence, not verdicts."
2. **Try the guided example** → *State X jobless rate falls…* Underlined claims are colour-coded by evidence status.
3. Click **"Manufacturing employment grew 40 percent"**. The widget opens on that claim: *Contradicts*. The record says 4.0%, the transcript shows the later clarification. Click **Inspect record** to show the highlighted excerpt.
4. **Coverage tab:** 98, "Broad coverage", even with a contradiction. Explain coverage ≠ truth. Show **Context gaps** ("Experts say…" → unnamed source; "grew 40 percent" → missing time period).
5. **Focus tab:** topic chart. Pick a topic to show the keywords behind each classification. "Topic share is not bias."
6. **Publisher tab:** ownership lineage, the parent firm's PAC giving equally to both candidates, and "Editorial control: Not established".
7. Scroll down to **Language analysis → Neutral summary**. The original is on the left, the restatement on the right, and the guardrail banner confirms quotes are verbatim.
8. Open **Opinion: Our housing crunch…** to show the "Insufficient evidence" state: no fake score.
9. **Analyze** → *Campaign speech* sample → Analyze. Show statement types, the language audit, and "Why no score?".
10. **Candidate Comparison:** identical columns; swap columns; Candidate C shows the missing-data state; alignment index with n and minimum.
11. **Financial Transparency:** campaign receipts vs. outside spending; money flows; the IE definition. Then the **Rhetoric scanner** tab.
12. **Geopolitical Context:** drag the **as of** slider; contested vs. documented events; NGO vs. government estimates shown separately; empirical vs. value-judgement arguments.
13. **Methodology:** formulas, weights, lexicons, limitations and source status. Mention 93 backend tests, including paired-swap nonpartisanship tests that caught a real bias bug.
