# Changelog

## 3.0.0

- Reorganised the platform as a question-based Crypto Intelligence Desk.
- Added Today, My Portfolio, What's Moving?, Market Themes and Needs Attention.
- Moved older technical pages into Technical Tools.
- Fixed smaller tracked assets disappearing from the top-N scanner request.
- Added explicit tracked-asset fetch and CoinGecko-ID merge.
- Added live/snapshot pricing-health indicators.
- Replaced the front-line momentum layout with scan-friendly cards.
- Retained all existing analytical engines and historical data.

## 2.2.0

- Added Momentum Radar.
- Added persistent 15-minute momentum snapshots.
- Added 15m, 1h, 4h, 12h and 24h movement display.
- Added direction arrows and explicit timeframe labels.
- Added acceleration, volume confirmation and confidence scoring.
- Added Building, Accelerating, Strong, Stable, Weakening and Rolling Over states.
- Reduced live market cache from five minutes to three minutes.
- Replaced near-black theme with dark charcoal and slate.
- Retained all Release 2.1.3 and previous fixes.

## 2.1.3

- Fully rewrote Personal Intelligence numeric handling.
- Fixed crashes caused by None, malformed or incomplete live API values.
- Added regression tests for partial scanner rows.
- Increased sidebar contrast and navigation font weight.
- Added a stronger selected-page state.
- Added consistent colour hierarchy for headings and collapsed sections.
- Retained all Release 2.1.2 and earlier fixes.

## 2.1.2

- Fixed Morning Brief crash caused by descriptive conviction labels.
- Added numeric conviction scores to the portfolio profile.
- Added safe label-to-score conversion in Personal Intelligence.
- Fixed unreadable low-opacity sidebar navigation in permanent dark mode.
- Improved dark-mode metric, caption, alert and expander readability.
- Retained all Release 2.1.1 fixes.

## 2.1.1

- Fixed permanent dark mode when hidden `.streamlit` files are not uploaded.
- Added a comprehensive in-app dark CSS fallback.
- Changed CoinGecko display currency from USD to AUD.
- Fixed live portfolio values being labelled as AUD while calculated from USD prices.
- Added live-price and snapshot-fallback counts.
- Preserved all Release 2.1.0 features.

## 2.1.0

- Added permanent dark theme through `.streamlit/config.toml`.
- Rebuilt visual styling around a deep-charcoal, calm morning experience.
- Added recent balances and snapshot values for all supplied holdings.
- Added live AUD value estimation from balances and current market prices.
- Added portfolio weights and weighted 24-hour portfolio movement.
- Added portfolio-aware focus ranking.
- Added a calm “nothing urgent” state.
- Reduced front-page visual noise and retained technical tools under Deep Dive.
- Retained all Release 2.0.0, Event Detection and previous fixes.

## 2.0.0

- Added Morning Brief as the default front-line terminal.
- Reduced the daily experience to a five-minute overview.
- Moved specialist analysis under Deep Dive.
