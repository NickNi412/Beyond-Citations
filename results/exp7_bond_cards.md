# Audit cards linked to the literature through Valency MCP Bond

One card per report (anthropic/claude-haiku-4.5). Reference matching and the literature for each single point of failure come from Bond; nothing here has been checked by a person yet.

## vitd: Does vitamin D supplementation reduce the risk of acute respiratory infections in adults?

**Conclusion.** Vitamin D supplementation does not consistently reduce the risk of acute respiratory infections in adults, although a possible small benefit may remain for people with severe vitamin D deficiency or for specific dosing regimens.
**Target.** The conclusion should hold even if any 1 study is wrong (k = 2).

**Status: NOT CERTIFIED yet.**
- If every assumption below holds, the conclusion holds even if any 1 study is wrong.
- Now: no guarantee yet, since every route still rests on an unchecked assumption.
- Best reachable by checking: the conclusion holds even if any 1 study is wrong.

**Checklist to reach the target** (4 checks; all must be confirmed; single points of failure first)
1. U1 [single point of failure]: Meta-analyses and systematic reviews of RCTs provide valid evidence for population-level preventive effects  *Look in:* refs 1, 2, 3, 4.  *If false:* no support remains; stop.
2. C2: The baseline vitamin D concentrations and deficiency thresholds in the trials match clinically relevant definitions of severe deficiency  *Look in:* refs 1, 3.  *If false:* at best the conclusion holds only if every study it uses is correct.
3. C3: The dosing regimens tested (including 400-1,200 IU daily) represent the relevant supplementation strategies for clinical practice  *Look in:* refs 2.  *If false:* at best the conclusion holds even if any 1 study is wrong.
4. C4: Seasonal variation in benefit (spring, autumn, winter) is generalizable across different geographic and climate contexts  *Look in:* refs 2.  *If false:* at best the conclusion holds even if any 1 study is wrong.
*If all 4 are confirmed:* the conclusion holds even if any 1 study is wrong.

**Studies behind the references**
- S1: Martineau 2017 individual-participant-data meta-analysis of 25 RCTs (ref 1)
- S2: 2024 systematic review and meta-analysis of 43 RCTs (ref 2)
- S3: 2024 systematic review focused on ARI prevention (ref 3)
- S4: 2024 aggregate-data meta-analysis of 46 RCTs (ref 4)

**Smallest ways the conclusion can lose all support** (29 in total): U1 false; C2 false and S2 wrong; S1, S2 wrong; C1, C3 false and S3 wrong; C1, C4 false and S3 wrong; C1 false and S2, S3 wrong ...

**Not covered by this card**
- Whether each cited passage says what the report claims (citation checks are assumed done).
- Assumptions the report never states, added during reading: U1, U2; a person must accept them.
- References whose study could not be identified: none.

