APP_NAME = "Crypto Intelligence Terminal V2"
APP_VERSION = "0.5.0"

COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
FEAR_GREED_URL = "https://api.alternative.me/fng/"
DEFILLAMA_BASE_URL = "https://api.llama.fi"

MARKET_CACHE_SECONDS = 300
REQUEST_TIMEOUT_SECONDS = 20
DISPLAY_CURRENCY = "usd"

TRACKED_COINS = (
    "bitcoin",
    "ethereum",
    "chainlink",
    "hyperliquid",
    "ondo-finance",
    "coti",
    "zilliqa",
)

SCANNER_MARKET_COUNT = 100
SCANNER_MIN_MARKET_CAP = 50_000_000
SCANNER_MIN_VOLUME = 2_000_000
SCANNER_MAX_ABS_24H_CHANGE = 80.0
HOT_CATEGORY_COUNT = 10
DEFI_PROTOCOL_COUNT = 150
