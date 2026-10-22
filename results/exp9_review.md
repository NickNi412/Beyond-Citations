# Experiment 9: condition scopes, for spot checks

## exp4_extract.jsonl / creatine / anthropic/claude-haiku-4.5
bottlenecks before [] -> after []; plan 4 -> 5
- C1 [single]: The user is a healthy adult with no pre-existing kidney disease
- C2 [each_study]: Creatine is used at standard doses, typically 3–5 g/day
- C6 [single]: Elevated serum creatinine from supplementation does not reflect actual kidney damage and should be interpreted with complementary measures
- C7 [each_study]: The study populations in references 1-5 are representative of the healthy adult population to which the conclusion applies
- U1 [single]: Absence of evidence of kidney harm in the studies reviewed constitutes sufficient evidence of safety
- U2 [single]: The distinction between elevated creatinine and actual kidney dysfunction is clinically meaningful and actionable

## exp4_extract.jsonl / creatine / openai/gpt-4.1
bottlenecks before ['R:C1', 'R:C2', 'R:C3', 'R:C4'] -> after ['R:C2', 'R:C3', 'R:C4']; plan 4 -> 5
- C1 [each_study]: The populations, doses, and durations studied in the cited reviews and studies are representative of healthy adults using standard creatine supplementation protocols.
- C2 [single]: The absence of observed kidney dysfunction in the cited studies is sufficient to infer safety for kidney function in healthy adults at standard doses.
- C3 [single]: The increase in serum creatinine observed with creatine supplementation does not reflect actual kidney injury in healthy adults.
- C4 [single]: The findings from studies with durations up to 60 months can be generalized to 'long-term' use as referenced in the conclusion.

## exp4_extract.jsonl / creatine / qwen/qwen3-235b-a22b-2507
bottlenecks before ['R:U1'] -> after ['R:U1']; plan 3 -> 3
- C1 [each_study]: The populations studied in the Antonio 2019 meta-analysis are representative of healthy adults using standard-dose creatine supplementation.
- C2 [each_study]: The populations studied in the 2025 meta-analysis are representative of healthy adults using standard-dose creatine supplementation.
- C3 [each_study]: The study cited in the 2023 review (comparing non-users with users up to 21 months) applies to healthy adults and uses standard creatine dosing protocols.
- C4 [each_study]: The broader safety data summarized in the 2025 safety review apply to healthy adults and cover doses and durations relevant to long-term use.
- C5 [each_study]: The International Society of Sports Nutrition position stand's assessment is based on evidence from healthy adults using creatine monohydrate at commonly studied doses (e.g., up to 30 g/day for five years).
- C6 [single]: The increase in serum creatinine due to creatine supplementation does not reflect actual kidney injury and can be distinguished using alternative markers like cystatin C or clinical context.
- U1 [single]: Standard doses of creatine supplementation (e.g., 3–5 g/day) do not cause structural or functional kidney damage in healthy adults over the long term.

## exp4_extract.jsonl / fasting / anthropic/claude-haiku-4.5
bottlenecks before ['R:U1'] -> after ['R:U1']; plan 4 -> skipped
- C1 [each_study]: The trials included in the systematic reviews are representative of real-world weight loss outcomes in adults
- C2 [each_study]: The modest differences in weight loss (0.94-1.29 kg) reported are clinically meaningful or not meaningful as intended by the conclusion
- C3 [single]: Short-term advantages (3-6 months) do not translate to long-term superiority of intermittent fasting
- C4 [each_study]: When total calorie reduction is matched between intermittent fasting and continuous restriction, the populations, adherence rates, and other variables are sufficiently comparable
- C5 [each_study]: The apparent short-term advantage of some fasting regimens reflects greater energy reduction or adherence rather than a unique metabolic effect of fasting itself
- C6 [single]: Weight regain at 4-6 months reported in reference 5 is representative of longer-term outcomes for intermittent fasting
- U1 [single]: Systematic reviews and meta-analyses of RCTs provide valid evidence for drawing conclusions about the comparative effectiveness of weight loss interventions
- U2 [single]: Statistical significance or lack thereof is an appropriate criterion for determining whether one weight loss method is superior to another

## exp4_extract.jsonl / fasting / openai/gpt-4.1
bottlenecks before ['R:C1', 'R:C2', 'R:C3', 'R:C4', 'R:U1'] -> after ['R:U1']; plan 5 -> skipped
- C1 [each_study]: The populations, interventions, and comparators in the cited trials are sufficiently similar to the general adult population considering weight loss strategies.
- C2 [each_study]: The durations of the trials are long enough to assess meaningful differences in weight loss between intermittent fasting and continuous calorie restriction.
- C3 [each_study]: The calorie intake in the intermittent fasting and continuous restriction arms is comparable in the relevant studies.
- C4 [each_study]: The adherence rates in the studies reflect what would be expected in real-world settings.
- U1 [single]: Weight loss is the primary and sufficient outcome for evaluating the superiority of one dietary strategy over another for adults.

## exp4_extract.jsonl / fasting / qwen/qwen3-235b-a22b-2507
bottlenecks before ['R:U1', 'R:U2'] -> after ['R:U1']; plan 5 -> 6
- C1 [each_study]: The trials in the Oi-Ying Yu et al. 2025 meta-analysis are representative of adult populations seeking weight loss and use comparable energy intake between intermittent and continuous restriction.
- C2 [each_study]: The 2024 Obesity meta-analysis includes trials where fasting and continuous restriction were matched for total caloric intake over time.
- C3 [each_study]: The Cochrane 2021 review includes trials with sufficient duration and adherence to detect differences in weight loss between intermittent fasting and continuous restriction.
- C4 [each_study]: The BMC Endocrine Disorders 2018 meta-analysis compares intermittent and continuous energy restriction under isocaloric conditions.
- C5 [each_study]: The IJBNPA 2024 network meta-analysis reflects real-world adherence patterns and includes trials with accurate reporting of energy intake.
- U1 [single]: Weight loss outcomes from clinical trials generalize to the broader adult population considering weight-loss strategies.
- U2 [each_study]: The definition of 'intermittent fasting' and 'continuous calorie restriction' is consistent across all included studies in the cited reviews.
- U3 [single]: Short-term weight loss differences are indicative of long-term outcomes when adherence is maintained.

## exp4_extract.jsonl / heatpump / anthropic/claude-haiku-4.5
bottlenecks before [] -> after []; plan 4 -> 4
- C1 [each_study]: The 84% emissions reduction in 2024 and comparison with 2014 applies to UK household heating contexts with current electricity grid composition
- C3 [each_study]: The UCL lifecycle assessment carbon intensities (0.111 kg CO₂e/kWh for air-source, 0.097 for ground-source, 0.241 for gas boiler) apply to UK conditions and current technology
- C4 [each_study]: The 30% greenhouse-gas emissions reduction over 20 years applies to the specific hybrid heat pump and condensing gas boiler systems compared
- C5 [each_study]: The UK lifecycle study reporting up to 6% CO₂-equivalent savings for air-source and 36% for water-source systems reflects conditions that are less favorable than current UK electricity and technology conditions
- C6 [single]: The practical variables identified (seasonal coefficient of performance, sizing, installation, flow temperature, building fabric, electricity carbon intensity) are the primary determinants of emissions outcomes
- C7 [single]: A 'well-designed' heat pump with 'correct sizing and installation' and 'increasingly low-carbon UK electricity' represents typical or achievable conditions for UK households
- U1 [each_study]: The lifecycle assessment studies adequately account for all relevant emissions sources (manufacturing, installation, operation, refrigerant leakage, end-of-life) to enable valid comparison
- U2 [each_study]: The gas boiler baseline (200-215 g CO₂/kWh) is representative of typical UK gas boiler systems being replaced
- U3 [single]: Results from peer-reviewed lifecycle studies are generalizable to the broader UK domestic heat pump population

## exp4_extract.jsonl / heatpump / openai/gpt-4.1
bottlenecks before ['R:C3', 'R:C5', 'R:U1'] -> after ['R:C5', 'R:U1']; plan 6 -> skipped
- C1 [each_study]: The heat pumps and gas boilers assessed in the cited studies are representative of those currently installed in UK homes.
- C2 [each_study]: The carbon intensity of UK electricity in the cited studies matches or is relevant to current and near-future UK conditions.
- C3 [each_study]: The seasonal performance factors (efficiency) of heat pumps in the studies are typical of real-world UK installations.
- C4 [each_study]: The lifecycle assessments include all relevant emissions sources (operation, manufacture, refrigerants, etc.) in a comparable way for both heat pumps and gas boilers.
- C5 [single]: The operational and lifecycle emissions reductions found in the cited studies are transferable to the general UK domestic context.
- U1 [single]: Reducing heating-related CO₂ emissions is a desirable or relevant goal for UK domestic heating policy or consumer choice.

