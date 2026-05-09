"""Scalable-ish duplicate candidate detection for person records."""
from __future__ import annotations
import argparse,csv,datetime as dt,re
from collections import defaultdict
from pathlib import Path
from typing import Dict,Iterable,List,Optional,Tuple
import polars as pl
try:
    from rapidfuzz import fuzz
    def _sim(a:str,b:str)->float: return fuzz.ratio(a,b)/100.0
except Exception:
    from difflib import SequenceMatcher
    def _sim(a:str,b:str)->float: return SequenceMatcher(None,a,b).ratio()
_NAME_COLS=["first_name","middle_name","last_name"]
_REQUIRED=[*_NAME_COLS,"date_of_birth","social_security_number"]

def normalize_name(v:Optional[str])->str:
    return re.sub(r"[^a-zA-Z]","",str(v or "")).lower().strip()

def normalize_ssn(v:Optional[str])->str:
    return re.sub(r"\D","",str(v or ""))

def parse_dob(v:Optional[str])->Optional[dt.date]:
    s=str(v or "").strip()
    if not s:return None
    for fmt in ("%Y-%m-%d","%m/%d/%Y","%d-%m-%Y"):
        try:return dt.datetime.strptime(s,fmt).date()
        except ValueError:pass
    return None

def canonical_name_tokens(first:str,middle:str,last:str)->str:
    return " ".join(sorted([p for p in (first,middle,last) if p]))

def name_similarity(r1:Dict,r2:Dict)->float:
    full=_sim(canonical_name_tokens(r1['first'],r1['middle'],r1['last']),canonical_name_tokens(r2['first'],r2['middle'],r2['last']))
    direct=(_sim(r1['first'],r2['first'])+_sim(r1['last'],r2['last']))/2
    cross=(_sim(r1['first'],r2['last'])+_sim(r1['last'],r2['first']))/2
    return max(full,direct,cross)

def dob_similarity(d1:Optional[dt.date],d2:Optional[dt.date])->float:
    if d1 is None or d2 is None:return 0.0
    if d1==d2:return 1.0
    days=abs((d1-d2).days)
    if days<=1:return 0.97
    if d1.year==d2.year and d1.month==d2.day and d1.day==d2.month:return 0.95
    if d1.year==d2.year and days<=31:return 0.80
    return 0.0

def ssn_similarity(s1:str,s2:str)->float:
    if not s1 or not s2:return 0.0
    if s1==s2:return 1.0
    if len(s1)>=4 and len(s2)>=4 and s1[-4:]==s2[-4:]:return 0.85
    return _sim(s1,s2)

def score_pair(r1:Dict,r2:Dict,w_name:float,w_dob:float,w_ssn:float)->Dict:
    ns,ds,ss=name_similarity(r1,r2),dob_similarity(r1['dob'],r2['dob']),ssn_similarity(r1['ssn'],r2['ssn'])
    return {"name_similarity":round(ns,4),"dob_similarity":round(ds,4),"ssn_similarity":round(ss,4),"overall_score":round(w_name*ns+w_dob*ds+w_ssn*ss,4)}

def block_keys(r:Dict)->List[Tuple[str,str]]:
    keys=[]
    if r['dob'] and len(r['ssn'])>=4: keys.append(("dob_ssn4",f"{r['dob'].isoformat()}|{r['ssn'][-4:]}"))
    if r['dob'] and r['last']: keys.append(("dob_last_i",f"{r['dob'].isoformat()}|{r['last'][0]}"))
    if len(r['ssn'])>=4 and r['first']: keys.append(("ssn4_first_i",f"{r['ssn'][-4:]}|{r['first'][0]}"))
    return keys

def iter_records(input_csv:Path,chunk_size:int)->Iterable[Dict]:
    for df in pl.read_csv(input_csv,infer_schema_length=10000,batch_size=chunk_size).iter_slices(n_rows=chunk_size):
        for row in df.iter_rows(named=True):
            yield {"record_id":row.get("record_id"),"first":normalize_name(row.get("first_name")),"middle":normalize_name(row.get("middle_name")),"last":normalize_name(row.get("last_name")),"dob":parse_dob(row.get("date_of_birth")),"ssn":normalize_ssn(row.get("social_security_number"))}

def dedupe(input_csv:Path,output_csv:Path,chunk_size:int,name_threshold:float,dob_threshold:float,ssn_threshold:float,overall_threshold:float,w_name:float,w_dob:float,w_ssn:float)->None:
    blocks:Dict[Tuple[str,str],List[Dict]]=defaultdict(list)
    seen_pairs=set()
    with output_csv.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=["record_id_1","record_id_2","name_similarity","dob_similarity","ssn_similarity","overall_score"])
        writer.writeheader()
        for rec in iter_records(input_csv,chunk_size):
            candidates=[]
            for bk in block_keys(rec): candidates.extend(blocks[bk])
            for cand in candidates:
                pair=tuple(sorted((rec['record_id'],cand['record_id'])))
                if pair in seen_pairs: continue
                seen_pairs.add(pair)
                s=score_pair(rec,cand,w_name,w_dob,w_ssn)
                if s['name_similarity']>=name_threshold and s['dob_similarity']>=dob_threshold and s['ssn_similarity']>=ssn_threshold and s['overall_score']>=overall_threshold:
                    writer.writerow({"record_id_1":pair[0],"record_id_2":pair[1],**s})
            for bk in block_keys(rec): blocks[bk].append(rec)

def validate_columns(path:Path)->None:
    cols=pl.read_csv(path,n_rows=5).columns
    if "record_id" not in cols: raise ValueError("Input must contain a unique 'record_id' column.")
    missing=[c for c in _REQUIRED if c not in cols]
    if missing: raise ValueError(f"Missing required columns: {missing}")

def main()->None:
    p=argparse.ArgumentParser(description="Detect potential duplicate person records.")
    p.add_argument("--input",required=True,type=Path);p.add_argument("--output",required=True,type=Path);p.add_argument("--chunk-size",type=int,default=200_000)
    p.add_argument("--name-threshold",type=float,default=0.85);p.add_argument("--dob-threshold",type=float,default=0.95);p.add_argument("--ssn-threshold",type=float,default=0.85);p.add_argument("--overall-threshold",type=float,default=0.90)
    p.add_argument("--w-name",type=float,default=0.45);p.add_argument("--w-dob",type=float,default=0.25);p.add_argument("--w-ssn",type=float,default=0.30)
    a=p.parse_args();validate_columns(a.input)
    if abs((a.w_name+a.w_dob+a.w_ssn)-1.0)>1e-9: raise ValueError("Weights must sum to 1.0")
    dedupe(a.input,a.output,a.chunk_size,a.name_threshold,a.dob_threshold,a.ssn_threshold,a.overall_threshold,a.w_name,a.w_dob,a.w_ssn)
if __name__=="__main__": main()
