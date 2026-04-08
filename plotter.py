import json
import statistics
from collections import defaultdict

import matplotlib.pyplot as plt


def load_results_jsonl(path: str) -> list[dict]:
    results = []

    with open(path, "r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON on line {line_number}: {e}") from e

            if not isinstance(obj, dict):
                raise ValueError(
                    f"Expected JSON object on line {line_number}, got {type(obj).__name__}"
                )

            results.append(obj)

    return results


def aggregate(results: list[dict]) -> dict[int, list[dict]]:
    grouped = defaultdict(lambda: defaultdict(lambda: {
        "success_values": [],
        "failed_values": [],
        "failed_batches_percent_values": [],
        "simulations_count": 0,
    }))

    for sim in results:
        bp = sim["bastard_percentage"]
        buckets = sim.get("buckets")
        batch_size = sim.get("batch_size")
        success_shreds = sim.get("success_shreds", [])
        failed_shreds = sim.get("failed_shreds", [])

        if not isinstance(batch_size, int) or batch_size <= 0:
            raise ValueError(f"batch_size must be a positive int for bastard_percentage={bp}")

        if not isinstance(buckets, int) or buckets <= 0:
            raise ValueError(f"buckets must be a positive int for bastard_percentage={bp}")

        failed_batches_count = sum(1 for x in failed_shreds if x > (batch_size / 2))
        failed_batches_percent = (failed_batches_count / buckets) * 100

        g = grouped[bp][buckets]
        g["success_values"].extend(success_shreds)
        g["failed_values"].extend(failed_shreds)
        g["failed_batches_percent_values"].append(failed_batches_percent)
        g["simulations_count"] += 1

    result = {}
    for bp in sorted(grouped.keys()):
        rows = []
        for buckets in sorted(grouped[bp].keys()):
            data = grouped[bp][buckets]
            sv = data["success_values"]
            fv = data["failed_values"]
            fbpv = data["failed_batches_percent_values"]
            rows.append({
                "buckets": buckets,
                "success_shreds_avg": statistics.mean(sv) if sv else 0,
                "success_shreds_median": statistics.median(sv) if sv else 0,
                "failed_shreds_avg": statistics.mean(fv) if fv else 0,
                "failed_shreds_median": statistics.median(fv) if fv else 0,
                "failed_batches_percent_avg": statistics.mean(fbpv) if fbpv else 0,
                "simulations_count": data["simulations_count"],
            })
        result[bp] = rows

    return result


def print_table(aggregated: dict[int, list[dict]]) -> None:
    for bp, rows in aggregated.items():
        print(f"\n--- bastard_percentage={bp}% ---")
        for row in rows:
            print(
                f"  buckets={row['buckets']:>3} | "
                f"success_avg={row['success_shreds_avg']:.2f} | "
                f"success_median={row['success_shreds_median']:.2f} | "
                f"failed_avg={row['failed_shreds_avg']:.2f} | "
                f"failed_median={row['failed_shreds_median']:.2f} | "
                f"failed_batches_avg_percent={row['failed_batches_percent_avg']:.2f}% | "
                f"simulations={row['simulations_count']}"
            )


def plot_for_bp(bp: int, rows: list[dict]) -> None:
    x = [row["buckets"] for row in rows]

    success_avg = [row["success_shreds_avg"] for row in rows]
    success_median = [row["success_shreds_median"] for row in rows]
    failed_avg = [row["failed_shreds_avg"] for row in rows]
    failed_median = [row["failed_shreds_median"] for row in rows]
    failed_batches_percent_avg = [row["failed_batches_percent_avg"] for row in rows]

    fig, axes = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    axes[0].plot(x, success_avg, marker="o", label="success_shreds_avg")
    axes[0].plot(x, success_median, marker="o", label="success_shreds_median")
    axes[0].plot(x, failed_avg, marker="o", label="failed_shreds_avg")
    axes[0].plot(x, failed_median, marker="o", label="failed_shreds_median")
    axes[0].set_ylabel("shreds")
    axes[0].set_title(f"Simulation statistics — bastard_percentage={bp}%")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()

    axes[1].plot(x, failed_batches_percent_avg, marker="o", label="failed_batches_avg_percent")
    axes[1].set_xlabel("buckets")
    axes[1].set_ylabel("failed batches, %")
    axes[1].set_title(f"Average failed batches percentage — bastard_percentage={bp}%")
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()

    plt.tight_layout()
    filename = f"plot_bp_{bp}.png"
    plt.savefig(filename, dpi=150)
    plt.close(fig)
    print(f"Saved {filename}")


def main() -> None:
    results = load_results_jsonl("results.jsonl")
    aggregated = aggregate(results)

    print_table(aggregated)

    for bp, rows in aggregated.items():
        plot_for_bp(bp, rows)


if __name__ == "__main__":
    main()
