"""
validators.py — Input validation before any API call is made.
Raises ValueError with clear messages on bad input.
"""

import logging

logger = logging.getLogger("trading_bot.validators")

VALID_SIDES       = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}   # extend as needed


def validate_symbol(symbol: str) -> str:
    s = symbol.strip().upper()
    if not s.isalpha() or len(s) < 5:
        raise ValueError(
            f"Invalid symbol '{symbol}'. "
            "Expected something like BTCUSDT, ETHUSDT, etc."
        )
    logger.debug("Symbol validated: %s", s)
    return s


def validate_side(side: str) -> str:
    s = side.strip().upper()
    if s not in VALID_SIDES:
        raise ValueError(
            f"Invalid side '{side}'. Must be one of: {', '.join(VALID_SIDES)}"
        )
    logger.debug("Side validated: %s", s)
    return s


def validate_order_type(order_type: str) -> str:
    t = order_type.strip().upper()
    if t not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Invalid order type '{order_type}'. "
            f"Must be one of: {', '.join(VALID_ORDER_TYPES)}"
        )
    logger.debug("Order type validated: %s", t)
    return t


def validate_quantity(quantity: str) -> float:
    try:
        q = float(quantity)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid quantity '{quantity}'. Must be a positive number.")
    if q <= 0:
        raise ValueError(f"Quantity must be greater than 0. Got: {q}")
    logger.debug("Quantity validated: %s", q)
    return q


def validate_price(price: str | None, order_type: str) -> float | None:
    """
    Price is required for LIMIT orders, forbidden for MARKET orders.
    Returns float or None.
    """
    if order_type == "LIMIT":
        if price is None:
            raise ValueError("Price is required for LIMIT orders. Use --price <value>.")
        try:
            p = float(price)
        except (TypeError, ValueError):
            raise ValueError(f"Invalid price '{price}'. Must be a positive number.")
        if p <= 0:
            raise ValueError(f"Price must be greater than 0. Got: {p}")
        logger.debug("Price validated: %s", p)
        return p

    if order_type == "MARKET" and price is not None:
        logger.warning("Price '%s' supplied for MARKET order — it will be ignored.", price)

    return None


def validate_stop_price(stop_price: str | None, order_type: str) -> float | None:
    """Stop price is required for STOP_MARKET orders."""
    if order_type == "STOP_MARKET":
        if stop_price is None:
            raise ValueError("--stop-price is required for STOP_MARKET orders.")
        try:
            sp = float(stop_price)
        except (TypeError, ValueError):
            raise ValueError(f"Invalid stop price '{stop_price}'.")
        if sp <= 0:
            raise ValueError(f"Stop price must be > 0. Got: {sp}")
        logger.debug("Stop price validated: %s", sp)
        return sp
    return None


def validate_all(symbol, side, order_type, quantity, price=None, stop_price=None):
    """Run all validators and return a clean dict of validated values."""
    return {
        "symbol":     validate_symbol(symbol),
        "side":       validate_side(side),
        "order_type": validate_order_type(order_type),
        "quantity":   validate_quantity(quantity),
        "price":      validate_price(price, order_type.upper()),
        "stop_price": validate_stop_price(stop_price, order_type.upper()),
    }