## exp4_extract.jsonl / heatpump / qwen/qwen3-235b-a22b-2507
bottlenecks before ['R:C6'] -> after []; plan 6 -> skipped
- C1 [each_study]: The seasonal coefficient of performance (SCOP) of the heat pump is sufficient to maintain low electricity consumption relative to heat output.
- C2 [single]: The UK electricity grid carbon intensity in the time and context of the analysis matches or is similar to the values used in the cited studies (e.g., 2024 levels).
- C3 [each_study]: The heat pump is correctly sized and installed, and operates with appropriate flow temperatures and building insulation levels.
- C4 [each_study]: Manufacturing, refrigerant leakage, and infrastructure emissions for heat pumps are within the ranges assumed in the lifecycle studies cited.
- C5 [each_study]: The gas boiler being compared is a standard condensing gas boiler with typical efficiency and emissions characteristics in the UK context.
- C6 [each_study]: The comparison between heating systems includes the same functional unit (e.g., per kWh of useful heat delivered).
- U1 [each_study]: The electricity carbon intensity used in the Carbon Brief analysis (ref 14 and 6) is representative of the national average for household heating use over the year.
- U2 [single]: The seasonal performance factor (SPF) of 3.0 mentioned in the UK housing analysis (ref 10) is achievable in real-world UK domestic settings.
- U3 [each_study]: The lifecycle studies (refs 3, 5) include all relevant stages: production, operation, refrigerant use, and end-of-life, with UK-relevant data.

## exp4_extract.jsonl / lfp / anthropic/claude-haiku-4.5
bottlenecks before [] -> after []; plan 9 -> skipped
- C1 [single]: The Wilhelm et al. 2018 study's findings on commercial lithium-iron-phosphate/graphite cells' cycle stability up to 10,000 FECs apply to home-storage battery products
- C2 [single]: The Wilhelm et al. 2018 estimate that a typical home-storage system operating for 20 years would experience about 6,000 FECs applies to the systems being evaluated
- C3 [single]: The Omar et al. 2014 experimental findings on LFP battery cycle life at different depths of discharge, temperatures, and charging rates apply to commercial home-storage products
- C4 [each_study]: Pylontech EVOLVE LFP's specification of more than 6,000 cycles at 90% depth of discharge and 25°C is accurate as stated in the datasheet
- C5 [each_study]: GoodWe Lynx A G3's specification of more than 6,000 cycles at 70% remaining capacity end-of-life criterion is accurate as stated in the datasheet
- C6 [each_study]: Deye SE-F12's specification of exactly 6,000 cycles is accurate as stated in the datasheet
- C7 [each_study]: The tested cells in Omar et al. 2014 are representative of LFP chemistry used in commercial home-storage batteries
- U1 [each_study]: The definition of 'full-equivalent cycle' used in the cited studies matches the definition used by the commercial manufacturers cited
- U2 [each_study]: The end-of-life capacity thresholds (70%, 80%, 90%) used in different studies and products are comparable or their differences are accounted for in the comparison

## exp4_extract.jsonl / lfp / openai/gpt-4.1
bottlenecks before ['R:C3', 'R:C4'] -> after []; plan 4 -> 12
- C1 [each_study]: The laboratory-tested cells in Wilhelm 2018 and Omar 2014 are representative of commercial LFP home-storage batteries.
- C2 [each_study]: The cycle-life specifications in the Pylontech, GoodWe, and Deye datasheets reflect actual product performance under typical home-storage conditions.
- C3 [each_study]: The definition of 'full-equivalent cycle' and end-of-life threshold used in the studies and datasheets matches the one in the report's conclusion.
- C4 [each_study]: The operating conditions (depth of discharge, temperature, charge rate) in the cited studies and datasheets are comparable to those in typical home battery use.

## exp4_extract.jsonl / lfp / qwen/qwen3-235b-a22b-2507
bottlenecks before ['R:U3'] -> after []; plan 8 -> skipped
- C1 [each_study]: The tested LFP cells in Wilhelm et al. 2018 are representative of those used in home-storage batteries.
- C2 [each_study]: The operating conditions (depth of discharge, temperature, charge rate) in Wilhelm et al. 2018 match those claimed in the conclusion.
- C3 [each_study]: The end-of-life capacity threshold (80%) in Wilhelm et al. 2018 is consistent with the warranty conditions of commercial products.
- C4 [each_study]: The cycle model and calendar ageing estimates in Wilhelm et al. 2018 apply to real-world home-storage usage patterns over 20 years.
- C5 [each_study]: The LFP cells tested in Omar et al. 2014 are representative of those used in home-storage batteries.
- C6 [each_study]: The depth of discharge (80% and 20%), temperature (25°C and 40°C), and charge rates in Omar et al. 2014 are relevant to typical home-storage operation.
- C7 [single]: The Pylontech EVOLVE LFP battery is representative of high-quality LFP home-storage batteries.
- C8 [each_study]: The stated specification (>6,000 cycles at 90% DoD, 25°C) in the Pylontech datasheet reflects achievable real-world performance under those conditions.
- C9 [single]: The GoodWe Lynx A G3 battery is representative of high-quality LFP home-storage batteries.
- C10 [each_study]: The stated specification (>6,000 cycles with 70% end-of-life threshold) in the GoodWe datasheet reflects achievable real-world performance under test conditions.
- C11 [single]: The Deye/SANA Energy battery specification (exactly 6,000 cycles) is representative of alternative LFP products in the market.
- U1 [each_study]: Manufacturer specifications are accurate and based on standardized test methods.
- U2 [single]: Laboratory results can be generalized to commercial products in real-world conditions.
- U3 [each_study]: The definition of 'home-storage battery' in the studies and datasheets matches the one in the conclusion.

## exp4_extract.jsonl / melatonin / anthropic/claude-haiku-4.5
bottlenecks before ['R:U1'] -> after ['R:U1']; plan 4 -> 5
- C1 [single]: The findings from studies of melatonin in adults with chronic insomnia transfer to the general adult population seeking treatment for chronic insomnia
- C2 [single]: Improvements in sleep-onset latency alone constitute 'small improvements in some sleep measures' rather than clinically important overall sleep quality improvement
- C3 [each_study]: The 2013 meta-analysis (ref 3) findings on primary sleep disorders do not represent reliable treatment effects specifically for chronic insomnia in adults
- C4 [each_study]: The 2021 meta-analysis (ref 4) findings from diverse medical conditions do not represent reliable treatment effects for chronic insomnia specifically
- C5 [single]: Findings from prolonged-release melatonin in adults aged 55+ do not apply to immediate-release, over-the-counter melatonin in the general adult population
- C6 [single]: Findings from older adults do not generalize to the broader adult population with chronic insomnia
- C7 [each_study]: Major clinical guidelines (AASM, NCCIH, VA/DoD) represent current authoritative guidance on melatonin use for chronic insomnia
- U1 [single]: Lack of clinically important improvement in overall sleep quality is a sufficient basis for recommending against routine use of a treatment
- U2 [single]: Statistical significance or effect size measures are appropriate proxies for clinical importance in sleep quality outcomes

## exp4_extract.jsonl / melatonin / openai/gpt-4.1
bottlenecks before ['R:C1', 'R:C2', 'R:C5', 'R:U1'] -> after ['R:C5', 'R:U1']; plan 5 -> skipped
- C1 [each_study]: The populations, doses, and formulations studied in the cited trials and reviews are representative of adults with chronic insomnia in general clinical practice.
- C2 [each_study]: The sleep quality measures used in the cited studies are valid indicators of clinically important improvement.
- C3 [single]: Findings from studies including children, adolescents, older adults, or populations with diverse medical conditions do not generalize to the general adult population with chronic insomnia.
- C4 [each_study]: Guideline recommendations are based on comprehensive and up-to-date reviews of the evidence.
- C5 [single]: Improvements in sleep-onset latency or total sleep time without improvement in overall sleep quality are not clinically important for adults with chronic insomnia.
- U1 [single]: A clinically important improvement in overall sleep quality is necessary for recommending routine use of melatonin in adults with chronic insomnia.

## exp4_extract.jsonl / melatonin / qwen/qwen3-235b-a22b-2507
bottlenecks before [] -> after []; plan 5 -> skipped
- C1 [each_study]: The populations in the studies cited (refs 1, 2, 3, 4) are representative of adults with chronic insomnia.
- C2 [each_study]: The melatonin formulations and doses used in the studies (refs 1, 2, 3, 4) are comparable to those used by the general adult population (e.g., immediate-release, over-the-counter).
- C3 [each_study]: The outcome measures of sleep quality in the studies (refs 1, 2, 3, 4) align with clinically meaningful improvements in overall sleep quality.
- C5 [single]: The positive results in populations with diverse medical conditions (ref 4) do not generalize to adults with chronic insomnia alone.
- C6 [single]: The results from studies on older adults (refs 5, 6) do not generalize to the general adult population with chronic insomnia.
- C7 [each_study]: The inclusion of ramelteon in some studies (ref 5) does not confound the assessment of melatonin's effects.
- C8 [each_study]: The clinical guidelines cited (refs 7, 8) are based on current and comprehensive evidence evaluations relevant to adults with chronic insomnia.
- U1 [single]: Improvements in sleep measures such as sleep-onset latency or total sleep time are not sufficient to constitute clinically important improvement in overall sleep quality.
- U2 [each_study]: Guidelines recommending against melatonin use are based on the same evidence base and interpret it consistently.

