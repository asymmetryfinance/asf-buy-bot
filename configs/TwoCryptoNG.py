topic0 = "0x143f1f8e861fbdeddd5b46e844b7d3ac7b86a122f36e8c463859ee6811b1f29c"

# Curve pools that include ASF token
pools = {
    "0x3D0d331390D14DF42c16FC20700F7e6Ad4849c50": {
        "ASF_token_index": 1,
        "tokens_decimals": [18, 18],
        "paired_token": "ETH",
    }
}

filters = [
    {"address": [pool_address], "topics": [topic0]} for pool_address in pools.keys()
]
