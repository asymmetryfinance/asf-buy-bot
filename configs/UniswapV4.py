topic0 = "0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"

# key is pool id as Uniswap v4 pools are stored in PoolManager state
pools = {
    "0xf43260c4e3df4bc3c35e1a3568127cd2b79ee33c0d515a7b14454af044b04c77": {
        "ASF_token_index": 0,
        "tokens_decimals": [18, 6],
        "paired_token": "USDT",
    },
    "0x675866a0582c22877ed2ab566157d7bfc850bbf936e9fe14d82a68bbd805525d": {
        "ASF_token_index": 0,
        "tokens_decimals": [18, 6],
        "paired_token": "USDC",
    },
}

filters = [
    {"address": ["0x000000000004444c5dc75cB358380D2e3dE08A90"], "topics": [topic0]}
]
