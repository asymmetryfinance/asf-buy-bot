topic0 = "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"

pools = {
    "0x6Eb95848E9b3e0F98CCf8e1B17C37788E0532846": {
        "ASF_token_index": 0,
        "tokens_decimals": [18, 18],
        "paired_token": "ETH",
    },
}

filters = [
    {"address": [pool_address], "topics": [topic0]} for pool_address in pools.keys()
]
