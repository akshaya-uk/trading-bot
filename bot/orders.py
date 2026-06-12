"""
orders.py — Order placement logic.
Translates validated user inputs into Binance API parameters
and returns a clean result dict.
"""

import logging
from bot.client import BinanceClient

logger = logging.getLogger("trading_bot.orders")


def place_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float | None = None,
    stop_price: float | None = None,
) -> dict:
    """
    Build the correct parameter set for the given order type and call
    client.place_order().  Returns a normalised result dict.
    """
    params = {
        "symbol":   symbol,
        "side":     side,
        "type":     order_type,
        "quantity": quantity,
    }

    if order_type == "LIMIT":
        params["price"]       = price
        params["timeInForce"] = "GTC"          # Good-Till-Cancelled

    elif order_type == "STOP_MARKET":
        params["stopPrice"] = stop_price

    logger.info(
        "Placing %s %s order | symbol=%s qty=%s price=%s stopPrice=%s",
        side, order_type, symbol, quantity, price, stop_price,
    )

    raw = client.place_order(**params)
    return _parse_response(raw)


def _parse_response(raw: dict) -> dict:
    """Extract the fields we care about from the raw Binance response."""
    return {
        "orderId":     raw.get("orderId"),
        "symbol":      raw.get("symbol"),
        "side":        raw.get("side"),
        "type":        raw.get("type"),
        "status":      raw.get("status"),
        "origQty":     raw.get("origQty"),
        "executedQty": raw.get("executedQty"),
        "avgPrice":    raw.get("avgPrice") or raw.get("price") or "N/A",
        "timeInForce": raw.get("timeInForce", "N/A"),
        "updateTime":  raw.get("updateTime"),
    }