## exp4_extract.jsonl / vitd / anthropic/claude-haiku-4.5
bottlenecks before ['R:U1'] -> after ['R:U1']; plan 4 -> 5
- C1 [single]: The findings from trials including participants aged 0-95 years transfer to adults specifically
- C2 [each_study]: The baseline vitamin D concentrations and deficiency thresholds in the trials match clinically relevant definitions of severe deficiency
- C3 [each_study]: The dosing regimens tested (including 400-1,200 IU daily) represent the relevant supplementation strategies for clinical practice
- C4 [single]: Seasonal variation in benefit (spring, autumn, winter) is generalizable across different geographic and climate contexts
- C5 [each_study]: The definition and measurement of acute respiratory infections is consistent across the included trials
- C6 [each_study]: The participants in these trials are representative of generally healthy working-age adults to whom the conclusion applies
- U1 [single]: Meta-analyses and systematic reviews of RCTs provide valid evidence for population-level preventive effects
- U2 [single]: Absence of statistical significance in pooled estimates indicates absence of clinically meaningful effect

## exp4_extract.jsonl / vitd / openai/gpt-4.1
bottlenecks before ['R:C1', 'R:U1'] -> after ['R:C1@2024 systematic review and meta analysis springer unknown authors', 'R:U1@2024 systematic review and meta analysis springer unknown authors']; plan None -> None
- C1 [each_study]: The populations, dosing regimens, and ARI definitions in the cited meta-analyses are sufficiently similar to the general adult population and supplementation practices addressed in the conclusion.
- C2 [each_study]: The lack of statistically significant effect in the recent meta-analyses reflects a true absence of clinically meaningful benefit, rather than limitations of study power or design.
- C3 [single]: The results from studies including children and older adults (as in Martineau 2017) do not directly establish effects in generally healthy working-age adults.
- C4 [single]: Any possible benefit in severely deficient adults or with specific dosing regimens remains uncertain and requires further targeted trials.
- U1 [each_study]: The meta-analyses included all relevant and high-quality randomized controlled trials up to their respective dates.

## exp4_extract.jsonl / vitd / qwen/qwen3-235b-a22b-2507
bottlenecks before ['R:U1'] -> after []; plan 6 -> skipped
- C1 [single]: The effect of vitamin D supplementation on ARIs in children and older adults generalizes to generally healthy working-age adults.
- C2 [each_study]: The dosing regimens studied (e.g., daily 400–1,200 IU) are representative of typical supplementation patterns in the target population.
- C3 [each_study]: The definition and measurement of acute respiratory infections are consistent across the included studies.
- C4 [each_study]: Baseline vitamin D status in participants reflects clinically relevant deficiency levels (e.g., <25 nmol/L).
- C5 [each_study]: The statistical methods used in the meta-analyses appropriately account for heterogeneity and risk of bias across trials.
- C6 [each_study]: The newer large trials included in the 2024 reviews are methodologically sound and representative of the population of interest.
- C7 [single]: The absence of a significant subgroup effect by baseline vitamin D status in the 2024 reviews applies to severely deficient individuals specifically.
- U1 [each_study]: The outcome of 'experiencing at least one ARI' is clinically meaningful and comparable across studies.
- U2 [single]: The biological mechanism by which vitamin D could influence ARI risk operates similarly across different populations and settings.

## exp4_extract_runA.jsonl / creatine / anthropic/claude-haiku-4.5
bottlenecks before ['R:C1', 'R:C2', 'R:U1', 'R:U2'] -> after ['R:U1']; plan 4 -> skipped
- C1 [each_study]: The participants in the cited studies are healthy adults without chronic kidney disease, prior kidney injury, or substantial risk factors for renal impairment
- C2 [each_study]: The creatine doses used in the cited studies are customary or standard maintenance doses (approximately 3-5 g/day)
- C3 [each_study]: The serum creatinine increase observed in the studies reflects creatine metabolism rather than actual kidney injury
- C4 [single]: Glomerular filtration rate (GFR) is a more reliable indicator of true kidney function than serum creatinine in creatine users
- U1 [single]: Long-term safety in the context of this report means a duration and exposure level sufficient to support clinical recommendations for healthy adults
- U2 [each_study]: The studies cited used appropriate methodology and reliable measurements of kidney function

## exp4_extract_runA.jsonl / creatine / openai/gpt-4.1
bottlenecks before ['R:C1', 'R:C2', 'R:C3', 'R:U1'] -> after []; plan 4 -> skipped
- C1 [each_study]: The populations in the cited studies are representative of healthy adults.
- C2 [each_study]: The doses and durations of creatine supplementation in the cited studies match customary doses (e.g., 3–5 g/day) and typical long-term use.
- C3 [each_study]: The kidney function markers used in the studies (e.g., serum creatinine, eGFR) are adequate to detect clinically relevant kidney injury.
- C4 [single]: The findings from studies using creatine monohydrate generalize to all commonly used forms of creatine at customary doses.
- U1 [each_study]: No significant harmful effects on kidney function would have been detected and reported in the studies if they had occurred.

## exp4_extract_runA.jsonl / creatine / qwen/qwen3-235b-a22b-2507
bottlenecks before ['R:C1', 'R:C2'] -> after []; plan 5 -> skipped
- C1 [each_study]: The studies referenced (including those in the 2025 meta-analysis) involve healthy adults.
- C2 [each_study]: Customary doses of creatine (e.g., 3–5 g/day maintenance, up to 20 g/day loading) are used in the studies.
- C3 [each_study]: Kidney function outcomes in the studies are assessed using measures such as serum creatinine and eGFR, and findings are interpreted in light of creatine's known effect on creatinine levels.
- C4 [single]: The absence of significant adverse effects on GFR in short- to medium-term studies (up to 24 months) can be extrapolated to long-term use in healthy adults.
- C5 [each_study]: The populations in the cited reviews and position statements include only healthy adults without pre-existing kidney conditions.
- C6 [single]: The results from creatine monohydrate studies apply to the same form and dosage regimen of creatine supplementation.
- U1 [each_study]: Changes in serum creatinine due to creatine supplementation do not reflect true glomerular filtration rate decline when more accurate measures (e.g., measured GFR, cystatin C) are used.
- U2 [single]: The absence of observed harm in studies of up to 24 months implies safety for longer durations of use in healthy adults.

## exp4_extract_runA.jsonl / fasting / anthropic/claude-haiku-4.5
bottlenecks before [] -> after []; plan 2 -> 2
- C1 [single]: The findings from studies in adults with obesity generalize to adults without obesity
- C2 [single]: Weight loss differences of less than approximately 1 kg are not clinically significant
- C3 [single]: Short-term weight loss outcomes (6-12 months) are representative of long-term outcomes
- C4 [single]: The specific fasting patterns tested (alternate-day fasting, time-restricted eating, 5:2 diets, week-on/week-off) are representative of intermittent fasting approaches generally
- C5 [each_study]: Calorie intake was comparable between intermittent fasting and continuous restriction groups across studies
- U1 [single]: Statistical significance does not necessarily imply clinical significance
- U2 [single]: The timing of calorie restriction (intermittent versus continuous) is not inherently superior to continuous restriction when total calorie reduction is equivalent

## exp4_extract_runA.jsonl / fasting / openai/gpt-4.1
bottlenecks before ['R:C1', 'R:C2', 'R:C3', 'R:C4', 'R:U1'] -> after ['R:U1']; plan 5 -> skipped
- C1 [each_study]: The populations, interventions, and settings in the cited studies are sufficiently similar to the general adult population and typical weight-loss interventions to generalize the findings.
- C2 [each_study]: The durations of the interventions in the cited studies are long enough to assess clinically meaningful weight loss and maintenance.
- C3 [each_study]: The definitions of intermittent fasting and continuous calorie restriction are consistent across studies and match those in the conclusion.
- C4 [each_study]: Adherence rates and total calorie intake are comparable between intermittent fasting and continuous restriction groups in the studies cited.
- U1 [single]: Weight loss differences smaller than 1 kg or not sustained long-term are not clinically important for adults.

## exp4_extract_runA.jsonl / fasting / qwen/qwen3-235b-a22b-2507
bottlenecks before ['R:C2', 'R:C3', 'R:C4'] -> after []; plan 5 -> skipped
- C1 [each_study]: The fasting patterns studied (e.g., alternate-day fasting, 5:2, time-restricted eating) match those in the conclusion population
- C2 [each_study]: The populations in the studies (adults with overweight or obesity) are representative of the general adult population to which the conclusion applies
- C3 [each_study]: Total calorie intake is comparable between intermittent fasting and continuous restriction in the studies
- C4 [each_study]: Weight loss outcomes measured in the studies (e.g., at 6 or 12 months) reflect long-term clinical effectiveness
- C6 [each_study]: The definition of 'clinically significant' weight loss used in the studies aligns with the threshold implied in the conclusion
- U1 [single]: Weight loss differences less than 1 kg are not clinically meaningful
- U2 [single]: Similar improvements in cardiovascular risk factors imply equivalent overall health benefits
- U3 [single]: Results from trials with moderate certainty evidence are sufficient to generalize to broader populations

## exp4_extract_runA.jsonl / heatpump / anthropic/claude-haiku-4.5
bottlenecks before ['R:C1', 'R:U1'] -> after ['R:U1']; plan 4 -> skipped
- C1 [each_study]: The heat pump is air-source (ASHP) or the conclusions apply to the specific heat pump technology studied
- C2 [each_study]: The comparison applies to UK electricity grid carbon intensity at the time of the study
- C3 [each_study]: The building is a typical UK domestic dwelling
- C4 [each_study]: The heat pump is well-installed and properly operated
- C5 [each_study]: The comparison is for the same useful heat output between heat pump and gas boiler
- C6 [each_study]: Building insulation levels are adequate or the conclusion applies to poorly insulated buildings
- C7 [each_study]: The heat pump operates at low flow temperatures
- C8 [single]: The 15-year timeframe in reference 5 is relevant to the conclusion about general emissions reduction
- C9 [each_study]: The electricity emissions factor used reflects current or near-current UK grid carbon intensity
- U1 [single]: Results from individual studies or assessments of specific buildings/systems are generalizable to domestic heat pumps in the UK more broadly

