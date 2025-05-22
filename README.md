# ASF Buy Bot tracking Uniswap v2/3/4, Curve TwoCryptoNG and Bilaxy buys

## Requirements

This project is managed using `uv`

```bash
pip install uv
```

or

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

You will also need:

- A Discord bot token
- A Discord channel ID for the bot to send messages to
- HTTP and Websocket RPC URLs for Ethereum Mainnet

## Setup

```bash
git clone https://github.com/pastelfork/asf-buy-bot
```

```bash
cd asf-buy-bot
```

```bash
cp .env.example .env
```

Paste your enviroment variables in the .env file (see requirements above).

```bash
uv run main.py
```

The bot should now be running and monitoring blockchain logs in realtime.
