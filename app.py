import streamlit as st
from components.theme import apply_theme
from config import APP_NAME
st.set_page_config(page_title=APP_NAME,page_icon='☕',layout='wide',initial_sidebar_state='expanded')
apply_theme()
navigation=st.navigation({
 'Morning':[st.Page('pages/morning_brief.py',title='Morning Brief',icon='☕',default=True),st.Page('pages/my_market.py',title='My Market',icon='⭐')],
 'Deep Dive':[st.Page('pages/events.py',title='Event Detection',icon='🔔'),st.Page('pages/mission_control.py',title='Mission Control',icon='🎯'),st.Page('pages/market_pulse.py',title='Market Pulse',icon='⚡'),st.Page('pages/market_briefing.py',title='Market Briefing',icon='📰'),st.Page('pages/whats_hot.py',title="What's Hot",icon='🔥'),st.Page('pages/opportunity_radar.py',title='Opportunity Radar',icon='📡'),st.Page('pages/opportunity_scanner.py',title='Full Scanner',icon='🔎'),st.Page('pages/conviction.py',title='Conviction Engine',icon='⭐'),st.Page('pages/intelligence_engine.py',title='Intelligence Engine',icon='🧠'),st.Page('pages/defi_intelligence.py',title='DeFi Intelligence',icon='🌐'),st.Page('pages/portfolio.py',title='Portfolio',icon='💼'),st.Page('pages/watchlist.py',title='Watchlist',icon='👁️'),st.Page('pages/history.py',title='History',icon='📈'),st.Page('pages/developer_status.py',title='Developer Status',icon='🛠️')]
})
navigation.run()
