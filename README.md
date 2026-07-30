# Crypto Intelligence Terminal V2 — Release 1.0.1

Release 1.0.1 is a complete full-project release.

## Fixes

- Fixed the My Market startup ImportError caused when an older `config.py`
  remained in GitHub during upload.
- My Market now uses safe configuration defaults and will load even if
  `PERSONAL_ATTENTION_LIMIT` is missing.
- Added retries for temporary CoinGecko and other live-data interruptions.
- Added clearer connection details when a live-data service fails.
- Includes every feature and fix from Release 1.0.0 and Market Pulse 0.9.1.

## Deployment

Extract the ZIP and upload **everything inside the extracted release folder**
into the root of the GitHub repository, replacing existing files.
