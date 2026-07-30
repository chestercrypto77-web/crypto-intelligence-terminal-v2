from intelligence.engine import executive_brief
from ui.components import section,metric,money,signed,attention_card,progress
top=st.columns(4)
with top[0]:metric("Portfolio value",money(portfolio["total"]),signed(portfolio["daily_pct"])+" today")
with top[1]:metric("Today's P/L",money(portfolio["daily_change"]),"Portfolio contribution")
with top[2]:metric("Portfolio health",f'{portfolio["health"]:.0f}/100',f'{portfolio["risk"]} risk')
wc=sum(1 for x in portfolio["attention"] if x["action"]!="Hold");workload="LOW" if wc<=1 else "MEDIUM" if wc<=3 else "HIGH"
with top[3]:metric("Today's workload",workload,f"{wc} holdings deserve attention")
left,right=st.columns([1.45,1])
with left:section("Executive brief");st.markdown(f'<div class="summary-box">{executive_brief(portfolio)}</div>',unsafe_allow_html=True)
with right:section("Portfolio health");progress("Overall intelligence",portfolio["health"],"Momentum, participation, conviction and risk")
section("Today's attention");cols=st.columns(4)
for col,item in zip(cols,portfolio["attention"]):
 with col:attention_card(item)
section("What drove the portfolio");leaders=sorted(portfolio["items"],key=lambda x:x["contribution"],reverse=True);cols=st.columns(4)
for col,item in zip(cols,leaders[:4]):
 with col:metric(item["symbol"],money(item["contribution"]),f'{signed(item["change_24h"])} · {item["weight"]:.1f}% weight')
section("Money flow");cols=st.columns(min(4,len(portfolio["themes"])))
for col,t in zip(cols,portfolio["themes"][:4]):
 with col:progress(t["name"],t["strength"],f'{signed(t["change"])} portfolio-weighted')