## exp4_extract_runA.jsonl / heatpump / openai/gpt-4.1
bottlenecks before ['R:C1', 'R:C2', 'R:C3', 'R:C4', 'R:U1'] -> after ['R:U1']; plan 5 -> skipped
- C1 [each_study]: The heat pumps and gas boilers assessed in the cited studies are representative of those installed in UK homes.
- C2 [each_study]: The electricity carbon intensity used in the studies matches or is relevant to current or near-future UK grid conditions.
- C3 [each_study]: The buildings in the studies are typical of UK domestic housing stock in terms of insulation and heating demand.
- C4 [each_study]: The operational performance (efficiency, installation quality, flow temperature) of heat pumps in the studies is achievable in real-world UK installations.
- C5 [each_study]: Whole-life emissions estimates in the studies include all relevant factors (manufacture, operation, disposal) and are comparable between technologies.
- C6 [each_study]: The time periods and scenarios modelled in the studies are relevant to current or near-future UK conditions.
- U1 [single]: CO₂ emissions per unit of useful heat delivered is the relevant metric for comparing heating technologies.

## exp4_extract_runA.jsonl / heatpump / qwen/qwen3-235b-a22b-2507
bottlenecks before ['R:C1', 'R:U2'] -> after []; plan 7 -> skipped
- C1 [each_study]: The heat pump efficiency and electricity carbon intensity in the studies match those in typical current UK conditions.
- C2 [each_study]: The building insulation levels in the studies reflect those of the UK housing stock to which the conclusion is applied.
- C3 [each_study]: The operational performance of heat pumps in the studies (e.g., flow temperatures, controls) is representative of real-world installations in the UK.
- C4 [each_study]: The time period of the electricity grid carbon intensity in the studies is comparable to the current or projected UK grid.
- C5 [each_study]: The system boundaries (operational vs. whole-life emissions) in the studies are consistent with the scope of the conclusion.
- C6 [each_study]: The type of heat pump (e.g., air-source, CO₂, water-source) in the study is representative of the domestic heat pumps being considered in the conclusion.
- U1 [single]: The carbon intensity of the UK electricity grid has decreased since 2012 and continues to decrease, making past assessments with higher grid emissions less representative of current conditions.
- U2 [each_study]: The useful heat output (heating demand) is comparable across systems and studies, allowing fair comparison of emissions per unit of useful heat.
- U3 [single]: The lifetime of heat pumps and gas boilers is similar enough that differences in manufacturing and installation emissions do not reverse the operational emissions advantage.

## exp4_extract_runA.jsonl / lfp / anthropic/claude-haiku-4.5
bottlenecks before [] -> after []; plan 4 -> 4
- C1 [each_study]: The LFP cells tested in reference 1 are representative of cells used in home-storage batteries
- C2 [each_study]: The commercial LFP/graphite cells tested in reference 2 are representative of cells used in home-storage batteries
- C3 [single]: The 80% capacity threshold used in references 1 and 2 is a valid end-of-life criterion for home-storage batteries
- C4 [each_study]: The experimental conditions in reference 3 (depth of discharge, temperature, charging rate) are representative of conditions that affect home-storage battery cycle life
- C5 [single]: The DAT Solar LV-BAT-W10.24Ac product (reference 4) is a representative LFP home-storage system
- C6 [single]: The GoodWe Lynx A G3 Series product (reference 5) is a representative LFP home-storage system
- C7 [single]: The NREL modelling in reference 6 applies to residential home-storage conditions
- C8 [single]: Calendar ageing effects modelled in reference 6 are applicable to typical household storage scenarios
- C9 [single]: One full-equivalent cycle per day is a representative usage pattern for household battery cycling
- U1 [single]: Laboratory cycle-life test results transfer to field performance in home installations
- U2 [single]: Manufacturer ratings based on controlled laboratory conditions are credible indicators of product design capability

## exp4_extract_runA.jsonl / lfp / openai/gpt-4.1
bottlenecks before ['R:U1'] -> after ['R:U1']; plan 5 -> skipped
- C1 [single]: Laboratory and modeling results for LFP cells are representative of well-designed commercial home-storage batteries.
- C2 [each_study]: Manufacturer datasheet cycle ratings reflect actual battery performance under typical home use, or at least credible laboratory testing.
- C3 [each_study]: The end-of-life thresholds (e.g., 70% or 80% remaining capacity) used in studies and datasheets are comparable and relevant to home battery users.
- C4 [each_study]: The test conditions (DoD, temperature, charge/discharge rate) in cited studies and datasheets are similar to or at least relevant for typical home battery operation.
- C5 [single]: NREL modeling of commercial cells under residential-storage conditions is applicable to the range of products and climates discussed in the conclusion.
- U1 [single]: The definition of 'well-designed' LFP home batteries includes those tested or rated in the cited studies and datasheets.

## exp4_extract_runA.jsonl / lfp / qwen/qwen3-235b-a22b-2507
bottlenecks before ['R:U1'] -> after []; plan 5 -> skipped
- C1 [each_study]: The LFP cells tested in the NREL 2018 study are representative of those used in home-storage batteries.
- C2 [each_study]: The commercial LFP/graphite cells in the ScienceDirect 2018 study are comparable in design and use to home-storage batteries.
- C3 [each_study]: The experimental conditions in the ScienceDirect 2013 study (e.g., DoD, temperature, charge rate) are relevant to residential battery operation.
- C4 [each_study]: The cycle life ratings in the DAT Solar 2025 datasheet are based on full-equivalent cycles under conditions applicable to typical home use.
- C5 [each_study]: The GoodWe 2026 product specifications reflect tested performance under standardized conditions that allow comparison with other products.
- C6 [each_study]: The NREL 2023 modelling of commercial cells applies to residential storage conditions and accurately captures real-world degradation factors.
- U1 [each_study]: The end-of-life threshold (e.g., 70% or 80% capacity) used in studies and product ratings is consistently applied and comparable across sources.
- U2 [each_study]: Full-equivalent cycles are calculated using a consistent methodology across studies and manufacturer ratings.
- U3 [single]: Laboratory or modelling results can be generalized to real-world home-storage systems with similar operating parameters.

## exp4_extract_runA.jsonl / melatonin / anthropic/claude-haiku-4.5
bottlenecks before [] -> after []; plan 4 -> 6
- C1 [single]: Reference 1's findings from primary sleep disorders transfer to chronic insomnia specifically
- C2 [single]: Reference 2's findings from mixed medical conditions transfer to chronic insomnia specifically
- C3 [each_study]: Reference 3's findings on sleep-onset latency, total sleep time, and sleep efficiency represent the full scope of sleep quality relevant to the conclusion
- C4 [each_study]: Reference 4's characterization of mixed findings and the 3 mg melatonin trial result are representative of the broader evidence base
- C5 [each_study]: The guideline judgments in references 5, 6, and 7 reflect accurate synthesis of underlying evidence
- C6 [single]: Clinical guidance recommendations against routine use (references 5, 6, 7) are appropriate proxies for whether melatonin reliably improves sleep quality
- U1 [single]: Small effect sizes and statistical significance are insufficient for clinical importance or reliable improvement
- U2 [single]: Mixed or inconsistent findings across studies indicate unreliability rather than population heterogeneity requiring subgroup matching

## exp4_extract_runA.jsonl / melatonin / openai/gpt-4.1
bottlenecks before ['R:C1', 'R:C3', 'R:U1'] -> after ['R:C1@aasm 2017 clinical guideline', 'R:C1@acp 2016 clinical guideline', 'R:C1@nccih 2026 evidence summary', 'R:C1@unknown 2022 systematic review sciencedirect s1087079222001058', 'R:C3@aasm 2017 clinical guideline', 'R:C3@acp 2016 clinical guideline', 'R:C3@nccih 2026 evidence summary', 'R:C3@unknown 2022 systematic review sciencedirect s1087079222001058', 'R:U1']; plan None -> skipped
- C1 [each_study]: The populations, doses, and outcome measures in the cited studies and guidelines are sufficiently similar to adults with chronic insomnia as defined in the report's conclusion.
- C2 [each_study]: The lack of significant benefit in the 2022 systematic review (ref 3) is not due to methodological limitations or insufficient statistical power.
- C3 [each_study]: The clinical guidelines (refs 5, 6, 7) accurately reflect and synthesize the current evidence base relevant to chronic insomnia in adults.
- C4 [each_study]: The modest improvements found in meta-analyses (refs 1, 2) are not clinically meaningful for adults with chronic insomnia.
- C5 [each_study]: The evidence summarized by Canada’s Drug Agency (ref 4) is representative of the broader literature on melatonin for chronic insomnia.
- U1 [single]: The absence of consistent, clinically meaningful benefit in systematic reviews and guidelines justifies not recommending routine use of melatonin for chronic insomnia in adults.

