# Beyond Citations

**A mathematical framework that shows auditors where AI-generated research can fail.**

Team CloseAI · OSI Research Hackathon 2026 · Valency track, built with Valency's MCP Bond

## The idea

AI research tools answer scientific questions with a confident conclusion and a list of citations. Readers count the citations and assume each one is independent support. It rarely is. Citations overlap, and several of them often rest on one shared condition that nobody has checked. When that condition fails, they all fail together.

Beyond Citations makes this visible and computable. We take a cited AI report, write down exactly what its conclusion depends on, compute every way its support can be lost, and hand the auditor a short list of checks in the order that settles the claim fastest. The output is an **audit card**.

## The audit card

Every report gets a card with five parts:

1. **Claim and status.** The conclusion as the report states it, and whether it is certified at the chosen target, for example "survives any one wrong study".
2. **Sources.** Each citation matched through Bond to the paper it points to, and the studies that paper relies on. Citations that lead to the same study count once.
3. **Checks, in order.** The conditions to confirm, sorted so that the most decisive check comes first, with the result of each.
4. **What the evidence does support.** The narrower claims that hold.
5. **Next check.** The one thing to read next.

Here is the card for a real AI report on creatine and kidney safety. The full card is in [`cards/creatine_audit_card.md`](cards/creatine_audit_card.md).

| | |
| --- | --- |
| **Claim** | Long-term creatine use at standard doses is safe for kidney function in healthy adults. |
| **Status** | NOT CERTIFIED |
| **Sources** | 5 citations; 4 of them trace back to 3 overlapping groups of studies |
| **Check 1: measurement** | 3 of 5 studies use creatinine-based markers, which creatine itself raises: fail |
| **Check 2: duration** | the 2 studies with direct measurements lasted 12 weeks: fail |
| **Check 3: population** | not needed |
| **Supported instead** | creatinine markers stay normal for years in athletes; measured kidney function holds over 12 weeks |
| **Next check** | full text of the 2019 meta-analysis |

The plan settled the claim in 7 checks instead of 15. Three frontier models that audited the same report directly all said it had no single point of failure.

Cards for all six reports in our study are in [`results/exp4_cards_practical.md`](results/exp4_cards_practical.md), and with Bond links in [`results/exp7_bond_cards.md`](results/exp7_bond_cards.md).

## How it works

1. **Read.** Valency's MCP Bond matches each numbered citation to the paper it actually points to.
2. **Structure.** A language model writes the argument as routes. Each route needs some sources and some checkable conditions, such as "kidney function was measured in a way creatine does not distort". A researcher confirms it.
3. **Verify.** We compute the minimal failure certificates, the source resilience, the guaranteed range while conditions are open, and the fewest checks that reach the target. These fill the card.

## How we use Valency's MCP Bond

Bond connects a report's reference list to the literature, so every audit runs on real papers. `exp7/bond.py` is a lightweight client for Bond's MCP endpoint (JSON-RPC over HTTP, using only `requests`). `exp7/link.py` uses it in three steps:

| Step | Bond tool | What it adds to the audit |
| --- | --- | --- |
| `resolve` | `get_paper_by_id` for references with a PMC id, `search_by_title` filtered by year for the rest | Matches each reference to an indexed paper. References that resolve to the same paper count as one source. Titles that differ from the paper's own, or that drop narrowing words such as "older adults" or "narrative review", are flagged for a scope check. |
| `evidence` | `semantic_search_papers` | For every single point of failure, finds the papers that bear on that condition and marks which ones the report already cites. |
| `render` | none | Writes a plain-language card per report with the Bond links. |

Across six AI-written reports, Bond matched 19 of 33 references to indexed papers and caught citation errors the reports had introduced. One report cited a paper as "...Kidney Dysfunction?" when its real title ends "...Kidney Failure?".

## The mathematics

A report's argument is a monotone Boolean function over sources $S$ and conditions $R$. Each term is one minimal route to the conclusion $f$:

$$F_f=\bigvee_{w\in\mathcal W_f}\ \bigwedge_{v\in w} v,\qquad v\in S\cup R .$$

