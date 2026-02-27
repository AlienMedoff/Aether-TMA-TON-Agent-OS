# 🌌 Aether-TMA-TON-Agent-OS

**Universal Agentic Runtime & Orchestration Layer for Telegram Mini Apps**

Gives any LLM agent (Claude, GPT, Grok, Llama) real **eyes and hands** inside Telegram WebView — and a **verified, auditable on-chain execution layer** on TON.

The agent doesn't just write text. It **sees** the interface, **understands** it, **controls** it in real time — and executes financial operations through cryptographically secure smart contracts.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    AI LLM AGENT                         │
│         (Claude / GPT / Grok / custom logic)            │
└───────────────────────┬─────────────────────────────────┘
                        │  observe → decide → act
                        ▼
┌─────────────────────────────────────────────────────────┐
│              AETHER RUNTIME  (FastAPI + Redis)          │
│         WebSocket state stream · /control endpoint      │
└──────────┬─────────────────────────────┬────────────────┘
           │                             │
           ▼                             ▼
┌──────────────────┐         ┌───────────────────────────┐
│   Telegram MiniApp│         │   TON Smart Contracts     │
│   + Bridge.js     │         │                           │
│                  │         │  AetherVault    (escrow)   │
│  DOM → JSON map  │         │  AetherOracle   (multisig) │
│  safe-area aware │         │  AetherGovernance(timelock)│
└──────────────────┘         └───────────────────────────┘
```

---

## What's Working Right Now

| Component | Status | Description |
|-----------|--------|-------------|
| `runtime/` | ✅ Live | FastAPI + Redis + WebSocket — DOM streaming in JSON |
| `bridge/Bridge.js` | ✅ Live | Injected into TMA WebView, maps DOM → JSON with safe-area support |
| `/ton` endpoint | ✅ Live | Queries Toncenter API, returns on-chain data |
| `examples/simple_agent.py` | ✅ Live | Full observe → decide → act loop demo |
| `contracts/AetherVault.tact` | ✅ Ready | Agent escrow with limits, Guardian 2-key, CEI |
| `contracts/AetherOracle.tact` | ✅ Ready | Ed25519 k-of-N multisig, trust scores, staking |
| `contracts/AetherGovernance.tact` | ✅ Ready | 48h timelock, proposers, DAO-ready |
| `tests/governance.spec.ts` | ✅ Ready | 38 security tests, full E2E coverage |

---

## Quick Start — Runtime (2 minutes)

```bash
git clone https://github.com/AlienMedoff/Aether-TMA-TON-Agent-OS.git
cd Aether-TMA-TON-Agent-OS
docker-compose up --build
```

After launch:

- **DOM Stream:** `ws://localhost:8000/observe`
- **Control:** `POST http://localhost:8000/control`

Example control payload:

```json
{
  "action": "CLICK",
  "selector": "#buy-button",
  "memo": "agent_task_42"
}
```

---

## Smart Contracts (TON / Tact 1.x)

Three modular contracts with strict separation of concerns.  
Each contract only does one thing — and does it well.

### AetherVault — Core Escrow

Manages money. Nothing else.

```
Owner registers agents with independent daily/per-TX limits.
Agent sends AgentAction → Vault checks limits → executes transfer.
Large transfers (≥ threshold) → Guardian pending queue (30 min TTL).
Guardian approves or rejects → auto-refund on reject.
```

**Security layers:**
- Per-TX cap + daily limit (auto-reset every 24h)
- Guardian 2-key for large amounts
- CEI pattern (state before external calls, everywhere)
- GAS_RESERVE — vault never drains itself dry
- Kill-switch pause / unpause
- EmergencyWithdraw (requires pause first)
- 2-step ownership transfer

### AetherOracle — Multisig + Trust

Verifies signatures. Scores wallets. Responds to Vault queries.

```
Ed25519 k-of-N verification — O(1) lookup (no loop over all oracles).
Signature format: [oracle_address | sig_hi | sig_lo] × N (linked cell list).
Trust Score (0–100) set by oracles, cached in Vault via Request-Response.
Stake-to-Play: 5 TON required to use signal execution.
24h unstake lockup after last trade.
Sentinel: independent emergency pause (no owner required).
```

**The multisig fix (vs naive implementations):**  
No `newAddress(0, pub_key)` bug. Oracle address is passed explicitly in each signature block → O(1) `oracle_pub_keys.get(oracle_addr)` lookup. Duplicate key detection via `seen_keys` map.

### AetherGovernance — Timelock + DAO

Changes parameters. Only after 48 hours.

```
ProposeAction (owner or registered proposer)
  → stored in timelock queue
  → ready_at = now + 48h
  → expires_at = ready_at + 7 days

ExecuteAction (owner, after 48h, before 7-day expiry)
  → dispatches UpdateParams to Vault or Oracle
  → Vault/Oracle accept ONLY if sender == governance_address
```

**Supported actions:**