## exp4_extract_runA.jsonl / melatonin / qwen/qwen3-235b-a22b-2507
bottlenecks before ['R:U2', 'R:U3'] -> after []; plan 4 -> skipped
- C1 [each_study]: The participants in the Buscemi 2006 meta-analysis (with primary sleep disorders) are representative of adults with chronic insomnia.
- C2 [each_study]: The participants in the Gholizadeh 2021 meta-analysis (including those with various medical conditions) are representative of adults with chronic insomnia.
- C3 [each_study]: The 2022 systematic review (unknown authors) includes sufficient data on sleep quality in adults with chronic insomnia to support a conclusion about melatonin's effectiveness.
- C4 [each_study]: The Canada’s Drug Agency 2022 review accurately summarizes the findings of the included studies, including the trial using 3 mg melatonin in primary insomnia.
- C5 [single]: The American Academy of Sleep Medicine 2017 guideline's assessment of weak evidence against melatonin applies to sleep quality in adults with chronic insomnia.
- C6 [single]: The American College of Physicians 2016 guideline's finding of insufficient evidence applies to melatonin's effect on sleep quality in adults with chronic insomnia.
- C7 [each_study]: The NCCIH 2026 review accurately reflects the overall evidence on melatonin and sleep quality in adults with chronic insomnia.
- U1 [single]: Improvements in surrogate outcomes (e.g., sleep-onset latency, total sleep time) translate to meaningful improvements in overall sleep quality for adults with chronic insomnia.
- U2 [each_study]: The definition of 'chronic insomnia' is consistent across all studies and guidelines cited.
- U3 [each_study]: The doses, formulations, and durations of melatonin used in the studies are comparable to those used in routine clinical practice.

## exp4_extract_runA.jsonl / vitd / anthropic/claude-haiku-4.5
bottlenecks before ['R:U1', 'R:U2'] -> after []; plan 5 -> skipped
- C1 [single]: The findings from meta-analyses of mixed adult and child populations (ref 1) apply to adults specifically
- C2 [single]: Severe vitamin D deficiency is defined as baseline 25-hydroxyvitamin D concentrations below 25 nmol/L
- C3 [single]: Regular dosing without large bolus doses refers to daily or weekly supplementation patterns
- C4 [each_study]: The newer meta-analyses (refs 2, 3, 4) represent more reliable evidence than the earlier meta-analysis (ref 1) due to larger sample sizes and more recent trials
- C5 [each_study]: The lack of subgroup effects in newer analyses (refs 2, 4) indicates that baseline vitamin D status, dosing frequency, treatment duration, and participant characteristics do not meaningfully modify the overall null effect
- C6 [single]: The findings from older adults (ref 5) are representative of the broader adult population
- U1 [each_study]: Acute respiratory infections measured across these studies are comparable in definition and clinical significance
- U2 [each_study]: The randomized controlled trial design in these studies provides valid evidence for causal inference about supplementation effects

## exp4_extract_runA.jsonl / vitd / openai/gpt-4.1
bottlenecks before ['R:C1', 'R:C2', 'R:U1'] -> after []; plan 5 -> skipped
- C1 [each_study]: The populations, dosing regimens, and ARI outcomes in the cited studies are sufficiently similar to the general adult population and supplementation practices addressed in the conclusion.
- C2 [each_study]: The statistical power and methods of the meta-analyses and trials are adequate to detect clinically meaningful effects.
- C3 [single]: The lack of significant subgroup effects in recent meta-analyses applies to adults with severe vitamin D deficiency and to regular versus intermittent dosing.
- C4 [each_study]: The findings from studies including children or mixed populations can be generalized to adults, or are appropriately separated in the analyses.
- U1 [each_study]: The meta-analyses and trials included all relevant and high-quality studies, and publication bias or selective reporting does not substantially affect the results.

## exp4_extract_runA.jsonl / vitd / qwen/qwen3-235b-a22b-2507
bottlenecks before ['R:U1', 'R:U3', 'R:U4'] -> after []; plan 6 -> skipped
- C1 [single]: The effect of vitamin D supplementation observed in the Martineau 2017 meta-analysis, which included both adults and children, applies to adults overall.
- C2 [single]: The effect of vitamin D supplementation observed in the Cochrane 2024 review applies to adults overall.
- C3 [single]: The effect of vitamin D supplementation observed in the Zhang 2024 meta-analysis applies to adults overall.
- C4 [single]: The effect of vitamin D supplementation observed in the Martineau 2024 meta-analysis applies to adults overall.
- C5 [single]: The effect of daily vitamin D supplementation observed in the Bischoff-Ferrari 2023 trial in older adults applies to adults overall.
- C6 [single]: The absence of significant subgroup effects in the Cochrane 2024 review implies no meaningful benefit in any subgroup, including those with severe deficiency or regular dosing.
- C7 [single]: The lack of statistical significance in the Martineau 2024 meta-analysis (p=0.057) implies no clear preventive effect of vitamin D on ARIs in adults overall.
- C8 [single]: The findings from the updated aggregate-data meta-analysis (Martineau 2024) generalize to the population of interest, including those with varying baseline vitamin D levels, dosing regimens, and durations.
- U1 [each_study]: The definition of acute respiratory infection in each study is consistent with the conclusion's meaning of ARI.
- U2 [each_study]: The vitamin D dosing regimens and forms (e.g., D2 vs D3) in the studies are comparable to those that would be used in practice for adults.
- U3 [each_study]: The populations in the studies are representative of the general adult population in terms of health status, geography, and seasonality.
- U4 [each_study]: The outcome measures across studies (e.g., self-reported vs laboratory-confirmed ARI) are sufficiently comparable to allow synthesis.
- U5 [each_study]: The statistical models used in the meta-analyses appropriately account for heterogeneity and potential biases in the included trials.

## exp5_extract.jsonl / creatine / anthropic/claude-opus-5.5
bottlenecks before ['R:U1', 'R:U2'] -> after ['R:U1']; plan 5 -> skipped
- C1 [each_study]: The participants in the studies pooled by the 2019 meta-analysis are healthy adults using standard doses, matching the population and doses in the conclusion.
- C2 [each_study]: The kidney outcomes measured in the 2025 meta-analysis (GFR) are not distorted by the creatine-induced rise in creatinine, for example because GFR was measured or estimated by methods other than serum creatinine, so that 'no adverse GFR effect' reflects real kidney function.
- C3 [each_study]: The participants in the 2025 meta-analysis are healthy adults on standard protocols, matching the conclusion population and doses.
- C4 [each_study]: The athletes in the 21-month comparison study are representative of healthy adults generally.
- C5 [each_study]: The kidney-function markers used (serum and urinary creatinine, urea, eGFR, proteinuria, albuminuria) are sensitive enough to detect clinically relevant renal harm.
- C6 [each_study]: The protocols covered by the 2025 safety review include standard doses (3–5 g/day) in healthy adults, so its null findings apply to the conclusion's setting.
- C7 [single]: The ISSN statement that there is 'no compelling evidence' of kidney dysfunction amounts to positive evidence of safety, not merely an absence of studies.
- C8 [single]: The creatine-induced rise in serum creatinine comes from creatine-to-creatinine conversion and not from reduced filtration.
- U1 [single]: Absence of renal harm over the study durations (at most about 5 years, mostly far shorter) holds for the longer-term use intended by the conclusion.
- U2 [each_study]: The creatine products and forms tested (mainly creatine monohydrate) match the products consumers actually use.

## exp5_extract.jsonl / creatine / google/gemini-3.1-pro-preview
bottlenecks before ['R:C1', 'R:C2', 'R:C3', 'R:U1'] -> after []; plan 4 -> skipped
- C1 [each_study]: The population consists of healthy adults and excludes individuals with pre-existing kidney disease, unexplained abnormal renal tests, dehydration, or concurrent nephrotoxic medication use.
- C2 [each_study]: The durations investigated in the cited studies (e.g., up to 21 months, 60 months, or 5 years) are sufficient to represent and establish 'long-term' safety.
- C3 [each_study]: Standard consumer doses (typically 3-5 g/day) fall within the bounds of safety established by the doses tested in the cited studies (which range up to 80 g/day).
- C4 [each_study]: Elevations in blood creatinine during supplementation are an artifact of creatine metabolism rather than an indicator of actual declining renal function.
- U1 [each_study]: The measured biomarkers (such as glomerular filtration rate, cystatin C, urinalysis, and albuminuria) are valid and reliable indicators of true kidney function and safety.

## exp5_extract.jsonl / creatine / openai/gpt-6.1-sol
bottlenecks before ['R:C1', 'R:C2', 'R:C3', 'R:C4', 'R:U1'] -> after []; plan 5 -> skipped
- C1 [each_study]: The healthy participants represented in the cited evidence are sufficiently representative of the healthy adults covered by the conclusion.
- C2 [each_study]: The formulations and dosing protocols represented in the cited evidence support conclusions about creatine monohydrate at standard doses, typically 3–5 g/day with or without a loading phase.
- C3 [each_study]: The follow-up periods represented in the cited evidence are sufficient to support the report's characterization of long-term safety, without assuming that safety over those periods establishes safety over decades.
- C4 [each_study]: The renal outcomes used in the cited evidence adequately distinguish actual loss of kidney function from supplementation-related increases in creatinine that do not reflect kidney injury.
- U1 [each_study]: The evidence supporting each route has sufficient statistical power and methodological reliability that its failure to detect clinically important renal harm supports likely safety, rather than merely reflecting an inability to detect harm.

