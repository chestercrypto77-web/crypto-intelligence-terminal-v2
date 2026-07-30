# Crypto Intelligence Terminal V2 — Release 2.1.1

Release 2.1.1 fixes the two deployment issues reported after Release 2.1.0.

## Fixes

### Permanent dark mode

The app now forces dark mode through both:

- `.streamlit/config.toml`
- an in-app CSS fallback loaded from `components/theme.py`

This means the terminal remains dark even if a GitHub upload method omits the
hidden `.streamlit` folder.

### Correct AUD portfolio values

CoinGecko prices are now requested directly in Australian dollars. Release
2.1.0 requested USD prices and displayed them as AUD, which made the estimated
portfolio figures incorrect.

The Morning Brief now reports how many holdings use:

- live AUD market prices
- recent screenshot values as a fallback

## Portfolio included

BTC, SOL, AVAX, POL, DOT, ZIL, COTI, NEAR, SUI, SUPER, Sonic, AIOZ, FIL and SEI.

## Deployment

This is a complete project release. Extract the ZIP and upload everything inside
the extracted folder into the root of the GitHub repository, replacing the
existing files.

When using GitHub's browser uploader, verify that `components/theme.py`,
`config.py`, `pages/morning_brief.py` and `services/portfolio_snapshot.py`
show the new commit. The CSS fallback means `.streamlit/config.toml` is no
longer essential for dark mode.
