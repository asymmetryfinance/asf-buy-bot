topic0 = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"

# low liquidity pool commented out
pools = {
    "0x93B012EE7363f60a0AC19044EDA8c94E41970c56": {
        "ASF_token_index": 0,
        "tokens_decimals": [18, 18],
        "paired_token": "ETH",
    },
    # "0x65b36082B34dAeEED8A5245DEa4D5De663812Cc4": {
    #     "ASF_token_index": 0,
    #     "tokens_decimals": [18, 6],
    #     "paired_token": "USDC",
    # },
}

filters = [
    {"address": [pool_address], "topics": [topic0]} for pool_address in pools.keys()
]
