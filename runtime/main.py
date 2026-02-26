from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import redis
import json

app = FastAPI(title="Aether-TMA Runtime")

# Enable CORS for Telegram Mini App environment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to Redis (High-speed state management)
r = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)

# --- UI INTERACTION LAYER (EYES & HANDS) ---

@app.post("/control")
async def control_agent(command: dict):
    """
    Receives interaction commands (click, input) and dispatches them to Bridge.js
    """
    r.set("last_command", json.dumps(command))
    return {"status": "dispatched", "command": command}

@app.websocket("/observe")
async def websocket_endpoint(websocket: WebSocket):
    """
    Streams live UI state (DOM-to-JSON) to the Agent via WebSockets
    """
    await websocket.accept()
    try:
        while True:
            # Retrieve current UI state from Redis and stream to Agent
            ui_state = r.get("ui_state") or "{}"
            await websocket.send_text(ui_state)
    except WebSocketDisconnect:
        print("Agent disconnected from observation stream")

# --- TON BLOCKCHAIN INTEGRATION (PHASE 2) ---

@app.post("/ton")
async def ton_handler(request: dict):
    """
    Dedicated endpoint for Agent interaction with TON Blockchain
    """
    action = request.get("action")
    
    if action == "balance":
        address = request.get("address", "Not provided")
        # To be replaced with actual tonweb/ton-core logic
        return {
            "status": "success", 
            "address": address, 
            "balance": "0.0", 
            "note": "Phase 2 simulation active"
        }
    
    elif action == "call":
        # Smart-contract interaction logic
        method = request.get("method")
        return {
            "status": "dispatched", 
            "method": method, 
            "params": request.get("params")
        }
    
    return {"error": "Unknown TON action requested"}
