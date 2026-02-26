from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import redis
import json
from .ton_service import TONService # Импортируем наш новый сервис

app = FastAPI(title="Aether-TMA Runtime")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

r = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)
ton_service = TONService() # Инициализируем сервис

# --- UI LAYER ---
@app.post("/control")
async def control_agent(command: dict):
    r.set("last_command", json.dumps(command))
    return {"status": "dispatched", "command": command}

@app.websocket("/observe")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            ui_state = r.get("ui_state") or "{}"
            await websocket.send_text(ui_state)
    except WebSocketDisconnect:
        print("Agent disconnected")

# --- TON LAYER (PHASE 2) ---
@app.post("/ton")
async def ton_handler(request: dict):
    action = request.get("action")
    address = request.get("address")
    
    if not address:
        return {"error": "Address is required"}

    if action == "balance":
        return await ton_service.get_balance(address)
    
    elif action == "call":
        return await ton_service.call_contract(
            address, 
            request.get("method"), 
            request.get("params", [])
        )
    
    return {"error": "Unknown TON action"}
