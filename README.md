# Crypto Intelligence Terminal V2 — Release 3.1.0

Release 3.1 adds a dedicated **Volume Intelligence** layer.

## New capabilities

- Records one volume snapshot every 15 minutes.
- Builds a local rolling volume baseline.
- Calculates Relative Volume (RVOL).
- Tracks one-hour, four-hour and twelve-hour volume direction.
- Compares price direction with volume participation.
- Labels activity as Extreme, High, Elevated, Normal or Quiet.
- Identifies Strong participation, Heavy selling and unconfirmed price moves.
- Adds a combined Market Strength score.
- Adds volume activity and strength to What's Moving?

## Important behaviour

The current 24-hour volume is available immediately. Relative volume and
shorter-period volume trends improve as the terminal collects snapshots.
The median of prior snapshots is used as the baseline to reduce distortion from
single spikes.

## Investment limitation

Volume is supporting evidence, not a guarantee. Exchange activity, token
migrations, wash trading and one-off events can distort reported turnover.

## Deployment

Extract the ZIP and upload everything inside the extracted folder into the root
of the GitHub repository, replacing existing files.
