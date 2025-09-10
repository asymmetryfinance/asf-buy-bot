import asyncio
import json
import os

from dotenv import load_dotenv
from rich import print
from rich.traceback import install
from web3 import AsyncHTTPProvider, AsyncWeb3, Web3, WebSocketProvider
from websockets.asyncio.client import connect

from configs.Aero import filters as aero_filters
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
BASE_WS_RPC_URL = os.getenv("BASE_WS_RPC_URL")

# Flag to enable/disable CEX subscription
ENABLE_CEX_SUBSCRIPTION = True

# Minimum dollar value threshold for buy notifications
MIN_BUY_THRESHOLD_USD = 100
CEX_MIN_BUY_THRESHOLD_USD = 500


async def onchain_subs():
    while True:
        try:
            async_w3 = AsyncWeb3(WebSocketProvider(MAINNET_WS_RPC_URL))
            
            async with async_w3 as w3:
                print(f"w3 is connected to Mainnet: {await w3.is_connected()}")
                print("[green]Monitoring onchain events...")
                
                filters = two_crypto_ng_filters + uni_v2_filters + uni_v4_filters
                # Subscribe to log filters as defined in configs files
                for f in filters:
                    await w3.eth.subscribe("logs", f)

                async for event in w3.socket.process_subscriptions():
                    try:
                        swap_result: SwapResult | None = handle_onchain_event(event)
                        if not swap_result:
                            continue

                        if swap_result.is_asf_buy:
                            eth_price = None
                            if swap_result.paired_token == "ETH":
                                eth_price = await get_eth_price()

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
                                    chain="mainnet",
                                )
                    except Exception as e:
                        print(f"Error processing mainnet event: {e}")
                        continue
        except Exception as e:
            print(f"Mainnet WebSocket connection error: {e}. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)


async def base_subs():
    while True:
        try:
            async_w3 = AsyncWeb3(WebSocketProvider(BASE_WS_RPC_URL))
            
            async with async_w3 as w3:
                print(f"w3 is connected to Base: {await w3.is_connected()}")
                print("[green]Monitoring onchain events...")
                
                filters = aero_filters
                # Subscribe to log filters as defined in configs files
                for f in filters:
                    await w3.eth.subscribe("logs", f)

                async for event in w3.socket.process_subscriptions():
                    try:
                        swap_result: SwapResult | None = handle_onchain_event(event)
                        if not swap_result:
                            continue

                        if swap_result.is_asf_buy:
                            # Don't show low amount trades (L2 problem)
                            if swap_result.tokens_bought < 0.1:
                                continue

                            eth_price = None
                            if swap_result.paired_token == "ETH":
                                eth_price = await get_eth_price()

                            await send_message_to_channel(
                                asf_amount=swap_result.tokens_bought,
                                sold_amount=swap_result.tokens_sold,
                                price=swap_result.price,
                                eth_price=eth_price,
                                paired_token=swap_result.paired_token,
                                txn_hash=Web3.to_hex(swap_result.txn_hash),
                                chain="base",
                            )
                    except Exception as e:
                        print(f"Error processing base event: {e}")
                        continue
        except Exception as e:
            print(f"Base WebSocket connection error: {e}. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)


async def cex_subs():
    while True:
        try:
            async with connect("wss://bilaxy.com/stream?symbol=4794") as ws:
                print("Subscribed to CEX events")
                while True:
                    message = await ws.recv()
                    try:
                        message = json.loads(message)
                        buy_trades: list[BuyTrade] | None = handle_cex_trades(message)
                        if buy_trades:
                            eth_price = await get_eth_price()
                            for trade in buy_trades:
                                # filter out low value trades
                                if (trade.sold_amount * eth_price) < CEX_MIN_BUY_THRESHOLD_USD:
                                    continue

                                await send_message_to_channel(
                                    asf_amount=trade.asf_amount,
                                    sold_amount=trade.sold_amount,
                                    price=trade.price,
                                    eth_price=eth_price,
                                    paired_token=trade.paired_token,
                                    txn_hash=None,
                                )

                    except Exception as e:
                        if "close frame" in str(e):
                            break  # Break inner loop to reconnect
                        print(f"Error in handle_cex_trades: {e}")
                        continue
        except Exception as e:
            print(f"CEX WebSocket connection error: {e}. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)


async def main():
    subs = [onchain_subs(), base_subs()]
    if ENABLE_CEX_SUBSCRIPTION:
        subs.append(cex_subs())
    await asyncio.gather(*subs)


if __name__ == "__main__":
    asyncio.run(main())
