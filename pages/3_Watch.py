from _shared import setup
from ui.components import page_header,section,attention_card
portfolio,source,updated=setup("Watch · Intelligence Desk");page_header("Needs Attention","Only the holdings with the most meaningful changes.")
section("Priority briefs")
for start in range(0,len(portfolio["attention"]),2):
 cols=st.columns(2)
 for col,item in zip(cols,portfolio["attention"][start:start+2]):
  with col:attention_card(item)
section("Interpretation");st.markdown('<div class="summary-box">A watch item is not automatically a buy or sell signal. It means price, participation, risk or momentum changed enough to deserve a closer look. The terminal deliberately limits this page so routine market noise does not compete for attention.</div>',unsafe_allow_html=True)
