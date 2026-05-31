"""Synapse judgment layer — turns Nansen smart-money data into a verdict.

Deterministic, inspectable scoring (no LLM here — that's the brain layer).
Ports the Alpha Seoul "committee" idea: track / watch / ignore + a 0-100
attention score, with the signals and risks shown, not hidden. No fake
certainty, no LLM-first scoring.
"""
from __future__ import annotations

from dataclasses import dataclass, field

# --- tunable thresholds ---
MIN_LIQUIDITY_USD = 50_000   # below this, hard to act safely
STRONG_TRADERS = 10          # many independent smart wallets = real conviction
SOME_TRADERS = 4
TRACK_SCORE = 70
WATCH_SCORE = 45


@dataclass
class Verdict:
    symbol: str
    chain: str
    verdict: str                       # track | watch | ignore
    score: int                         # 0-100 attention / conviction
    reasons: list = field(default_factory=list)
    risks: list = field(default_factory=list)
    metrics: dict = field(default_factory=dict)


def _num(v, default=0.0):
    return v if isinstance(v, (int, float)) else default


def judge_token(t: dict) -> Verdict:
    """Score one token from the Nansen screener and assign a verdict."""
    netflow = _num(t.get("netflow"))
    traders = int(_num(t.get("nof_traders")))
    chg = _num(t.get("price_change"))      # fraction: 0.42 = +42%
    liq = _num(t.get("liquidity"))
    buy = _num(t.get("buy_volume"))
    sell = _num(t.get("sell_volume"))
    age = _num(t.get("token_age_days"))

    score = 50.0
    reasons: list = []
    risks: list = []

    # 1. Netflow direction — the strongest smart-money signal
    if netflow > 0:
        score += 20
        reasons.append(f"smart money net buying (+${netflow:,.0f})")
    elif netflow < 0:
        score -= 30
        risks.append(f"smart money net selling (${netflow:,.0f})")

    # 2. Breadth — how many independent smart wallets, not a one-off
    if traders >= STRONG_TRADERS:
        score += 18
        reasons.append(f"{traders} smart wallets (broad)")
    elif traders >= SOME_TRADERS:
        score += 8
        reasons.append(f"{traders} smart wallets")
    elif traders <= 1:
        score -= 15
        risks.append("only 1 smart wallet — could be a one-off")

    # 3. Momentum — confirmation when aligned with netflow
    if chg > 0 and netflow > 0:
        score += 10
        reasons.append(f"price confirming (+{chg * 100:.0f}%)")
    elif chg < -0.1:
        score -= 8
        risks.append(f"price falling ({chg * 100:.0f}%)")
    if chg > 1.0:
        risks.append(f"already +{chg * 100:.0f}% — possibly late / volatile")

    # 4. Buy vs sell pressure
    if sell > 0 and buy / sell >= 2:
        score += 6
        reasons.append("buy volume >> sell volume")

    # 5. Liquidity / tradability
    if liq < MIN_LIQUIDITY_USD:
        risks.append(f"thin liquidity (${liq:,.0f}) — hard to act safely")
        score = min(score, 55)   # can't strongly track an illiquid token

    # 6. Very young token = higher risk
    if 0 < age <= 2:
        risks.append(f"very new token ({age:.0f}d)")

    score = int(max(0, min(100, round(score))))

    # verdict: net selling is an automatic ignore; otherwise by score
    if netflow <= 0:
        verdict = "ignore"
    elif score >= TRACK_SCORE:
        verdict = "track"
    elif score >= WATCH_SCORE:
        verdict = "watch"
    else:
        verdict = "ignore"

    return Verdict(
        symbol=str(t.get("token_symbol", "?"))[:16],
        chain=t.get("chain", "?"),
        verdict=verdict,
        score=score,
        reasons=reasons,
        risks=risks,
        metrics={"netflow": netflow, "traders": traders,
                 "price_change": chg, "liquidity": liq},
    )


def judge_tokens(tokens: list) -> list:
    """Judge a list of tokens, sorted by score (highest conviction first)."""
    return sorted((judge_token(t) for t in tokens),
                  key=lambda v: v.score, reverse=True)


if __name__ == "__main__":
    from nansen import smart_money_tokens

    verdicts = judge_tokens(smart_money_tokens())
    icon = {"track": "🟢 TRACK ", "watch": "🟡 WATCH ", "ignore": "⚪ IGNORE"}
    n = {v: sum(1 for x in verdicts if x.verdict == v) for v in ("track", "watch", "ignore")}
    print(f"Synapse judged {len(verdicts)} tokens — "
          f"{n['track']} track / {n['watch']} watch / {n['ignore']} ignore\n")
    for v in verdicts[:14]:
        why = "; ".join(v.reasons[:2]) or "—"
        risk = f"  ⚠ {v.risks[0]}" if v.risks else ""
        print(f"{icon[v.verdict]} [{v.score:3d}] {v.symbol:<14} {v.chain:<7} {why}{risk}")
