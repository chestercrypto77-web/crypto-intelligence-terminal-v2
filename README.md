# Crypto Intelligence Terminal V2 — Release 0.9.0

Release 0.9 introduces **Market Pulse**, a live decision-support page designed to answer:

> What changed, why does it matter, and what deserves attention now?

## Market Pulse features

- composite Market Pulse score
- health label and improving / cooling direction
- concise daily intelligence brief
- live intelligence feed
- biggest conviction movers
- narrative heatmap
- portfolio status monitor
- focused research list

## Scoring inputs

The Market Pulse score combines:

- global market-cap movement
- Fear & Greed sentiment
- relative category rotation
- portfolio intelligence score

## Historical intelligence

Conviction movers use stored snapshots where available. Projects without a historical baseline are labelled **New baseline** rather than assigned an invented change.

## Data integrity

Capital rotation is a relative activity signal based on category movement and turnover. It is not represented as measured on-chain capital flow.

The terminal continues not to fabricate wallet, developer, fee, stablecoin-flow or unavailable TVL metrics.

## Installation

Extract the ZIP and upload every item inside the extracted release folder to the repository root, replacing existing files.

Entry point: `app.py`
