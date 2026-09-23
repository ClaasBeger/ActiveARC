import os,sys
sys.path.insert(0,".")
from types import SimpleNamespace
from pipelines.run_active_arc_batch import _task_ids, _output_basename
ids=_task_ids(SimpleNamespace(dataset="conceptarc",offset=0,limit=160,per_concept_limit=10,task_ids=None))
d1={f[:-5] for f in os.listdir("experiments/runs/sciK_ca160_ds41f_s0_b") if f.endswith(".json") and not f.startswith(("manifest","summary","INVALID","program"))}
print("n=",len(ids),"matches draw1:",{_output_basename(t) for t in ids}==d1)
import os as _os
J=_os.path.join(_os.path.dirname(_os.path.abspath(__file__)),"shards")
for k in range(4):
    sh=ids[k::4]
    open(f"{J}/ca160_shard{k}.args","w").write(" ".join(f"--task-id {t}" for t in sh))
    print("shard",k,len(sh),"concepts",len({t.split('/')[0] for t in sh}))
all_=[t for k in range(4) for t in ids[k::4]]
print("disjoint+complete:",sorted(all_)==sorted(ids) and len(set(all_))==160)
