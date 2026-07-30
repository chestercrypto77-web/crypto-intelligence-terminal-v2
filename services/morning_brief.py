from __future__ import annotations
from typing import Any

def market_mood(market: dict[str, Any], rows: list[dict[str, Any]]) -> tuple[str, str]:
    change=float(market.get('market_cap_change_24h') or 0)
    available=[r for r in rows if r.get('available')]
    positive=sum(1 for r in available if float(r.get('change_24h') or 0)>0)
    breadth=positive/len(available) if available else .5
    score=change*8+(breadth-.5)*55
    if score>=18: return 'Positive','Markets and your monitored positions are broadly strengthening.'
    if score>=4: return 'Constructive','The market has a positive bias, but leadership remains selective.'
    if score<=-18: return 'Defensive','Weak market breadth and falling prices warrant caution.'
    if score<=-4: return 'Cautious','The market is soft and risk should be watched closely.'
    return 'Mixed','The market lacks a strong direction and conditions are selective.'

def portfolio_health(rows):
    personal=[r for r in rows if r.get('available') and int(r.get('priority',3))<=2]
    if not personal: return 50,'Waiting for portfolio data'
    a24=sum(float(r.get('change_24h') or 0) for r in personal)/len(personal)
    a7=sum(float(r.get('change_7d') or 0) for r in personal)/len(personal)
    urgent=sum(1 for r in personal if float(r.get('attention') or 0)>=70)
    weak=sum(1 for r in personal if str(r.get('momentum_state')) in {'Weakening','Deteriorating'})
    health=int(max(0,min(100,round(68+a24*1.6+a7*.35+min(urgent,3)*2-weak*5))))
    label='Strong' if health>=82 else 'Healthy' if health>=68 else 'Mixed' if health>=52 else 'Under pressure' if health>=35 else 'Weak'
    return health,label

def overnight_story(market, rows):
    available=[r for r in rows if r.get('available')]
    if not available: return 'Live personal-market data is temporarily unavailable.'
    gainers=sorted(available,key=lambda r:float(r.get('change_24h') or 0),reverse=True)
    losers=sorted(available,key=lambda r:float(r.get('change_24h') or 0))
    lead,weak=gainers[0],losers[0]
    urgent=[r for r in available if float(r.get('attention') or 0)>=70]
    mc=float(market.get('market_cap_change_24h') or 0)
    direction='strengthened' if mc>.5 else 'weakened' if mc<-.5 else 'was broadly steady'
    story=f"The wider crypto market {direction} over the past 24 hours ({mc:+.1f}%). {lead['name']} is the strongest project in your monitored market at {float(lead.get('change_24h') or 0):+.1f}%."
    if float(weak.get('change_24h') or 0)<=-4: story+=f" {weak['name']} is the weakest at {float(weak.get('change_24h') or 0):+.1f}%."
    story+=f" {len(urgent)} project{'s' if len(urgent)!=1 else ''} currently deserve closer attention." if urgent else ' No monitored project currently requires urgent attention.'
    return story

def top_attention(rows, limit=4):
    p=[r for r in rows if r.get('available') and int(r.get('priority',3))<=2]
    return sorted(p,key=lambda r:(-float(r.get('attention') or 0),int(r.get('priority',3))))[:limit]

def movers(rows,limit=3):
    a=[r for r in rows if r.get('available')]
    return sorted(a,key=lambda r:float(r.get('change_24h') or 0),reverse=True)[:limit], sorted(a,key=lambda r:float(r.get('change_24h') or 0))[:limit]

def opportunities(rows,limit=3):
    c=[r for r in rows if r.get('available') and float(r.get('change_24h') or 0)>0 and str(r.get('momentum_state')) in {'Accelerating','Strong','Improving','Building'}]
    return sorted(c,key=lambda r:(-float(r.get('attention') or 0),-float(r.get('change_24h') or 0)))[:limit]

def risks(rows,limit=3):
    c=[r for r in rows if r.get('available') and (float(r.get('change_24h') or 0)<=-4 or str(r.get('momentum_state')) in {'Weakening','Deteriorating'} or str(r.get('risk','')).upper()=='HIGH')]
    return sorted(c,key=lambda r:(float(r.get('change_24h') or 0),-float(r.get('attention') or 0)))[:limit]
