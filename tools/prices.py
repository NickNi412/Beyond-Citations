"""Current OpenRouter prices for given models, and a rough cost estimate for Round 8.

  python -m tools.prices anthropic/claude-opus-5.5 openai/gpt-5.5 google/gemini-3.1-pro-preview
No API key needed (public model list).
"""
import json
import sys

import requests

# Rough per-call token budgets (input, output incl. reasoning), from the Qwen-thinking runs of Rounds 6.
CALLS = {"exp5 extract (6 calls)": (6, 1400, 7000), "exp5 audit (12 calls)": (12, 1400, 6000),
         "exp3 direct_ex (72 calls)": (72, 700, 9000)}


def main():
    ids = sys.argv[1:]
    data = requests.get("https://openrouter.ai/api/v1/models", timeout=60).json()["data"]
    by = {m["id"]: m for m in data}
    for i in ids:
        m = by.get(i)
        if not m:
            print(f"{i}: NOT FOUND on OpenRouter")
            continue
        pin, pout = float(m["pricing"]["prompt"]) * 1e6, float(m["pricing"]["completion"]) * 1e6
        params = m.get("supported_parameters", [])
        print(f"{i}: ${pin:.2f}/M in, ${pout:.2f}/M out; context {m.get('context_length')}; "
              f"reasoning={'reasoning' in params}; temperature={'temperature' in params}")
        for name, (n, tin, tout) in CALLS.items():
            print(f"    {name}: ~${n * (tin * pin + tout * pout) / 1e6:.2f}")


if __name__ == "__main__":
    main()
