#!/usr/bin/env bash
set -euo pipefail

PYTHON_SCRIPT="simulation.py"

NODES=1000
BATCH_SIZE=64
SIMULATIONS=10

START_BP=5
END_BP=25
STEP_BP=5

START_BUCKETS=10
END_BUCKETS=200
STEP_BUCKETS=5

JOBS="$(nproc)"


rm results.jsonl

for bp in $(seq "$START_BP" "$STEP_BP" "$END_BP"); do
    for buckets in $(seq "$START_BUCKETS" "$STEP_BUCKETS" "$END_BUCKETS"); do
        echo "Running bastard_percentage=${bp} buckets=${buckets} with ${JOBS} parallel simulations"

        for ((i=1; i<=JOBS; i++)); do
            python3 "$PYTHON_SCRIPT" \
                --bastard_percentage "$bp" \
                --id "$i"\
                -n "$NODES" \
                -b "$buckets" \
                --batch_size "$BATCH_SIZE" \
                -s "$SIMULATIONS" &

        done

        wait
    done
done