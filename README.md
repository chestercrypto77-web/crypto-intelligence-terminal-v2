# Crypto Intelligence Terminal V2 — Release 0.8.0

Release 0.8 introduces the terminal's Intelligence Engine.

## New capabilities

### Evidence Engine

Every project conclusion is supported by visible evidence, including available conviction, price momentum, liquidity and matched TVL changes. The interface also reports an evidence-confidence percentage based on data coverage and agreement.

### Investment Health Score

Projects receive a transparent breakdown across:

- fundamentals
- momentum
- liquidity
- adoption / TVL
- risk quality

The overall score is a weighted synthesis of those components.

### Rule-based Intelligence Summary

Project summaries are generated directly from observed data. They do not use unsupported claims or fabricate missing metrics.

### Capital Rotation

Category movement and turnover are combined into a relative rotation signal. This is clearly labelled as an activity indicator—not verified on-chain capital flow.

### Research Queue

Opportunity Radar presents a focused list of emerging research candidates rather than an endless coin list.

### Opportunity Timeline

Saved historical snapshots are used to chart conviction and opportunity scores. The timeline becomes more useful as snapshots accumulate.

## Data integrity rule

The terminal does not estimate wallet activity, developer activity, fees, stablecoin flows or TVL. TVL appears only when a reliable DeFiLlama match is available.

## Installation

Extract the ZIP and upload every item inside the extracted release folder to the repository root, replacing existing files.

Entry point: `app.py`
