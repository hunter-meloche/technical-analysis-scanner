"""Technical Analysis Scanner — FastAPI Backend"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import time
from typing import Optional
from indicators import compute_sma, compute_rsi, compute_macd, compute_bollinger, classify_signal

app = FastAPI(title="Technical Analysis Scanner", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DEFAULT_TICKERS = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN",
    "META", "TSLA", "BRK-B", "JPM", "JNJ",
    "V", "XOM", "UNH", "LLY", "AVGO",
    "PG", "MA", "HD", "CVX", "MRK",
]

CACHE_TTL = 60  # seconds
_cache: dict = {}


def safe_float(val) -> Optional[float]:
    if val is None:
        return None
    try:
        f = float(val)
        return None if pd.isna(f) else round(f, 4)
    except (TypeError, ValueError):
        return None


def fetch_ohlcv(symbol: str, period: str = "6mo") -> Optional[pd.DataFrame]:
    """Fetch OHLCV data via yfinance. Returns None if data unavailable."""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        if df.empty:
            return None
        return df[["Open", "High", "Low", "Close", "Volume"]]
    except Exception:
        return None


@app.get("/api/tickers")
def get_tickers():
    """Return the default watchlist of tickers."""
    return DEFAULT_TICKERS


@app.get("/api/ticker/{symbol}/indicators")
def get_indicators(symbol: str):
    """Compute and return technical indicators for a given ticker."""
    key = symbol.upper()

    # Return cached result if still fresh
    cached = _cache.get(key)
    if cached and time.time() - cached["ts"] < CACHE_TTL:
        return cached["data"]

    df = fetch_ohlcv(key)
    if df is None:
        raise HTTPException(status_code=404, detail=f"No data found for {symbol}")

    close = df["Close"]
    sma20 = compute_sma(close, 20)
    sma50 = compute_sma(close, 50)
    rsi = compute_rsi(close)
    macd, macd_signal = compute_macd(close)
    bb_upper, bb_lower = compute_bollinger(close)

    last_rsi = safe_float(rsi.iloc[-1])
    last_sma20 = safe_float(sma20.iloc[-1])
    last_sma50 = safe_float(sma50.iloc[-1])
    signal = classify_signal(
        rsi=last_rsi or 50,
        sma_20=last_sma20,
        sma_50=last_sma50
    )

    # Build history (last 90 rows max) — slice all series at once by shared index
    tail_idx = df.index[-90:]
    hist_df = pd.DataFrame({
        "open":        df["Open"].reindex(tail_idx),
        "high":        df["High"].reindex(tail_idx),
        "low":         df["Low"].reindex(tail_idx),
        "close":       df["Close"].reindex(tail_idx),
        "volume":      df["Volume"].reindex(tail_idx),
        "sma_20":      sma20.reindex(tail_idx),
        "sma_50":      sma50.reindex(tail_idx),
        "rsi":         rsi.reindex(tail_idx),
        "macd":        macd.reindex(tail_idx),
        "macd_signal": macd_signal.reindex(tail_idx),
        "bb_upper":    bb_upper.reindex(tail_idx),
        "bb_lower":    bb_lower.reindex(tail_idx),
    })

    history = [
        {
            "date": str(idx.date()),
            "open": safe_float(row["open"]),
            "high": safe_float(row["high"]),
            "low": safe_float(row["low"]),
            "close": safe_float(row["close"]),
            "volume": int(row["volume"]) if pd.notna(row["volume"]) else 0,
            "sma_20": safe_float(row["sma_20"]),
            "sma_50": safe_float(row["sma_50"]),
            "rsi": safe_float(row["rsi"]),
            "macd": safe_float(row["macd"]),
            "macd_signal": safe_float(row["macd_signal"]),
            "bb_upper": safe_float(row["bb_upper"]),
            "bb_lower": safe_float(row["bb_lower"]),
        }
        for idx, row in hist_df.iterrows()
    ]

    result = {
        "symbol": key,
        "last_price": safe_float(close.iloc[-1]),
        "sma_20": last_sma20,
        "sma_50": last_sma50,
        "rsi": last_rsi,
        "macd": safe_float(macd.iloc[-1]),
        "macd_signal": safe_float(macd_signal.iloc[-1]),
        "bb_upper": safe_float(bb_upper.iloc[-1]),
        "bb_lower": safe_float(bb_lower.iloc[-1]),
        "signal": signal,
        "history": history,
    }
    _cache[key] = {"ts": time.time(), "data": result}
    return result


@app.get("/health")
def health():
    return {"status": "ok"}