## exp5_extract.jsonl / creatine / qwen/qwen3-235b-a22b-thinking-2507
bottlenecks before ['R:C2', 'R:U1', 'R:U2'] -> after ['R:U2']; plan 5 -> skipped
- C1 [each_study]: The populations in the cited studies consist of healthy adults without pre-existing renal conditions, matching the conclusion's target demographic.
- C2 [each_study]: The dosing regimens and supplementation durations investigated in the cited studies adequately cover the 'standard doses' and 'long-term' periods referenced in the conclusion.
- C3 [each_study]: The renal biomarkers used in the cited studies (e.g., serum creatinine, estimated GFR, cystatin C) accurately reflect true kidney health and are not confounded by creatine metabolism.
- C5 [single]: Clinical guidelines for interpreting elevated creatinine (e.g., using cystatin C or clinical context) effectively prevent misdiagnosis, supporting the safety claim despite the biomarker elevation.
- U1 [each_study]: Systematic reviews, meta-analyses, and professional position stands accurately synthesize primary research and provide reliable evidence of safety.
- U2 [single]: The absence of reported renal impairment in controlled trials and observational studies constitutes evidence of physiological safety rather than merely an absence of detected harm.

## exp5_extract.jsonl / fasting / anthropic/claude-opus-5.5
bottlenecks before ['R:C1', 'R:C3', 'R:U1'] -> after ['R:C3', 'R:U1']; plan 7 -> skipped
- C1 [each_study]: The trial participants (mixed health status, including obese adults in ref 2) are representative of adults in general.
- C2 [each_study]: The intermittent-fasting regimens tested (alternate-day fasting, time-restricted eating, 5:2, etc.) represent intermittent fasting as a whole.
- C3 [single]: Results from trials lasting mostly 3–12 months transfer to judgments about longer-term weight loss.
- C4 [each_study]: The continuous-restriction comparator arms in the pooled trials were comparable in total energy intake, so that the 'when energy intake is comparable' claim is supported.
- C5 [single]: Pooled differences of about 1 kg (0.94–1.29 kg) are clinically small enough to count as 'similar' weight loss.
- C6 [each_study]: The non-significant pooled differences (refs 3, 4) reflect a true absence of a meaningful difference rather than insufficient statistical power.
- C7 [single]: Weight outcomes from a Cochrane review framed around cardiovascular disease prevention apply to the weight-loss comparison in adults.
- C8 [each_study]: The network meta-analytic indirect comparisons are valid (transitivity holds), and heterogeneity in duration, calorie targets, health and adherence does not bias the pooled estimates.
- C9 [single]: Ref 5's ranking among caloric restriction regimens, and its weight regain at 4–6 months, applies specifically to intermittent fasting versus continuous restriction.
- C10 [each_study]: The short-term advantage of alternate-day fasting is attributable to greater energy reduction or adherence rather than a fasting-specific metabolic effect.
- C11 [single]: Ref 4's mismatched journal citation (stated as BMC Endocrine Disorders; the URL is Journal of Translational Medicine) identifies the intended 2018 meta-analysis.
- U1 [single]: Adherence and conditions in controlled trials transfer to free-living adults choosing a weight-loss strategy.

## exp5_extract.jsonl / fasting / google/gemini-3.1-pro-preview
bottlenecks before ['R:U1'] -> after ['R:U1']; plan 1 -> 1
- C1 [single]: A statistically significant additional reduction of around 0.94 kg to 1.29 kg is clinically modest/small and does not establish broad superiority.
- C2 [each_study]: The variability in trial duration, calorie targets, participant health, and adherence does not invalidate the comparison but highlights that apparent advantages may reflect energy reduction/adherence rather than fasting itself.
- U1 [single]: The randomized clinical trial populations and settings evaluated in the systematic reviews accurately reflect the outcomes for the general adult population using these weight-loss strategies.

## exp5_extract.jsonl / fasting / openai/gpt-6.1-sol
bottlenecks before ['R:U1'] -> after []; plan 5 -> 6
- C1 [each_study]: The comparisons synthesized in reference 1 are sufficiently comparable across calorie targets, participant health, duration and adherence for its pooled and network estimates to support an overall comparison of fasting with continuous restriction.
- C2 [each_study]: The comparisons in reference 1 either involve comparable actual energy intake or otherwise support extending their findings to the report's equal-energy-intake claim.
- C3 [each_study]: Reference 1's estimated 1.29 kg additional loss with alternate-day fasting is small enough, over the relevant follow-up periods, to qualify as a modest exception rather than broad practical superiority.
- C4 [each_study]: The comparisons in reference 2 either involve comparable actual energy intake or otherwise support extending their findings to the report's equal-energy-intake claim.
- C5 [each_study]: Reference 2's approximately 0.94 kg short-term weight difference is clinically small, and its longer-term follow-up is adequate to support the reported absence of a superior long-term outcome.
- C6 [each_study]: The comparisons in reference 3 either involve comparable actual energy intake or otherwise support extending their findings to the report's equal-energy-intake claim.
- C7 [each_study]: Reference 3's estimates and uncertainty support generally similar weight loss, rather than merely failing to detect a potentially important difference.
- C8 [each_study]: The comparisons in reference 4 either involve comparable actual energy intake or otherwise support extending their findings to the report's equal-energy-intake claim.
- C9 [each_study]: Reference 4's nonsignificant pooled difference of −0.61 kg is sufficiently precise to support generally similar weight loss, rather than merely reflecting insufficient statistical power.
- U1 [each_study]: The populations, fasting regimens and treatment settings represented in the cited trials are sufficiently representative of adult weight-loss practice to justify the report's general conclusion about adults.

## exp5_extract.jsonl / fasting / qwen/qwen3-235b-a22b-thinking-2507
bottlenecks before ['R:C1', 'R:C2', 'R:C3', 'R:U1', 'R:U2'] -> after ['R:C3', 'R:U1', 'R:U2']; plan 7 -> skipped
- C1 [each_study]: The trial participants (predominantly overweight/obese adults) are representative of the general adult population to which the conclusion applies.
- C2 [each_study]: The fasting and continuous restriction protocols in the trials accurately reflect standard implementations of these dietary approaches.
- C3 [single]: A weight loss difference of approximately 1 kg is below the threshold for clinical significance, requiring an assumed cutoff to dismiss superiority.
- C4 [each_study]: The cited trials adequately matched or controlled for total energy intake, ensuring that comparable caloric deficits produce comparable weight loss.
- C5 [each_study]: Follow-up durations of 3–12 months are sufficient to assess long-term efficacy and rule out sustained superiority.
- U1 [single]: Systematic reviews and meta-analyses of randomized controlled trials provide reliable, generalizable evidence for dietary intervention efficacy.
- U2 [single]: Weight loss magnitude is the sole or primary metric for determining the clinical superiority of a weight-loss strategy.

## exp5_extract.jsonl / heatpump / anthropic/claude-opus-5.5
bottlenecks before ['R:U1', 'R:U2'] -> after []; plan 9 -> skipped
- C1 [each_study]: In-text citation [14], which has no entry in the reference list, actually refers to the Carbon Brief 2025 analysis (ref 6), and that source contains the 84%/45% and 0.4 t/1.4 t household figures.
- C2 [each_study]: The heat-pump efficiency and household heat demand assumed in the Carbon Brief calculation represent typical UK domestic installations.
- C3 [single]: The 2024 UK electricity carbon intensity holds for the period the conclusion covers, i.e. the grid does not become materially more carbon-intensive.
- C4 [single]: Including manufacture, installation and refrigerant leakage does not overturn the operational-only emissions advantage.
- C5 [each_study]: In-text citation [3] refers to the UCL circular-economy comparative assessment (ref 2), which reports 0.111/0.097/0.241 kg CO₂e/kWh.
- C6 [each_study]: The electricity mix, efficiencies and equipment assumed in the 2021 UCL LCA match current UK conditions.
- C7 [single]: CO₂-equivalent or greenhouse-gas results (the climate-change impact category) stand for the CO₂ emissions named in the conclusion.
- C8 [each_study]: In-text citation [5] refers to the UCL hybrid heat pump study (ref 3), which reports the 30% reduction over 20 years.
- C9 [single]: Results for a hybrid heat pump (heat pump plus gas boiler) transfer to standalone domestic heat pumps.
- C10 [each_study]: The 20-year system life and the grid trajectory assumed in the hybrid study apply to UK installations.
- U1 [each_study]: The gas boiler used as the comparator in each source (its efficiency and type) represents the boilers that heat pumps actually replace in UK homes.
- U2 [each_study]: Heat pumps deliver the same useful heat and comfort as the boilers they replace, so a lower per-kWh or per-household emission means lower heating emissions.

## exp5_extract.jsonl / heatpump / google/gemini-3.1-pro-preview
bottlenecks before ['R:C2', 'R:U1'] -> after ['R:C2']; plan 4 -> 5
- C1 [each_study]: The seasonal efficiency (coefficient of performance) of the heat pump in practice is high enough to realise the emissions savings.
- C2 [single]: The carbon intensity of the UK electricity grid remains sufficiently low to maintain the operational emissions advantage over gas.
- C3 [each_study]: The lifecycle impacts, including manufacturing, installation, and refrigerant leakage, do not outweigh the operational CO₂ savings.
- U1 [each_study]: The heating demand met by the heat pump is comparable to that of the gas boiler it replaces.

