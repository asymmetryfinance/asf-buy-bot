import time
from dataclasses import dataclass

from rich import print
from rich.traceback import install

install()


@dataclass
class BuyTrade:
    asf_amount: float
    sold_amount: float
    price: float
    paired_token: str


# Logic only for Bilaxy for now
def handle_cex_trades(message: dict):
    if message.get("method") != "trade":
        return None
    message_ts = int(time.time())
    # Bilaxy API is not well documented, may stream trades up to 2 hours before, so we need to trim the message.
    # Adjust lookback_window accordingly
    lookback_window: int = 20  # seconds
    trades: list[dict] = message.get("result", [])

    stale_trade = next(
        (
            trade
            for trade in trades
            if (trade["ts"] / 1000) < message_ts - lookback_window
        ),
        None,
    )
    if stale_trade:
        trades = trades[: trades.index(stale_trade)]  # discard stale trades
    trades = [trade for trade in trades if trade["buy"]]  # filter for buys

    if len(trades) == 0:
        return None

    buy_trades = []
    for trade in trades:
        asf_amount = trade["q"]
        price = trade["p"]
        sold_amount = asf_amount * price
        buy_trades.append(BuyTrade(asf_amount, sold_amount, price, "ETH"))

    return buy_trades
