# Crypto Intelligence Terminal V4.0

A personal crypto intelligence desk designed to brief the owner on their portfolio in under five minutes.

## Pages
- Today — executive brief, workload, attention, contribution and money flow
- Portfolio — intelligence cards for every holding
- Markets — capital rotation and portfolio exposure
- Watch — deliberately limited priority signals
- Research — transparent evidence and methodology

## Run
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Edit token balances in `config.py`. The included balances are provisional values transcribed from the previously supplied portfolio screenshot.

This application provides research and decision-support information only. It is not financial advice.
