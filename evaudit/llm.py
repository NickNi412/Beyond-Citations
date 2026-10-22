"""OpenRouter calls with a hard spending cap.

The API key is read from the environment or an env file and is never printed or written to disk.
Every call asks OpenRouter to report its cost; the Budget stops further calls once the cap is reached.
"""
import json
import threading
import time

URL = "https://openrouter.ai/api/v1/chat/completions"


class BudgetExceeded(RuntimeError):
    pass


class Budget:
    """Thread-safe running total of reported cost, in US dollars."""

    def __init__(self, cap_usd):
        self.cap, self.spent, self.calls, self._lock = cap_usd, 0.0, 0, threading.Lock()

    def check(self):
        with self._lock:
            if self.spent >= self.cap:
                raise BudgetExceeded(f"spending cap ${self.cap:.2f} reached (spent ${self.spent:.3f})")

    def add(self, usage, fallback_price=None):
        cost = usage.get("cost")
        if cost is None and fallback_price:   # (input $/M, output $/M) when the provider reports no cost
            cost = (usage.get("prompt_tokens", 0) * fallback_price[0]
                    + usage.get("completion_tokens", 0) * fallback_price[1]) / 1e6
        with self._lock:
            self.spent += float(cost or 0.0)
            self.calls += 1
            return self.spent


def call(model, prompt, key, budget, temperature=0.0, max_tokens=1500, timeout=300, retries=5,
         fallback_price=None, reasoning=None):
    """Returns (text, usage). Raises BudgetExceeded before a call once the cap is reached."""
    import requests

    budget.check()
    body = {"model": model, "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}], "usage": {"include": True}}
    if temperature is not None:          # some reasoning models accept no temperature
        body["temperature"] = temperature
    if reasoning:                        # OpenRouter's unified reasoning setting, e.g. "medium"
        body["reasoning"] = {"effort": reasoning}
    err = "no response"
    for attempt in range(retries):
        try:
            r = requests.post(URL, headers={"Authorization": f"Bearer {key}"}, json=body, timeout=timeout)
            if r.status_code == 200:
                j = r.json()
                msg = j["choices"][0]["message"]
                usage = j.get("usage", {}) or {}
                budget.add(usage, fallback_price)
                usage["finish_reason"] = j["choices"][0].get("finish_reason")
                return msg.get("content") or "", usage
            if r.status_code == 402:
                raise BudgetExceeded("OpenRouter reports insufficient credit (HTTP 402)")
            if r.status_code in (408, 429, 500, 502, 503, 504):
                time.sleep(2 ** attempt)
                continue
            return f"HTTP {r.status_code}: {r.text[:300]}", {}
        except BudgetExceeded:
            raise
        except Exception as e:  # network hiccup
            err = type(e).__name__
            time.sleep(2 ** attempt)
    return f"ERROR: {err}", {}


def last_object(text, key):
    """The last top-level JSON object in a reply that contains `key` (models sometimes revise their answer)."""
    dec, objs, i = json.JSONDecoder(), [], 0
    text = text or ""
    while True:
        j = text.find("{", i)
        if j < 0:
            break
        try:
            o, end = dec.raw_decode(text, j)
            objs.append(o)
            i = end
        except json.JSONDecodeError:
            i = j + 1
    objs = [o for o in objs if isinstance(o, dict) and key in o]
    return objs[-1] if objs else None
