# Synapse — Agent Harness

The harness is the product. Anyone can call an LLM; the moat is the operating
structure that makes the agent reliable, inspectable, and able to compound
memory over time. This is the Hermes philosophy applied to an on-chain agent.

## Design goals
1. **Autonomous & survivable** — runs unattended; self-corrects on infra failures (gas/nonce/API/restart). Engine, not pitch.
2. **Verifiable & inspectable** — every decision shows its sources + reasons. No fake certainty, no LLM-first scoring.
3. **Memory that compounds** — the agent reads its own past verdicts + outcomes each cycle, so it gets sharper. Context = moat.
4. **Cheap where deterministic, expensive only where judgment is needed** — model routing.

## Topology — roles in ONE loop (not heavy separate agents)
Keep it a single orchestrated process with clear stages (scope discipline — no agent sprawl):
```
Orchestrator(loop)
  → Scout    (perceive: Nansen / Elfa / Surf)
  → Judge    (deterministic verdict — src/judge.py, no LLM)
  → Analyst  (LLM reasoning: "why it matters" + final call)
  → Recorder (on-chain write to Mantle — gated, high-risk)
```

## Action space (tools — schema-first, narrow, stable names)
| tool | type | risk | output shape |
|---|---|---|---|
| `get_smart_money_tokens` | medium | low | list[token] |
| `get_signals` (Elfa) | medium | low | list[signal] |
| `judge_token` | medium | none (pure) | Verdict |
| `reason_over` (LLM) | medium | low | {call, why} |
| `record_decision` | **micro** | **high** | {tx_hash, status} |

Every tool returns a deterministic observation:
```
{ status: success|warning|error, summary: str, data: ..., next_actions: [...], artifacts: [...] }
```

## Verification gates (must pass BEFORE the high-risk on-chain write)
1. **Freshness** — perception data is recent (else skip cycle).
2. **Evidence** — verdict has ≥1 concrete reason (no empty/■ scores recorded).
3. **Confidence** — only record verdicts above threshold (or record all but flag low).
4. **Safety** (Phase-1 reliability knowledge) — gas runway ok, nonce fresh, contract reachable, slippage/route sane.
5. **Idempotency** — never double-record the same (token, cycle); dedupe by key.

## Routing
- Judge = deterministic Python, **no LLM** (cheap, inspectable).
- Analyst = LLM (Claude / AltLLM when credits land), **only** on the shortlist of judged candidates — not raw 100-token dumps.

## Memory / state — TWO LAYERS (the compounding moat)
This is the "verifiable AI second brain" — the unique combination.
1. **Obsidian-style notes = the rich memory.** Each decision is written as a markdown note
   (token, verdict, score, reasons, risks, LLM reasoning, links to related tokens/wallets).
   The notes form a *graph* — the agent's growing brain. The agent **reads prior notes first
   each cycle** → avoids repeats, builds context, "learns." This is `context-is-the-real-moat`
   + `llm-wiki-as-operating-memory` made literal.
2. **On-chain = the proof.** Each note is hashed; the hash + verdict + score + timestamp are
   recorded on Mantle (ERC-8004 identity + decision log). Gas-cheap, tamper-proof, verifiable.
   Anyone can check the hash against the published note → can't-lie track record.

So: full content lives in Obsidian (memory); the hash lives on-chain (proof). Not either/or.

## Interface & visual layer
- **Web dashboard (required — 20-Deploy + Best-UI/UX):** renders the agent's growing brain graph
  + live decisions + on-chain proof links. Publicly accessible (non-localhost).
- **Visual stack (all already in Jeff's vault):**
  - **Quartz** (`jackyzha0/quartz` + `quartz-community/graph`) — turns the markdown notes into a
    published Obsidian-like knowledge-graph site. Most on-concept ("browse the agent's brain"),
    lowest custom effort, web-publishable. **Primary recommendation.**
  - **React Flow / XYFlow** — interactive node maps for a live, dynamic dashboard feel.
  - **Sigma.js / Graphology** — Jeff's existing Alpha Seoul "radial-brain" graph (reuse).
  - **shadcn/ui + Tremor** — polished dashboard shell, cards, metrics (for the UI/UX award).
- **Telegram (optional, Jeff's strength):** bot pushes each verdict + on-chain link. Thin add.
- Scope: ONE good visual. Quartz for the brain-graph is scope-smart (agent writes md → Quartz renders).

## Recovery contract (per error path)
- root-cause hint + safe-retry instruction + explicit stop condition.
- Circuit breakers: API down → backoff + use cached snapshot; on-chain write fail → log, do NOT blind-retry; N consecutive failures → halt.

## Loop lifecycle
```
wake → perceive → judge → [gates] → reason → [gates] → record → persist → sleep → repeat
```
Demo mode: frozen fixtures so the demo never dies on a live API hiccup.

## Architecture pattern
**Hybrid** — typed deterministic pipeline (perceive→judge→record) with a single LLM ReAct-style reasoning step at the Analyst stage. Deterministic flow for everything that can be deterministic; LLM only where judgment genuinely helps.

## Benchmarks to track
- cycles run without manual intervention
- verdicts recorded on-chain (verifiable count)
- decision precision over time (did track-calls age well?)
- cost per cycle
