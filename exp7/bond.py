"""Minimal client for Valency's MCP Bond (streamable HTTP, JSON-RPC), using only `requests`.

The token is read from the environment (VALENCY_TOKEN) or an env file and is never printed or written to disk.

  python -m exp7.bond probe --env-file .env      # lists Bond's tools with their input schemas -> results/bond_tools.json
                                                 # and calls list_sources            -> results/bond_sources.json
"""
import argparse
import itertools
import json
import os
import sys
from pathlib import Path

URL = "https://mcp.valency.io/"
ROOT = Path(__file__).resolve().parents[1]


def load_token(env_file=None):
    if os.environ.get("VALENCY_TOKEN"):
        return os.environ["VALENCY_TOKEN"]
    if env_file:
        for line in Path(env_file).expanduser().read_text().splitlines():
            if line.strip().startswith("VALENCY_TOKEN"):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("No VALENCY_TOKEN found (environment or --env-file). Copy it from app.valency.io/settings.")


class Bond:
    def __init__(self, token, timeout=120):
        import requests
        self.s, self.timeout, self.ids = requests.Session(), timeout, itertools.count(1)
        self.s.headers.update({"Authorization": f"Bearer {token}", "Content-Type": "application/json",
                               "Accept": "application/json, text/event-stream"})
        r = self._post({"jsonrpc": "2.0", "id": next(self.ids), "method": "initialize",
                        "params": {"protocolVersion": "2025-11-25", "capabilities": {},
                                   "clientInfo": {"name": "evidence-audit", "version": "0.1"}}})
        sid = r.headers.get("Mcp-Session-Id") or r.headers.get("mcp-session-id")
        if sid:
            self.s.headers["Mcp-Session-Id"] = sid
        self.server = self._result(r)
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def _post(self, body):
        r = self.s.post(URL, json=body, timeout=self.timeout)
        if r.status_code >= 400:
            raise RuntimeError(f"Bond HTTP {r.status_code}: {r.text[:300]}")
        return r

    @staticmethod
    def _result(r):
        text = r.text
        if "text/event-stream" in r.headers.get("Content-Type", ""):
            msgs = [json.loads(l[5:].strip()) for l in text.splitlines() if l.startswith("data:") and l[5:].strip()]
            msgs = [m for m in msgs if "result" in m or "error" in m]
            if not msgs:
                raise RuntimeError("Bond: empty event stream")
            j = msgs[-1]
        else:
            j = json.loads(text)
        if "error" in j:
            raise RuntimeError(f"Bond error: {j['error']}")
        return j["result"]

    def tools(self):
        return self._result(self._post({"jsonrpc": "2.0", "id": next(self.ids), "method": "tools/list"}))["tools"]

    def call(self, name, **arguments):
        res = self._result(self._post({"jsonrpc": "2.0", "id": next(self.ids), "method": "tools/call",
                                       "params": {"name": name, "arguments": arguments}}))
        out = []
        for c in res.get("content", []):
            if c.get("type") == "text":
                try:
                    out.append(json.loads(c["text"]))
                except json.JSONDecodeError:
                    out.append(c["text"])
        if res.get("structuredContent") is not None:
            return res["structuredContent"]
        return out[0] if len(out) == 1 else out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["probe"])
    ap.add_argument("--env-file")
    a = ap.parse_args()
    b = Bond(load_token(a.env_file))
    (ROOT / "results").mkdir(exist_ok=True)
    tools = b.tools()
    json.dump(tools, open(ROOT / "results" / "bond_tools.json", "w"), indent=1)
    print(f"server: {b.server.get('serverInfo')}; {len(tools)} tools -> results/bond_tools.json")
    src = b.call("list_sources")
    json.dump(src, open(ROOT / "results" / "bond_sources.json", "w"), indent=1, default=str)
    print("list_sources -> results/bond_sources.json")
    print(json.dumps(src, default=str)[:800])


if __name__ == "__main__":
    main()
