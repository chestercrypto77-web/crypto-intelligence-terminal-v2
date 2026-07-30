import streamlit as st

CSS = """
<style>
:root {
  color-scheme: dark;
  --bg: #1B2028;
  --sidebar: #202631;
  --panel: #282F3A;
  --panel-soft: rgba(255,255,255,0.028);
  --border: rgba(255,255,255,0.075);
  --text: #F1F3F6;
  --muted: #AEB8C5;
  --blue: #6F96FF;
  --green: #63D7B0;
  --amber: #E7BE63;
  --red: #F17F8D;
}

html, body, [data-testid="stAppViewContainer"], .stApp {
  background: var(--bg) !important;
  color: var(--text) !important;
}
[data-testid="stHeader"] {
  background: rgba(11,15,23,0.88) !important;
  backdrop-filter: blur(12px);
}
[data-testid="stSidebar"] {
  background: var(--sidebar) !important;
  border-right: 1px solid var(--border);
}
[data-testid="stSidebarNav"] span {
  font-size: 0.91rem;
}
.block-container {
  padding-top: 1.45rem;
  padding-bottom: 4rem;
  max-width: 1320px;
}
h1 {
  letter-spacing: -0.045em;
  font-weight: 760;
  font-size: clamp(2rem, 4vw, 3.35rem);
}
h2, h3 {
  letter-spacing: -0.025em;
  font-weight: 700;
}
p, div, span {
  text-rendering: optimizeLegibility;
}
[data-testid="stMetric"] {
  background: var(--panel-soft);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 15px 17px;
}
[data-testid="stMetricLabel"] {
  color: var(--muted);
}
[data-testid="stMetricValue"] {
  letter-spacing: -0.035em;
}
[data-testid="stMetricDelta"] {
  opacity: 0.82;
}
[data-testid="stExpander"] {
  border: 1px solid var(--border) !important;
  border-radius: 14px !important;
  background: rgba(255,255,255,0.018);
}
button, [data-testid="stBaseButton-secondary"] {
  border-radius: 11px !important;
}
hr {
  border-color: var(--border) !important;
  margin: 2rem 0 !important;
}
.morning-story {
  border: 1px solid rgba(111,150,255,0.20);
  border-radius: 23px;
  padding: 28px 30px;
  background:
    radial-gradient(circle at top right, rgba(111,150,255,0.12), transparent 38%),
    linear-gradient(140deg, #282F3A, #232A34);
  box-shadow: 0 18px 50px rgba(0,0,0,0.20);
  margin: 1.15rem 0 1.8rem;
}
.morning-kicker {
  font-size: 0.70rem;
  letter-spacing: 0.14em;
  color: var(--muted);
  font-weight: 750;
}
.morning-headline {
  font-size: 2rem;
  font-weight: 770;
  letter-spacing: -0.04em;
  margin: 7px 0 10px;
}
.morning-copy {
  font-size: 1.06rem;
  line-height: 1.7;
  max-width: 1040px;
  color: #D7DEE9;
}
.morning-note {
  margin-top: 12px;
  color: var(--muted);
  font-size: 0.86rem;
}
.calm-banner {
  display: flex;
  align-items: center;
  gap: 14px;
  border: 1px solid rgba(99,215,176,0.22);
  background: rgba(99,215,176,0.055);
  border-radius: 16px;
  padding: 14px 17px;
  margin: 1rem 0;
}
.calm-icon {
  width: 32px;
  height: 32px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: rgba(99,215,176,0.14);
  color: var(--green);
  font-weight: 800;
}
.calm-title { font-weight: 720; }
.calm-copy { color: var(--muted); font-size: 0.84rem; margin-top: 2px; }
.morning-asset {
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 17px;
  background: linear-gradient(150deg, rgba(255,255,255,0.038), rgba(255,255,255,0.014));
  min-height: 205px;
}
.morning-asset-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.morning-asset-symbol { font-size: 1.05rem; font-weight: 760; }
.portfolio-weight {
  color: var(--muted);
  font-size: 0.76rem;
  border: 1px solid var(--border);
  border-radius: 99px;
  padding: 3px 7px;
}
.morning-asset-change {
  font-size: 1.75rem;
  font-weight: 800;
  letter-spacing: -0.04em;
  margin-top: 12px;
}
.morning-asset-value { color: #DCE4EF; font-size: 0.88rem; margin-top: 1px; }
.morning-asset-label { color: var(--muted); font-size: 0.76rem; margin-top: 6px; }
.morning-asset-reason { color: #AAB4C3; font-size: 0.82rem; line-height: 1.45; margin-top: 12px; }
.holding-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 13px 4px;
  border-bottom: 1px solid rgba(255,255,255,0.055);
}
.holding-symbol {
  color: var(--muted);
  font-size: 0.76rem;
  margin-left: 8px;
}
.holding-right {
  display: flex;
  align-items: center;
  gap: 14px;
}
.holding-change {
  color: var(--muted);
  width: 58px;
  text-align: right;
}
.attention-line {
  display: grid;
  grid-template-columns: 9px 1fr;
  gap: 11px;
  padding: 10px 0;
  border-bottom: 1px solid rgba(255,255,255,0.055);
}
.attention-line div div {
  color: var(--muted);
  font-size: 0.82rem;
  line-height: 1.42;
  margin-top: 3px;
}
.attention-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--amber);
  margin-top: 7px;
}
.risk-line { padding: 7px 0; color: #B7C0CE; }
.terminal-card, .project-card, .feed-item, .briefing-panel,
.evidence-panel, .pulse-panel, .mode-panel {
  border: 1px solid var(--border);
  background: var(--panel-soft);
  border-radius: 15px;
}
div[data-testid="stDataFrame"] {
  border: 1px solid var(--border);
  border-radius: 13px;
  overflow: hidden;
}
.flow-up, .signal-positive { color: var(--green); }
.flow-flat, .signal-caution { color: var(--amber); }
.flow-down, .signal-negative { color: var(--red); }
.severity-critical { border-left: 3px solid var(--red); }
.severity-high { border-left: 3px solid var(--amber); }
.severity-medium { border-left: 3px solid var(--blue); }

/* Release 2.1.1: hard dark-mode fallback.
   This applies even when GitHub upload tools omit the hidden .streamlit folder. */
#root,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
section.main,
.main,
.stApp,
.stApp > div {
  background-color: #1B2028 !important;
  color: #F1F3F6 !important;
}

[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stBottomBlockContainer"] {
  background: transparent !important;
}

[data-testid="stSidebarContent"],
[data-testid="stSidebarUserContent"],
[data-testid="stSidebarNav"],
[data-testid="stSidebarNavItems"] {
  background-color: #202631 !important;
}

[data-testid="stMetric"],
[data-testid="stAlert"],
[data-testid="stExpander"],
[data-testid="stForm"],
[data-testid="stDataFrame"],
[data-testid="stTable"],
[data-testid="stJson"],
[data-testid="stCodeBlock"],
[data-testid="stVerticalBlockBorderWrapper"] {
  background-color: #282F3A !important;
  color: #F1F3F6 !important;
}

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div,
input,
textarea {
  background-color: #282F3A !important;
  color: #F1F3F6 !important;
  border-color: rgba(255,255,255,0.10) !important;
}

[data-baseweb="popover"],
[data-baseweb="menu"],
[role="listbox"],
[role="option"] {
  background-color: #282F3A !important;
  color: #F1F3F6 !important;
}

[data-testid="stDataFrame"] iframe {
  background-color: #282F3A !important;
  color-scheme: dark !important;
}

.stMarkdown,
.stMarkdown p,
.stMarkdown span,
.stCaption,
label,
h1, h2, h3, h4, h5, h6 {
  color: #F1F3F6 !important;
}

.stCaption,
[data-testid="stCaptionContainer"],
[data-testid="stMetricLabel"],
[data-testid="stWidgetLabel"] {
  color: #AEB8C5 !important;
}


/* Release 2.1.2: restore readable navigation and widget text. */
[data-testid="stSidebar"] *,
[data-testid="stSidebarContent"] *,
[data-testid="stSidebarNav"] *,
[data-testid="stSidebarNavItems"] *,
[data-testid="stSidebarNavLink"] *,
[data-testid="stSidebarNavLink"] span,
[data-testid="stSidebarNavLink"] p {
  color: #C8D2E1 !important;
  opacity: 1 !important;
}

[data-testid="stSidebarNavLink"][aria-current="page"],
[data-testid="stSidebarNavLink"][aria-current="page"] *,
[data-testid="stSidebarNavLink"]:hover,
[data-testid="stSidebarNavLink"]:hover * {
  color: #F4F7FB !important;
  opacity: 1 !important;
}

[data-testid="stSidebarNavLink"][aria-current="page"] {
  background: rgba(111,150,255,0.15) !important;
  border: 1px solid rgba(111,150,255,0.18) !important;
  border-radius: 8px !important;
}

[data-testid="stSidebarNavSeparator"] *,
[data-testid="stSidebarNavItems"] > div > span,
[data-testid="stSidebarNavItems"] > div > p {
  color: #7F8CA0 !important;
  opacity: 1 !important;
}

[data-testid="stMetric"] *,
[data-testid="stExpander"] *,
[data-testid="stAlert"] *,
[data-testid="stWidgetLabel"] *,
[data-testid="stCaptionContainer"] *,
[data-testid="stMarkdownContainer"] {
  opacity: 1 !important;
}

[data-testid="stMetricValue"] {
  color: #F2F5FA !important;
}

[data-testid="stMetricDelta"] {
  color: #AEB9C8 !important;
}

a, a:visited {
  color: #8FAEFF !important;
}


/* Release 2.1.3: high-contrast navigation and page hierarchy. */
[data-testid="stSidebar"] {
  background: #202631 !important;
  min-width: 250px !important;
}

[data-testid="stSidebar"] a,
[data-testid="stSidebar"] button,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div {
  color: #DDE6F3 !important;
  opacity: 1 !important;
  -webkit-text-fill-color: #DDE6F3 !important;
}

[data-testid="stSidebar"] a {
  font-size: 0.94rem !important;
  font-weight: 560 !important;
}

[data-testid="stSidebar"] a:hover {
  background: rgba(111,150,255,0.12) !important;
  border-radius: 9px !important;
}

[data-testid="stSidebar"] a[aria-current="page"],
[data-testid="stSidebar"] a[aria-current="page"] * {
  background: rgba(111,150,255,0.20) !important;
  color: #FFFFFF !important;
  -webkit-text-fill-color: #FFFFFF !important;
  font-weight: 720 !important;
  border-radius: 9px !important;
}

[data-testid="stSidebar"] [data-testid*="NavSectionHeader"],
[data-testid="stSidebar"] [class*="section"],
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
  color: #8FAEFF !important;
  -webkit-text-fill-color: #8FAEFF !important;
  font-weight: 800 !important;
  letter-spacing: 0.04em !important;
}

/* Calm but clear colour hierarchy across all pages. */
[data-testid="stMain"] h1,
[data-testid="stAppViewContainer"] h1 {
  color: #F4F7FC !important;
  -webkit-text-fill-color: #F4F7FC !important;
}

[data-testid="stMain"] h2,
[data-testid="stAppViewContainer"] h2 {
  color: #8FAEFF !important;
  -webkit-text-fill-color: #8FAEFF !important;
  border-left: 3px solid #6F96FF;
  padding-left: 10px;
  margin-top: 1.7rem;
}

[data-testid="stMain"] h3,
[data-testid="stAppViewContainer"] h3 {
  color: #E7BE63 !important;
  -webkit-text-fill-color: #E7BE63 !important;
}

[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span {
  color: #69D8B3 !important;
  -webkit-text-fill-color: #69D8B3 !important;
  font-weight: 680 !important;
}

[data-testid="stMetricLabel"] p,
[data-testid="stMetricLabel"] div {
  color: #A8B5C7 !important;
  -webkit-text-fill-color: #A8B5C7 !important;
}

[data-testid="stMetricValue"] {
  color: #F4F7FC !important;
  -webkit-text-fill-color: #F4F7FC !important;
}

[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stCaptionContainer"] {
  color: #C4CEDC !important;
  -webkit-text-fill-color: #C4CEDC !important;
  opacity: 1 !important;
}

.project-title,
.feed-title,
.terminal-card-title {
  color: #8FAEFF !important;
}

.terminal-card-label,
.feed-time,
.morning-asset-label,
.morning-note {
  color: #9EABBD !important;
}

/* Keep error text readable but do not let errors dominate the whole interface. */
[data-testid="stException"] {
  border: 1px solid rgba(241,127,141,0.30) !important;
  background: rgba(241,127,141,0.08) !important;
}


/* Release 2.2.0: charcoal visual system and Momentum Radar. */
[data-testid="stApp"], [data-testid="stAppViewContainer"], [data-testid="stMain"], .stApp {
  background: #1B2028 !important;
}
[data-testid="stSidebar"] {
  background: #202631 !important;
  border-right: 1px solid #353D49 !important;
}
[data-testid="stMetric"], [data-testid="stExpander"], [data-testid="stAlert"], [data-testid="stDataFrame"] {
  background: #282F3A !important;
  border-color: #3A4350 !important;
}
.momentum-row {
  display: grid;
  grid-template-columns: 150px 1fr 250px;
  gap: 18px;
  align-items: center;
  background: #282F3A;
  border: 1px solid #3A4350;
  border-radius: 16px;
  padding: 15px 17px;
  margin: 10px 0;
}
.momentum-symbol { font-size: 1.1rem; font-weight: 780; color: #F4F6F9; }
.momentum-name { color: #AEB8C5; font-size: 0.78rem; margin-top: 2px; }
.momentum-grid { display: grid; grid-template-columns: repeat(5, minmax(78px, 1fr)); gap: 7px; }
.momentum-cell {
  background: #232A34;
  border: 1px solid #353D49;
  border-radius: 10px;
  padding: 8px 9px;
}
.momentum-time { color: #98A5B5; font-size: 0.68rem; text-transform: uppercase; }
.momentum-value { color: #EDF1F6; font-weight: 680; margin-top: 3px; white-space: nowrap; }
.momentum-summary { border-left: 1px solid #3A4350; padding-left: 16px; }
.momentum-status {
  display: inline-block;
  border-radius: 99px;
  padding: 4px 9px;
  font-size: 0.74rem;
  font-weight: 760;
  margin-bottom: 6px;
}
.status-accelerating, .status-building, .status-strong {
  color: #75D9B8;
  background: rgba(99,215,176,0.11);
}
.status-weakening, .status-under-pressure, .status-rolling-over {
  color: #F08B96;
  background: rgba(241,127,141,0.11);
}
.status-stable, .status-mixed {
  color: #E9C46A;
  background: rgba(231,190,99,0.11);
}
.momentum-meta { color: #B7C1CE; font-size: 0.76rem; line-height: 1.45; }
.momentum-confidence { color: #8FAEFF; font-size: 0.74rem; margin-top: 5px; }
@media (max-width: 900px) {
  .momentum-row { grid-template-columns: 1fr; }
  .momentum-summary {
    border-left: 0;
    border-top: 1px solid #3A4350;
    padding-left: 0;
    padding-top: 10px;
  }
  .momentum-grid { grid-template-columns: repeat(3, 1fr); }
}

</style>
"""

def apply_theme() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
