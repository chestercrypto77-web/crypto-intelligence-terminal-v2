import html
import streamlit as st
import config
from components.layout import page_header
from portfolio_profile import PORTFOLIO_PROFILE, PROFILE_STATUS
from services.category_data import CategoryDataError, get_hot_categories
from services.conviction import build_conviction_list
from services.event_engine import run_event_detection
from services.event_store import recent_events
from services.formatting import compact_currency, signed_percentage, utc_time
from services.market_data import MarketDataError, get_market_snapshot, get_scanner_market
from services.morning_brief import market_mood, movers, opportunities, overnight_story, portfolio_health, risks, top_attention
from services.personal_intelligence import build_personal_market
from services.scanner import build_opportunity_list

APP_VERSION=getattr(config,'APP_VERSION','2.0.0')
page_header('Good morning, Mark','Your five-minute personal crypto briefing')
try:
    market=get_market_snapshot(); scanner=build_opportunity_list(get_scanner_market())
    try:
        categories=get_hot_categories(); leader_change=categories['leaders'][0]['change_24h'] if categories.get('leaders') else None
    except CategoryDataError:
        leader_change=None
    held={str(a['symbol']).upper() for a in PORTFOLIO_PROFILE if int(a.get('priority',3))<=2}
    conviction=build_conviction_list(scanner['rows'],leader_change,held)
    rows=build_personal_market(scanner['rows'],conviction,PORTFOLIO_PROFILE)
    run_event_detection(rows)
    mood,mood_note=market_mood(market,rows); health,health_label=portfolio_health(rows)
    important=top_attention(rows,4); gainers,losers=movers(rows,3); opps=opportunities(rows,3); risk_rows=risks(rows,3)
    events=recent_events(hours=24,limit=10,minimum_severity='High')
    st.caption(f"Updated {utc_time(market['updated_at'])} · {PROFILE_STATUS} · Release {APP_VERSION}")
    a,b,c,d=st.columns(4)
    a.metric('Market mood',mood,f"{float(market.get('market_cap_change_24h') or 0):+.1f}%")
    b.metric('Portfolio health',f'{health}/100',health_label)
    c.metric('Needs attention',len([r for r in important if float(r.get('attention') or 0)>=70]))
    d.metric('High-priority events',len(events))
    st.markdown(f"""<div class="morning-story"><div class="morning-kicker">THE OVERNIGHT STORY</div><div class="morning-headline">{html.escape(mood)} market</div><div class="morning-copy">{html.escape(overnight_story(market,rows))}</div><div class="morning-note">{html.escape(mood_note)}</div></div>""",unsafe_allow_html=True)
    st.subheader('What matters to you today')
    if important:
        cols=st.columns(min(4,len(important)))
        for col,row in zip(cols,important):
            with col:
                change=float(row.get('change_24h') or 0); marker='🔥' if float(row.get('attention') or 0)>=85 else '⚡' if change>=0 else '🔻'
                st.markdown(f"""<div class="morning-asset"><div class="morning-asset-symbol">{marker} {html.escape(row['symbol'])}</div><div class="morning-asset-change">{change:+.1f}%</div><div class="morning-asset-label">Attention {float(row.get('attention') or 0):.0f}/100</div><div class="morning-asset-reason">{html.escape(row.get('reason',''))}</div></div>""",unsafe_allow_html=True)
    else: st.info('No personal positions are currently producing a strong signal.')
    left,right=st.columns(2)
    with left:
        st.subheader('Biggest movers')
        for title,items in (('Leaders',gainers),('Under pressure',losers)):
            st.markdown(f'**{title}**')
            for row in items: st.markdown(f'<div class="brief-row"><strong>{html.escape(row["symbol"])}</strong><span>{float(row.get("change_24h") or 0):+.1f}%</span></div>',unsafe_allow_html=True)
    with right:
        st.subheader("Today's shortlist")
        if opps:
            for i,row in enumerate(opps,1): st.markdown(f"""<div class="brief-list-item"><div class="brief-list-number">{i}</div><div><strong>{html.escape(row['name'])}</strong><div>{html.escape(row.get('reason',''))}</div></div></div>""",unsafe_allow_html=True)
        else: st.caption('No clear momentum opportunity currently meets the shortlist rules.')
        st.markdown('**Risks to watch**')
        if risk_rows:
            for row in risk_rows: st.markdown(f'<div class="risk-line">⚠️ <strong>{html.escape(row["symbol"])}</strong> — {html.escape(row.get("reason",""))}</div>',unsafe_allow_html=True)
        else: st.caption('No major personal-market weakness currently detected.')
    st.divider()
    with st.expander('Portfolio details'):
        st.caption('Indicative classifications based on the supplied transaction-history snapshot. Balances and position sizes can be corrected later.')
        st.dataframe([{'Project':r['name'],'Symbol':r['symbol'],'Classification':r['group'],'24h':signed_percentage(r.get('change_24h')) if r.get('available') else '—','7d':signed_percentage(r.get('change_7d')) if r.get('available') else '—','Attention':r.get('attention',0),'State':r.get('momentum_state','Data unavailable')} for r in rows if int(r.get('priority',3))<=2],use_container_width=True,hide_index=True)
    with st.expander('Market details'):
        m1,m2,m3,m4=st.columns(4); m1.metric('Market capitalisation',compact_currency(market.get('total_market_cap'))); m2.metric('24h volume',compact_currency(market.get('total_volume'))); m3.metric('BTC dominance',f"{float(market.get('btc_dominance') or 0):.1f}%"); m4.metric('ETH dominance',f"{float(market.get('eth_dominance') or 0):.1f}%")
    with st.expander('Event details'):
        if events:
            for e in events[:8]: st.markdown(f"**{e['severity']} · {e['symbol']}** — {e['title']}  \n{e['detail']}")
        else: st.caption('No high-priority events in the past 24 hours.')
    with st.expander('How this morning brief works'):
        st.write('The front page deliberately limits itself to the overnight story, four personal projects, the largest movers, three opportunities and three risks. Full technical engines remain under Deep Dive.')
except MarketDataError as exc:
    st.error(str(exc))
