import streamlit as st

CSS = '''
<style>
:root {
  --cit-border: rgba(255,255,255,0.10);
  --cit-panel: rgba(255,255,255,0.035);
  --cit-blue: #5B8CFF;
}
.block-container { padding-top: 1.35rem; padding-bottom: 3rem; max-width: 1500px; }
h1 { letter-spacing: -0.035em; }
h2, h3 { letter-spacing: -0.02em; }
[data-testid="stSidebar"] { border-right: 1px solid rgba(255,255,255,0.07); }

.terminal-card {
  border: 1px solid var(--cit-border); border-radius: 14px; padding: 16px;
  min-height: 112px; background: var(--cit-panel);
}
.terminal-card-label {
  opacity: 0.68; font-size: 0.78rem; text-transform: uppercase;
  letter-spacing: 0.055em;
}
.terminal-card-value { font-size: 1.38rem; font-weight: 720; margin-top: 8px; line-height: 1.2; }
.terminal-card-note { opacity: 0.62; font-size: 0.78rem; margin-top: 9px; }
.terminal-status {
  border: 1px solid rgba(255,255,255,0.08); border-radius: 10px;
  padding: 9px 13px; background: rgba(255,255,255,0.025); margin-bottom: 1rem;
  font-size: 0.84rem;
}
.briefing-panel, .evidence-panel, .pulse-panel {
  border: 1px solid rgba(91,140,255,0.30); border-radius: 14px;
  padding: 18px; background: rgba(91,140,255,0.055); line-height: 1.62;
}
.mode-panel {
  border: 1px solid rgba(91,140,255,0.22); border-radius: 16px;
  padding: 15px 18px; background: rgba(91,140,255,0.035); margin-bottom: 1rem;
}
.project-card, .feed-item {
  border: 1px solid rgba(255,255,255,0.10); border-radius: 14px;
  padding: 15px 17px; background: rgba(255,255,255,0.027); margin-bottom: 10px;
}
.project-title, .feed-title { font-size: 1.04rem; font-weight: 720; }
.project-reason, .feed-detail { opacity: 0.74; line-height: 1.45; margin-top: 7px; }
.feed-time {
  opacity: 0.55; font-size: 0.75rem; letter-spacing: 0.04em;
  text-transform: uppercase; margin-bottom: 4px;
}
.section-label {
  font-size: 0.76rem; text-transform: uppercase; letter-spacing: 0.08em;
  opacity: 0.58; margin-bottom: 0.35rem;
}
.health-row {
  display: grid; grid-template-columns: minmax(120px, 1.2fr) 3fr 56px;
  gap: 12px; align-items: center; margin: 9px 0;
}
.health-track, .heat-track {
  height: 9px; border-radius: 99px; background: rgba(255,255,255,0.08);
  overflow: hidden;
}
.health-fill, .heat-fill {
  height: 100%; border-radius: 99px;
  background: linear-gradient(90deg, #5B8CFF, #37c99b);
}
.pulse-meter {
  border: 1px solid rgba(91,140,255,0.28); border-radius: 18px;
  padding: 22px; background: rgba(91,140,255,0.06);
}
.pulse-number { font-size: 3rem; font-weight: 800; letter-spacing: -0.05em; }
.pulse-label { font-size: 1.05rem; font-weight: 700; margin-top: 4px; }
.pulse-direction { opacity: 0.72; margin-top: 5px; }
.heat-row {
  display: grid; grid-template-columns: minmax(110px,1fr) 3fr 90px;
  gap: 12px; align-items: center; margin: 12px 0;
}
.evidence-item { padding: 7px 0; border-bottom: 1px solid rgba(255,255,255,0.06); }
.evidence-item:last-child { border-bottom: 0; }
.flow-up { color: #37c99b; font-weight: 750; }
.flow-flat { color: #e4b84c; font-weight: 750; }
.flow-down { color: #ee7282; font-weight: 750; }
.signal-positive { color: #37c99b; font-weight: 700; }
.signal-caution { color: #e4b84c; font-weight: 700; }
.signal-negative { color: #ee7282; font-weight: 700; }
div[data-testid="stDataFrame"] {
  border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; overflow: hidden;
}
div[role="radiogroup"] { gap: 0.35rem; }

.severity-critical { border-left: 4px solid #ee7282; background: rgba(238,114,130,0.055); }
.severity-high { border-left: 4px solid #e4b84c; background: rgba(228,184,76,0.045); }
.severity-medium { border-left: 4px solid #5B8CFF; }
.severity-informational { border-left: 4px solid rgba(255,255,255,0.25); }


.morning-story{border:1px solid rgba(91,140,255,.22);border-radius:22px;padding:28px 30px;background:linear-gradient(135deg,rgba(91,140,255,.10),rgba(255,255,255,.025));margin:1rem 0 1.6rem}.morning-kicker{font-size:.72rem;letter-spacing:.12em;opacity:.58;font-weight:750}.morning-headline{font-size:2rem;font-weight:780;letter-spacing:-.035em;margin:7px 0 10px}.morning-copy{font-size:1.08rem;line-height:1.62;max-width:1050px}.morning-note{margin-top:11px;opacity:.62;font-size:.88rem}.morning-asset{border:1px solid rgba(255,255,255,.09);border-radius:17px;padding:17px;background:rgba(255,255,255,.025);min-height:185px}.morning-asset-symbol{font-size:1.1rem;font-weight:780}.morning-asset-change{font-size:1.65rem;font-weight:800;margin-top:7px}.morning-asset-label{opacity:.60;font-size:.78rem;margin-top:2px}.morning-asset-reason{opacity:.74;font-size:.84rem;line-height:1.42;margin-top:12px}.brief-row{display:flex;justify-content:space-between;align-items:center;padding:9px 2px;border-bottom:1px solid rgba(255,255,255,.07)}.brief-list-item{display:grid;grid-template-columns:30px 1fr;gap:10px;padding:10px 0;border-bottom:1px solid rgba(255,255,255,.07);line-height:1.4}.brief-list-number{width:25px;height:25px;border-radius:50%;background:rgba(91,140,255,.14);display:grid;place-items:center;font-weight:750}.brief-list-item div div{opacity:.68;font-size:.84rem;margin-top:2px}.risk-line{padding:8px 0;opacity:.82}

</style>
'''

def apply_theme() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
