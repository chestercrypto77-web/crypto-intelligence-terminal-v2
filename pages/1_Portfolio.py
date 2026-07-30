from _shared import setup
from ui.components import page_header,section,metric,money,signed,asset_card
portfolio,source,updated=setup("Portfolio · Intelligence Desk");page_header("My Portfolio","How am I doing, and which holdings matter most today?")
s=st.columns(4)
with s[0]:metric("Total value",money(portfolio["total"]),signed(portfolio["daily_pct"])+" today")
with s[1]:metric("Daily contribution",money(portfolio["daily_change"]),"Across all holdings")
with s[2]:metric("Health",f'{portfolio["health"]:.0f}/100',f'{portfolio["risk"]} risk')
with s[3]:metric("Largest position",portfolio["items"][0]["symbol"],f'{portfolio["items"][0]["weight"]:.1f}% of portfolio')
section("Holding briefs")
for start in range(0,len(portfolio["items"]),3):
 cols=st.columns(3)
 for col,item in zip(cols,portfolio["items"][start:start+3]):
  with col:asset_card(item)
 st.write("")
