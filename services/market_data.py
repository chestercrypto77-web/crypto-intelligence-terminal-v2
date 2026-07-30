from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
import requests
import streamlit as st
from config import COINGECKO_MARKETS_URL, CURRENCY, PORTFOLIO

FALLBACK={
"bitcoin":(178500.0,1.4,3.8,58200000000),"solana":(285.0,3.2,8.1,8200000000),
"avalanche-2":(42.0,-0.8,2.4,590000000),"polygon-ecosystem-token":(0.42,1.1,-1.5,210000000),
"polkadot":(5.40,-0.4,1.8,185000000),"zilliqa":(0.016,-1.9,-4.3,11000000),
"coti":(0.091,8.4,16.0,38400000),"near":(4.15,2.6,6.2,240000000),
"sui":(5.05,5.3,12.4,1680000000),"superfarm":(0.84,1.8,4.6,24000000),
"sonic-3":(0.54,3.1,7.0,92000000),"aioz-network":(0.69,4.5,10.2,31000000),
"filecoin":(3.75,-0.7,0.8,145000000),"sei-network":(0.36,2.0,5.1,118000000)}

def _fallback_rows():
    out=[]
    for h in PORTFOLIO:
        p,c24,c7,v=FALLBACK.get(h["coin_id"],(1.0,0.0,0.0,1000000))
        out.append({"id":h["coin_id"],"symbol":h["symbol"].lower(),"name":h["name"],"current_price":p,"price_change_percentage_24h":c24,"price_change_percentage_7d_in_currency":c7,"total_volume":v,"market_cap":p*10000000})
    return out

@st.cache_data(ttl=300,show_spinner=False)
def get_market_rows():
    params={"vs_currency":CURRENCY,"ids":",".join(x["coin_id"] for x in PORTFOLIO),"price_change_percentage":"1h,24h,7d","sparkline":"false"}
    try:
        r=requests.get(COINGECKO_MARKETS_URL,params=params,timeout=15); r.raise_for_status(); rows=r.json()
        if not isinstance(rows,list) or len(rows)<7: raise RuntimeError("Incomplete response")
        return rows,"Live CoinGecko",datetime.now(timezone.utc).isoformat()
    except Exception:
        return _fallback_rows(),"Snapshot fallback",datetime.now(timezone.utc).isoformat()
