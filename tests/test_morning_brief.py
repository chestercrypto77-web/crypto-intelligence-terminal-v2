from services.morning_brief import market_mood, opportunities, portfolio_health, top_attention

def row(symbol,c24,c7,attention,state,priority=1): return {'available':True,'symbol':symbol,'name':symbol,'priority':priority,'change_24h':c24,'change_7d':c7,'attention':attention,'momentum_state':state}
def test_limits(): assert len(top_attention([row(str(i),i,i,90-i,'Strong') for i in range(8)],4))==4
def test_health():
 s,l=portfolio_health([row('COTI',8,15,90,'Accelerating')]); assert 0<=s<=100 and l
def test_opportunities(): assert [r['symbol'] for r in opportunities([row('COTI',9,12,90,'Accelerating'),row('ZIL',-7,-10,80,'Weakening')])]==['COTI']
def test_mood():
 m,n=market_mood({'market_cap_change_24h':2},[row('COTI',5,8,80,'Strong')]); assert m and n
