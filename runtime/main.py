from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import redis
import json

app = FastAPI(title="Aether-TMA Runtime")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

r = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)

# --- DATA MODELS (The Protocol) ---

class ControlCommand(BaseModel):
    action: str = Field(..., example="CLICK")
    selector: str = Field(..., example="#buy-button")
    value: Optional[str] = None

class TonRequest(BaseModel):
    action: str = Field(..., example="balance")
    address: str = Field(..., example="EQD...")
    method: Optional[str] = None
    params: Optional[list] = []

# --- UI LAYER ---

@app.post("/control")
async def control_agent(command: ControlCommand):
    """Dispatches interaction commands to Bridge.js"""
    r.set("last_command", command.model_dump_json())
    return {"status": "dispatched", "command": command}

@app.websocket("/observe")
async def websocket_endpoint(websocket: WebSocket):
    """Streams live DOM-to-JSON state to the Agent"""
    await websocket.accept()
    try:
        while True:
            ui_state = r.get("ui_state") or "{}"
            await websocket.send_text(ui_state)
    except WebSocketDisconnect:
        print("Agent disconnected")

# --- TON LAYER (Phase 2) ---

@app.post("/ton")
async def ton_handler(request: TonRequest):
    """Bridge to TON Blockchain via pytonlib/httpx"""
    if request.action == "balance":
        # Integration with pytonlib starts here
        return {
            "status": "success",
            "address": request.address,
            "balance": "0.0",
            "sync": "simulated"
        }
    
    elif request.action == "call":
        return {
            "status": "dispatched",
            "method": request.method,
            "params": request.params
        }
    
    raise HTTPException(status_code=400, detail="Unknown TON action")
