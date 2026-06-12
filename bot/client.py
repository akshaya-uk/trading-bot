"""
client.py — Binance Futures Testnet API wrapper.
Handles authentication, request signing, and raw HTTP calls.
"""

import time
import hmac
import hashlib
import logging
import requests
from urllib.parse import urlencode

logger = logging.getLogger("trading_bot.client")

BASE_URL = "https://testnet.binancefuture.com"


class BinanceClient:
    """
    Low-level wrapper around Binance Futures Testnet REST API.
    Handles HMAC-SHA256 signing and HTTP communication.
    """

    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        self.session.headers.update({
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        })
        logger.info("BinanceClient initialized. Base URL: %s", BASE_URL)

    def _sign(self, params: dict) -> dict:
        """Append timestamp and HMAC-SHA256 signature to params."""
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _post(self, endpoint: str, params: dict) -> dict:
        """Sign and POST to a private endpoint."""
        signed_params = self._sign(params)
        url = BASE_URL + endpoint
        logger.info("POST %s | params: %s", url, {k: v for k, v in signed_params.items() if k != "signature"})
        try:
            response = self.session.post(url, data=signed_params, timeout=10)
            response.raise_for_status()
            data = response.json()
            logger.info("Response [%s]: %s", response.status_code, data)
            return data
        except requests.exceptions.HTTPError as e:
            # Binance returns error details in JSON even on 4xx
            try:
                err_body = e.response.json()
            except Exception:
                err_body = e.response.text
            logger.error("HTTP error from Binance: %s | body: %s", e, err_body)
            raise BinanceAPIError(err_body) from e
        except requests.exceptions.ConnectionError as e:
            logger.error("Network connection error: %s", e)
            raise NetworkError("Could not connect to Binance Testnet. Check your internet connection.") from e
        except requests.exceptions.Timeout as e:
            logger.error("Request timed out: %s", e)
            raise NetworkError("Request to Binance Testnet timed out.") from e

    def _get(self, endpoint: str, params: dict = None) -> dict:
        """GET from a public (unsigned) endpoint."""
        url = BASE_URL + endpoint
        logger.info("GET %s | params: %s", url, params)
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            logger.debug("Response [%s]: %s", response.status_code, data)
            return data
        except requests.exceptions.RequestException as e:
            logger.error("GET request failed: %s", e)
            raise NetworkError(f"GET request failed: {e}") from e

    def place_order(self, **kwargs) -> dict:
        """Place an order on Binance Futures Testnet."""
        return self._post("/fapi/v1/order", kwargs)

    def get_exchange_info(self) -> dict:
        """Fetch exchange info (symbol rules, precision, etc.)."""
        return self._get("/fapi/v1/exchangeInfo")

    def get_symbol_price(self, symbol: str) -> dict:
        """Fetch current mark price for a symbol."""
        return self._get("/fapi/v1/ticker/price", {"symbol": symbol})


# ---------------------------------------------------------------------------
# Custom exceptions (kept here so both layers can import from one place)
# ---------------------------------------------------------------------------

class BinanceAPIError(Exception):
    """Raised when Binance returns a non-2xx response."""
    def __init__(self, body):
        self.body = body
        code = body.get("code", "?") if isinstance(body, dict) else "?"
        msg  = body.get("msg",  str(body)) if isinstance(body, dict) else str(body)
        super().__init__(f"Binance API error {code}: {msg}")


class NetworkError(Exception):
    """Raised on connection/timeout failures."""