## exp5_extract.jsonl / heatpump / openai/gpt-6.1-sol
bottlenecks before ['R:U1'] -> after []; plan 6 -> skipped
- C1 [each_study]: The electricity carbon intensity, heat-pump seasonal performance and gas-boiler performance used for the reported 2024 operational comparison are representative of ordinary current UK domestic heating.
- C2 [single]: Where the operational comparison is used to support a lifecycle conclusion, additional manufacturing, installation, infrastructure and refrigerant emissions do not reverse the operational advantage.
- C3 [each_study]: The lifecycle assessment giving 0.111 and 0.097 kg CO₂e per kWh of useful heat for heat pumps and 0.241 for gas boilers is correctly identified and actually reports those results; the bibliography entry numbered 3 instead names a hybrid-system comparison.
- C4 [each_study]: The equipment, efficiencies, electricity mix, lifetimes and lifecycle boundaries behind the reported air-source and ground-source results are sufficiently representative of current UK domestic installations.
- C5 [single]: The lifecycle greenhouse-gas reductions expressed in CO₂-equivalent are an appropriate basis for the report's conclusion phrased as a reduction in CO₂ emissions.
- C6 [each_study]: The study reporting a 30% lifecycle greenhouse-gas reduction for a hybrid heat pump is correctly identified and actually reports that result; the bibliography entry numbered 5 instead names a running-cost report.
- C7 [single]: The hybrid heat-pump comparison over a 20-year lifetime can be generalized to the domestic heat pumps and operating lifetimes covered by the conclusion.
- C8 [each_study]: The efficiencies, electricity mix, gas-boiler comparator and lifecycle boundaries used in the hybrid comparison are sufficiently representative of current UK domestic heating.
- C9 [each_study]: Reference 1 ultimately reports the older UK lifecycle assessment and the potential savings of up to 6% for air-source and 36% for water-source systems attributed to it in the report.
- C10 [each_study]: The favourable cases yielding potential savings in the older lifecycle assessment are sufficiently representative, or become sufficiently representative under current UK electricity conditions, to support a general rather than merely possible emissions advantage.
- C11 [each_study]: The older assessment's equipment-manufacturing, refrigerant and efficiency assumptions transfer sufficiently well to current UK domestic heat pumps.
- U1 [each_study]: The heat-pump and gas-boiler alternatives are compared while providing equivalent useful domestic heating service.

## exp5_extract.jsonl / heatpump / qwen/qwen3-235b-a22b-thinking-2507
bottlenecks before ['R:U1', 'R:U2'] -> after ['R:U2']; plan 5 -> 6
- C1 [each_study]: The UK electricity carbon intensity data from 2024 accurately reflects the operational conditions and grid decarbonization trend applicable to the conclusion's timeframe.
- C2 [each_study]: The seasonal performance factor (SPF) or coefficient of performance (COP) values modelled or measured in the cited studies match typical real-world UK heat pump installations.
- C3 [each_study]: The lifecycle boundaries (manufacture, installation, refrigerant leakage, infrastructure) used in the cited assessments are comparable to standard UK heat pump and gas boiler systems.
- C5 [single]: The observed decarbonization of the UK electricity grid between 2014 and 2024 will persist or remain sufficiently low-carbon to sustain the reported operational advantages.
- U1 [each_study]: The scientific methodologies and data collection techniques used in the cited lifecycle assessments and operational analyses are valid, reproducible, and applicable to UK conditions.
- U2 [single]: CO₂ emissions are an appropriate and sufficient metric for determining the overall climate benefit of residential heating systems in this context.

## exp5_extract.jsonl / lfp / anthropic/claude-opus-5.5
bottlenecks before [] -> after []; plan 4 -> 4
- C1 [single]: The EVOLVE LFP product in the datasheet is an LFP home-storage battery.
- C2 [each_study]: The datasheet's '>6,000 cycles at 90% depth of discharge' amounts to more than 6,000 full-equivalent cycles. Taken literally, 6,000 cycles at 90% DoD is about 5,400 FEC.
- C3 [single]: The GoodWe Lynx A G3 is an LFP residential home-storage battery.
- C4 [each_study]: GoodWe's '>6,000 cycles' figure, whose depth of discharge and test conditions are not stated, counts full-equivalent cycles.
- C5 [each_study]: The commercial LFP/graphite cells tested by Wilhelm et al. are representative of the cells used in LFP home-storage batteries.
- C6 [single]: The laboratory cycling conditions in Wilhelm et al. (temperature, C-rate, depth of discharge) transfer to real home-storage operation.
- C7 [single]: Calendar ageing over the service period does not prevent a home battery from reaching more than 6,000 FEC before end of life.
- C8 [single]: The 80%-remaining-capacity end-of-life threshold used for cell-level results matches what counts as the battery 'lasting' in the conclusion.

## exp5_extract.jsonl / lfp / google/gemini-3.1-pro-preview
bottlenecks before ['R:C1', 'R:C2', 'R:C3', 'R:U1'] -> after ['R:C1@omar 2014 study', 'R:C1@wilhelm 2018 study', 'R:C2', 'R:C3@omar 2014 study', 'R:C3@wilhelm 2018 study', 'R:U1@omar 2014 study', 'R:U1@wilhelm 2018 study']; plan None -> None
- C1 [each_study]: The commercial LiFePO4/graphite cells tested in laboratory settings are representative of the LFP chemistry used in commercial home-storage batteries.
- C2 [single]: The dependencies on depth of discharge, temperature, and charge rate observed in the experimental work transfer to real-world residential operating conditions.
- C3 [each_study]: The design life and cycle ratings provided in manufacturer datasheets accurately reflect the specified capabilities of those products.
- U1 [each_study]: The 'cycles' specified in the referenced manufacturer datasheets correspond to 'full-equivalent cycles' as defined in the report.

## exp5_extract.jsonl / lfp / openai/gpt-6.1-sol
bottlenecks before [] -> after []; plan 6 -> 6
- C1 [single]: The EVOLVE LFP specification applies to an LFP battery suitable for residential storage.
- C2 [each_study]: EVOLVE's stated life of more than 6,000 cycles at 90% depth of discharge corresponds to more than 6,000 full-equivalent cycles, rather than merely more than 6,000 partial cycles.
- C3 [each_study]: The EVOLVE rating is interpreted subject to its specified 90% depth of discharge, 25°C temperature, and applicable charge-rate and end-of-life conditions.
- C4 [single]: The Lynx A G3 specification applies to an LFP battery suitable for residential storage.
- C5 [each_study]: GoodWe's stated life of more than 6,000 cycles corresponds to more than 6,000 full-equivalent cycles under the specification's actual depth-of-discharge and capacity-accounting conventions.
- C6 [each_study]: The Lynx A G3 rating is interpreted at its stated 70% remaining-capacity endpoint and subject to its applicable operating and test conditions.

## exp5_extract.jsonl / lfp / qwen/qwen3-235b-a22b-thinking-2507
bottlenecks before ['R:U1', 'R:U2'] -> after []; plan 7 -> skipped
- C1 [each_study]: The cited commercial datasheets accurately reflect current product specifications for high-quality LFP home batteries.
- C2 [each_study]: The cycle counts in the datasheets are measured in full-equivalent cycles (FECs) rather than partial or equivalent cycles.
- C3 [each_study]: The laboratory cells and modeling parameters in the cited studies are representative of commercial LFP chemistry used in home-storage systems.
- C4 [each_study]: The laboratory testing conditions can be scaled or mapped to typical residential home-storage operating profiles.
- C5 [single]: Different end-of-life capacity thresholds (70%, 80%, 90%) cited across sources do not invalidate the comparative claim that cycle life exceeds 6,000 FECs.
- U1 [each_study]: The term 'full-equivalent cycle' (FEC) is defined and measured consistently across academic literature, manufacturer datasheets, and the report's analysis.
- U2 [each_study]: The cited manufacturer datasheets and independent studies employ testing protocols that are directly comparable to residential home-storage usage patterns without undisclosed bias.

## exp5_extract.jsonl / melatonin / anthropic/claude-opus-5.5
bottlenecks before ['R:U1'] -> after ['R:U1']; plan 3 -> 3
- C1 [each_study]: The trials in the 2022 review [1] enrolled adults with chronic insomnia and used melatonin doses and formulations representative of those in the conclusion.
- C2 [each_study]: A non-significant pooled result in [1] reflects a true absence of clinically important benefit rather than insufficient statistical power.
- C3 [each_study]: The melatonin trials in the 2020 network meta-analysis [2] involved adults with chronic insomnia comparable to the population in the conclusion.
- C4 [each_study]: The sleep-quality, wakefulness and insomnia-severity outcomes in [2] adequately capture 'overall sleep quality' as used in the conclusion.
- C5 [single]: A standardized mean difference of 0.22 in sleep quality ([3]) falls below the threshold for clinically important improvement.
- C6 [each_study]: The primary sleep disorder populations in [3] are comparable to adults with chronic insomnia.
- C7 [each_study]: The 2017 AASM guideline [7] still reflects current evidence on melatonin for chronic insomnia, and its recommendation against use rests on a lack of clinically meaningful benefit for sleep quality.
- C8 [each_study]: The reviews and guidelines summarized by NCCIH [8] address adults with chronic insomnia and remain current.
- C9 [each_study]: The positive PSQI findings in [4] come from populations with diverse medical conditions that do not represent adults with chronic insomnia, so they do not transfer to that population.
- C10 [each_study]: The positive older-adult results in [5] are driven by ramelteon or by heterogeneity, not by melatonin's effect in adults with chronic insomnia.
- C11 [single]: The prolonged-release melatonin results in adults aged 55 and older [6] do not transfer to immediate-release over-the-counter melatonin or to the general adult population.
- U1 [single]: No newer or larger trials than those covered by the cited reviews and guidelines show a clinically important improvement in sleep quality with melatonin in adults with chronic insomnia.

