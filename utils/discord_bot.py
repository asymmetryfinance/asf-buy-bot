import os

import hikari
from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")


async def send_message_to_channel(
    asf_amount: float,
    sold_amount: float,
    price: float,
    eth_price: float | None,
    paired_token: str,
    txn_hash: str | None = None,
    chain: str | None = None,
):
    rest = hikari.RESTApp()

    await rest.start()

    message = format_message(
        asf_amount, sold_amount, price, eth_price, paired_token, txn_hash, chain
    )

    # We acquire a client with a given token. This allows one REST app instance
    # with one internal connection pool to be reused.
    async with rest.acquire(DISCORD_BOT_TOKEN, "Bot") as client:
        await client.create_message(
            CHANNEL_ID,
            embed=hikari.Embed(
                description=message,
            ),
        )

    await rest.close()


def format_message(
    asf_amount: float,
    sold_amount: float,
    price: float,
    eth_price: float | None,
    paired_token: str,
    txn_hash: str | None = None,
    chain: str | None = None,
) -> str:
    sold_value_str = (
        f"(${round(sold_amount * eth_price, 2):,})"
        if paired_token == "ETH"
        else f"(${round(sold_amount, 2):,})"
    )
    sold_amount_str = (
        f"{round(sold_amount, 4):,}"
        if paired_token == "ETH"
        else f"{round(sold_amount, 2):,}"
    )
    asf_amount_str = f"{round(asf_amount, 2):,}"
    price_value_str = (
        f"(${round(price * eth_price, 2):,})"
        if paired_token == "ETH"
        else f"(${round(price, 2):,})"
    )
    price_amount_str = (
        f"{round(price, 7):,}" if paired_token == "ETH" else f"{round(price, 2):,}"
    )
    explorer_base_url = ""
    if chain == "mainnet":
        explorer_base_url = "https://etherscan.io"
    elif chain == "base":
        explorer_base_url = "https://basescan.org"
    txn_link_str = (
        f"\n[TX]({explorer_base_url}/tx/{txn_hash})" if txn_hash else "\nBilaxy"
    )
    emoji_str = "🟢" * min(max(int(asf_amount * 0.07), 1), 80)
    message = f"**Asymmetry Finance Token Buy!** \n{emoji_str} \n**Spent:** {sold_amount_str} {paired_token} {sold_value_str} \n**Got:** {asf_amount_str} ASF \n**Price:** {price_amount_str} {paired_token} {price_value_str} {txn_link_str}"
    return message
