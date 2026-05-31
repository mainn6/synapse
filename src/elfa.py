"""Elfa real-time awareness client — Synapse's narrative/signal layer.

Reads ELFA_API_KEY from env. Surfaces social mention momentum that
complements Nansen smart-money flows (does narrative back the money?).
"""
from __future__ import annotations

import os

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.elfa.ai/v2"
API_KEY = os.getenv("ELFA_API_KEY")


def _get(path: str, params: dict | None = None) -> dict:
    if not API_KEY:
        raise RuntimeError("ELFA_API_KEY not set — copy .env.example to .env")
    resp = requests.get(
        f"{BASE_URL}{path}",
        headers={"x-elfa-api-key": API_KEY},
        params=params or {},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def trending_tokens(time_window: str = "24h", limit: int = 20) -> list:
    """Tokens ranked by social mention momentum (narrative signal)."""
    data = _get("/aggregations/trending-tokens",
                {"timeWindow": time_window, "pageSize": limit})
    return data.get("data", {}).get("data", [])


if __name__ == "__main__":
    print("Elfa — trending tokens by mention momentum (24h):\n")
    for t in trending_tokens(limit=10):
        sym = str(t.get("token", "?")).upper()
        cnt = t.get("current_count")
        chg = t.get("change_percent")
        chg_s = f"{chg:+.0f}%" if isinstance(chg, (int, float)) else "n/a"
        print(f"  {sym:<10} mentions={cnt:<6} 24h={chg_s}")
