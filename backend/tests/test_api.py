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

    def test_classify_signal_trending_up(self):
        from indicators import classify_signal
        assert classify_signal(rsi=50, sma_20=155.0, sma_50=150.0) == "trending_up"

    def test_classify_signal_trending_down(self):
        from indicators import classify_signal
        assert classify_signal(rsi=50, sma_20=145.0, sma_50=150.0) == "trending_down"

    def test_classify_signal_sma_equal_returns_neutral(self):
        from indicators import classify_signal
        assert classify_signal(rsi=50, sma_20=150.0, sma_50=150.0) == "neutral"

    def test_rsi_boundary_exactly_70_is_overbought(self):
        from indicators import classify_signal
        assert classify_signal(rsi=70) == "overbought"

    def test_rsi_boundary_exactly_30_is_oversold(self):
        from indicators import classify_signal
        assert classify_signal(rsi=30) == "oversold"


class TestHealthEndpoint:
    def test_health_returns_200(self):
        client = get_client()
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_returns_ok_status(self):
        client = get_client()
        resp = client.get("/health")
        data = resp.json()
        assert data["status"] == "ok"


class TestSafeFloat:
    def test_safe_float_none_returns_none(self):
        from main import safe_float
        assert safe_float(None) is None

    def test_safe_float_nan_returns_none(self):
        import math
        from main import safe_float
        assert safe_float(float("nan")) is None

    def test_safe_float_valid_float_returns_rounded(self):
        from main import safe_float
        result = safe_float(3.14159)
        assert result == 3.1416

    def test_safe_float_invalid_string_returns_none(self):
        from main import safe_float
        assert safe_float("not_a_number") is None

    def test_safe_float_integer_returns_float(self):
        from main import safe_float
        result = safe_float(42)
        assert result == 42.0
        assert isinstance(result, float)


class TestFetchOhlcv:
    def test_fetch_ohlcv_returns_none_on_exception(self):
        import yfinance as yf
        from main import fetch_ohlcv
        with patch.object(yf.Ticker, "history", side_effect=Exception("network error")):
            result = fetch_ohlcv("FAKE")
        assert result is None

    def test_fetch_ohlcv_returns_none_on_empty_df(self):
        import pandas as pd
        from main import fetch_ohlcv
        empty_df = pd.DataFrame()
        with patch("main.yf.Ticker") as mock_ticker:
            mock_ticker.return_value.history.return_value = empty_df
            result = fetch_ohlcv("EMPTY")
        assert result is None


class TestCaching:
    def test_cache_hit_skips_fetch(self):
        import main
        import time
        client = get_client()
        mock_df = make_mock_df()
        # Warm the cache
        with patch("main.fetch_ohlcv", return_value=mock_df) as mock_fetch:
            client.get("/api/ticker/AAPL/indicators")
            first_call_count = mock_fetch.call_count

        # Second call should hit cache — fetch_ohlcv not called again
        with patch("main.fetch_ohlcv", return_value=mock_df) as mock_fetch2:
            client.get("/api/ticker/AAPL/indicators")
            assert mock_fetch2.call_count == 0, "Cache hit should skip fetch_ohlcv"


class TestHistoryLength:
    def test_history_capped_at_90_rows(self):
        client = get_client()
        # 200 rows of data — history should be capped at 90
        mock_df = make_mock_df(200)
        with patch("main.fetch_ohlcv", return_value=mock_df):
            resp = client.get("/api/ticker/MSFT/indicators")
        data = resp.json()
        assert len(data["history"]) <= 90

    def test_history_includes_indicator_columns(self):
        client = get_client()
        mock_df = make_mock_df()
        with patch("main.fetch_ohlcv", return_value=mock_df):
            resp = client.get("/api/ticker/MSFT/indicators")
        data = resp.json()
        entry = data["history"][0]
        for field in ("sma_20", "sma_50", "rsi", "macd", "macd_signal", "bb_upper", "bb_lower"):
            assert field in entry
