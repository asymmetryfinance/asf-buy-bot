from web3 import Web3

from abis.EACAggregatorProxy import EAC_Aggregator_Proxy_abi


# Simple getter function to fetch ETH price from Chainlink oracle
async def get_eth_price(w3):
    eth_price_feed = w3.eth.contract(
        address="0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419",
        abi=EAC_Aggregator_Proxy_abi,
    )
    latest_round_data = await eth_price_feed.functions.latestRoundData().call()
    return latest_round_data[1] / 10**8