**References matched to indexed papers (Bond)**
- ref 1: [Vitamin D supplementation to prevent acute respiratory tract infections: systematic review and meta-analysis of individual participant data.](https://pubmed.ncbi.nlm.nih.gov/28202713/) (pubmed, via title search)
- ref 2: not found in the index: Optimal methods of vitamin D supplementation to prevent acute respiratory infections: a systematic review and meta-analysis
- ref 3: [Vitamin D supplementation for prevention of acute respiratory infections in older adults: A systematic review and meta-analysis.](https://pubmed.ncbi.nlm.nih.gov/38787821/) (pubmed, via pmc id)
- ref 4: [Vitamin D supplementation to prevent acute respiratory infections: systematic review and meta-analysis of stratified aggregate data.](https://pubmed.ncbi.nlm.nih.gov/39993397/) (pubmed, via title search)

**Literature bearing on each single point of failure (Bond)**
- U1: Meta-analyses and systematic reviews of RCTs provide valid evidence for population-level preventive effects (match: good_match)
    - [Vitamin D supplementation to prevent acute respiratory infections: individual participant data meta-analysis.](https://pubmed.ncbi.nlm.nih.gov/30675873/) (pubmed)
    - [Vitamin D supplementation to prevent acute respiratory tract infections: systematic review and meta-analysis of individual participant data.](https://pubmed.ncbi.nlm.nih.gov/28202713/) (pubmed, cited by the report)
    - [Effect of Vitamin D3 Supplementation on Respiratory Tract Infections in Healthy Individuals: A Systematic Review and Meta-Analysis of Randomized Controlled Trials.](https://pubmed.ncbi.nlm.nih.gov/27631625/) (pubmed)

## creatine: Is long-term creatine supplementation safe for kidney function in healthy adults?

**Conclusion.** Long-term creatine supplementation appears safe for kidney function in healthy adults when used at standard doses, although it can modestly raise blood creatinine without indicating actual kidney injury.
**Target.** The conclusion should hold even if any 1 study is wrong (k = 2).

**Status: NOT CERTIFIED yet.**
- If every assumption below holds, the conclusion holds even if any 3 studies are wrong.
- Now: no guarantee yet, since every route still rests on an unchecked assumption.
- Best reachable by checking: the conclusion holds even if any 3 studies are wrong.

**Checklist to reach the target** (4 checks; all must be confirmed; single points of failure first)
1. C1: The user is a healthy adult with no pre-existing kidney disease  *Look in:* refs 1, 2, 3, 4, 5.  *If false:* at best the conclusion holds only if every study it uses is correct.
2. C2: Creatine is used at standard doses, typically 3–5 g/day  *Look in:* refs 1, 2, 3, 5.  *If false:* at best the conclusion holds even if any 1 study is wrong.
3. C7: The study populations in references 1-5 are representative of the healthy adult population to which the conclusion applies  *Look in:* refs 1, 2, 3, 4, 5.  *If false:* at best the conclusion holds only if every study it uses is correct.
4. U1: Absence of evidence of kidney harm in the studies reviewed constitutes sufficient evidence of safety  *Look in:* refs 1, 2, 3, 4, 5.  *If false:* at best the conclusion holds only if every study it uses is correct.
*If all 4 are confirmed:* the conclusion holds even if any 3 studies are wrong.

**Studies behind the references**
- S1: Antonio et al. 2019 systematic review and meta-analysis (ref 1)
- S2: 2025 systematic review and meta-analysis on creatine and kidney function (ref 2)
- S3: 2023 review on creatine supplementation and kidney dysfunction (ref 3)
- S4: 2025 safety review of creatine supplementation (ref 4)
- S5: Kreider et al. 2017 International Society of Sports Nutrition position stand (ref 5)

**Smallest ways the conclusion can lose all support** (18 in total): C1, C6 false; C1, U2 false; C1 false and S3 wrong; C1 false and S2 wrong; C6, C7 false; C6, U1 false ...

**Not covered by this card**
- Whether each cited passage says what the report claims (citation checks are assumed done).
- Assumptions the report never states, added during reading: U1, U2; a person must accept them.
- References whose study could not be identified: none.

**References matched to indexed papers (Bond)**
- ref 1: [Effects of Creatine Supplementation on Renal Function: A Systematic Review and Meta-Analysis.](https://pubmed.ncbi.nlm.nih.gov/31375416/) (pubmed, via title search)
- ref 2: [Effect of creatine supplementation on kidney function: a systematic review and meta-analysis.](https://pubmed.ncbi.nlm.nih.gov/41199218/) (pubmed, via pmc id)
    - check: the report gives this reference as "Effect of Creatine Supplementation on Kidney Function"; the indexed paper's title differs (similarity 0.74). Confirm that the cited paper supports the claim at the report's scope.
- ref 3: [Is It Time for a Requiem for Creatine Supplementation-Induced Kidney Failure? A Narrative Review.](https://pubmed.ncbi.nlm.nih.gov/36986197/) (pubmed, via pmc id)
    - check: the report gives this reference as "Is It Time for a Requiem for Creatine Supplementation-Induced Kidney Dysfunction?"; the indexed paper's title differs (similarity 0.85). Confirm that the cited paper supports the claim at the report's scope.
- ref 4: [A short review of the most common safety concerns regarding creatine ingestion.](https://pubmed.ncbi.nlm.nih.gov/41404326/) (pubmed, via title search)
- ref 5: [International Society of Sports Nutrition position stand: safety and efficacy of creatine supplementation in exercise, sport, and medicine.](https://pubmed.ncbi.nlm.nih.gov/28615996/) (pubmed, via pmc id)

## lfp: Do lithium iron phosphate (LFP) home storage batteries last more than 6000 full cycles?

**Conclusion.** Some LFP home-storage batteries are specified to last more than 6,000 full-equivalent cycles, but this depends strongly on depth of discharge, temperature, charge rate, and the manufacturer's end-of-life definition.
**Target.** The conclusion should hold even if any 1 study is wrong (k = 2).

**Status: NOT CERTIFIED yet.**
- If every assumption below holds, the conclusion holds even if any 1 study is wrong.
- Now: no guarantee yet, since every route still rests on an unchecked assumption.
- Best reachable by checking: the conclusion holds even if any 1 study is wrong.

**Checklist to reach the target** (9 checks; all must be confirmed; single points of failure first)
1. C1: The Wilhelm et al. 2018 study's findings on commercial lithium-iron-phosphate/graphite cells' cycle stability up to 10,000 FECs apply to home-storage battery products  *Look in:* refs 1, 2.  *If false:* at best the conclusion holds only if every study it uses is correct.
2. C2: The Wilhelm et al. 2018 estimate that a typical home-storage system operating for 20 years would experience about 6,000 FECs applies to the systems being evaluated  *Look in:* refs 1, 2.  *If false:* at best the conclusion holds only if every study it uses is correct.
3. C3: The Omar et al. 2014 experimental findings on LFP battery cycle life at different depths of discharge, temperatures, and charging rates apply to commercial home-storage products  *Look in:* refs 1, 2.  *If false:* at best the conclusion holds only if every study it uses is correct.
4. C4: Pylontech EVOLVE LFP's specification of more than 6,000 cycles at 90% depth of discharge and 25°C is accurate as stated in the datasheet  *Look in:* refs 3, 4, 5.  *If false:* at best the conclusion holds only if every study it uses is correct.
5. C5: GoodWe Lynx A G3's specification of more than 6,000 cycles at 70% remaining capacity end-of-life criterion is accurate as stated in the datasheet  *Look in:* refs 3, 4, 5.  *If false:* at best the conclusion holds only if every study it uses is correct.
6. C6: Deye SE-F12's specification of exactly 6,000 cycles is accurate as stated in the datasheet  *Look in:* refs 3, 4, 5.  *If false:* at best the conclusion holds only if every study it uses is correct.
7. C7: The tested cells in Omar et al. 2014 are representative of LFP chemistry used in commercial home-storage batteries  *Look in:* refs 1, 2.  *If false:* at best the conclusion holds only if every study it uses is correct.
8. U1: The definition of 'full-equivalent cycle' used in the cited studies matches the definition used by the commercial manufacturers cited  *Look in:* refs 1, 2.  *If false:* at best the conclusion holds only if every study it uses is correct.
9. U2: The end-of-life capacity thresholds (70%, 80%, 90%) used in different studies and products are comparable or their differences are accounted for in the comparison  *Look in:* refs 1, 2.  *If false:* at best the conclusion holds only if every study it uses is correct.
*If all 9 are confirmed:* the conclusion holds even if any 1 study is wrong.

**Studies behind the references**
- S1: Wilhelm et al. 2018 laboratory and modelling study (ref 1)
- S2: Omar et al. 2014 experimental study (ref 2)
- S3: Pylontech EVOLVE LFP product datasheet 2025 (ref 3)
- S4: GoodWe Lynx A G3 product datasheet 2026 (ref 4)
- S5: Deye SE-F12 product datasheet 2026 (ref 5)

**Smallest ways the conclusion can lose all support** (48 in total): C1, C4 false; C1, C5 false; C1, C6 false; C1 false and S5 wrong; C1 false and S4 wrong; C1 false and S3 wrong ...

**Not covered by this card**
- Whether each cited passage says what the report claims (citation checks are assumed done).
- Assumptions the report never states, added during reading: U1, U2; a person must accept them.
- References whose study could not be identified: none.

**References matched to indexed papers (Bond)**
- ref 1: not found in the index: Analysis and modeling of calendar aging of a commercial LiFePO₄/graphite battery
- ref 2: not found in the index: Lithium iron phosphate based battery – Assessment of the aging parameters and development of cycle life model
- ref 3: not found in the index: EVOLVE LFP: Industry-leading lithium-ion batteries
- ref 4: not found in the index: Lynx A G3 Series
- ref 5: not found in the index: Deye SE-F12 Battery

## fasting: Does intermittent fasting produce more weight loss than continuous calorie restriction in adults?

**Conclusion.** Intermittent fasting does not consistently produce more weight loss than continuous calorie restriction in adults, and when energy intake is comparable, both approaches generally yield similar weight loss, although alternate-day fasting may provide a small additional short-term advantage.
**Target.** The conclusion should hold even if any 1 study is wrong (k = 2).

**Status: NOT CERTIFIED yet.**
- If every assumption below holds, the conclusion holds even if any 4 studies are wrong.
- Now: no guarantee yet, since every route still rests on an unchecked assumption.
- Best reachable by checking: the conclusion holds even if any 4 studies are wrong.

**Checklist to reach the target** (4 checks; all must be confirmed; single points of failure first)
1. U1 [single point of failure]: Systematic reviews and meta-analyses of RCTs provide valid evidence for drawing conclusions about the comparative effectiveness of weight loss interventions  *Look in:* refs 1, 2, 3, 4, 5.  *If false:* no support remains; stop.
2. C1: The trials included in the systematic reviews are representative of real-world weight loss outcomes in adults  *Look in:* refs 1, 2, 3, 4, 5.  *If false:* at best the conclusion holds only if every study it uses is correct.
3. C2: The modest differences in weight loss (0.94-1.29 kg) reported are clinically meaningful or not meaningful as intended by the conclusion  *Look in:* refs 1, 2.  *If false:* at best the conclusion holds even if any 2 studies are wrong.
4. C3: Short-term advantages (3-6 months) do not translate to long-term superiority of intermittent fasting  *Look in:* refs 3, 5.  *If false:* at best the conclusion holds even if any 2 studies are wrong.
*If all 4 are confirmed:* the conclusion holds even if any 1 study is wrong.

**Studies behind the references**
- S1: Yu et al. 2025 systematic review and network meta-analysis of 99 RCTs (ref 1)
- S2: 2024 systematic review and meta-analysis of 10 RCTs on fasting vs continuous caloric restriction (ref 2)
- S3: Allaf et al. 2021 Cochrane systematic review (ref 3)
- S4: 2018 systematic review and meta-analysis of RCTs on intermittent vs continuous energy restriction (ref 4)
- S5: 2024 network meta-analysis of 47 RCTs on caloric restriction regimens (ref 5)

**Smallest ways the conclusion can lose all support** (24 in total): U1 false; C1, C4 false; C1, C5 false; C1 false and S4 wrong; C1 false and S2 wrong; C1 false and S1 wrong ...

**Not covered by this card**
- Whether each cited passage says what the report claims (citation checks are assumed done).
- Assumptions the report never states, added during reading: U1, U2; a person must accept them.
- References whose study could not be identified: none.

**References matched to indexed papers (Bond)**
- ref 1: [Intermittent fasting strategies and their effects on body weight and other cardiometabolic risk factors: systematic review and network meta-analysis of randomised clinical trials.](https://pubmed.ncbi.nlm.nih.gov/40533200/) (pubmed, via title search)
- ref 2: [Is Fasting Superior to Continuous Caloric Restriction for Weight Loss and Metabolic Outcomes in Obese Adults? A Systematic Review and Meta-Analysis of Randomized Clinical Trials.](https://pubmed.ncbi.nlm.nih.gov/39458528/) (pubmed, via pmc id)
- ref 3: [Intermittent fasting for the prevention of cardiovascular disease.](https://pubmed.ncbi.nlm.nih.gov/33512717/) (pubmed, via title search)
- ref 4: [Intermittent versus continuous energy restriction on weight loss and cardiometabolic outcomes: a systematic review and meta-analysis of randomized controlled trials.](https://pubmed.ncbi.nlm.nih.gov/30583725/) (pubmed, via title search)
- ref 5: [Comparing caloric restriction regimens for effective weight management in adults: a systematic review and network meta-analysis.](https://pubmed.ncbi.nlm.nih.gov/39327619/) (pubmed, via pmc id)

**Literature bearing on each single point of failure (Bond)**
- U1: Systematic reviews and meta-analyses of RCTs provide valid evidence for drawing conclusions about the comparative effectiveness of weight loss interventions (match: high_confidence_match)
    - [Intermittent fasting for adults with overweight or obesity.](https://pubmed.ncbi.nlm.nih.gov/41692034/) (pubmed)
    - [Intermittent fasting interventions for treatment of overweight and obesity in adults: a systematic review and meta-analysis.](https://pubmed.ncbi.nlm.nih.gov/29419624/) (pubmed)
    - [Is Fasting Superior to Continuous Caloric Restriction for Weight Loss and Metabolic Outcomes in Obese Adults? A Systematic Review and Meta-Analysis of Randomized Clinical Trials.](https://pubmed.ncbi.nlm.nih.gov/39458528/) (pubmed, cited by the report)

## heatpump: Do domestic heat pumps reduce heating-related CO2 emissions compared with gas boilers in the UK?

**Conclusion.** Domestic heat pumps generally reduce heating-related CO₂ emissions compared with gas boilers in the UK, although the size of the reduction depends on heat-pump type, seasonal efficiency, electricity carbon intensity, refrigerant impacts, and whether manufacture and installation are included.
**Target.** The conclusion should hold even if any 1 study is wrong (k = 2).

**Status: NOT CERTIFIED yet.**
- If every assumption below holds, the conclusion holds even if any 3 studies are wrong.
- Now: no guarantee yet, since every route still rests on an unchecked assumption.
- Best reachable by checking: the conclusion holds even if any 3 studies are wrong.

**Checklist to reach the target** (4 checks; all must be confirmed; single points of failure first)
1. C1: The 84% emissions reduction in 2024 and comparison with 2014 applies to UK household heating contexts with current electricity grid composition  *Look in:* refs 3, 5, 6.  *If false:* at best the conclusion holds even if any 2 studies are wrong.
2. C3: The UCL lifecycle assessment carbon intensities (0.111 kg CO₂e/kWh for air-source, 0.097 for ground-source, 0.241 for gas boiler) apply to UK conditions and current technology  *Look in:* refs 3, 5, 6.  *If false:* at best the conclusion holds even if any 2 studies are wrong.
3. U1: The lifecycle assessment studies adequately account for all relevant emissions sources (manufacturing, installation, operation, refrigerant leakage, end-of-life) to enable valid comparison  *Look in:* refs 1, 3, 5, 6.  *If false:* at best the conclusion holds only if every study it uses is correct.
4. U2: The gas boiler baseline (200-215 g CO₂/kWh) is representative of typical UK gas boiler systems being replaced  *Look in:* refs 1, 3, 5, 6.  *If false:* at best the conclusion holds only if every study it uses is correct.
*If all 4 are confirmed:* the conclusion holds even if any 1 study is wrong.

**Studies behind the references**
- S1: unknown (refs 1, 2, 4)
- S2: Sevindik et al. 2021 UCL lifecycle assessment (ref 3)
- S3: Sevindik et al. 2021 UCL hybrid heat pump lifecycle assessment (ref 5)
- S4: Carbon Brief 2024 UK electricity analysis (ref 6)

**Smallest ways the conclusion can lose all support** (20 in total): C1, U1 false; C1, U2 false; U1 false and S4 wrong; U2 false and S4 wrong; C1, C3, C4, C5 false; C1, C3, C4 false and ref1 wrong ...

**Not covered by this card**
- Whether each cited passage says what the report claims (citation checks are assumed done).
- Assumptions the report never states, added during reading: U1, U2, U3; a person must accept them.
- References whose study could not be identified: 1.

**References matched to indexed papers (Bond)**
- ref 1: not found in the index: Gas boiler vs heat pump: Which is right for your home?
- ref 2: not found in the index: A Comparative Environmental Assessment of Heat Pumps and Gas Boilers towards a Circular Economy in the UK
- ref 3: not found in the index: Comparative assessment of hybrid heat pumps vs gas boilers in the UK
- ref 4: not found in the index: Life cycle environmental impacts and potential implications for the UK
- ref 5: not found in the index: The running cost of heat pumps
- ref 6: not found in the index: Analysis: UK’s electricity was cleanest ever in 2024

## melatonin: Does melatonin improve sleep quality in adults with chronic insomnia?

**Conclusion.** Melatonin may produce small improvements in some sleep measures, but evidence does not establish a clinically important improvement in overall sleep quality for adults with chronic insomnia, and major guidelines therefore recommend against routine use.
**Target.** The conclusion should hold even if any 1 study is wrong (k = 2).

**Status: NOT CERTIFIED yet.**
- If every assumption below holds, the conclusion holds even if any 3 studies are wrong.
- Now: no guarantee yet, since every route still rests on an unchecked assumption.
- Best reachable by checking: the conclusion holds even if any 3 studies are wrong.

**Checklist to reach the target** (4 checks; all must be confirmed; single points of failure first)
1. U1 [single point of failure]: Lack of clinically important improvement in overall sleep quality is a sufficient basis for recommending against routine use of a treatment  *Look in:* refs 1, 2, 3, 4, 5, 6, 7, 8.  *If false:* no support remains; stop.
2. C3: The 2013 meta-analysis (ref 3) findings on primary sleep disorders do not represent reliable treatment effects specifically for chronic insomnia in adults  *Look in:* refs 3, 4.  *If false:* at best the conclusion holds even if any 2 studies are wrong.
3. C4: The 2021 meta-analysis (ref 4) findings from diverse medical conditions do not represent reliable treatment effects for chronic insomnia specifically  *Look in:* refs 3, 4.  *If false:* at best the conclusion holds even if any 2 studies are wrong.
4. C7: Major clinical guidelines (AASM, NCCIH, VA/DoD) represent current authoritative guidance on melatonin use for chronic insomnia  *Look in:* refs 7, 8.  *If false:* at best the conclusion holds even if any 2 studies are wrong.
*If all 4 are confirmed:* the conclusion holds even if any 1 study is wrong.

**Studies behind the references**
- S1: 2022 systematic review of 24 placebo-controlled randomized trials on melatonin for chronic insomnia (ref 1)
- S2: 2020 systematic review and network meta-analysis of pharmacological and nonpharmacological interventions for insomnia (ref 2)
- S3: Ferracioli-Oda et al. 2013 meta-analysis of melatonin for primary sleep disorders (ref 3)
- S4: 2021 systematic review and meta-analysis of melatonin supplementation on sleep quality in randomized controlled trials (ref 4)
- S5: 2022 systematic review and meta-analysis of melatonin and ramelteon for insomnia in older adults (ref 5)
- S6: American Academy of Family Physicians 2021 review of melatonin for insomnia in older adults (ref 6)
- S7: American Academy of Sleep Medicine 2017 clinical practice guideline for pharmacologic treatment of chronic insomnia in adults (ref 7)
- S8: National Center for Complementary and Integrative Health updated resource on sleep disorders and complementary health approaches (ref 8)

**Smallest ways the conclusion can lose all support** (241 in total): U1 false; C1, C3, C5, C7 false; C1, C3, C5 false and S7 wrong; C1, C3, C5 false and S8 wrong; C1, C3, C6, C7 false; C1, C3, C6 false and S7 wrong ...

**Not covered by this card**
- Whether each cited passage says what the report claims (citation checks are assumed done).
- Assumptions the report never states, added during reading: U1, U2; a person must accept them.
- References whose study could not be identified: none.

**References matched to indexed papers (Bond)**
- ref 1: [Efficacy of melatonin for chronic insomnia: Systematic reviews and meta-analyses.](https://pubmed.ncbi.nlm.nih.gov/36179487/) (pubmed, via title search)
- ref 2: [A Systematic Review and Network Meta-Analysis of Randomized Controlled Trials Evaluating the Evidence Base of Melatonin, Light Exposure, Exercise, and Complementary and Alternative Medicine for Patients with Insomnia Disorder.](https://pubmed.ncbi.nlm.nih.gov/32580450/) (pubmed, via pmc id)
    - check: the report gives this reference as "A Systematic Review and Network Meta-Analysis of Pharmacological and Nonpharmacological Interventions for the Treatment of Insomnia"; the indexed paper's title differs (similarity 0.49). Confirm that the cited paper supports the claim at the report's scope.
- ref 3: [Meta-analysis: melatonin for the treatment of primary sleep disorders.](https://pubmed.ncbi.nlm.nih.gov/23691095/) (pubmed, via pmc id)
- ref 4: [Effect of melatonin supplementation on sleep quality: a systematic review and meta-analysis of randomized controlled trials.](https://pubmed.ncbi.nlm.nih.gov/33417003/) (pubmed, via title search)
- ref 5: [Use of Melatonin and/on Ramelteon for the Treatment of Insomnia in Older Adults: A Systematic Review and Meta-Analysis.](https://pubmed.ncbi.nlm.nih.gov/36079069/) (pubmed, via title search)
- ref 6: [Melatonin to Treat Insomnia in Older Adults.](https://pubmed.ncbi.nlm.nih.gov/34523886/) (pubmed, via title search)
- ref 7: not found in the index: Clinical Practice Guideline for the Pharmacologic Treatment of Chronic Insomnia in Adults
- ref 8: not found in the index: Sleep Disorders and Complementary Health Approaches: Usefulness and Safety

**Literature bearing on each single point of failure (Bond)**
- U1: Lack of clinically important improvement in overall sleep quality is a sufficient basis for recommending against routine use of a treatment (match: ambiguous_match)
    - [Efficacy of melatonin for chronic insomnia: Systematic reviews and meta-analyses.](https://pubmed.ncbi.nlm.nih.gov/36179487/) (pubmed, cited by the report)
    - [Exogenous Melatonin and Sleep Quality: A Scoping Review of Systematic Reviews.](https://pubmed.ncbi.nlm.nih.gov/41014554/) (pubmed)
    - [Use of melatonin for children and adolescents with chronic insomnia attributable to disorders beyond indication: a systematic review, meta-analysis and clinical recommendation.](https://pubmed.ncbi.nlm.nih.gov/37457114/) (pubmed)

