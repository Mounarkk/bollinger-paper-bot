from services.strategy import MeanReversionStrategy
from tests.helpers import make_candles


def test_buy_below_lower_band_and_sell_above_upper_band():
    closes = [100, 101] * 10 + [90, 100, 101, 100] + [115]
    signals = MeanReversionStrategy(lookback=20, threshold=1.5).generate_signals(make_candles(closes))

    assert signals.iloc[20] == 1    # sharp drop -> BUY
    assert signals.iloc[-1] == -1   # sharp rise -> SELL
    assert set(signals.iloc[21:24]) == {0}


def test_no_signal_before_the_bands_exist():
    closes = [100] * 5 + [50] + [100] * 20
    signals = MeanReversionStrategy(lookback=20).generate_signals(make_candles(closes))
    assert (signals.iloc[:19] == 0).all()


def test_does_not_mutate_the_input():
    data = make_candles([100, 101] * 15)
    columns = list(data.columns)
    MeanReversionStrategy().generate_signals(data)
    assert list(data.columns) == columns
