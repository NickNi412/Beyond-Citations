"""Experiment 3 — shared conditions. Builds short report excerpts with known support structure.

Each base scenario (domain x source structure) yields four items with the SAME source projection:
  shared_same      one condition needed by every route, stated in the same words in each route
  shared_para      one condition needed by every route, worded differently in each route
  separate_diss    a different condition for each route, dissimilar wording
  separate_sim     a different condition for each route, deliberately similar wording
In the separate variants the evidence is about the product itself (sep_sub), so the routes share no unstated
premise; in the shared variants the product-formulation link is the stated shared condition.
Ground truth: witnesses over studies + conditions; a condition is identified by the set of routes it guards.

  python -m exp3.generate --out data/exp3/items.jsonl
"""
import argparse
import json
import random

DOMAINS = [
    dict(key="conductivity", sep_sub=[('formulation E-12', 'Voltrex-7')], direct_extra="the electrodes were cleaned between measurements", M="electrolyte product Voltrex-7", E="formulation E-12", prop="ionic conductivity",
         claim="Voltrex-7 has an ionic conductivity above 10 mS/cm at 25 °C",
         direct="measured formulation E-12 at 25 °C and found {v} mS/cm", vals=["12.1", "11.4", "13.0"],
         other="measured formulation E-12 at 40 °C and found 12.0 mS/cm",
         conv="gives a temperature correction calibrated for formulation E-12 (multiply 40 °C values by 0.9), which yields 10.8 mS/cm at 25 °C",
         shared=["Voltrex-7 is made with formulation E-12",
                 "the commercial product Voltrex-7 uses the same formulation that was tested, E-12",
                 "formulation E-12 is what is sold as Voltrex-7"],
         sep_diss=["the samples were stored below 30 °C before testing",
                   "the correction factor applies within Voltrex-7's salt concentration range",
                   "the conductivity cell was calibrated against a standard solution"],
         sep_sim="the batch tested in {S} matches the Voltrex-7 production specification"),
    dict(key="drug", sep_sub=[('compound CX-4 at 200 mg', 'Calmora tablets'), ('compound CX-4 at 400 mg', 'a double dose of Calmora'), ('for CX-4', 'for Calmora'), ('at 200 mg', 'at the standard dose')], direct_extra="the trial excluded patients with chronic pain", M="the over-the-counter tablet Calmora", E="compound CX-4 at 200 mg", prop="pain relief",
         claim="Calmora reduces post-operative pain scores by at least 20%",
         direct="tested compound CX-4 at 200 mg after surgery and found a {v}% reduction in pain scores", vals=["27", "24", "31"],
         other="tested compound CX-4 at 400 mg and found a 38% reduction in pain scores",
         conv="reports a dose-response curve for CX-4 indicating that halving the dose retains about 60% of the effect, which implies about 23% at 200 mg",
         shared=["each Calmora tablet delivers compound CX-4 at 200 mg",
                 "the dose a patient receives from one Calmora tablet is 200 mg of CX-4",
                 "200 mg of CX-4 is exactly what one Calmora tablet contains"],
         sep_diss=["the trial's pain scale was administered by blinded staff",
                   "the dose-response curve holds for adults under 65",
                   "patients in the trial did not take other analgesics"],
         sep_sim="the patient group in {S} is comparable to Calmora's intended users"),
    dict(key="crop", sep_sub=[('line HL-3', 'Harvela'), ('for HL-3', 'for Harvela')], direct_extra="the trial sites had typical rainfall for the region", M="the seed variety Harvela", E="line HL-3", prop="yield",
         claim="Harvela yields more than 6 tonnes per hectare in temperate climates",
         direct="grew line HL-3 in temperate field trials and recorded {v} t/ha", vals=["6.8", "6.5", "7.1"],
         other="grew line HL-3 in greenhouse trials and recorded 8.0 t/ha",
         conv="gives a field-to-greenhouse ratio for HL-3 of 0.8, which implies 6.4 t/ha in the field",
         shared=["Harvela is the commercial name of line HL-3",
                 "the seed sold as Harvela is genetically the same as line HL-3",
                 "line HL-3 is the variety marketed as Harvela"],
         sep_diss=["the trial plots received standard fertiliser rates",
                   "the greenhouse-to-field ratio applies to cereal crops of this maturity group",
                   "the harvest was measured at standard moisture content"],
         sep_sim="the seed lot used in {S} is representative of Harvela as sold"),
    dict(key="battery", sep_sub=[('cell type LF-21', 'CellMax 20 packs'), ('LF-21 cells', 'CellMax 20 packs')], direct_extra="the cells were not pre-conditioned before cycling", M="the power bank CellMax 20", E="cell type LF-21", prop="cycle life",
         claim="CellMax 20 retains 80% capacity after 1000 cycles",
         direct="cycled cell type LF-21 at 1C and found {v}% capacity after 1000 cycles", vals=["84", "82", "86"],
         other="cycled cell type LF-21 at 0.5C and found 90% capacity after 1000 cycles",
         conv="gives a rate correction for LF-21 cells of 0.92 from 0.5C to 1C, which implies 83% at 1C",
         shared=["CellMax 20 is built from LF-21 cells",
                 "the cells inside CellMax 20 are of type LF-21",
                 "LF-21 is the cell type used in CellMax 20"],
         sep_diss=["the cycling was done at room temperature",
                   "the rate correction holds for cells cycled between 20 and 30 °C",
                   "capacity was measured with the standard discharge protocol"],
         sep_sim="the cells tested in {S} come from the same supplier lot as CellMax 20"),
    dict(key="emissions", sep_sub=[('motor model DM-9', 'the Transit-E van'), ('DM-9 drivetrains', 'the Transit-E van')], direct_extra="the climate control was switched off during the test", M="the delivery van Transit-E", E="motor model DM-9", prop="energy use",
         claim="Transit-E uses less than 25 kWh per 100 km in urban driving",
         direct="tested motor model DM-9 on an urban cycle and measured {v} kWh/100 km", vals=["22.5", "23.1", "21.8"],
         other="tested motor model DM-9 on a highway cycle and measured 27.0 kWh/100 km",
         conv="gives an urban-to-highway factor for DM-9 drivetrains of 0.85, which implies 23.0 kWh/100 km in town",
         shared=["Transit-E is fitted with motor model DM-9",
                 "the motor in the Transit-E is a DM-9",
                 "DM-9 is the drivetrain installed in Transit-E"],
         sep_diss=["the test vehicle carried a standard payload",
                   "the urban-to-highway factor applies to vans under 3.5 tonnes",
                   "the test was run with tyres at nominal pressure"],
         sep_sim="the vehicle tested in {S} has the same battery pack as Transit-E"),
    dict(key="concrete", sep_sub=[('mix design C35-R cylinders', 'cylinders of PB-40 production concrete'), ('for C35-R', 'for PB-40 production concrete')], direct_extra="the cylinders were capped according to the standard", M="the precast beam PB-40", E="mix design C35-R", prop="strength",
         claim="PB-40 beams reach a compressive strength above 35 MPa at 28 days",
         direct="tested mix design C35-R cylinders at 28 days and found {v} MPa", vals=["38.2", "37.0", "39.5"],
         other="tested mix design C35-R cylinders at 7 days and found 26.0 MPa",
         conv="gives a 7-to-28-day maturity factor for C35-R of 1.4, which implies 36.4 MPa at 28 days",
         shared=["PB-40 beams are cast from mix design C35-R",
                 "the concrete in PB-40 beams follows the C35-R mix",
                 "mix design C35-R is the one used to cast PB-40"],
         sep_diss=["the cylinders were cured in water at 20 °C",
                   "the maturity factor holds for cement of strength class 42.5",
                   "the testing machine was calibrated within the last year"],
         sep_sim="the cylinders tested in {S} were cast on the PB-40 production line"),
]
STUDY_NAMES = ["Okafor et al. (2021)", "Lindqvist and Haas (2019)", "Mbeki et al. (2022)",
               "Tanaka et al. (2020)", "Ruiz and Chen (2023)", "Abara et al. (2018)"]
