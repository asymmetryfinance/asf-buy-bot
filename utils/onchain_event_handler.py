from dataclasses import dataclass

from eth_abi import decode
from rich import print
from rich.traceback import install
from web3 import Web3

from configs import TwoCryptoNG, UniswapV2, UniswapV3, UniswapV4

install()


@dataclass
class SwapResult:
    txn_hash: str
    is_asf_buy: bool
    tokens_bought: float
    tokens_sold: float
    price: float
    paired_token: str


def handle_onchain_event(event):
    topic0 = Web3.to_hex(event["result"]["topics"][0])

    if topic0 == TwoCryptoNG.topic0:
        return handle_curve_two_crypto_ng_swap(event)
    elif topic0 == UniswapV2.topic0:
        return handle_uni_cp_swap(event)
    elif topic0 == UniswapV3.topic0:
        return handle_uni_v3_swap(event)
    elif topic0 == UniswapV4.topic0:
        return handle_uni_v4_swap(event)
    else:
        return None


def handle_curve_two_crypto_ng_swap(event):
    """
    handles Curve TwoCryptoNG TokenExchange events
    """
    sold_id, tokens_sold, bought_id, tokens_bought, fee, packed_price_scale = decode(
        ["uint256", "uint256", "uint256", "uint256", "uint256", "uint256"],
        event["result"]["data"],
    )
    pool_address = Web3.to_checksum_address(event["result"]["address"])
    pool_config = TwoCryptoNG.pools[pool_address]
    ASF_token_index = pool_config["ASF_token_index"]
    tokens_decimals = pool_config["tokens_decimals"]
    is_asf_buy = bought_id == ASF_token_index

    price: float = packed_price_scale / 10**18
    price = 1 / price if ASF_token_index == 0 else price

    return SwapResult(
        txn_hash=event["result"]["transactionHash"],
        is_asf_buy=is_asf_buy,
        tokens_bought=tokens_bought / 10 ** tokens_decimals[bought_id],
        tokens_sold=tokens_sold / 10 ** tokens_decimals[sold_id],
        price=price,
        paired_token=pool_config["paired_token"],
    )


def handle_uni_cp_swap(event):
    """
    handles Uniswap Constant Product Pools Swap events
    """
    amount0In, amount1In, amount0Out, amount1Out = decode(
        ["uint256", "uint256", "uint256", "uint256"],
        event["result"]["data"],
    )
    pool_address = Web3.to_checksum_address(event["result"]["address"])
    pool_config = UniswapV2.pools[pool_address]
    ASF_token_index = pool_config["ASF_token_index"]
    tokens_decimals = pool_config["tokens_decimals"]

    is_asf_buy = amount0Out > 0 if ASF_token_index == 0 else amount1Out > 0
    tokens_bought = max(amount0Out, amount1Out)
    tokens_bought = (
        tokens_bought / 10 ** tokens_decimals[0]
        if amount0Out > 0
        else tokens_bought / 10 ** tokens_decimals[1]
    )
    tokens_sold = max(amount0In, amount1In)
    tokens_sold = (
        tokens_sold / 10 ** tokens_decimals[0]
        if amount0In > 0
        else tokens_sold / 10 ** tokens_decimals[1]
    )
    price = (max(amount1In, amount1Out) / 10 ** tokens_decimals[1]) / (
        max(amount0In, amount0Out) / 10 ** tokens_decimals[0]
    )
    price = 1 / price if ASF_token_index == 1 else price

    return SwapResult(
        txn_hash=event["result"]["transactionHash"],
        is_asf_buy=is_asf_buy,
        tokens_bought=tokens_bought,
        tokens_sold=tokens_sold,
        price=price,
        paired_token=pool_config["paired_token"],
    )


def handle_uni_v3_swap(event):
    """
    preprocesses Uniswap V3 Swap events
    """
    amount0, amount1, sqrtPriceX96, liquidity, tick = decode(
        ["int256", "int256", "uint160", "uint128", "int24"],
        event["result"]["data"],
    )
    pool_address = Web3.to_checksum_address(event["result"]["address"])
    pool_config = UniswapV3.pools[pool_address]

    return handle_uni_cl_swap(event, [amount0, amount1], sqrtPriceX96, pool_config)


def handle_uni_v4_swap(event):
    """
    preprocesses Uniswap V4 Swap events
    @dev: see negation logic below
    """
    pool_id = Web3.to_hex(event["result"]["topics"][1])
    if pool_id not in UniswapV4.pools.keys():
        return None

    amount0, amount1, sqrtPriceX96, liquidity, tick, fee = decode(
        ["int128", "int128", "uint160", "uint128", "int24", "uint24"],
        event["result"]["data"],
    )
    pool_config = UniswapV4.pools[pool_id]

    # amount0 and amount1 deltas emitted from Swap logs mean different things in v3 and v4
    # https://docs.uniswap.org/contracts/v4/guides/unlock-callback
    # here we negate the v4 values to conform with v3,
    # so the amounts will always correspond to the absolute change of the tokens amounts in the pool after swap
    return handle_uni_cl_swap(event, [-amount0, -amount1], sqrtPriceX96, pool_config)


def handle_uni_cl_swap(
    event, amounts_deltas: list[int], sqrtPriceX96: int, pool_config: dict
):
    """
    handles Uniswap V3 and V4 Swap events
    """
    ASF_token_index = pool_config["ASF_token_index"]
    tokens_decimals = pool_config["tokens_decimals"]

    is_asf_buy = amounts_deltas[ASF_token_index] < 0
    tokens_bought = min(amounts_deltas)
    tokens_bought = (
        abs(tokens_bought) / 10 ** tokens_decimals[amounts_deltas.index(tokens_bought)]
    )
    tokens_sold = max(amounts_deltas)
    tokens_sold = (
        abs(tokens_sold) / 10 ** tokens_decimals[amounts_deltas.index(tokens_sold)]
    )

    price: float = ((sqrtPriceX96 / 2**96) ** 2) / (
        10 ** (tokens_decimals[1] - tokens_decimals[0])
    )
    price = 1 / price if ASF_token_index == 1 else price

    return SwapResult(
        txn_hash=event["result"]["transactionHash"],
        is_asf_buy=is_asf_buy,
        tokens_bought=tokens_bought,
        tokens_sold=tokens_sold,
        price=price,
        paired_token=pool_config["paired_token"],
    )
