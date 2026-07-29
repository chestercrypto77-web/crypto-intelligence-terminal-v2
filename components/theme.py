import streamlit as st

CSS = '''
<style>
:root {
  --cit-border: rgba(255,255,255,0.10);
  --cit-panel: rgba(255,255,255,0.035);
}
.block-container { padding-top: 2rem; padding-bottom: 3rem; }
.terminal-card {
  border: 1px solid var(--cit-border);
  border-radius: 14px;
  padding: 18px;
  min-height: 126px;
  background: var(--cit-panel);
}
.terminal-card-label { opacity: 0.72; font-size: 0.85rem; }
.terminal-card-value { font-size: 1.45rem; font-weight: 700; margin-top: 8px; }
.terminal-card-note { opacity: 0.65; font-size: 0.8rem; margin-top: 10px; }
.terminal-status {
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 10px;
  padding: 10px 14px;
  background: rgba(255,255,255,0.025);
  margin-bottom: 1rem;
}
.briefing-panel {
  border: 1px solid rgba(91,140,255,0.35);
  border-radius: 14px;
  padding: 20px;
  background: rgba(91,140,255,0.06);
  line-height: 1.65;
}
.signal-positive { color: #37c99b; font-weight: 700; }
.signal-caution { color: #e4b84c; font-weight: 700; }
.signal-negative { color: #ee7282; font-weight: 700; }
</style>
'''


def apply_theme() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
