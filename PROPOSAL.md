# Proposal: Aether-TMA Agent OS

## 1. Executive Summary
Aether-TMA is an open-source **Agentic Runtime** designed to solve the "Blind Agent" problem in the Telegram ecosystem. It provides a standardized infrastructure for AI agents to perceive and interact with Telegram Mini Apps (TMA) and the TON Blockchain simultaneously.

## 2. The Problem
Currently, AI agents in Telegram are limited to text-based chat. They cannot:
- **See**: They don't have access to the UI/DOM of Mini Apps.
- **Act**: They cannot interact with complex UI elements (buttons, sliders, forms).
- **Verify**: They cannot easily cross-reference UI states with on-chain data in a single runtime loop.

## 3. The Solution: Agent OS
Aether-TMA acts as the **Operating System** for agents:
- **Visual Bridge**: Converts live TMA DOM into structured JSON for LLM consumption.
- **Unified Control**: Provides a single API to execute both UI actions (clicks/typing) and Blockchain actions (TON smart-contract calls).
- **Deterministic Execution**: Ensures that agent decisions are based on real-time interface states and verified on-chain balances.

## 4. Key Use-Cases
- **Autonomous DeFi Managers**: Agents that can monitor DEX prices in a TMA and execute swaps or provide liquidity based on balance thresholds.
- **P2P Arbitrage Bots**: Agents that navigate P2P marketplaces, verify seller ratings via UI, and confirm transaction status on-chain.
- **AI Personal Assistants**: Proactive agents that can help users manage farm games, claim rewards, or set up complex automation within any TMA.

## 5. Technical Stack
- **Backend**: FastAPI (Async Python 3.10+).
- **State Store**: Redis for low-latency command dispatching.
- **Blockchain**: Integration with TON via Toncenter RPC (httpx).
- **Frontend Bridge**: Light-weight JavaScript injection for DOM-to-JSON mapping.

## 6. Roadmap
- **Phase 1 (Done)**: Core architecture and DOM-to-JSON streaming.
- **Phase 2 (In Progress)**: Deep TON SDK integration (pytonlib) and standardized `/ton` endpoint.
- **Phase 3 (Next)**: Multi-agent orchestration and visual verification (screenshot layer).

## 7. Vision
Our goal is to make TON the primary home for autonomous agents. By providing the "eyes and hands," Aether-TMA enables a new generation of apps that don't just wait for user input but actively work for the user 24/7.
