PROFILE_STATUS = "Indicative — balances to be confirmed"
CORE_CONVICTION = (
    {"id":"coti","name":"COTI","symbol":"COTI","narrative":"Privacy infrastructure"},
    {"id":"polkadot","name":"Polkadot","symbol":"DOT","narrative":"Interoperability"},
    {"id":"zilliqa","name":"Zilliqa","symbol":"ZIL","narrative":"Layer 1"},
    {"id":"sonic-3","name":"Sonic","symbol":"S","narrative":"Layer 1 and DeFi"},
)
ACTIVE_POSITIONS = (
    {"id":"sui","name":"Sui","symbol":"SUI","narrative":"High-performance Layer 1"},
    {"id":"avalanche-2","name":"Avalanche","symbol":"AVAX","narrative":"Layer 1 and subnets"},
    {"id":"near","name":"NEAR Protocol","symbol":"NEAR","narrative":"AI and chain abstraction"},
    {"id":"polygon-ecosystem-token","name":"Polygon","symbol":"POL","narrative":"Ethereum scaling"},
    {"id":"verasity","name":"Verasity","symbol":"VRA","narrative":"Ad-tech and proof of view"},
    {"id":"aioz-network","name":"AIOZ Network","symbol":"AIOZ","narrative":"DePIN and media"},
    {"id":"superfarm","name":"SuperVerse","symbol":"SUPER","narrative":"Gaming"},
    {"id":"sei-network","name":"Sei","symbol":"SEI","narrative":"Trading-focused Layer 1"},
)
SECONDARY_POSITIONS = (
    {"id":"beam-2","name":"Beam","symbol":"BEAM","narrative":"Gaming infrastructure"},
    {"id":"the-sandbox","name":"The Sandbox","symbol":"SAND","narrative":"Gaming and metaverse"},
    {"id":"filecoin","name":"Filecoin","symbol":"FIL","narrative":"Decentralised storage"},
    {"id":"harmony","name":"Harmony","symbol":"ONE","narrative":"Layer 1"},
    {"id":"siacoin","name":"Siacoin","symbol":"SC","narrative":"Decentralised storage"},
    {"id":"immutable-x","name":"Immutable","symbol":"IMX","narrative":"Gaming infrastructure"},
)
MARKET_CONTEXT = (
    {"id":"bitcoin","name":"Bitcoin","symbol":"BTC","narrative":"Store of value"},
    {"id":"ethereum","name":"Ethereum","symbol":"ETH","narrative":"Core infrastructure"},
    {"id":"solana","name":"Solana","symbol":"SOL","narrative":"High-throughput Layer 1"},
    {"id":"ripple","name":"XRP","symbol":"XRP","narrative":"Payments"},
)
PORTFOLIO_PROFILE = (
    *({**a,"priority":1,"group":"Core conviction"} for a in CORE_CONVICTION),
    *({**a,"priority":2,"group":"Active position"} for a in ACTIVE_POSITIONS),
    *({**a,"priority":2,"group":"Secondary position"} for a in SECONDARY_POSITIONS),
    *({**a,"priority":3,"group":"Market context"} for a in MARKET_CONTEXT),
)
