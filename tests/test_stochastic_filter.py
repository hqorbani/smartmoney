
import numpy as np
import pandas as pd
import pytest

from smartmoney.config import Config
from smartmoney.services.stochastic_filter import StochasticFilter


@pytest.fixture
def valid_df():
    rng = np.random.default_rng(42)
    close = 100 + np.cumsum(rng.normal(0, 0.5, 100))

    return pd.DataFrame({
        "high": close + rng.uniform(0.1, 1.0, 100),
        "low": close - rng.uniform(0.1, 1.0, 100),
        "close": close,
    })


def test_filter_disabled_allows_entry(monkeypatch):
    monkeypatch.setattr(Config, "ENABLE_STOCHASTIC_FILTER", False)

    assert StochasticFilter.is_entry_allowed(None, "BUY") is True
    assert StochasticFilter.is_entry_allowed(None, "SELL") is True


@pytest.mark.parametrize("direction", ["BUY", "SELL"])
def test_insufficient_data_blocks_entry(monkeypatch, direction):
    monkeypatch.setattr(Config, "ENABLE_STOCHASTIC_FILTER", True)

    df = pd.DataFrame({
        "high": [101.0],
        "low": [99.0],
        "close": [100.0],
    })

    assert StochasticFilter.is_entry_allowed(df, direction) is False


def test_missing_columns_block_entry(monkeypatch):
    monkeypatch.setattr(Config, "ENABLE_STOCHASTIC_FILTER", True)

    df = pd.DataFrame({"close": [100.0]})

    assert StochasticFilter.is_entry_allowed(df, "BUY") is False


def test_invalid_direction_blocks_entry(monkeypatch, valid_df):
    monkeypatch.setattr(Config, "ENABLE_STOCHASTIC_FILTER", True)

    assert StochasticFilter.is_entry_allowed(valid_df, "HOLD") is False


@pytest.mark.parametrize("direction", ["BUY", "SELL"])
def test_non_finite_data_blocks_entry(monkeypatch, direction):
    monkeypatch.setattr(Config, "ENABLE_STOCHASTIC_FILTER", True)

    df = pd.DataFrame({
        "high": [np.nan] * 100,
        "low": [np.nan] * 100,
        "close": [np.nan] * 100,
    })

    assert StochasticFilter.is_entry_allowed(df, direction) is False


def test_buy_sell_threshold_logic(monkeypatch, valid_df):
    monkeypatch.setattr(Config, "ENABLE_STOCHASTIC_FILTER", True)

    # Mock the calculated %K value to test thresholds directly.
    import smartmoney.services.stochastic_filter as module

    monkeypatch.setattr(
        module.talib,
        "STOCH",
        lambda *args, **kwargs: (
            np.array([50.0] * (len(args[0]) - 1) + [79.0]),
            np.array([50.0] * len(args[0])),
        ),
    )

    assert StochasticFilter.is_entry_allowed(valid_df, "BUY") is True
    assert StochasticFilter.is_entry_allowed(valid_df, "SELL") is True

    monkeypatch.setattr(
        module.talib,
        "STOCH",
        lambda *args, **kwargs: (
            np.array([50.0] * (len(args[0]) - 1) + [80.0]),
            np.array([50.0] * len(args[0])),
        ),
    )

    assert StochasticFilter.is_entry_allowed(valid_df, "BUY") is False

    monkeypatch.setattr(
        module.talib,
        "STOCH",
        lambda *args, **kwargs: (
            np.array([50.0] * (len(args[0]) - 1) + [20.0]),
            np.array([50.0] * len(args[0])),
        ),
    )

    assert StochasticFilter.is_entry_allowed(valid_df, "SELL") is False
