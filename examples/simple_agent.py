import asyncio
import websockets
import httpx
import json

# Конфигурация нашего рантайма
RUNTIME_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/observe"

async def start_agent():
    print("🚀 Agent is starting... Connecting to Aether-TMA Runtime")
    
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("✅ Connected to UI Stream. Waiting for DOM data...")
            
            while True:
                # 1. Получаем состояние UI от Bridge.js через наш рантайм
                message = await websocket.recv()
                ui_state = json.loads(message)
                
                # 2. Логика "зрения" (Vision Logic)
                # Ищем кнопку "Claim" или "Connect Wallet" в полученном JSON
                elements = ui_state.get("elements", [])
                for el in elements:
                    if "Claim" in el.get("text", "") or el.get("id") == "connect-btn":
                        print(f"🎯 Target found: {el.get('text')}! Sending control command...")
                        
                        # 3. Отправляем команду действия (Action)
                        payload = {
                            "action": "CLICK",
                            "selector": f"#{el.get('id')}" if el.get("id") else el.get("tag")
                        }
                        
                        async with httpx.AsyncClient() as client:
                            response = await client.post(f"{RUNTIME_URL}/control", json=payload)
                            print(f"📡 Action dispatched: {response.json()}")
                
                await asyncio.sleep(1) # Пауза между циклами размышления
                
    except Exception as e:
        print(f"❌ Connection error: {e}. Is the runtime running?")

if __name__ == "__main__":
    asyncio.run(start_agent())
