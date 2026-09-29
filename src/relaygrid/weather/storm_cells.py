from __future__ import annotations
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class StormCell:
    cell_id: str
    center_lat: float
    center_lon: float
    radius_km: float
    wind_mps: float
    lightning_rate: float
    start_s: float
    end_s: float


def km_per_degree_lat(): return 111.195

def point_distance_km(lat1,lon1,lat2,lon2):
    y=(lat2-lat1)*km_per_degree_lat(); x=(lon2-lon1)*km_per_degree_lat()*math.cos(math.radians((lat1+lat2)/2))
    return math.hypot(x,y)


def contains(cell:StormCell,lat:float,lon:float,timestamp_s:float):
    return cell.start_s<=timestamp_s<=cell.end_s and point_distance_km(cell.center_lat,cell.center_lon,lat,lon)<=cell.radius_km


def severity(cell:StormCell):
    wind=max(0.0,(cell.wind_mps-15)/25)
    lightning=min(1.0,max(0.0,cell.lightning_rate)/60)
    return min(1.0,.7*wind+.3*lightning)


def affected_assets(cell:StormCell,assets:list[tuple[str,float,float]],timestamp_s:float):
    hits={}
    for aid,lat,lon in assets:
        if aid in hits or not contains(cell,lat,lon,timestamp_s): continue
        hits[aid]=point_distance_km(cell.center_lat,cell.center_lon,lat,lon)
    return list(hits.items())


def _overlap(a:StormCell,b:StormCell,overlap_ratio:float):
    d=point_distance_km(a.center_lat,a.center_lon,b.center_lat,b.center_lon)
    return d<=overlap_ratio*(a.radius_km+b.radius_km) and not (a.end_s<b.start_s or b.end_s<a.start_s)


def merge_cells(cells:list[StormCell],overlap_ratio:float=.5):
    ordered=sorted(cells,key=lambda c:c.start_s)
    parent=list(range(len(ordered)))
    def find(i):
        while parent[i]!=i:
            parent[i]=parent[parent[i]]; i=parent[i]
        return i
    def union(i,j):
        ri,rj=find(i),find(j)
        if ri!=rj: parent[rj]=ri
    for i in range(len(ordered)):
        for j in range(i+1,len(ordered)):
            if _overlap(ordered[i],ordered[j],overlap_ratio): union(i,j)
    groups: dict[int,list[StormCell]]={}
    for i,cell in enumerate(ordered):
        groups.setdefault(find(i),[]).append(cell)
    return list(groups.values())
