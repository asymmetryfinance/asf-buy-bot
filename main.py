import asyncio
import json
import os

from dotenv import load_dotenv
from rich import print
from rich.traceback import install
from web3 import AsyncHTTPProvider, AsyncWeb3, Web3, WebSocketProvider
from websockets.asyncio.client import connect

from configs.TwoCryptoNG import filters as two_crypto_ng_filters
from configs.UniswapV2 import filters as uni_v2_filters
# from configs.UniswapV3 import filters as uni_v3_filters
from configs.UniswapV4 import filters as uni_v4_filters
from utils.cex_trades_handler import BuyTrade, handle_cex_trades
from utils.discord_bot import send_message_to_channel
from utils.eth_oracle import get_eth_price
from utils.onchain_event_handler import SwapResult, handle_onchain_event

load_dotenv()
install()

MAINNET_WS_RPC_URL = os.getenv("MAINNET_WS_RPC_URL")
MAINNET_HTTP_RPC_URL = os.getenv("MAINNET_HTTP_RPC_URL")

# Flag to enable/disable CEX subscription
ENABLE_CEX_SUBSCRIPTION = False

# Minimum dollar value threshold for buy notifications
MIN_BUY_THRESHOLD_USD = 100


async def onchain_subs():
    async_w3 = AsyncWeb3(WebSocketProvider(MAINNET_WS_RPC_URL))

    async for w3 in async_w3:
        print(f"w3 is connected: {await w3.is_connected()}")
        print("[green]Monitoring onchain events...")
        subs_tasks = []
        filters = (
            two_crypto_ng_filters + uni_v2_filters + uni_v4_filters
        )
        # Subscribe to log filters as defined in configs files
        for f in filters:
            task = asyncio.create_task(w3.eth.subscribe("logs", f))
            subs_tasks.append(task)

        await asyncio.gather(*subs_tasks)

        async for event in w3.socket.process_subscriptions():
            swap_result: SwapResult | None = handle_onchain_event(event)
            if not swap_result:
                continue

            if swap_result.is_asf_buy:
                eth_price = None
                if swap_result.paired_token == "ETH":
                    eth_price = await get_eth_price(w3)
                
                # Calculate USD value of the transaction
                usd_value = 0
                if swap_result.paired_token == "ETH" and eth_price:
                    usd_value = swap_result.tokens_sold * eth_price
                elif swap_result.paired_token in ["USDT", "USDC", "DAI"]:
                    usd_value = swap_result.tokens_sold
                
                # Only send notification if the buy is above the threshold
                if usd_value >= MIN_BUY_THRESHOLD_USD:
                    await send_message_to_channel(
                        asf_amount=swap_result.tokens_bought,
                        sold_amount=swap_result.tokens_sold,
                        price=swap_result.price,
                        eth_price=eth_price,
                        paired_token=swap_result.paired_token,
                        txn_hash=Web3.to_hex(swap_result.txn_hash),
                    )


async def cex_subs():
    w3 = AsyncWeb3(AsyncHTTPProvider(MAINNET_HTTP_RPC_URL))
    async with connect("wss://bilaxy.com/stream?symbol=4794") as ws:
        while True:
            message = await ws.recv()
            try:
                message = json.loads(message)
                buy_trades: list[BuyTrade] | None = handle_cex_trades(message)
                if buy_trades:
                    eth_price = await get_eth_price(w3)
                    for trade in buy_trades:
                        # Calculate USD value of the trade
                        usd_value = 0
                        if trade.paired_token == "ETH" and eth_price:
                            usd_value = trade.sold_amount * eth_price
                        elif trade.paired_token in ["USDT", "USDC", "DAI"]:
                            usd_value = trade.sold_amount
                        
                        # Only send notification if the buy is above the threshold
                        if usd_value >= MIN_BUY_THRESHOLD_USD:
                            await send_message_to_channel(
                                asf_amount=trade.asf_amount,
                                sold_amount=trade.sold_amount,
                                price=trade.price,
                                eth_price=eth_price,
                                paired_token=trade.paired_token,
                                txn_hash=None,
                            )

            except Exception as e:
                print(f"Error in handle_cex_trades: {e}")
                continue


async def main():
    if ENABLE_CEX_SUBSCRIPTION:
        # Run both onchain and CEX subscriptions
        await asyncio.gather(onchain_subs(), cex_subs())
    else:
        # Run only onchain subscriptions
        await onchain_subs()


if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
        except Exception as e:
            print(f"Error: {e}. Continuing...")
            continue