## exp5_extract.jsonl / melatonin / google/gemini-3.1-pro-preview
bottlenecks before [] -> after []; plan 0 -> 0
- C1 [each_study]: The populations and medical conditions included in the 2013 and 2021 meta-analyses do not reflect the specific effects of melatonin on general adults with chronic insomnia.
- C2 [single]: Findings from older adults, prolonged-release formulations, or ramelteon do not generalize to the use of immediate-release, over-the-counter melatonin in the general adult population.

## exp5_extract.jsonl / melatonin / openai/gpt-6.1-sol
bottlenecks before [] -> after []; plan 3 -> 3
- C1 [each_study]: The adult populations, melatonin regimens, treatment periods, and insomnia definitions in the 2022 chronic-insomnia review are applicable to adults with chronic insomnia addressed by the conclusion.
- C2 [each_study]: The sleep-onset latency, total sleep time, and sleep-efficiency results in reference 1 adequately inform whether a clinically important improvement in overall sleep quality has been established.
- C3 [each_study]: The nonsignificant findings in reference 1 warrant saying that clinically important benefit is not established, rather than treating nonsignificance as proof that benefit is absent.
- C4 [each_study]: The melatonin evidence in the 2020 network meta-analysis applies to adults with chronic insomnia and to the treatment regimens addressed by the conclusion.
- C5 [each_study]: The sleep-quality and insomnia-severity measures in reference 2 adequately capture the clinically important overall benefit at issue; its sleep-onset improvement does not by itself establish that benefit.
- C12 [each_study]: The AASM recommendation cited in reference 7 applies to routine melatonin treatment of adult chronic insomnia and reflects insufficient evidence of clinically important benefit, rather than an unrelated reason for recommending against treatment.
- C13 [each_study]: The reviews summarized by NCCIH in reference 8 concern populations, melatonin regimens, and sleep-quality outcomes applicable to adults with chronic insomnia.
- C14 [each_study]: NCCIH's account of the AASM and VA/DoD recommendations accurately represents their scope and their stated evidentiary reasons for recommending against melatonin.

## exp5_extract.jsonl / melatonin / qwen/qwen3-235b-a22b-thinking-2507
bottlenecks before ['R:U1'] -> after ['R:U1']; plan 3 -> 4
- C1 [each_study]: The adult populations with chronic insomnia in the 2022 and 2020 systematic reviews (Refs 1, 2) are clinically representative of the general target population.
- C2 [each_study]: The heterogeneous medical conditions and inclusion of primary sleep disorders in Refs 3 and 4 prevent their positive findings from reliably generalizing to adults with chronic insomnia.
- C3 [single]: The observed benefits in older adults or with prolonged-release formulations (Refs 5, 6) do not apply to immediate-release, over-the-counter melatonin for the general adult population.
- C4 [each_study]: The clinical guidelines (Refs 7, 8) accurately reflect the current body of evidence and their recommendations against routine use are directly supported by the cited trials.
- C5 [each_study]: The effect sizes and outcomes reported in the meta-analyses align with established thresholds for clinically important improvement in sleep quality.
- U1 [single]: Systematic reviews, meta-analyses, and professional clinical guidelines provide a valid and reliable basis for determining treatment efficacy and standard-of-care recommendations.

## exp5_extract.jsonl / vitd / anthropic/claude-opus-5.5
bottlenecks before ['R:C1', 'R:C6', 'R:U1'] -> after ['R:C6']; plan 5 -> 7
- C1 [each_study]: Where the newer, larger meta-analyses (refs 2–4) conflict with the earlier positive Martineau 2017 IPD result, the newer pooled estimates are the more reliable guide, with the discrepancy attributable to differences in included trials, methods and newly added large trials.
- C2 [each_study]: The narrow null pooled estimate of ref 2 (RR 0.99, 95% CI 0.97–1.01) reflects absence of a meaningful overall preventive effect, and its exploratory season- and dose-specific benefit does not overturn this.
- C3 [each_study]: The null pooled estimate of ref 3 (RR 0.99, 95% CI 0.97–1.02) reflects absence of a meaningful effect, and its lack of subgroup effects by baseline vitamin D status, dose frequency, duration or health condition is reliable.
- C4 [each_study]: The borderline non-significant pooled estimate of ref 4 (OR 0.94, 95% CI 0.88–1.00; P=0.057) indicates no reliable protection rather than a small real effect.
- C5 [each_study]: The not-yet-peer-reviewed medRxiv preprint (ref 4) reports results that are accurate and stable.
- C6 [single]: Incidence of at least one ARI, the outcome measured in the cited meta-analyses, is the relevant outcome for the conclusion about ARI risk, not severity, duration, hospitalization or mortality.
- U1 [each_study]: The participant populations pooled in refs 2–4, which may include children and older people, are representative of adults, so their overall null results apply to adults specifically.

## exp5_extract.jsonl / vitd / google/gemini-3.1-pro-preview
bottlenecks before ['R:C1', 'R:C2', 'R:U1'] -> after ['R:C1@2024 systematic review and meta analysis springer', 'R:C1@martineau 2017 meta analysis', 'R:C2@2024 systematic review and meta analysis springer', 'R:C2@martineau 2017 meta analysis', 'R:U1']; plan None -> None
- C1 [each_study]: The populations studied in the cited meta-analyses (which may include children and older adults) are sufficiently representative of adults to draw conclusions about adults.
- C2 [each_study]: The newer and larger meta-analyses are more reliable indicators of the true effect than the earlier meta-analysis.
- U1 [single]: A lack of statistical significance for overall protection in a meta-analysis implies that the intervention does not consistently reduce the risk.

## exp5_extract.jsonl / vitd / openai/gpt-6.1-sol
bottlenecks before ['R:C5', 'R:C6', 'R:U1'] -> after ['R:C6']; plan 7 -> 9
- C1 [each_study]: The populations included in the 43-trial meta-analysis permit its overall findings to inform prevention in adults, rather than being driven by results in children or other populations that differ materially from adults generally.
- C2 [each_study]: The supplementation regimens, baseline vitamin D distributions, and settings represented in the 43-trial meta-analysis adequately inform population-wide supplementation in adults.
- C3 [each_study]: The populations included in the 46-trial meta-analysis permit its overall findings to inform prevention in adults, rather than being driven by results in children or other populations that differ materially from adults generally.
- C4 [each_study]: The supplementation regimens, baseline vitamin D distributions, and settings represented in the 46-trial meta-analysis adequately inform population-wide supplementation in adults.
- C5 [each_study]: The measured ARI outcomes are sufficiently comparable to whether adults experience an infection; findings about incidence are not being transferred to severity, duration, hospitalization, or mortality.
- C6 [single]: The near-null pooled results and their uncertainty justify withholding a claim of dependable population-wide prevention, without requiring that every subgroup or regimen have exactly zero benefit.
- U1 [each_study]: Bias in the included trials, selective reporting, and errors in evidence synthesis are not large enough to overturn the interpretation of the cited pooled results.

## exp5_extract.jsonl / vitd / qwen/qwen3-235b-a22b-thinking-2507
bottlenecks before ['R:C5', 'R:U1', 'R:U2'] -> after ['R:C5@2024 springer systematic review and meta analysis', 'R:U1@2024 springer systematic review and meta analysis', 'R:U2@2024 springer systematic review and meta analysis']; plan None -> skipped
- C1 [each_study]: The subgroup of participants with baseline 25-hydroxyvitamin D <25 nmol/L in the 2017 IPD meta-analysis is clinically comparable to adults with severe vitamin D deficiency.
- C2 [each_study]: The 2024 systematic reviews and meta-analyses (Refs 2–4) include a complete, unbiased set of trials relevant to adult ARI prevention.
- C3 [each_study]: The exploratory finding of a small benefit for daily 400–1,200 IU doses in spring, autumn, or winter (Ref 2) reflects a true causal effect rather than chance or subgroup fishing.
- C4 [single]: The absence of significant subgroup effects for baseline status, dose frequency, and treatment duration in Ref 3 applies to the dosing schedules and deficiency states discussed in the conclusion.
- C5 [each_study]: The statistical pooling methods and heterogeneity assessments used in the cited meta-analyses appropriately account for differences in trial design, follow-up duration, and ARI case definitions.
- U1 [each_study]: The randomized controlled trials included in the cited meta-analyses are methodologically rigorous with a low overall risk of bias.
- U2 [each_study]: The meta-analytic statistical models correctly handle between-trial heterogeneity and publication bias.

