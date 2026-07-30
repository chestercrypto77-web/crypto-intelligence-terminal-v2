from collections import defaultdict
from config import PORTFOLIO

def clamp(v,lo=0,hi=100): return max(lo,min(hi,v))
def activity_label(r):
    if r>=2.2:return "Extreme"
    if r>=1.5:return "High"
    if r>=1.15:return "Elevated"
    if r<0.70:return "Quiet"
    return "Normal"
def momentum_label(c24,c7):
    s=c24*.55+c7*.45
    if s>=7:return "Accelerating"
    if s>=2:return "Building"
    if s<=-7:return "Breaking down"
    if s<=-2:return "Weakening"
    return "Stable"
def action_label(score,risk):
    if risk=="HIGH":return "Review"
    if score>=78:return "Watch closely"
    if score>=55:return "Hold"
    return "Review"

def build_portfolio(rows):
    m={str(r.get("id")):r for r in rows}; items=[]; total=0.0
    for h in PORTFOLIO:
        r=m.get(h["coin_id"],{}); p=float(r.get("current_price") or 0); c24=float(r.get("price_change_percentage_24h") or 0); c7=float(r.get("price_change_percentage_7d_in_currency") or c24); vol=float(r.get("total_volume") or 0); cap=float(r.get("market_cap") or 1)
        rvol=clamp(.70+(vol/max(cap,1))*8+abs(c24)/25,.35,3.0); value=p*float(h["tokens"]); total+=value
        ms=clamp(50+c24*3.1+c7*1.25); vs=clamp(35+rvol*29); rs=clamp(58-h["conviction"]*.30+abs(c24)*1.8); risk="HIGH" if rs>=68 else "MEDIUM" if rs>=42 else "LOW"
        score=clamp(ms*.34+vs*.27+h["conviction"]*.25+(100-rs)*.14); contrib=value*c24/(100+c24) if c24>-99 else 0
        items.append({**h,"price":p,"value":value,"change_24h":c24,"change_7d":c7,"volume":vol,"rvol":rvol,"volume_label":activity_label(rvol),"momentum":momentum_label(c24,c7),"momentum_score":ms,"volume_score":vs,"risk_score":rs,"risk":risk,"score":score,"contribution":contrib})
    for i in items:
        i["weight"]=i["value"]/total*100 if total else 0; i["action"]=action_label(i["score"],i["risk"])
    daily=sum(i["contribution"] for i in items); prev=total-daily; pct=daily/prev*100 if prev else 0
    ws=sum(i["score"]*i["weight"] for i in items)/100 if total else 0; wr=sum(i["risk_score"]*i["weight"] for i in items)/100 if total else 0; health=clamp(ws*.70+(100-wr)*.30)
    themes=defaultdict(lambda:{"value":0.0,"weighted_change":0.0})
    for i in items:
        for n in [x.strip() for x in i["narrative"].split("/")]: themes[n]["value"]+=i["value"]; themes[n]["weighted_change"]+=i["value"]*i["change_24h"]
    theme_rows=[]
    for n,d in themes.items():
        ch=d["weighted_change"]/d["value"] if d["value"] else 0; theme_rows.append({"name":n,"value":d["value"],"change":ch,"strength":clamp(50+ch*5)})
    theme_rows.sort(key=lambda x:x["strength"],reverse=True); items.sort(key=lambda x:x["value"],reverse=True)
    attention=sorted(items,key=lambda x:abs(x["change_24h"])*.35+x["rvol"]*14+(100-x["score"])*.08,reverse=True)[:4]
    return {"items":items,"total":total,"daily_change":daily,"daily_pct":pct,"health":health,"risk":"HIGH" if wr>=64 else "MEDIUM" if wr>=40 else "LOW","themes":theme_rows,"attention":attention}

def executive_brief(p):
    items=p["items"]; leaders=sorted(items,key=lambda x:x["contribution"],reverse=True); strongest=max(items,key=lambda x:x["score"]); active=max(items,key=lambda x:x["rvol"]); direction="gained" if p["daily_change"]>=0 else "declined"
    return f"Your portfolio {direction} today. {leaders[0]['symbol']} and {leaders[1]['symbol']} are the largest positive contributors. {strongest['symbol']} has the strongest combined intelligence score, while {active['symbol']} shows the highest participation signal. Overall portfolio health is {p['health']:.0f}/100 with {p['risk'].lower()} risk. " + ("No urgent defensive action is indicated." if p["risk"]!="HIGH" else "Review the highest-risk positions before making new allocations.")
