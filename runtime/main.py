from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import redis
import json
import os
import httpx

# --- TON SERVICE CLASS ---
class TONService:
    def __init__(self):
        self.api_url = "https://toncenter.com/api/v2/jsonRPC"
        self.api_key = os.getenv("TON_API_KEY", "")  # Add your key to .env later
        self.headers = {"X-API-Key": self.api_key} if self.api_key else {}

    async def get_balance(self, address: str):
        payload = {
            "id": "1", "jsonrpc": "2.0",
            "method": "getAddressInformation",
            "params": {"address": address}
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.api_url, json=payload, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                balance_nanoton = int(data.get("result", {}).get("balance", 0))
                return {"status": "success", "address": address, "balance": balance_nanoton / 10**9, "unit": "TON"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def call_contract(self, address: str, method: str, params: list):
        stack = []
        for p in params:
            if isinstance(p, int): stack.append(["num", str(p)])
            elif isinstance(p, str): stack.append(["str", p])
            else: stack.append(["num", str(p)])

        payload = {
            "id": "1", "jsonrpc": "2.0",
            "method": "runGetMethod",
            "params": {"address": address, "method": method, "stack": stack}
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.api_url, json=payload, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                return {"status": "success", "address": address, "method": method, "result": data.get("result", {})}
        except Exception as e:
            return {"status": "error", "message": str(e)}

# --- FASTAPI APP SETUP ---
app = FastAPI(title="Aether-TMA Runtime")
ton_service = TONService()
r = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELS ---
class ControlCommand(BaseModel):
    action: str
    selector: str
    value: Optional[str] = None

class TonRequest(BaseModel):
    action: str
    address: str
    method: Optional[str] = None
    params: Optional[list] = []

# --- ENDPOINTS ---
@app.post("/control")
async def control_agent(command: ControlCommand):
    r.set("last_command", command.model_dump_json())
    return {"status": "dispatched", "command": command}

@app.websocket("/observe")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            ui_state = r.get("ui_state") or "{}"
            await websocket.send_text(ui_state)
    except WebSocketDisconnect:
        pass

@app.post("/ton")
async def ton_handler(request: TonRequest):
    if request.action == "balance":
        return await ton_service.get_balance(request.address)
    elif request.action == "call":
        return await ton_service.call_contract(request.address, request.method, request.params)
    raise HTTPException(status_code=400, detail="Unknown TON action")
