import os
import re
import uuid
import logging
import httpx
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# TON address: EQ/UQ prefix + 46 base64url chars, or raw 48-char base64url
_TON_ADDRESS_RE = re.compile(r'^(?:EQ|UQ|kQ|0Q)[A-Za-z0-9_-]{46}$')

class TONService:
    """
    Hardened TON Blockchain service for safe agent interaction.
    Read-only whitelist model — no state-changing calls allowed.
    """

    SAFE_METHODS = frozenset([
        "get_balance",
        "get_pool_data",
        "get_nft_data",
        "get_jetton_data",
    ])

    _HTTP_TIMEOUT = 10.0   # seconds
    _MAX_PARAMS   = 10

    def __init__(self):
        self.api_url = "https://toncenter.com/api/v2/jsonRPC"
        self.api_key = os.getenv("TON_API_KEY")
        if not self.api_key:
            logger.warning("TON_API_KEY not set — requests may be rate-limited")
        self.headers = {"X-API-Key": self.api_key or ""}

    # ── Public API ───────────────────────────────────────────────

    async def secure_call(self, address: str, method: str, params: list):
        """
        Gatekeeper: validates address format, method whitelist,
        and param count before execution.
        """
        # 1. Validate address format
        if not _TON_ADDRESS_RE.match(address):
            logger.warning(f"BLOCKED: Invalid address format: {address!r}")
            return {"status": "error", "message": "Invalid TON address format"}

        # 2. Validate method against whitelist
        if method not in self.SAFE_METHODS:
            logger.warning(f"BLOCKED: Unauthorized method attempt: {method!r}")
            return {"status": "error", "message": f"Method '{method}' is not allowed"}

        # 3. Validate param count
        if len(params) > self._MAX_PARAMS:
            logger.warning(f"BLOCKED: Too many params ({len(params)}) for {method!r}")
            return {"status": "error", "message": "Too many params"}

        return await self._call_contract(address, method, params)

    async def get_balance(self, address: str):
        """Fetches account balance from Toncenter API."""
        if not _TON_ADDRESS_RE.match(address):
            return {"status": "error", "message": "Invalid TON address format"}

        payload = {
            "id":      str(uuid.uuid4()),
            "jsonrpc": "2.0",
            "method":  "getAddressInformation",
            "params":  {"address": address},
        }
        try:
            async with httpx.AsyncClient(timeout=self._HTTP_TIMEOUT) as client:
                response = await client.post(
                    self.api_url, json=payload, headers=self.headers
                )
                response.raise_for_status()
                data = response.json()
                balance_nano = int(data.get("result", {}).get("balance", 0))
                return {
                    "status":  "success",
                    "balance": balance_nano / 10**9,
                    "unit":    "TON",
                }
        except httpx.TimeoutException:
            logger.error("Toncenter request timed out")
            return {"status": "error", "message": "Request timed out"}
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return {"status": "error", "message": str(e)}

    # ── Private — not accessible directly by agent ───────────────

    async def _call_contract(self, address: str, method: str, params: list):
        """
        Executes a get-method on a smart contract.
        Private — always goes through secure_call().
        """
        stack = []
        for p in params:
            if isinstance(p, int):
                stack.append(["num", str(p)])
            elif isinstance(p, str):
                stack.append(["str", p])
            else:
                # Reject unexpected param types instead of silently coercing
                return {"status": "error", "message": f"Unsupported param type: {type(p).__name__}"}

        payload = {
            "id":      str(uuid.uuid4()),
            "jsonrpc": "2.0",
            "method":  "runGetMethod",
            "params":  {
                "address": address,
                "method":  method,
                "stack":   stack,
            },
        }
        try:
            async with httpx.AsyncClient(timeout=self._HTTP_TIMEOUT) as client:
                response = await client.post(
                    self.api_url, json=payload, headers=self.headers
                )
                response.raise_for_status()
                data = response.json()
                return {
                    "status": "success",
                    "method": method,
                    "result": data.get("result", {}),
                }
        except httpx.TimeoutException:
            logger.error(f"Contract call timed out: {method!r} on {address!r}")
            return {"status": "error", "message": "Request timed out"}
        except Exception as e:
            logger.error(f"Error calling contract: {e}")
            return {"status": "error", "message": str(e)}
