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
    seen:set[str]=set(); hits=[]
    for aid,lat,lon in assets:
        if aid in seen: continue
        d=point_distance_km(cell.center_lat,cell.center_lon,lat,lon)
        if contains(cell,lat,lon,timestamp_s):
            seen.add(aid); hits.append((aid,d))
    return hits


def _overlaps(cell:StormCell,other:StormCell,overlap_ratio:float):
    d=point_distance_km(cell.center_lat,cell.center_lon,other.center_lat,other.center_lon)
    return cell.start_s<=other.end_s and d<=overlap_ratio*(cell.radius_km+other.radius_km)


def merge_cells(cells:list[StormCell],overlap_ratio:float=.5):
    groups: list[list[StormCell]]=[]
    for cell in sorted(cells,key=lambda c:c.start_s):
        idxs=[i for i,g in enumerate(groups) if any(_overlaps(cell,m,overlap_ratio) for m in g)]
        if not idxs:
            groups.append([cell]); continue
        merged:list[StormCell]=[cell]
        for i in reversed(idxs):
            merged.extend(groups.pop(i))
        merged.sort(key=lambda c:(c.start_s,c.cell_id))
        groups.insert(idxs[0],merged)
    return groups
