# Crypto Intelligence Terminal V2 — Release 3.0.0

Release 3.0 reorganises the application into a focused **Crypto Intelligence Desk**.

## Main navigation

- **Today** — the five-minute morning briefing
- **My Portfolio** — live values, weights and pricing health
- **What's Moving?** — clear momentum cards with 1h, 4h and 24h arrows
- **Market Themes** — where category momentum is flowing
- **Needs Attention** — only important portfolio and market changes
- **Research** — scanners and specialist analysis
- **Technical Tools** — retained legacy pages

## COTI and smaller holdings fix

The market scanner previously requested only the top 150 assets. Smaller personal
holdings could therefore disappear from all market pages and silently fall back
to their old screenshot value.

Release 3.0 now makes a second request for every explicitly tracked CoinGecko ID
and merges those assets into the scanner universe. This ensures COTI, Zilliqa,
Polkadot, Sui and the other tracked projects remain available even when they are
outside the broad top-N request.

## Design philosophy

Every front-line page now answers one question. Legacy technical pages remain
available, but they no longer dominate the daily experience.

## Deployment

Extract the ZIP and upload everything inside the extracted folder into the root
of the GitHub repository, replacing existing files.
