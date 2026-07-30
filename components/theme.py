import streamlit as st

CSS = """
<style>
:root {
  color-scheme: dark;
  --bg: #0B0F17;
  --sidebar: #0E1420;
  --panel: #111827;
  --panel-soft: rgba(255,255,255,0.028);
  --border: rgba(255,255,255,0.075);
  --text: #E8EDF5;
  --muted: #8E9AAC;
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
    linear-gradient(140deg, #111827, #0E1521);
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
</style>
"""

def apply_theme() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
