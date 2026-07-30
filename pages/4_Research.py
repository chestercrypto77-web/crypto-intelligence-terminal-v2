from _shared import setup
from ui.components import page_header,section,signed
import pandas as pd
portfolio,source,updated=setup("Research · Intelligence Desk");page_header("Research","The evidence beneath the daily briefing.")
section("Intelligence matrix");rows=[]
for i in sorted(portfolio["items"],key=lambda x:x["score"],reverse=True):rows.append({"Asset":i["symbol"],"Score":round(i["score"]),"Momentum":i["momentum"],"Momentum score":round(i["momentum_score"]),"RVOL proxy":round(i["rvol"],2),"Volume":i["volume_label"],"24h":signed(i["change_24h"]),"7d":signed(i["change_7d"]),"Risk":i["risk"],"Narrative":i["narrative"]})
st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
section("Methodology");st.markdown('<div class="summary-box"><b>Overall Intelligence</b> combines momentum, participation, personal conviction and risk. Until sufficient rolling snapshots exist, Relative Volume is shown as a participation proxy derived from turnover and price activity. It is not an exact exchange-wide RVOL calculation. Live market data comes from CoinGecko, with a visible snapshot fallback.</div>',unsafe_allow_html=True)
