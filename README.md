​🌌 Aether-TMA: TON-Agent-OS


​The Universal Agentic Runtime & Orchestration Layer for Telegram Mini Apps (TMA).


​Aether-TMA is a production-ready infrastructure designed to solve the "Blind Agent" problem. It provides autonomous LLM-based agents with real-time visual observability and deterministic UI control within the Telegram WebView environment.


​🚀 Key Features




​Agentic Observability: Real-time DOM-to-JSON mapping via Bridge.js.


​Deterministic Control: JSON Control Protocol v2.0 for precise UI interactions (clicks, inputs, navigation).


​Environment Parity: Native handling of TMA-specific quirks (Safe Areas, Notch, Viewport height).


​High Performance: Redis-backed state management and asynchronous WebSocket streams.


​Production Ready: Dockerized environment for isolated, secure deployment.




​🏗 System Architecture


​The system consists of three core components:




​FastAPI Runtime: The brain of the operation. It receives commands from LLMs and streams UI state via WebSockets.


​Aether Bridge: A lightweight JavaScript layer injected into the TMA to synchronize the DOM state with the Runtime.


​Redis State Layer: Acts as the system's short-term memory, ensuring low-latency communication between the agent and the UI.




​🛠 Quick Start


​1. Requirements




​Docker & Docker Compose


​Python 3.10+ (for local development)




​2. Launch the Infrastructure

docker-compose up --build

🔗 Integration Points




​UI Stream: Connect to ws://localhost:8000/observe to receive live UI snapshots.


​Control API: Send JSON commands to http://localhost:8000/control.




​Example Command:

{
  "action": "CLICK",
  "selector": "#buy-button"
}

🎯 Vision


​Aether-TMA aims to be the standard orchestration layer for AI Agents on TON. By providing a reliable way for Agents to "see" and "touch" Mini Apps, we unlock a new generation of autonomous DeFi, Gaming, and Utility bots within Telegram.


​📄 License


​Distributed under the MIT License. See LICENSE for more information.


​Developed with ⚡ by AlienMedoff


