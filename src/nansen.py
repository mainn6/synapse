"""Nansen on-chain intelligence client — Synapse's perception layer.

Reads NANSEN_API_KEY from the environment (.env). Wraps the smart-money
endpoints the agent uses to see what smart money is doing on-chain.
"""
from __future__ import annotations

import os

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.nansen.ai/api/v1"
API_KEY = os.getenv("NANSEN_API_KEY")


def _post(path: str, payload: dict) -> dict:
    if not API_KEY:
        raise RuntimeError("NANSEN_API_KEY not set — copy .env.example to .env")
    resp = requests.post(
        f"{BASE_URL}{path}",
        headers={"apiKey": API_KEY, "Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def smart_money_tokens(chains=None, timeframe="24h", per_page=100):
    """Token screener: what smart money is buying, ranked by buy volume."""
    payload = {
        "chains": chains or ["ethereum", "solana", "base"],
        "timeframe": timeframe,
        "filters": {
            "only_smart_money": True,
            "token_age_days": {"min": 1, "max": 365},
        },
        "order_by": [{"field": "buy_volume", "direction": "DESC"}],
        "pagination": {"page": 1, "per_page": per_page},
    }
    return _post("/token-screener", payload).get("data", [])


def smart_money_netflow(chains=None):
    """Net capital flow from smart money, by chain."""
    return _post("/smart-money/netflow", {"chains": chains or ["ethereum", "base", "solana"]})


if __name__ == "__main__":
    tokens = smart_money_tokens()
    print(f"Smart money — top {min(10, len(tokens))} tokens by 24h buy volume:\n")
    for t in tokens[:10]:
        sym = str(t.get("token_symbol", "?"))[:14]
        chain = t.get("chain", "?")
        net = t.get("netflow")
        traders = t.get("nof_traders")
        chg = t.get("price_change")
        chg_s = f"{chg * 100:+.1f}%" if isinstance(chg, (int, float)) else "n/a"
        print(f"  {sym:<14} {chain:<9} netflow={net}  traders={traders}  24h={chg_s}")
