import pytest

from services.portfolio import Portfolio


def test_buy_then_sell_round_trip_with_fees():
    portfolio = Portfolio(1000)
    fee = portfolio.buy("BTCUSDT", 1, 100, fee_rate=0.01)
    assert fee == pytest.approx(1)
    assert portfolio.balance == pytest.approx(899)
    assert portfolio.positions["BTCUSDT"]["average_price"] == pytest.approx(101)  # the fee is part of the cost

    fee, pnl = portfolio.sell("BTCUSDT", 1, 110, fee_rate=0.01)
    assert fee == pytest.approx(1.1)
    assert pnl == pytest.approx(110 - 1.1 - 101)
    assert portfolio.balance == pytest.approx(899 + 108.9)
    assert "BTCUSDT" not in portfolio.positions


def test_average_price_across_two_buys():
    portfolio = Portfolio(1000)
    portfolio.buy("ETHUSDT", 1, 100)
    portfolio.buy("ETHUSDT", 1, 200)
    assert portfolio.positions["ETHUSDT"] == {"quantity": 2, "average_price": 150}


def test_cannot_overspend_or_oversell():
    portfolio = Portfolio(100)
    with pytest.raises(ValueError):
        portfolio.buy("BTCUSDT", 2, 100)
    portfolio.buy("BTCUSDT", 0.5, 100)
    with pytest.raises(ValueError):
        portfolio.sell("BTCUSDT", 1, 100)


def test_equity_marks_positions_to_market():
    portfolio = Portfolio(1000)
    portfolio.buy("BTCUSDT", 2, 100)
    assert portfolio.equity({"BTCUSDT": 150}) == pytest.approx(800 + 300)


def test_state_round_trip():
    portfolio = Portfolio(1000)
    portfolio.buy("BTCUSDT", 0.1, 100)
    restored = Portfolio.from_dict(portfolio.to_dict())
    assert restored.balance == portfolio.balance
    assert restored.positions == portfolio.positions
    assert restored.initial_balance == 1000
