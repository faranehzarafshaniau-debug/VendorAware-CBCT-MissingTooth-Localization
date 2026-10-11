#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH="/mnt/paper2_extra/paper2/exp_c_runtime_v1/monai160:/home/ubuntu/PAPER2_REVISION_R1/source/real_model_src${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONUNBUFFERED=1

PY="/home/ubuntu/PAPER2_REVISION_R1/.venv/bin/python"
PROJECT="/home/ubuntu/PAPER2_REVISION_R1/revision_exec/exp_a_matched_v1"
EXPC="/home/ubuntu/PAPER2_REVISION_R1/revision_exec/exp_c_monai_retinanet_v1"
OUTROOT="/mnt/paper2_extra/paper2/exp_c_outputs_v1"
TRAINER="/home/ubuntu/PAPER2_REVISION_R1/revision_exec/exp_c_monai_retinanet_v1/scripts/train_monai_retinanet_exp_c_v1.py"
ANCHOR="/home/ubuntu/PAPER2_REVISION_R1/revision_exec/exp_c_monai_retinanet_v1/reports/exp_c_anchor_contract_v1.json"

echo "============================================================"
echo " PAPER2 EXP-C FORMAL 25-RUN MONAI RETINANET"
echo "============================================================"
date -u

echo "formal_runs_expected=25"
echo "outer_test_accessed=false"
echo "calibration_accessed=false"

for repeat in 1 2 3 4 5; do
  for fold in 0 1 2 3 4; do

    CFG="$EXPC/configs/formal/r${repeat}/fold${fold}.json"
    OUT="$OUTROOT/formal/r${repeat}/fold${fold}"

    mkdir -p "$OUT"

    REPORT="$OUT/exp_c_formal_report.json"

    if [ -f "$REPORT" ]; then
      if "$PY" - "$REPORT" <<'PY2'
import json,sys
j=json.load(open(sys.argv[1]))
assert j["status"]=="PASS"
assert j["calibration_accessed"] is False
assert j["outer_test_accessed"] is False
PY2
      then
        echo "existing_valid_run=true repeat=$repeat fold=$fold"
        continue
      fi
    fi

    echo
    echo "------------------------------------------------------------"
    echo " EXP-C repeat=$repeat fold=$fold"
    echo "------------------------------------------------------------"
    date -u

    "$PY" "$TRAINER"       --project-root "$PROJECT"       --config "$CFG"       --anchor-contract "$ANCHOR"       --output-dir "$OUT"       2>&1 | tee -a "$OUT/run.log"

    echo "run_complete=true repeat=$repeat fold=$fold"
    date -u
  done
done

touch "$OUTROOT/formal/EXP_C_ALL_25_RUNS_COMPLETE"

echo
echo "EXP_C_ALL_25_RUNS_COMPLETE=true"
date -u
