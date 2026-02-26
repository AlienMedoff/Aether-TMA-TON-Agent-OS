from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import redis
import json

app = FastAPI(title="Aether-TMA Runtime")

# Разрешаем всё для работы из WebView
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

r = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)

# --- Блок управления UI ---

@app.post("/control")
async def control_agent(command: dict):
    """Принимает команды (click, type) и сохраняет для Bridge.js"""
    r.set("last_command", json.dumps(command))
    return {"status": "dispatched", "command": command}

@app.websocket("/observe")
async def websocket_endpoint(websocket: WebSocket):
    """Стримит состояние DOM агенту в реальном времени"""
    await websocket.accept()
    try:
        while True:
            ui_state = r.get("ui_state") or "{}"
            await websocket.send_text(ui_state)
    except WebSocketDisconnect:
        print("Agent disconnected")

# --- Блок интеграции с TON (Phase 2) ---

@app.post("/ton")
async def ton_handler(request: dict):
    """Обрабатывает запросы агента к блокчейну TON"""
    action = request.get("action")
    
    if action == "balance":
        address = request.get("address", "Not provided")
        # Тут будет реальный вызов к tonweb/tonsdk
        return {
            "status": "success", 
            "address": address, 
            "balance": "0.0", 
            "note": "Simulated for Phase 2"
        }
    
    elif action == "call":
        method = request.get("method")
        return {
            "status": "dispatched", 
            "method": method, 
            "params": request.get("params")
        }
    
    return {"error": "Unknown TON action"}
