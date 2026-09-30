import pytest

from services.portfolio import Portfolio
from services.risk_manager import RiskManager


def test_buy_spends_a_fraction_of_the_balance():
    quantity = RiskManager(trade_fraction=0.02).size_order(Portfolio(10_000), 1, 100, "BTCUSDT")
    assert quantity == pytest.approx(2)


def test_buy_below_min_notional_is_skipped():
    risk = RiskManager(trade_fraction=0.02, min_notional=10)
    assert risk.size_order(Portfolio(100), 1, 100, "BTCUSDT") == 0  # only a 2$ order


def test_sell_closes_the_whole_position():
    portfolio = Portfolio(10_000)
    portfolio.buy("BTCUSDT", 3, 100)
    assert RiskManager().size_order(portfolio, -1, 100, "BTCUSDT") == 3


def test_sell_without_position_and_hold_are_skipped():
    risk = RiskManager()
    assert risk.size_order(Portfolio(10_000), -1, 100, "BTCUSDT") == 0
    assert risk.size_order(Portfolio(10_000), 0, 100, "BTCUSDT") == 0
