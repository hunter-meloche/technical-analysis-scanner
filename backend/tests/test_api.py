"""
TDD Tests for Technical Analysis Scanner API
Written BEFORE implementation — these should fail initially (red phase).
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


# Import will fail until main.py is implemented
def get_client():
    from main import app
    return TestClient(app)


def make_mock_df(n=100):
    """Create a mock OHLCV DataFrame with enough rows for all indicators."""
    dates = pd.date_range("2025-01-01", periods=n, freq="B")
    np.random.seed(42)
    close = 150 + np.cumsum(np.random.randn(n))
    high = close + np.abs(np.random.randn(n))
    low = close - np.abs(np.random.randn(n))
    open_ = close + np.random.randn(n) * 0.5
    volume = np.random.randint(1_000_000, 10_000_000, n).astype(float)
    return pd.DataFrame({
        "Open": open_, "High": high, "Low": low,
        "Close": close, "Volume": volume
    }, index=dates)


class TestTickersEndpoint:
    def test_get_tickers_returns_200(self):
        client = get_client()
        resp = client.get("/api/tickers")
        assert resp.status_code == 200

    def test_get_tickers_returns_list(self):
        client = get_client()
        resp = client.get("/api/tickers")
        data = resp.json()
        assert isinstance(data, list)

    def test_get_tickers_has_at_least_10_entries(self):
        client = get_client()
        resp = client.get("/api/tickers")
        data = resp.json()
        assert len(data) >= 10

    def test_get_tickers_contains_aapl(self):
        client = get_client()
        resp = client.get("/api/tickers")
        symbols = resp.json()
        assert "AAPL" in symbols


class TestIndicatorsEndpoint:
    def test_indicators_returns_200(self):
        client = get_client()
        mock_df = make_mock_df()
        with patch("main.fetch_ohlcv", return_value=mock_df):
            resp = client.get("/api/ticker/AAPL/indicators")
        assert resp.status_code == 200

    def test_indicators_has_symbol_field(self):
        client = get_client()
        mock_df = make_mock_df()
        with patch("main.fetch_ohlcv", return_value=mock_df):
            resp = client.get("/api/ticker/AAPL/indicators")
        data = resp.json()
        assert data["symbol"] == "AAPL"

    def test_indicators_has_last_price(self):
        client = get_client()
        mock_df = make_mock_df()
        with patch("main.fetch_ohlcv", return_value=mock_df):
            resp = client.get("/api/ticker/AAPL/indicators")
        data = resp.json()
        assert "last_price" in data
        assert isinstance(data["last_price"], float)

    def test_indicators_has_sma20(self):
        client = get_client()
        mock_df = make_mock_df()
        with patch("main.fetch_ohlcv", return_value=mock_df):
            resp = client.get("/api/ticker/AAPL/indicators")
        data = resp.json()
        assert "sma_20" in data
        assert data["sma_20"] is not None

    def test_indicators_has_sma50(self):
        client = get_client()
        mock_df = make_mock_df()
        with patch("main.fetch_ohlcv", return_value=mock_df):
            resp = client.get("/api/ticker/AAPL/indicators")
        data = resp.json()
        assert "sma_50" in data
        assert data["sma_50"] is not None

    def test_indicators_has_rsi(self):
        client = get_client()
        mock_df = make_mock_df()
        with patch("main.fetch_ohlcv", return_value=mock_df):
            resp = client.get("/api/ticker/AAPL/indicators")
        data = resp.json()
        assert "rsi" in data
        assert data["rsi"] is not None
        assert 0 <= data["rsi"] <= 100

    def test_indicators_has_macd(self):
        client = get_client()
        mock_df = make_mock_df()
        with patch("main.fetch_ohlcv", return_value=mock_df):
            resp = client.get("/api/ticker/AAPL/indicators")
        data = resp.json()
        assert "macd" in data
        assert "macd_signal" in data

    def test_indicators_has_bollinger_bands(self):
        client = get_client()
        mock_df = make_mock_df()
        with patch("main.fetch_ohlcv", return_value=mock_df):
            resp = client.get("/api/ticker/AAPL/indicators")
        data = resp.json()
        assert "bb_upper" in data
        assert "bb_lower" in data
        assert data["bb_upper"] > data["bb_lower"]

    def test_indicators_has_signal(self):
        client = get_client()
        mock_df = make_mock_df()
        with patch("main.fetch_ohlcv", return_value=mock_df):
            resp = client.get("/api/ticker/AAPL/indicators")
        data = resp.json()
        assert "signal" in data
        assert data["signal"] in ("overbought", "oversold", "neutral", "trending_up", "trending_down")

    def test_indicators_has_history(self):
        client = get_client()
        mock_df = make_mock_df()
        with patch("main.fetch_ohlcv", return_value=mock_df):
            resp = client.get("/api/ticker/AAPL/indicators")
        data = resp.json()
        assert "history" in data
        assert isinstance(data["history"], list)
        assert len(data["history"]) > 0

    def test_indicators_history_has_ohlcv(self):
        client = get_client()
        mock_df = make_mock_df()
        with patch("main.fetch_ohlcv", return_value=mock_df):
            resp = client.get("/api/ticker/AAPL/indicators")
        data = resp.json()
        entry = data["history"][0]
        for field in ("date", "open", "high", "low", "close", "volume"):
            assert field in entry

    def test_indicators_unknown_ticker_returns_404(self):
        client = get_client()
        with patch("main.fetch_ohlcv", return_value=None):
            resp = client.get("/api/ticker/XXXXXX/indicators")
        assert resp.status_code == 404


class TestIndicatorLogic:
    """Unit tests for the indicator computation logic."""

    def test_sma20_computed_correctly(self):
        from indicators import compute_sma
        close = pd.Series(range(1, 26), dtype=float)
        sma = compute_sma(close, 20)
        # Last value should be mean of last 20 values (6..25)
        expected = sum(range(6, 26)) / 20
        assert abs(sma.iloc[-1] - expected) < 0.001

    def test_rsi_in_valid_range(self):
        from indicators import compute_rsi
        close = pd.Series(range(1, 51), dtype=float)  # all gains → high RSI
        rsi = compute_rsi(close, period=14)
        valid = rsi.dropna()
        assert all(0 <= v <= 100 for v in valid)

    def test_macd_returns_macd_and_signal(self):
        from indicators import compute_macd
        close = pd.Series(range(1, 101), dtype=float)
        macd, signal = compute_macd(close)
        assert len(macd) == len(close)
        assert len(signal) == len(close)

    def test_bollinger_bands_upper_above_lower(self):
        from indicators import compute_bollinger
        close = pd.Series(range(1, 51), dtype=float)
        upper, lower = compute_bollinger(close)
        valid_mask = upper.notna() & lower.notna()
        assert all(upper[valid_mask] >= lower[valid_mask])

    def test_classify_signal_overbought(self):
        from indicators import classify_signal
        assert classify_signal(rsi=75) == "overbought"

    def test_classify_signal_oversold(self):
        from indicators import classify_signal
        assert classify_signal(rsi=25) == "oversold"

    def test_classify_signal_neutral(self):
        from indicators import classify_signal
        assert classify_signal(rsi=50) == "neutral"
