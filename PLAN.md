# Synapse — Build Plan

**Hackathon:** Mantle Turing Test Hackathon 2026 (Phase 2 "AI Awakening")
**Track:** Agentic Economy (Byreal) — also touches AI Alpha & Data
**Deadline:** submit by **June 15, 2026** · Demo Day Jul 2–3 · winners Jul 10
**Repo:** github.com/mainn6/synapse

## Concept (one line)
An autonomous on-chain agent on Mantle that reads smart-money intelligence (Nansen),
reasons with a crypto LLM, and **acts on its own** — recording every judgment on-chain
(ERC-8004) as a verifiable, can't-lie track record. An agent with memory + action,
not a dashboard, not a stateless bot.

## Differentiator
- vs **Minara** (closed "trust me" product) → open + on-chain verifiable ("verify me")
- vs **Nansen** (data tool humans read) → autonomous agent that reads + decides + acts
- vs **HeliQuant/manscout** (stateless bots) → memory + verifiable track record

## Hard requirements (don't lose points)
- [ ] Smart contract deployed + **verified** on Mantle (mainnet or testnet)
- [ ] At least **one AI-powered function callable on-chain** (agent writes its decision on-chain)
- [ ] Public (non-localhost) frontend demo
- [ ] Deployment address in DoraHacks submission
- [ ] **2-min+ demo video** walking the core use case
- [ ] Open-source repo + README (setup, architecture, contract address)
- [ ] X thread with **#MantleAIHackathon** (pitch + video + GitHub + contract address)
→ Hitting all of the above also auto-qualifies for the **20 Project Deployment Award ($1K, first-come)**.

## Build bricks
- [x] **B0** Repo + README + registration + Nansen credit applied
- [x] **B1** Perception layer — Nansen smart-money (`src/nansen.py`: token screener + netflow) ✅ working
- [ ] **B2** Judgment — `src/judge.py`: deterministic verdict (track/watch/ignore) + conviction
      from netflow direction + trader count + momentum + liquidity (port Alpha Seoul committee logic)
- [ ] **B3** Brain — `src/brain.py`: LLM (AltLLM/Claude) reasons over scored candidates → "why it matters" + final call
- [ ] **B4** Action + on-chain record — minimal Mantle contract (ERC-8004 identity + `recordDecision()` AI-callable fn);
      agent writes its judgment on-chain. (Scaffold via `create-8004-agent`. Stretch: RealClaw execution.)
- [ ] **B5** Autonomous loop — `src/agent.py`: perceive → judge → reason → record, on a schedule (the "agent")
- [ ] **B6** Demo UI — show live decisions + growing memory + on-chain track record (reuse Alpha Seoul radial-brain graph). Public deploy.
- [ ] **B7** Submission — demo video + README + X thread + DoraHacks BUIDL

## 2-week timeline (today = May 31)
- **Week 1 (~Jun 7):** B2 → B3 → B4. Goal = thin end-to-end loop runs + contract deployed+verified on Mantle.
- **Week 2 (~Jun 14):** B5 → B6. Autonomous loop + public demo UI. Build to 50%, polish 50%.
- **Jun 13–15:** B7. Record demo, write README, submit **EARLY** (buffer + first-come deployment award).

## Scope discipline (the #1 risk = doing too much)
- ONE chain set for perception to start (ETH/Base/Solana via Nansen — already works).
- ONE minimal contract (one AI-callable function). No heavy on-chain logic.
- Action can start as "record decision on-chain"; live RealClaw execution = stretch only.
- "Doesn't die / reliability" is an engine, NOT the pitch. Pitch = "autonomous + verifiable."
- If a brick blocks for >1 day, cut scope, don't expand.

## Fast kill tests
- [x] Nansen data returns real smart-money tokens (HTTP 200, 100 tokens) ✅
- [ ] Deploy + verify a contract on Mantle (do this early — proves the contract path)
