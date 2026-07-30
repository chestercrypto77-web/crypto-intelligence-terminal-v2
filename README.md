# Crypto Intelligence Terminal V2 — Release 1.1.0

Release 1.1 introduces the **Event Detection Engine**.

The terminal now records personal-market observations, compares them with previous readings and creates a prioritised event feed for holdings, watchlist projects and Australian mainstream context.

## New features

- Event Detection page
- automatic event scan whenever My Market loads
- 24-hour and one-hour momentum events
- elevated trading-intensity events
- Attention Score threshold and change events
- conviction-change events
- momentum-state transition events
- risk-increase events
- Critical, High, Medium and Informational severity
- stronger severity weighting for Tier 1 holdings such as COTI
- 24-hour personal intelligence brief
- persistent SQLite event history
- event filters by time, project and severity
- duplicate suppression using 15-minute observation buckets

## Included fixes

This is a complete full-project release and includes:

- Market Pulse 0.9.1 fix
- My Market 1.0.1 configuration fallback
- live-data retry handling
- Personal Intelligence Layer

## Deployment

Extract the ZIP. Open the extracted release folder and upload **everything inside it** into the root of the GitHub repository, replacing existing files.
