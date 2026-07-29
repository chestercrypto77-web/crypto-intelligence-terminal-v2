APP_NAME = "Crypto Intelligence Terminal V2"
APP_VERSION = "0.8.0"

COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
FEAR_GREED_URL = "https://api.alternative.me/fng/"
DEFILLAMA_BASE_URL = "https://api.llama.fi"

MARKET_CACHE_SECONDS = 300
REQUEST_TIMEOUT_SECONDS = 20
DISPLAY_CURRENCY = "usd"

TRACKED_COINS = (
    "bitcoin",
    "ethereum",
    "solana",
    "ripple",
    "binancecoin",
    "chainlink",
    "hyperliquid",
    "ondo-finance",
    "aave",
    "uniswap",
    "avalanche-2",
    "sui",
)

CORE_ASSET_SYMBOLS = (
    "BTC",
    "ETH",
    "SOL",
    "XRP",
    "BNB",
    "LINK",
    "HYPE",
    "ONDO",
    "AAVE",
    "UNI",
    "AVAX",
    "SUI",
)

CORE_MAX_MARKET_RANK = 30
EMERGING_MIN_MARKET_RANK = 31
EMERGING_MAX_MARKET_RANK = 150
EMERGING_MIN_MARKET_CAP = 75_000_000
EMERGING_MAX_MARKET_CAP = 5_000_000_000
EMERGING_MIN_VOLUME = 3_000_000

SCANNER_MARKET_COUNT = 150
SCANNER_MIN_MARKET_CAP = 50_000_000
SCANNER_MIN_VOLUME = 2_000_000
SCANNER_MAX_ABS_24H_CHANGE = 80.0
HOT_CATEGORY_COUNT = 10
DEFI_PROTOCOL_COUNT = 150

HISTORY_DATABASE_PATH = "data/intelligence_history.db"
HISTORY_DEFAULT_DAYS = 30
WATCHLIST_DEFAULT_IDS = (
    "ethereum",
    "chainlink",
    "ondo-finance",
    "hyperliquid",
    "coti",
    "zilliqa",
)

INTELLIGENCE_EVIDENCE_LIMIT = 6
INTELLIGENCE_RESEARCH_QUEUE_SIZE = 5
INTELLIGENCE_TIMELINE_DAYS = 30