STRUCTURES = {"a|b": [["A"], ["B"]], "a|bc": [["A"], ["B", "C"]], "a|b|c": [["A"], ["B"], ["C"]]}
VARIANTS = ["shared_same", "shared_para", "separate_diss", "separate_sim"]


def build(dom, struct, variant, rng):
    routes = STRUCTURES[struct]
    letters = sorted({s for r in routes for s in r})
    names = dict(zip(letters, rng.sample(STUDY_NAMES, len(letters))))
    passages, pid = [], {}
    vi = iter(dom["vals"])
    def ev(text):
        # In separate variants the studies test the product itself, so no unstated bridge premise
        # ("the tested formulation is the product") is shared by all routes. In shared variants that bridge
        # is exactly the stated shared condition.
        if variant.startswith("separate"):
            for a_, b_ in dom["sep_sub"]:
                text = text.replace(a_, b_)
        return text

    for r in routes:
        if len(r) == 1:
            s = r[0]
            pid[s] = f"P{len(passages) + 1}"
            passages.append(f"[{pid[s]}] Study {s} ({names[s]}) {ev(dom['direct'].format(v=next(vi)))}.")
        else:
            b, c = r
            pid[b] = f"P{len(passages) + 1}"
            passages.append(f"[{pid[b]}] Study {b} ({names[b]}) {ev(dom['other'])}.")
            pid[c] = f"P{len(passages) + 1}"
            passages.append(f"[{pid[c]}] Study {c} ({names[c]}) {ev(dom['conv'])}.")
    conds, lines = [], []
    for i, r in enumerate(routes):
        if variant == "shared_same":
            text, cid = dom["shared"][0], "r"
        elif variant == "shared_para":
            text, cid = dom["shared"][i % 3], "r"
        elif variant == "separate_diss":
            pool = [dom["sep_diss"][0], dom["sep_diss"][2], dom["direct_extra"]]
            text = dom["sep_diss"][1] if len(r) > 1 else pool[i]
            cid = f"r{i + 1}"
        else:
            text, cid = dom["sep_sim"].format(S=" and ".join(f"Study {s}" for s in r)), f"r{i + 1}"
        conds.append(cid)
        refs = " and ".join(f"[{pid[s]}]" for s in r)
        how = "Directly from" if len(r) == 1 else "Combining the measurement and the correction in"
        lines.append(f"Route {i + 1}: {how} {refs}, the claim follows. This route assumes that {text}.")
    report = (f"Report excerpt on {dom['M']}.\nClaim: {dom['claim']}.\n\nEvidence:\n" + "\n".join(passages) +
              "\n\nReasoning:\n" + "\n".join(lines))
    truth_routes = [{"route": i + 1, "studies": r, "condition": c} for i, (r, c) in enumerate(zip(routes, conds))]
    return {"report": report, "routes": truth_routes, "studies": names}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/exp3/items.jsonl")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    rows = []
    for dom in DOMAINS:
        for struct in STRUCTURES:
            for variant in VARIANTS:
                it = build(dom, struct, variant, rng)
                rows.append({"id": f"{dom['key']}-{struct}-{variant}", "domain": dom["key"], "structure": struct,
                             "variant": variant, "shared": variant.startswith("shared"), **it})
    rng.shuffle(rows)
    with open(a.out, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{len(rows)} items -> {a.out}")


if __name__ == "__main__":
    main()
