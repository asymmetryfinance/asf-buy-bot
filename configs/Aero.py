topic0 = "0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b"

pools = {
    "0xaAD3B9047DCa4D5565471a3CCE2767c56535ec65": {
        "ASF_token_index": 1,
        "tokens_decimals": [18, 18],
        "paired_token": "ETH",
    },
}

filters = [
    {"address": [pool_address], "topics": [topic0]} for pool_address in pools.keys()
]
