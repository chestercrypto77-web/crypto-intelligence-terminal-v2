from _shared import setup
from ui.components import page_header,section,progress,metric,money,signed
portfolio,source,updated=setup("Markets · Intelligence Desk");page_header("Market Themes","Where is capital moving, and how is your portfolio exposed?")
section("Capital rotation")
for start in range(0,min(8,len(portfolio["themes"])),4):
 cols=st.columns(4)
 for col,t in zip(cols,portfolio["themes"][start:start+4]):
  with col:progress(t["name"],t["strength"],f'{signed(t["change"])} today')
section("Portfolio exposure");total=portfolio["total"];cols=st.columns(4)
for col,t in zip(cols,sorted(portfolio["themes"],key=lambda x:x["value"],reverse=True)[:4]):
 with col:metric(t["name"],f'{t["value"]/total*100:.1f}%',money(t["value"]))
section("What this means");leader=portfolio["themes"][0];exposed=[x["symbol"] for x in portfolio["items"] if leader["name"] in x["narrative"]];st.markdown(f'<div class="summary-box"><b>{leader["name"]}</b> is currently the strongest portfolio theme. Your directly aligned holdings are {", ".join(exposed) if exposed else "limited"}. Theme scores are decision-support signals, not forecasts.</div>',unsafe_allow_html=True)
