#!/bin/bash
# usage: with_key.sh VARNAME cmd...   — sets OPENROUTER_API_KEY from jagEval's stored env var.
# conda 26.7.1 does not apply jagEval env_vars, and the shell can carry stale copies; read the state file.
V="$1"; shift
export OPENROUTER_API_KEY="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["env_vars"][sys.argv[2]])' /Users/claasbeger/miniconda3/envs/jagEval/conda-meta/state "$V")"
[ ${#OPENROUTER_API_KEY} -gt 20 ] || { echo "[with_key] $V not found" >&2; exit 3; }
echo "[with_key] OPENROUTER_API_KEY <- $V"
exec "$@"
