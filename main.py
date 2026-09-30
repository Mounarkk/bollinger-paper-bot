import argparse
import logging

from config import load_credentials
from services.data_handler import DataHandler
from services.execution_manager import ExecutionManager
from services.live_runner import LiveRunner
from services.portfolio import Portfolio
from services.risk_manager import RiskManager
from services.strategy import MeanReversionStrategy
from services.trading_engine import TradingEngine
from utils.logger import setup_logging

logger = logging.getLogger("main")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Mean reversion paper trading bot for Binance")

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("symbol", help="trading pair, like BTCUSDT")
    common.add_argument("--interval", default="1h", help="candle interval like 15m, 1h, 4h or 1d (default 1h)")
    common.add_argument("--balance", type=float, default=10_000, help="starting balance, in the quote currency")
    common.add_argument("--lookback", type=int, default=20, help="number of candles in the moving average")
    common.add_argument("--threshold", type=float, default=1.5, help="band width in standard deviations")
    common.add_argument("--fraction", type=float, default=0.02, help="part of the cash spent on each buy")
    common.add_argument("--fee", type=float, default=0.001, help="fee rate per trade (default 0.001)")
    common.add_argument("--log-level", default="INFO")

    commands = parser.add_subparsers(dest="command", required=True)

    backtest = commands.add_parser("backtest", parents=[common], help="run the strategy on past data")
    backtest.add_argument("--start", required=True, help='start date, like "2024-01-01" or "6 months ago UTC"')
    backtest.add_argument("--end", default=None, help="end date (default now)")
    backtest.add_argument("--plot", metavar="PNG", help="save a chart of the backtest")

    live = commands.add_parser("live", parents=[common], help="paper trade on live data until Ctrl+C")
    live.add_argument("--poll", type=int, default=60, help="seconds between two checks for a new candle")
    live.add_argument("--state", default="state.json", help="file where the portfolio is saved")
    live.add_argument("--log-file", default="application.log")

    return parser.parse_args(argv)


def build_engine(args) -> TradingEngine:
    # keys are optional, the bot only reads public market data
    credentials = load_credentials()
    if not credentials.is_set:
        logger.info("No API keys found, using public data only")

    strategy = MeanReversionStrategy(lookback=args.lookback, threshold=args.threshold)
    return TradingEngine(
        data_handler=DataHandler(credentials),
        strategy=strategy,
        risk_manager=RiskManager(trade_fraction=args.fraction),
        execution_manager=ExecutionManager(fee_rate=args.fee),
        portfolio=Portfolio(initial_balance=args.balance),
    )


def print_summary(result):
    m = result.metrics
    win_rate = f"{m['win_rate']:.0%}" if m["win_rate"] is not None else "n/a"
    open_position = result.equity.iloc[-1] - result.final_balance
    print(f"""
{result.symbol}, {len(result.data)} candles from {result.data.index[0]} to {result.data.index[-1]}
  Strategy return      {m['total_return']:+.2%}
  Buy and hold return  {m['buy_and_hold_return']:+.2%}
  Max drawdown         {m['max_drawdown']:.2%}
  Trades               {m['trades']} ({m['closed_positions']} closed, win rate {win_rate})
  Fees paid            {m['fees_paid']:.2f}
  Final cash           {result.final_balance:.2f}  (+ open position: {open_position:.2f})
""")


def main(argv=None):
    args = parse_args(argv)
    setup_logging(args.log_level, getattr(args, "log_file", None))
    engine = build_engine(args)

    if args.command == "backtest":
        result = engine.backtest(args.symbol, args.interval, args.start, args.end)
        print_summary(result)
        if args.plot:
            from utils.plotting import plot_backtest
            plot_backtest(result, engine.strategy, args.plot)
            print(f"Chart saved to {args.plot}")
    else:
        LiveRunner(engine, recovery_file=args.state, poll_seconds=args.poll).run(args.symbol, args.interval)


if __name__ == "__main__":
    main()
