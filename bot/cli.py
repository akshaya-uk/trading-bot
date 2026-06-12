"""
cli.py — Command-line interface entry point.
Uses argparse.  All business logic is delegated to orders.py.
"""

import argparse
import logging
import os
import sys

from bot.logging_config import setup_logging
from bot.client         import BinanceClient, BinanceAPIError, NetworkError
from bot.validators     import validate_all
from bot.orders         import place_order

logger = logging.getLogger("trading_bot.cli")


# ── Helpers ─────────────────────────────────────────────────────────────────

def _print_summary(validated: dict) -> None:
    """Pretty-print the order request before sending."""
    print("\n" + "─" * 50)
    print("  ORDER REQUEST SUMMARY")
    print("─" * 50)
    print(f"  Symbol     : {validated['symbol']}")
    print(f"  Side       : {validated['side']}")
    print(f"  Type       : {validated['order_type']}")
    print(f"  Quantity   : {validated['quantity']}")
    if validated["price"]:
        print(f"  Price      : {validated['price']}")
    if validated["stop_price"]:
        print(f"  Stop Price : {validated['stop_price']}")
    print("─" * 50 + "\n")


def _print_result(result: dict) -> None:
    """Pretty-print the order response from Binance."""
    print("\n" + "─" * 50)
    print("  ORDER RESPONSE")
    print("─" * 50)
    print(f"  Order ID     : {result['orderId']}")
    print(f"  Symbol       : {result['symbol']}")
    print(f"  Side         : {result['side']}")
    print(f"  Type         : {result['type']}")
    print(f"  Status       : {result['status']}")
    print(f"  Orig Qty     : {result['origQty']}")
    print(f"  Executed Qty : {result['executedQty']}")
    print(f"  Avg Price    : {result['avgPrice']}")
    print(f"  Time-In-Force: {result['timeInForce']}")
    print("─" * 50)
    print("  ✅  Order placed successfully!")
    print("─" * 50 + "\n")


# ── Argument parser ──────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Place orders on Binance Futures Testnet (USDT-M)",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python -m bot.cli --symbol BTCUSDT --side BUY  --type MARKET --qty 0.001\n"
            "  python -m bot.cli --symbol ETHUSDT --side SELL --type LIMIT  --qty 0.01 --price 3200\n"
            "  python -m bot.cli --symbol BTCUSDT --side SELL --type STOP_MARKET --qty 0.001 --stop-price 58000\n"
        ),
    )

    parser.add_argument("--symbol",     required=True,  help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side",       required=True,  help="BUY or SELL")
    parser.add_argument("--type",       required=True,  dest="order_type", help="MARKET, LIMIT, or STOP_MARKET")
    parser.add_argument("--qty",        required=True,  dest="quantity",   help="Order quantity (e.g. 0.001)")
    parser.add_argument("--price",      default=None,   help="Limit price (required for LIMIT orders)")
    parser.add_argument("--stop-price", default=None,   dest="stop_price", help="Stop price (required for STOP_MARKET orders)")
    parser.add_argument("--verbose",    action="store_true", help="Enable DEBUG output on console")

    return parser


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = build_parser()
    args   = parser.parse_args()

    # 1. Logging
    setup_logging(verbose=args.verbose)
    logger.info("CLI started with args: %s", vars(args))

    # 2. API credentials from environment variables (never hardcoded)
    api_key    = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        print(
            "\n❌  Missing API credentials.\n"
            "    Set environment variables before running:\n"
            "      export BINANCE_API_KEY=<your_key>\n"
            "      export BINANCE_API_SECRET=<your_secret>\n"
        )
        logger.error("BINANCE_API_KEY or BINANCE_API_SECRET not set in environment.")
        sys.exit(1)

    # 3. Validate inputs
    try:
        validated = validate_all(
            symbol     = args.symbol,
            side       = args.side,
            order_type = args.order_type,
            quantity   = args.quantity,
            price      = args.price,
            stop_price = args.stop_price,
        )
    except ValueError as e:
        print(f"\n❌  Validation error: {e}\n")
        logger.error("Validation failed: %s", e)
        sys.exit(1)

    _print_summary(validated)

    # 4. Place order
    client = BinanceClient(api_key, api_secret)
    try:
        result = place_order(
            client     = client,
            symbol     = validated["symbol"],
            side       = validated["side"],
            order_type = validated["order_type"],
            quantity   = validated["quantity"],
            price      = validated["price"],
            stop_price = validated["stop_price"],
        )
        _print_result(result)
        logger.info("Order completed successfully. orderId=%s status=%s",
                    result["orderId"], result["status"])

    except BinanceAPIError as e:
        print(f"\n❌  Binance API Error: {e}\n")
        logger.error("Order failed with BinanceAPIError: %s", e)
        sys.exit(1)

    except NetworkError as e:
        print(f"\n❌  Network Error: {e}\n")
        logger.error("Order failed with NetworkError: %s", e)
        sys.exit(1)

    except Exception as e:
        print(f"\n❌  Unexpected error: {e}\n")
        logger.exception("Unexpected error during order placement.")
        sys.exit(1)


if __name__ == "__main__":
    main()