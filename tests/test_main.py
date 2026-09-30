import main
from tests.helpers import make_candles


class FakeDataHandler:
    def __init__(self, credentials=None):
        pass

    def get_historical_data(self, symbol, interval, start_date, end_date=None):
        return make_candles([100, 101] * 15 + [80, 85, 95, 100, 101, 100, 125, 120])


def test_backtest_command_end_to_end(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(main, "DataHandler", FakeDataHandler)
    chart = tmp_path / "chart.png"

    main.main(["backtest", "BTCUSDT", "--start", "2024-01-01", "--plot", str(chart), "--fraction", "0.5"])

    output = capsys.readouterr().out
    assert "Strategy return" in output
    assert "1 closed, win rate 100%" in output
    assert chart.stat().st_size > 0
