# Crypto Intelligence Terminal V2 — Release 0.6.0

Release 0.6 introduces historical intelligence and a streamlined navigation structure.

## New features

- Mission Control home page
- Historical Intelligence page
- Manual intelligence snapshot capture
- SQLite storage for market and asset scores
- Opportunity and conviction trend charts
- Market, portfolio and sentiment history
- Watchlist page
- Downloadable and restorable history database
- Navigation grouped into Intelligence, Research, Portfolio and System

## Important storage note

Streamlit Community Cloud uses temporary local application storage. History can be lost when the app restarts or is redeployed.

Use **History → Download history** before uploading a new release. After deployment, use **Restore history** to upload the saved database.

## Upload

Extract the ZIP and upload every item inside the extracted folder to the repository root, replacing existing files.

No hidden `.streamlit` folder is required.

## Entry point

`app.py`
