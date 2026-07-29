import streamlit as st

CSS = '''
<style>
:root {
  --cit-border: rgba(255,255,255,0.10);
  --cit-panel: rgba(255,255,255,0.035);
  --cit-blue: #5B8CFF;
}
.block-container {
  padding-top: 1.5rem;
  padding-bottom: 3rem;
  max-width: 1500px;
}
h1 { letter-spacing: -0.035em; }
h2, h3 { letter-spacing: -0.02em; }
[data-testid="stSidebar"] { border-right: 1px solid rgba(255,255,255,0.07); }
.terminal-card {
  border: 1px solid var(--cit-border);
  border-radius: 14px;
  padding: 16px;
  min-height: 118px;
  background: var(--cit-panel);
}
.terminal-card-label {
  opacity: 0.68;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.055em;
}
.terminal-card-value {
  font-size: 1.38rem;
  font-weight: 720;
  margin-top: 8px;
  line-height: 1.2;
}
.terminal-card-note {
  opacity: 0.62;
  font-size: 0.78rem;
  margin-top: 9px;
}
.terminal-status {
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 10px;
  padding: 9px 13px;
  background: rgba(255,255,255,0.025);
  margin-bottom: 1rem;
  font-size: 0.84rem;
}
.briefing-panel {
  border: 1px solid rgba(91,140,255,0.30);
  border-radius: 14px;
  padding: 18px;
  background: rgba(91,140,255,0.055);
  line-height: 1.62;
}
.section-label {
  font-size: 0.76rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  opacity: 0.58;
  margin-bottom: 0.35rem;
}
.signal-positive { color: #37c99b; font-weight: 700; }
.signal-caution { color: #e4b84c; font-weight: 700; }
.signal-negative { color: #ee7282; font-weight: 700; }
div[data-testid="stDataFrame"] {
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  overflow: hidden;
}
</style>
'''


def apply_theme() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
