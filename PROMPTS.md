# Prompts

Every prompt used in the paper, verbatim. `{report}` and similar fields are filled per item.

## Experiment 1, plain prompt.

```
You are assessing the evidence for a scientific claim.

Claim: {claim}

Evidence collected:
{items}

Taking all the evidence together, how strongly is the claim supported? Answer on a scale
from 0 (no support) to 100 (conclusively established).
Reply with JSON only: {"support": <integer 0-100>}
```

## Experiment 1, aware prompt.

```
You are assessing the evidence for a scientific claim.

Claim: {claim}

Evidence collected:
{items}

Several items may report the same underlying study; count each underlying study only once.
Taking all the evidence together, how strongly is the claim supported? Answer on a scale
from 0 (no support) to 100 (conclusively established), and say how many independent
underlying studies the evidence contains.
Reply with JSON only: {"support": <integer 0-100>, "independent_studies": <integer>}
```

## Experiment 2b.

```
Below are passages from a literature digest about a material sample. Each passage is
attributed to a paper.

{passages}

Question: {question}

1. List every distinct way the passages establish that the answer is yes. For each way, give
the minimal set of passage ids it relies on (facts and rules). Passages that restate the
same claim count as alternatives.
2. Treat each paper as a source. What is the minimum number of distinct papers that would
have to be wrong for the conclusion to no longer be established by any of these ways?
Reply with JSON only: {"derivations": [["P1", "P4"], ...], "min_papers_to_fail": <integer>}
```

## Experiment 3, direct.

```
Treat each cited study as a source that could turn out to be wrong, and each assumption
stated in the reasoning as a condition that could turn out to be false. Two stated
assumptions are the same condition only if they assert the same thing about the same
objects, whatever the wording; give each distinct condition one id (C1, C2, ...). Refer to
studies by their letter (A, B, C).

Then list every minimal failure set: a set of studies and/or condition ids such that, if all
of them failed, no route to the claim would remain, and no smaller subset would do. Finally
say whether one single study or condition, failing alone, would leave the claim with no
remaining route.
Reply with JSON only, no comments: {"conditions": [{"id": "C1", "text": "...", "routes": [1,
2]}], "failure_sets": [["A", "C1"]], "single_point_of_failure": "C1 or a study letter or
none"}

{report}
```

## Experiment 3, direct with definitions and worked example.

```
Treat each cited study as a source that could turn out to be wrong, and each assumption
stated in the reasoning as a condition that could turn out to be false. Two stated
assumptions are the same condition only if they assert the same thing about the same
objects, whatever the wording; give each distinct condition one id (C1, C2, ...). Refer to
studies by their letter (A, B, C).

Definitions. A route needs ALL of its studies and conditions; the claim survives while at
least one route has nothing failed. A failure set is a set of studies and/or conditions
that, if all failed, leaves NO route intact; it is minimal if no smaller subset does so. A
failure set must therefore hit every route. Listing what each route needs is not the same
thing.
Worked example (different topic). Claim: bridge X carries 40 t. Route 1 uses Study P and
assumes K1 (the steel grade is S355). Route 2 uses Study Q and assumes K1 and K2 (the load
test was static). Routes: {P, K1} and {Q, K1, K2}. Minimal failure sets: {K1}, {P, Q}, {P,
K2}. Single point of failure: K1. Wrong answer: {P, K1}, {Q, K1, K2} (these are the routes,
not failure sets).

Now do the same for the report below. List every minimal failure set, and say whether one
single study or condition, failing alone, would leave the claim with no remaining route.
Reply with JSON only, no comments: {"conditions": [{"id": "C1", "text": "...", "routes": [1,
2]}], "failure_sets": [["A", "C1"]], "single_point_of_failure": "C1 or a study letter or
none"}

{report}
```

## Experiment 3, extract (certificates computed by program).

```
Treat each cited study as a source that could turn out to be wrong, and each assumption
stated in the reasoning as a condition that could turn out to be false. Two stated
assumptions are the same condition only if they assert the same thing about the same
objects, whatever the wording; give each distinct condition one id (C1, C2, ...). Refer to
studies by their letter (A, B, C).

Only extract the structure. Do not assess robustness.
Reply with JSON only, no comments: {"conditions": [{"id": "C1", "text": "..."}], "routes":
[{"route": 1, "studies": ["A"], "conditions": ["C1"]}]}

{report}
```

## Experiment 3, extract, then model computes.

```
Treat each cited study as a source that could turn out to be wrong, and each assumption
stated in the reasoning as a condition that could turn out to be false. Two stated
assumptions are the same condition only if they assert the same thing about the same
objects, whatever the wording; give each distinct condition one id (C1, C2, ...). Refer to
studies by their letter (A, B, C).

First list, for each route, the studies and conditions it uses. Then, using only those
routes, list every minimal failure set: a set of studies and/or condition ids such that, if
all of them failed, no route to the claim would remain, and no smaller subset would do.
Finally say whether one single study or condition, failing alone, would leave the claim with
no remaining route.
Reply with JSON only, no comments: {"conditions": [{"id": "C1", "text": "..."}], "routes":
[{"route": 1, "studies": ["A"], "conditions": ["C1"]}], "failure_sets": [["A", "C1"]],
"single_point_of_failure": "C1 or a study letter or none"}

{report}
```

## Case study, report generation.

```
Write a short evidence report (400-700 words) answering the question below for an informed
reader. Search the literature. State one main conclusion in the first sentence. Support it
with the evidence you found, citing sources inline as [1], [2], ... End with a numbered
reference list giving, for each reference, its title, its authors or organisation, its year
and its URL.

Question: {question}
```

## Case study, extraction.

