#!/usr/bin/env bash
set -euo pipefail

PYTHON_SCRIPT="simulation.py"

NODES=128
BUCKETS=8
BATCH_SIZE=64
SIMULATIONS=1

START_BP=0
END_BP=95
STEP_BP=5
JOBS="$(nproc)"

for bp in $(seq "$START_BP" "$STEP_BP" "$END_BP"); do
    echo "Running bastard_percentage=${bp} with ${JOBS} parallel simulations"

    for ((i=1; i<=JOBS; i++)); do
        python3 "$PYTHON_SCRIPT" \
            --bastard_percentage "$bp" \
            --id "$i"\
            -n "$NODES" \
            -b "$BUCKETS" \
            --batch_size "$BATCH_SIZE" \
            -s "$SIMULATIONS" &

    done

    wait
done