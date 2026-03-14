# Technical Analysis Scanner

Real-time technical analysis dashboard for 20 major S&P 500 stocks. Computes SMA, RSI, MACD, and Bollinger Bands via a FastAPI backend and surfaces buy/sell signals in a React frontend.

## What it does

- **Signal classification** — labels each ticker as `overbought`, `oversold`, `trending_up`, `trending_down`, or `neutral` based on RSI and SMA crossovers
- **Indicator breakdown** — SMA(20), SMA(50), RSI(14), MACD(12/26/9), Bollinger Bands(20, 2σ)
- **90-day history** — per-ticker OHLCV + all indicators for charting
- **20-stock watchlist** — AAPL, MSFT, NVDA, GOOGL, AMZN, META, TSLA, BRK-B, JPM, JNJ, V, XOM, UNH, LLY, AVGO, PG, MA, HD, CVX, MRK
- **1-minute cache** — yfinance data cached per ticker to avoid rate limits

## Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI + yfinance + pandas |
| Frontend | React + Vite + Tailwind CSS |
| Container | Docker Compose |

## API

Base URL: `http://localhost:8104`

| Endpoint | Description |
|---|---|
| `GET /api/tickers` | Returns the default 20-ticker watchlist |
| `GET /api/ticker/{symbol}/indicators` | Full indicator set + 90-day history for a ticker |
| `GET /health` | Health check |

### Example

```bash
curl http://localhost:8104/api/ticker/AAPL/indicators
```

```json
{
  "symbol": "AAPL",
  "last_price": 213.49,
  "sma_20": 210.12,
  "sma_50": 205.88,
  "rsi": 58.3,
  "macd": 1.42,
  "macd_signal": 0.97,
  "bb_upper": 221.4,
  "bb_lower": 198.8,
  "signal": "trending_up",
  "history": [...]
}
```

## Running

```bash
docker compose up -d --build
```

- Frontend: http://localhost:5176
- Backend API: http://localhost:8104
- API docs: http://localhost:8104/docs

## Development

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8104
```

```bash
cd frontend
npm install
npm run dev
```

## Tests

```bash
cd backend
pytest tests/
```

> **Disclaimer:** See [DISCLAIMER.md](./DISCLAIMER.md) for legal notices.
