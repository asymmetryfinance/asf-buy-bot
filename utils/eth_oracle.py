import os

from dotenv import load_dotenv
from web3 import AsyncHTTPProvider, AsyncWeb3

from abis.EACAggregatorProxy import EAC_Aggregator_Proxy_abi

load_dotenv()

MAINNET_HTTP_RPC_URL = os.getenv("MAINNET_HTTP_RPC_URL")


# Simple getter function to fetch ETH price from Chainlink oracle
async def get_eth_price():
    w3 = AsyncWeb3(AsyncHTTPProvider(MAINNET_HTTP_RPC_URL))
    eth_price_feed = w3.eth.contract(
        address="0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419",
        abi=EAC_Aggregator_Proxy_abi,
    )
    latest_round_data = await eth_price_feed.functions.latestRoundData().call()
    return latest_round_data[1] / 10**8