A **failure certificate** is a set of sources and conditions that meets every route. The minimal certificates are exactly the ways support can be lost. The **source resilience** $\tau_S(f)$ is the size of the smallest certificate made of sources only, with every condition holding.

**Theorem (certificates and graded soundness).** If every reasoning step is valid and every condition holds, fewer than $\tau_S(f)$ wrong sources can never remove the conclusion, and some $\tau_S(f)$ can. While conditions are being checked, $\tau_S$ lies in an interval $L \le \tau_S \le H$ computed exactly from the confirmed, refuted and open conditions. The fewest checks that guarantee $\tau_S \ge k$ form an NP-hard problem in general, which we solve exactly at report scale.

`evaudit/core.py` implements all of this, and `tests/test_theory.py` verifies every proposition on random instances.

## Results

Every number below can be recomputed from `results/` with the commands in the next section.

| Finding | Result | Where |
| --- | --- | --- |
| AI reports cite five to seven references, yet most of their structures turn on one condition | 15 of 18 extracted structures have a single-condition bottleneck | Experiment 4 |
| Frontier models auditing the reports directly (Claude Opus 5.5, Gemini 3.1 Pro, GPT-6.1 Sol) | named 2 of 35 single points of failure; overstated resilience in 10 of 18 audits | Experiment 5 |
| The same models, told to look for shared conditions | named 26 of 35 | Experiment 8C |
| The same models, given their own structure written out | found 35 of 35; resilience correct in 18 of 18 | Experiment 8B |
| Conditions stated per study | free audits named 0 of 15; given the structure, the models found every one and got resilience right in 18 of 18 | Experiments 9 and 8B |
| Synthetic materials and energy structures at four sizes | resilience, single points of failure and minimum plans correct at every size | Experiment 8A |

The models can compute. What they need is the structure written down, and that is what Beyond Citations provides.

## Reproduce

Python 3.10 or later.

```bash
pip install -r requirements.txt
python -m unittest tests.test_core tests.test_theory      # 26 tests, no API calls

# Rebuild the cards and summaries from the saved model outputs (no API calls)
python -m exp4.run_exp4 cards
python -m exp4.practical_card
python -m exp7.link render
python -m exp5.run_exp5 analyze
python -m exp8.run_exp8 analyze
python -m exp9.split_conditions analyze --files results/exp4_extract_runA.jsonl results/exp5_extract.jsonl
```

To rerun a step that calls a model or Bond, add `--env-file .env` (see Keys below). Every such step also accepts `--mock` for an offline dry run.

## Repository layout

| Path | Contents |
| --- | --- |
| `cards/` | The completed audit card for the creatine report |
| `evaudit/core.py` | Support functions, witnesses, failure certificates, source resilience, verification intervals and minimum plans |
| `evaudit/llm.py` | OpenRouter client with a hard spending cap |
| `exp1/`, `exp2/`, `exp3/` | Duplicated evidence, generated rule theories, and structure recovery by language models |
| `exp4/` | Reports from a search-enabled model, extraction by three judges, audit cards |
| `exp5/` | Frontier models auditing the reports directly, graded against their own cards |
| `exp6/`, `exp8/` | Models computing on a structure that is written out (synthetic sizes, own extractions, hints) |
| `exp7/` | Valency MCP Bond client and the citation linking pipeline |
| `exp9/` | Stating conditions per study and recounting bottlenecks |
| `data/` | Built instances and generated items, with fixed seeds |
| `results/` | Raw model outputs, cards, summaries and review files |
| `PROMPTS.md` | Every prompt used in the experiments |

## Keys and costs

Copy `.env.example` to `.env` and fill in your own keys. Model calls go through OpenRouter. Bond calls use a Valency token from `app.valency.io/settings`. Keys are read from the environment or the env file and are never printed or written to disk. Every paid step takes `--max-usd` and stops at the cap. Bond itself is free.

## Data

Experiment 1 uses text from HealthVer (Sarrouti et al., 2021, github.com/sarrouti/HealthVer) and Climate-FEVER (Diggelmann et al., 2020, github.com/tdiggelm/climate-fever-dataset). Download the raw files into `data/raw/` to rebuild the instances with `python -m exp1.build_exp1`.

## License

MIT. See `LICENSE`.
