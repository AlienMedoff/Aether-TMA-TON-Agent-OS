# runtime/ton_service.py
import os
import httpx

class TONService:
    """
    Service for interacting with TON Blockchain via Toncenter API.
    Handles balances and smart-contract calls.
    """

    def __init__(self):
        # В продакшене ключ лучше хранить в переменных окружения
        self.api_url = "https://toncenter.com/api/v2/jsonRPC"
        self.api_key = os.getenv("TON_API_KEY", "YOUR_API_KEY_HERE")
        self.headers = {"X-API-Key": self.api_key}

    async def get_balance(self, address: str):
        """Fetches account balance from Toncenter API"""
        payload = {
            "id": "1",
            "jsonrpc": "2.0",
            "method": "getAddressInformation",
            "params": {"address": address}
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.api_url, json=payload, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                balance_nanoton = int(data.get("result", {}).get("balance", 0))
                return {
                    "status": "success",
                    "address": address,
                    "balance": balance_nanoton / 10**9,
                    "unit": "TON"
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def call_contract(self, address: str, method: str, params: list):
        """Executes a get-method on a smart contract"""
        # Toncenter ожидает стек параметров в формате [["num", "123"], ["cell", "0x..."], ...]
        stack = []
        for p in params:
            if isinstance(p, int):
                stack.append(["num", str(p)])
            elif isinstance(p, str):
                stack.append(["str", p])
            else:
                stack.append(["num", str(p)])  # fallback

        payload = {
            "id": "1",
            "jsonrpc": "2.0",
            "method": "runGetMethod",
            "params": {
                "address": address,
                "method": method,
                "stack": stack
            }
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.api_url, json=payload, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                return {
                    "status": "success",
                    "address": address,
                    "method": method,
                    "result": data.get("result", {})
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}
