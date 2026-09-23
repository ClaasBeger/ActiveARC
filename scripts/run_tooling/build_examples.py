import json,os,glob
R="experiments/runs/"
EX=set(json.load(open("experiments/conceptarc_extra50_task_ids.json")))
DS={"parc":"parc50","conceptarc":"ca160","arc":"arc400","arc2":"arc2_200"}
MODELS=[("astra","gpt-6-astra"),("g38","gemini-3.8-flash"),("luna","gpt-5.6-luna"),("opus5","claude-opus-5"),("ds41f","deepseek-v4.1-flash")]
def ok_dir(d, need_kinds=True):
    p=R+d
    if not os.path.isdir(p) or os.path.exists(p+"/INVALID_shared_test_context.json"): return False
    fs=[f for f in os.listdir(p) if f.endswith(".json") and not f.startswith(("manifest","summary","INVALID","program"))]
    if len(fs)<45: return False
    try: r=json.load(open(p+"/"+fs[0]))
    except Exception: return False
    return bool(r.get("test_item_kinds")) if need_kinds else True
def pick(cands):
    for d in cands:
        if ok_dir(d): return d
    return None
runs={}
for ds,tag in DS.items():
    for m,_ in MODELS:
        rk=pick([f"randK_{tag}_{m}_br",f"randK_{tag}_{m}_br_rep2",f"randK_{tag}_{m}_br_s1"])
        fk=pick([f"sciK_{tag}_{m}_s0_b",f"sciK_{tag}_{m}_s0_fix",f"sciK_{tag}_{m}_s0_b_rep2"])
        if rk and fk: runs[(ds,m)]=(rk,fk)
for k,v in runs.items(): print(k,v)
def load(d,t):
    f=R+d+"/"+t.replace("/","__")+".json"
    if not os.path.exists(f): return None
    r=json.load(open(f))
    return None if r.get("error") else r
def off_correct(r):
    k=r.get("test_item_kinds") or []; ic=r.get("test_item_correct") or []
    o=[x for x,kk in zip(ic,k) if kk=="official"]; return all(o) if o else bool(r.get("correct"))
def forced_queries(r):
    out=[]; hist=list((r.get("trial") or {}).get("query_history") or [])
    for x in r.get("transcript") or []:
        if x.get("phase")=="test": continue
        for tc,tr in zip(x.get("tool_calls") or [], x.get("tool_results") or []):
            if tc.get("name")!="submit_query": continue
            try: grid=json.loads(tc.get("arguments") or "{}").get("grid")
            except Exception: grid=None
            res=tr.get("result") or {}
            if isinstance(res,dict) and res.get("ok") is False:
                out.append({"in":grid,"out":None,"rejected":str(res.get("error"))[:80]})
            else:
                h=hist.pop(0) if hist else {}
                out.append({"in":h.get("input",grid),"out":h.get("output")})
    return out
def forced_prediction(r,item_index):
    g=None
    for x in r.get("transcript") or []:
        if x.get("phase")=="test" and x.get("test_item")==item_index:
            for tc in x.get("tool_calls") or []:
                if tc.get("name")=="submit_final_answer":
                    try: g=json.loads(tc.get("arguments") or "{}").get("grid")
                    except Exception: pass
    return g
out={"datasets":[]}
for ds,tag in DS.items():
    ms=[m for m,_ in MODELS if (ds,m) in runs]
    common=None
    for m in ms:
        for d in runs[(ds,m)]:
            ids={f[:-5] for f in os.listdir(R+d) if f.endswith(".json") and not f.startswith(("manifest","summary","INVALID","program"))}
            common=ids if common is None else common&ids
    common=sorted(t for t in common if t not in EX)
    scored=[]
    for tb in common:
        tid=tb.replace("__","/")
        rs={m:(load(runs[(ds,m)][0],tid),load(runs[(ds,m)][1],tid)) for m in ms}
        if any(a is None or b is None for a,b in rs.values()): continue
        rk=sum(off_correct(a) for a,_ in rs.values()); fk=sum(off_correct(b) for _,b in rs.values())
        size=max(len(g) for a,_ in rs.values() for p in a["train_pairs"] for g in (p["input"],))
        scored.append((tid,rk,fk,size))
    small=[s for s in scored if s[3]<=16] or scored
    picks=[]
    c1=max(small,key=lambda s:(s[1]-s[2],-s[3])); picks.append((c1,"Random-K solves it more often"))
    rest=[s for s in small if s[0]!=c1[0]]
    c2=max(rest,key=lambda s:(s[1]+s[2],-s[3])); picks.append((c2,"Both arms mostly solve it"))
    rest=[s for s in rest if s[0]!=c2[0]]
    c3=max(rest,key=lambda s:(s[2]-s[1],-s[3])); picks.append((c3,"Forced-K does as well or better"))
    dsout={"name":ds,"tag":tag,"tasks":[]}
    for (tid,rkc,fkc,_),why in picks:
        task={"id":tid,"why":why,"rk_correct":rkc,"fk_correct":fkc,"n_models":len(ms),"models":[]}
        for m in ms:
            a,b=load(runs[(ds,m)][0],tid),load(runs[(ds,m)][1],tid)
            ti=[x for x in a["test_items"] if x["kind"]=="official"][0]
            kinds=b.get("test_item_kinds") or []
            fidx=kinds.index("official") if "official" in kinds else None
            task["models"].append({
              "model":m,"label":dict(MODELS)[m],"rk_dir":runs[(ds,m)][0],"fk_dir":runs[(ds,m)][1],
              "test_in":ti["input"],"gold":ti["gold_output"],
              "rk":{"pairs":[{"in":p["input"],"out":p["output"]} for p in a["train_pairs"]],"pred":ti.get("prediction"),"ok":off_correct(a)},
              "fk":{"hot":(b.get("trial") or {}).get("hot_start_pair"),"queries":forced_queries(b),"pred":forced_prediction(b,fidx) if fidx is not None else None,"ok":off_correct(b),"end":str((b.get("final") or {}).get("reason")),"abandoned":fidx is None}})
        dsout["tasks"].append(task)
        print(ds,tid,why,f"randK {rkc}/{len(ms)} forcedK {fkc}/{len(ms)}")
    out["datasets"].append(dsout)
json.dump(out,open("examples.json","w"))
print("abandoned forced-K trials on page:",[(d["name"],t["id"],m["model"],m["fk"]["end"]) for d in out["datasets"] for t in d["tasks"] for m in t["models"] if m["fk"]["abandoned"]])
print("size KB",os.path.getsize("examples.json")//1024)
