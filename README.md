# 🤖 Binance Futures Testnet Trading Bot

A lightweight Python CLI app to place **Market**, **Limit**, and **Stop-Market** orders on the [Binance Futures USDT-M Testnet](https://testnet.binancefuture.com).

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py          # Package marker
│   ├── client.py            # Binance REST API wrapper (signing, HTTP)
│   ├── orders.py            # Order placement logic
│   ├── validators.py        # CLI input validation
│   ├── logging_config.py    # Rotating file + console logging
│   └── cli.py               # Argparse CLI entry point
├── logs/
│   └── trading_bot.log      # Auto-created on first run
├── README.md
└── requirements.txt
```

---

## Setup

### 1. Get Testnet API Credentials

1. Visit [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Log in with your GitHub account
3. Go to **API Key** tab → click **Generate** (no expiry needed)
4. Copy your **API Key** and **Secret Key**

### 2. Clone / Download the Project

```bash
git clone https://github.com/<your-username>/trading-bot.git
cd trading_bot
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Set Environment Variables

**Linux / macOS:**
```bash
export BINANCE_API_KEY=your_api_key_here
export BINANCE_API_SECRET=your_api_secret_here
```

**Windows (Command Prompt):**
```cmd
set BINANCE_API_KEY=your_api_key_here
set BINANCE_API_SECRET=your_api_secret_here
```

> ⚠️ Never hardcode your keys in source code. Always use environment variables.

---

## How to Run

### Syntax

```bash
python -m bot.cli --symbol <SYMBOL> --side <BUY|SELL> --type <ORDER_TYPE> --qty <QTY> [--price <PRICE>] [--stop-price <STOP_PRICE>] [--verbose]
```

### Examples

**1. Market Buy Order**
```bash
python -m bot.cli --symbol BTCUSDT --side BUY --type MARKET --qty 0.001
```

**2. Limit Sell Order**
```bash
python -m bot.cli --symbol ETHUSDT --side SELL --type LIMIT --qty 0.01 --price 3200
```

**3. Stop-Market Sell Order** *(Bonus order type)*
```bash
python -m bot.cli --symbol BTCUSDT --side SELL --type STOP_MARKET --qty 0.001 --stop-price 58000
```

**4. With verbose (DEBUG) output**
```bash
python -m bot.cli --symbol BTCUSDT --side BUY --type MARKET --qty 0.001 --verbose
```

---

## Sample Output

```
──────────────────────────────────────────────────
  ORDER REQUEST SUMMARY
──────────────────────────────────────────────────
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Quantity   : 0.001
──────────────────────────────────────────────────

──────────────────────────────────────────────────
  ORDER RESPONSE
──────────────────────────────────────────────────
  Order ID     : 3842910234
  Symbol       : BTCUSDT
  Side         : BUY
  Type         : MARKET
  Status       : FILLED
  Orig Qty     : 0.001
  Executed Qty : 0.001
  Avg Price    : 67412.30
  Time-In-Force: GTC
──────────────────────────────────────────────────
  ✅  Order placed successfully!
──────────────────────────────────────────────────
```

---

## Log Files

Logs are written to `logs/trading_bot.log` automatically.

```
2025-06-11 10:12:01 | INFO     | trading_bot.client | BinanceClient initialized. Base URL: https://testnet.binancefuture.com
2025-06-11 10:12:01 | INFO     | trading_bot.orders | Placing BUY MARKET order | symbol=BTCUSDT qty=0.001 price=None stopPrice=None
2025-06-11 10:12:01 | INFO     | trading_bot.client | POST https://testnet.binancefuture.com/fapi/v1/order | params: {...}
2025-06-11 10:12:02 | INFO     | trading_bot.client | Response [200]: {'orderId': 3842910234, 'status': 'FILLED', ...}
2025-06-11 10:12:02 | INFO     | trading_bot.cli    | Order completed successfully. orderId=3842910234 status=FILLED
```

---

## Validation Rules

| Field       | Rule                                               |
|-------------|---------------------------------------------------|
| symbol      | Alphabetic only, min 5 chars (e.g. BTCUSDT)       |
| side        | Must be BUY or SELL                               |
| type        | Must be MARKET, LIMIT, or STOP_MARKET             |
| qty         | Must be a positive number                         |
| price       | Required for LIMIT; ignored for MARKET            |
| stop-price  | Required for STOP_MARKET                          |

---

## Assumptions

- All orders target the **USDT-M Futures Testnet** (`https://testnet.binancefuture.com`).
- The testnet account must have sufficient **virtual USDT** balance (available from the testnet dashboard).
- Quantity precision must match symbol rules (e.g. BTC is typically 0.001 minimum). If Binance rejects the order with a precision error, adjust your `--qty` accordingly.
- `timeInForce` for LIMIT orders defaults to **GTC** (Good-Till-Cancelled).
- No real money is involved — this is a testnet-only bot.

---

## Dependencies

| Package  | Version   | Purpose              |
|----------|-----------|----------------------|
| requests | ≥ 2.31.0  | HTTP calls to Binance |

---

## Error Handling

| Scenario              | Behaviour                                      |
|-----------------------|------------------------------------------------|
| Missing API keys      | Clear message + exit code 1                    |
| Invalid CLI input     | Validation error message + exit code 1         |
| Binance API error     | Prints Binance error code + message + exit 1   |
| Network failure       | Prints connectivity hint + exit code 1         |
| Unexpected exception  | Full traceback logged to file; clean msg shown |