from __future__ import annotations

def incident_score(x):
    iid,customers,critical,hazard,age_min=x
    return customers+critical*500+hazard*800+age_min*2

def prioritize_incidents(incidents):
    # Collapse multiple reports of the same incident, keeping the newest
    # highest-risk evidence so each event is dispatched exactly once.
    best={}
    for x in incidents:
        iid=x[0]
        if iid not in best or incident_score(x)>=incident_score(best[iid]):
            best[iid]=x
    return sorted(best.values(),key=lambda x:(-incident_score(x),x[0]))

def sla_breached(opened_min: float,now_min: float,sla_min: float): return now_min-opened_min>sla_min
