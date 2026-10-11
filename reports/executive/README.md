# Executive field guide

[Ten-slide briefing](index.html) for product managers and engineering leaders.

The briefing explains five operational categories, concrete jobs, workflow-based
shortlists, output completeness, the prime fixture and user-visible wait, a
model-agnostic cost scenario, six residency surfaces and the three state contracts.
It ends with repository/evidence links. Public GitHub/Medium URLs remain unresolved
until a publication destination is supplied.

## Blog figures

- [Category map](categories.svg)
- [Workflow output completeness](output.svg)
- [Guest calculation vs client lifecycle](latency.svg)
- [Model-agnostic machine-cost scenario](cost.svg)
- [Six residency surfaces](residency.svg)
- [Three state contracts](state.svg)

SVGs are scalable, accessible and self-contained. The export command also produces
PNG figures, slide images, a contact sheet and a searchable ten-page PDF suitable
for an article attachment. It checks keyboard navigation, layout, local links and
browser exceptions using disposable headless Chrome.

[Download the ten-page PDF](agent-sandbox-executive.pdf).

```sh
python3 reports/executive/build_deck.py
python3 reports/executive/export_deck.py
```

Install presentation extras and Chrome as described in the root setup guide.
`cohorts.json` stores every selected cohort and its raw attempt references. The
builder pins the retained snapshot and excludes future attempt dates.
Each table cell keeps its own setup; no overall vendor reliability score is pooled.
The assumed $0.003 model budget is a scenario input, not a model price claim.