| Type | Target | Effect |
|------|--------|--------|
| 1 | Vault | Set fee_bps |
| 2 | Oracle | Set min_signatures |
| 3 | Vault | Set guardian_threshold |
| 4 | Vault | Pause |
| 5 | Vault | Unpause |
| 6 | Oracle | Set fee_bps |
| 7 | Oracle | Pause |
| 8 | Oracle | Unpause |

---

## Request-Response Protocol (Vault ↔ Oracle)

TON has no synchronous cross-contract calls. Aether implements a typed async protocol with correlation IDs:

```
Vault                           Oracle
  │                               │
  │── RequestTrustScore ─────────►│
  │   query_id=5, user=0xABC      │
  │   value: 0.1 TON (fwd gas)    │
  │                               │ lookup trust_score[user]
  │◄─ ResponseTrustScore ─────────│
  │   query_id=5, score=75        │ SendRemainingValue
  │                               │
  │ checks:                       │
  │   sender == oracle_address ✅ │
  │   query_id in pending      ✅ │
  │   timeout < 10 min         ✅ │
  │   user match               ✅ │
  │                               │
  │ cache trust_score[user] = 75  │
  │ del pending_queries[5]        │
```

**Security guarantees:**
- Fake response from any other address → rejected (`sender != oracle_address`)
- Replay attack → rejected (query_id deleted after first response)
- Late response (> 10 min) → rejected (timestamp check)
- User field tampering → rejected (integrity check)
- Expired query cleanup → `CleanupExpiredQuery` (owner only, after timeout)

---

## Testing

Full security suite — 38 tests across 8 blocks.

```bash
npm install
npx jest tests/governance.spec.ts --verbose
```

| Block | Tests | What's covered |
|-------|-------|----------------|
| 1. ProposeAction | 7 | Authorization, validation, bad params |
| 2. Timelock | 4 | 48h delay, 7-day expiry, independence |
| 3. Execute → UpdateParams | 10 | **E2E: fee, threshold, min_sigs, pause** |
| 4. Cancel | 5 | Who can cancel, double-cancel, post-exec cancel |
| 5. Request-Response | 8 | Fake response, replay, timeout, cleanup |
| 6. Concurrency | 3 | Multiple actions, independent execution |
| 7. Ownership | 3 | 2-step transfer through Governance |
| 8. Edge Cases | 5 | Unknown IDs, balance attacks, overflow |

**The golden test (3.1):**

```typescript
it("SetVaultFee: fee_bps changes in Vault after 48h", async () => {
    const feeBefore = await vault.getFeeBps();       // 50 (0.5%)

    await proposeWaitExecute(1n, 100n, "Fee to 1%"); // propose → 48h → execute

    const feeAfter = await vault.getFeeBps();        // 100 (1%)
    expect(feeAfter).toBe(100n);                     // ✅ Governance → Vault
});
```

---

## Deploy Order

```bash
npx blueprint run deploy --network testnet
```

**Order matters** (address dependencies):

```
1. AetherOracle.deploy(owner, storm_vault, fee_bps)
2. AetherVault.deploy(owner, oracle.address, guardian_threshold)
3. AetherGovernance.deploy(owner, vault.address, oracle.address)
4. Oracle.AddVaultToWhitelist(vault.address)
5. Vault.SetGuardian(guardian, threshold)
6. Oracle.AddOracle(addr1, pubkey1)
7. Oracle.AddOracle(addr2, pubkey2)
8. Vault.SetGovernance(governance.address)
9. Oracle.SetGovernance(governance.address)
10. Vault.TransferOwnership(governance.address)
11. Oracle.TransferOwnership(governance.address)
```

---

## Roadmap

| Phase | Status | Description |
|-------|--------|-------------|
| **Core Architecture** | ✅ Done | WebSocket DOM streaming, Redis state, Bridge.js |
| **On-chain Security Layer** | ✅ Done | AetherVault + Oracle + Governance + 38 tests |
| **TON Integration** | 🔄 In Progress | Toncenter API, jettons, smart-contract calls |
| **Multi-Agent Support** | 📋 Planned | Multiple TMA sessions from single runtime |
| **Visual Verification** | 📋 Planned | Screenshot-based confirmation for high-stakes actions |
| **DAO Governance** | 📋 Planned | On-chain voting, proposer quorum |

---

## Stack

| Layer | Tech |
|-------|------|
| Runtime | Python · FastAPI · Redis · WebSocket |
| Agent Interface | REST · JSON Protocol v2.0 |
| TMA Bridge | JavaScript · Telegram WebApp SDK |
| Smart Contracts | TON · Tact 1.x |
| Testing | TypeScript · @ton/sandbox · Jest |
| Infrastructure | Docker · docker-compose |

---

## Contributing

Open to PRs, ideas, and joint agent fleets.  
Create an issue — let's build together.

---

## License

MIT

**Built with ⚡ by [AlienMedoff](https://github.com/AlienMedoff)**
