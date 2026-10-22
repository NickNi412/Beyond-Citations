# Beyond Citations

**A mathematical framework that shows auditors where AI-generated research can fail.**

Team CloseAI · OSI Research Hackathon 2026 · Valency track, built with Valency's MCP Bond

## The idea in one paragraph

AI research tools now answer scientific questions with a confident conclusion and a list of citations. A reader sees five references and assumes five independent pieces of support. Often that is wrong. The references overlap, and several of them can rest on one shared condition that nobody has checked. If that condition fails, they all fail together. We take a cited AI report, write down exactly what its conclusion depends on, compute every way its support can be lost, and give a human auditor a short list of checks in the order that settles the claim fastest. The output is an **audit card**.

## What you get: the audit card

For each report, the pipeline produces a card with five parts:

1. **Claim and status.** The conclusion as the report states it, and whether it is certified at the chosen target (for example: "survives any one wrong study").
2. **Sources.** Each citation matched to the paper it points to (through Bond), and the studies that paper relies on. Citations that lead to the same study are counted once.
3. **Checks, in order.** The conditions a person has to confirm, sorted so that the check most likely to settle the claim comes first, with the result of each check once it is done.
4. **What the evidence does support.** The narrower claims that still hold.
5. **Next check.** The one thing to read next, if the status could still change.

Here is the card for a real AI report on creatine and kidney safety, after a researcher did the checks by hand. The full card is in [`cards/creatine_audit_card.md`](cards/creatine_audit_card.md).

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

Checking measurement first settled the claim in 7 checks instead of 15. Three frontier models that audited the same report directly said it had no single point of failure.

Cards produced by the program for six reports, before any human checking, are in [`results/exp4_cards_practical.md`](results/exp4_cards_practical.md) and, with Bond links, in [`results/exp7_bond_cards.md`](results/exp7_bond_cards.md).

## How it works

1. **Read.** Each numbered citation in the report is matched to the paper it actually points to, using Valency's MCP Bond.
2. **Structure.** A language model proposes the argument as routes. Each route needs some sources and some checkable conditions, such as "kidney function was measured in a way creatine does not distort". A researcher confirms or corrects the structure.
3. **Verify.** We compute the minimal failure certificates, the source resilience, the guaranteed range while conditions are still open, and the fewest checks that reach the target. These fill in the card.

## How we use Valency's MCP Bond

Bond links a report's reference list to the literature, so the audit runs on real papers rather than on titles a model wrote down. `exp7/bond.py` is a small client for Bond's MCP endpoint (JSON-RPC over HTTP, using only `requests`). `exp7/link.py` uses it in three steps:

| Step | Bond tool | What it adds to the audit |
| --- | --- | --- |
| `resolve` | `get_paper_by_id` for references with a PMC id, otherwise `search_by_title` filtered by year | Matches each reference to an indexed paper. References that resolve to the same paper count as one source. Titles that differ from the paper's title, or that drop narrowing words such as "older adults" or "narrative review", are flagged for a scope check. |
| `evidence` | `semantic_search_papers` | For every single point of failure on a card, finds papers that bear on that condition and marks whether the report already cites them. |
| `render` | none | Writes a plain-language card per report with the Bond links. |

On the six case-study reports, Bond matched 19 of 33 references to indexed papers. It also caught citation errors: one report cited a paper as "...Kidney Dysfunction?" when the real title ends "...Kidney Failure?".

## The mathematics

A report's argument is a monotone Boolean function over sources $S$ and conditions $R$. Each term is one minimal route to the conclusion $f$:

$$F_f=\bigvee_{w\in\mathcal W_f}\ \bigwedge_{v\in w} v,\qquad v\in S\cup R .$$

A **failure certificate** is a set of sources and conditions that meets every route. The minimal certificates are the ways support can be lost. The **source resilience** $\tau_S(f)$ is the size of the smallest certificate made of sources only, with every condition holding.

**Theorem (certificates and graded soundness).** If every reasoning step is valid and every condition holds, fewer than $\tau_S(f)$ wrong sources cannot remove the conclusion, and some $\tau_S(f)$ can. While conditions are still being checked, $\tau_S$ lies in an interval $L \le \tau_S \le H$ computed exactly from the confirmed, refuted and open conditions. Finding the fewest checks that guarantee $\tau_S \ge k$ is NP-hard in general and is solved exactly at report scale.

`evaudit/core.py` implements all of this. `tests/test_theory.py` checks the propositions on random instances.

## Results

Every number below can be recomputed from the files in `results/` with the commands in the next section.

| Finding | Result | Where |
| --- | --- | --- |
| AI reports cite five to seven references, yet most of the extracted structures turn on one condition | 15 of 18 structures have a single-condition bottleneck (6 of 18 once each condition is stated per study) | Experiments 4 and 9 |
| Frontier models auditing the reports directly (Claude Opus 5.5, Gemini 3.1 Pro, GPT-6.1 Sol) | named 2 of 35 single points of failure; overstated resilience in 10 of 18 audits | Experiment 5 |
| The same models, told to look for shared conditions | named 26 of 35 | Experiment 8C |
| The same models, given their own structure written out | found 35 of 35; resilience correct in 18 of 18 | Experiment 8B |
| Conditions stated per study, which removes bottlenecks created by merging | free audits named 0 of 15; given the structure, every one found and resilience correct in 18 of 18 | Experiments 9 and 8B |
| Synthetic materials and energy structures at four sizes | resilience, single points of failure and minimum plans correct at every size | Experiment 8A |

The models can compute these quantities. What their direct audits lack is the structure written down.

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
| `cards/` | The hand-checked audit card for the creatine report |
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

Copy `.env.example` to `.env` and fill in your own keys. Model calls go through OpenRouter. Bond calls need a Valency token from `app.valency.io/settings`. Keys are read from the environment or the env file and are never printed or written to disk. Every paid step takes `--max-usd` and stops at the cap. Bond itself is free.

## Data

Experiment 1 uses text from HealthVer (Sarrouti et al., 2021, github.com/sarrouti/HealthVer) and Climate-FEVER (Diggelmann et al., 2020, github.com/tdiggelm/climate-fever-dataset). The raw files are not redistributed here. Download them into `data/raw/` to rebuild the instances with `python -m exp1.build_exp1`.

## Limitations

The guarantees hold for the structure as accepted: valid reasoning steps, references correctly grouped into studies, and confirmed conditions. A language model proposes the structure; a person confirms it. Results on frontier models are scored against each model's own extraction, not against an independent ground truth. The case-study checks were done by hand from the cited papers.

## License

MIT. See `LICENSE`.
