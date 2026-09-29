from __future__ import annotations

def _incident_score(x):
    iid,customers,critical,hazard,age_min=x
    return customers+critical*500+hazard*800+age_min*2

def prioritize_incidents(incidents):
    evidence={}
    for x in incidents:
        iid=x[0]
        if iid not in evidence or _incident_score(x)>=_incident_score(evidence[iid]):
            evidence[iid]=x
    def key(x):
        return (-_incident_score(x),x[0])
    return [x for x in sorted(evidence.values(),key=key)]

def sla_breached(opened_min: float,now_min: float,sla_min: float): return now_min-opened_min>sla_min
