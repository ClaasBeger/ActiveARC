import sys
sys.path.insert(0,".")
from types import SimpleNamespace
from pipelines.run_active_arc_batch import _task_ids
import os as _os
J=_os.path.join(_os.path.dirname(_os.path.abspath(__file__)),"shards")
for ds,lim,tag,k in [("arc",400,"arc400",5),("arc2",200,"arc2_200",3)]:
    ids=_task_ids(SimpleNamespace(dataset=ds,offset=0,limit=lim,per_concept_limit=None,task_ids=None))
    assert len(ids)==lim, (ds,len(ids))
    allk=[]
    for i in range(k):
        sh=ids[i::k]; allk+=sh
        open(f"{J}/{tag}_shard{i}.args","w").write(" ".join(f"--task-id {t}" for t in sh))
        print(tag,"shard",i,len(sh))
    assert sorted(allk)==sorted(ids) and len(set(allk))==lim
    print(tag,"disjoint+complete OK")