```
You are auditing the argument of the report below. Do not judge whether the conclusion is
true; only record how the report supports it.
1. State the report's main conclusion in one sentence.
2. For each numbered reference, give the original study or dataset it ultimately reports
(for example 'Martineau 2017 meta-analysis' or 'UK BEIS 2021 field trial'). If two
references report the same study, give them the same name. If you cannot tell, write
'unknown'.
3. List the conditions the argument relies on: assumptions that a step needs and that a
person could check, such as that a tested population, product or setting matches the one in
the conclusion, or that a cited result transfers to a different dose, scale or period. Two
conditions are the same only if they assert the same thing about the same objects, whatever
the wording; give each distinct condition one id (C1, C2, ...).
4. List the routes: each route is a minimal set of references that, together with its
conditions, the report uses to support the conclusion on its own. A reference may appear in
several routes.
5. List premises that every route needs but the report never states (empty list if none).
Give each an id U1, U2, ... and add it to the conditions of every route that needs it.
Reply with JSON only, no comments: {"conclusion": "...", "references": [{"ref": 1,
"underlying_study": "..."}], "conditions": [{"id": "C1", "text": "..."}], "unstated":
[{"id": "U1", "text": "..."}], "routes": [{"route": 1, "refs": [1, 3], "conditions": ["C1",
"U1"], "summary": "..."}]}

Report:
{report}
```

## Experiment 5, direct audit (Free)

```
You are auditing the AI-generated report below for a reader who must decide whether to rely on its main conclusion. List, in order of priority, the things the reader should check before relying on the conclusion. For each check, say exactly what to verify and where to look (which numbered reference, or which part of the report).
Then answer three questions about your checks.
(a) Which checks, if that check alone turned out false, would leave the conclusion with no support at all?
(b) If everything your checks verify holds, how many of the cited studies could turn out to be wrong with the conclusion still supported?
(c) Which checks are enough, if all of them are confirmed, for the conclusion to stay supported even if any one cited study is wrong?
Reply with JSON only: {{"conclusion": "...", "checks": [{{"n": 1, "check": "...", "where": "..."}}], "alone_removes_support": [1], "studies_that_can_be_wrong": 0, "enough_for_one_wrong_study": [1]}}

Report:
{report}
```

## Experiment 5, direct audit with instruction (Instr.)

```
You are auditing the AI-generated report below for a reader who must decide whether to rely on its main conclusion. List, in order of priority, the things the reader should check before relying on the conclusion. For each check, say exactly what to verify and where to look (which numbered reference, or which part of the report).
Then answer three questions about your checks.
(a) Which checks, if that check alone turned out false, would leave the conclusion with no support at all?
(b) If everything your checks verify holds, how many of the cited studies could turn out to be wrong with the conclusion still supported?
(c) Which checks are enough, if all of them are confirmed, for the conclusion to stay supported even if any one cited study is wrong?
Before answering, look for assumptions that every line of reasoning in the report depends on, whichever study it cites (for example, that the population, product, dose or test conditions of the studies match the conclusion). If such an assumption is false, no cited study supports the conclusion, however many there are.
Reply with JSON only: {{"conclusion": "...", "checks": [{{"n": 1, "check": "...", "where": "..."}}], "alone_removes_support": [1], "studies_that_can_be_wrong": 0, "enough_for_one_wrong_study": [1]}}

Report:
{report}
```

## Experiment 5, own extraction written out (Given) and synthetic structures

```
Below is the evidence behind one conclusion of a technical report, with its structure written out. Each line of reasoning supports the conclusion on its own, provided that every reference it uses is correct and every assumption it lists holds. References that report the same underlying study stand or fall together: if a study is wrong, every reference to it is wrong.

Answer four questions.
(a) Suppose every assumption holds. What is the largest number k such that the conclusion stays supported whichever k studies turn out wrong? Count underlying studies, not references.
(b) Which assumptions would, if that one assumption alone were false (every other assumption holding and every study correct), leave the conclusion with no supporting line? Give their ids, or [] if there are none.
(c) All assumptions start unchecked, and an unchecked assumption may be false. Give a smallest set of assumptions such that, once all of them are confirmed, the conclusion stays supported even if any one study is wrong, whatever the truth of the assumptions left unchecked. Answer null if no set of assumptions achieves this.
(d) Suppose assumption {x} is false and every other assumption holds. What is the largest number of studies that can be wrong with the conclusion still supported? Answer -1 if no supporting line remains.

Reply with JSON only: {{"a": 0, "b": ["A1"], "c": ["A1", "A2"], "d": 0}}

{structure}
```

## Experiment 5, grader

```
You are grading an audit of a report. Below are (1) a list of CONDITIONS, each an assumption the report's argument depends on, and (2) the numbered CHECKS that an auditor proposed.
For each condition, list the numbers of the checks that ask the reader to verify that same assumption, or a narrower or broader version of it about the same objects (for example, the same population, dose, product or outcome). A check that only asks generally whether the evidence is good does not count. Use an empty list if no check matches.
Reply with JSON only: {{"matches": [{{"id": "C1", "checks": [2]}}]}}

CONDITIONS:
{conds}

CHECKS:
{checks}
```

## Condition scope classifier

```
Below are the conditions that an argument relies on, each with the references of the routes that use it. For each condition, decide its scope.
each_study: the condition attributes a property to the cited studies, trials, reviews, sources or their participants, methods, measurements, doses, durations or quality, so that it could hold for one cited study and fail for another.
single: the condition is one proposition that is true or false as a whole whichever study is cited, for example about the conclusion's wording or scope, a definition, a product's identity, or whether a result transfers from one setting to another.
If a condition mixes both, choose each_study.
Reply with JSON only: {{"scopes": [{{"id": "C1", "scope": "each_study"}}]}}

Conclusion: {conclusion}

Conditions:
{conds}
```
