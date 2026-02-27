# Aether-TMA: Universal Agentic Runtime & Orchestration Layer

**The missing middleware for autonomous AI agents on the TON ecosystem.**

---

Aether-TMA gives any LLM agent (Claude, GPT, Grok, etc.) real eyes, hands, and a hardened security backbone inside Telegram WebViews. It transforms blind scripts into autonomous financial agents capable of visual control, secure escrow, and real-time DeFi interaction.

## 🏗 System Architecture

### High-Level Flow
```mermaid
graph TD
    subgraph Agent_Layer [Agentic Runtime]
        LLM[LLM Agent] -- Control Payload --> RT[Aether Runtime FastAPI]
        RT -- WebSocket/JSON --> Bridge[Bridge.js / TMA]
    end

    subgraph Security_Layer [Hardened Security]
        V[AetherVault] -- ExecuteTrade --> ST[StormTrade]
        O[AetherOracle] -- Verify --> V
        G[AetherGovernance] -- UpdateParams --> V
    end

    RT -- AgentAction --> V
    V -- RequestTrustScore --> O

After launch:




​UI State Stream: ws://localhost:8000/observe


​Control endpoint: POST http://localhost:8000/control




​Example Control Payload:

{
  "action": "CLICK",
  "selector": "#buy-button",
  "strategy": "Density > 0.20"
}

🛡 Security Protocol


​AetherVault and Oracle interact via an asynchronous Request-Response protocol:




​Vault requests trust score via RequestTrustScore(query_id, user).


​Oracle verifies and replies with ResponseTrustScore(query_id, score) using SendRemainingValue.


​Vault checks sender == oracle_address and query_id matching to prevent replay attacks.




​🗺 Roadmap




​Phase 1 (Done): Core Agent Runtime & 3-Contract Security Architecture.


​Phase 2 (In-Progress): TON Integration (ton-core) for direct jetton/contract interaction.


​Phase 3 (Planned): Multi-agent fleet orchestration & Visual Confirmation layer.




​Built with ⚡ by AlienMedoff


