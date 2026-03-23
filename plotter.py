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


def aggregate_by_bastard_percentage(results: list[dict]) -> list[dict]:
    grouped = defaultdict(lambda: {
        "success_values": [],
        "failed_values": [],
        "failed_batches_percent_values": [],
        "simulations_count": 0,
        "batch_sizes": [],
        "empty_buckets": [],
        "algs": set(),
    })

    for sim in results:
        bp = sim["bastard_percentage"]
        success_shreds = sim.get("success_shreds", [])
        failed_shreds = sim.get("failed_shreds", [])
        batch_size = sim.get("batch_size")
        buckets = sim.get("buckets")

        if not isinstance(success_shreds, list):
            raise ValueError(
                f"success_shreds must be a list for bastard_percentage={bp}"
            )

        if not isinstance(failed_shreds, list):
            raise ValueError(
                f"failed_shreds must be a list for bastard_percentage={bp}"
            )

        if not isinstance(batch_size, int) or batch_size <= 0:
            raise ValueError(
                f"batch_size must be a positive int for bastard_percentage={bp}"
            )

        if not isinstance(buckets, int) or buckets <= 0:
            raise ValueError(
                f"buckets must be a positive int for bastard_percentage={bp}"
            )

        # A batch is failed_shreds > batch_size / 2
        failed_batches_count = sum(1 for x in failed_shreds if x > batch_size / 2)
        failed_batches_percent = (failed_batches_count / buckets) * 100

        grouped[bp]["success_values"].extend(success_shreds)
        grouped[bp]["failed_values"].extend(failed_shreds)
        grouped[bp]["failed_batches_percent_values"].append(failed_batches_percent)
        grouped[bp]["simulations_count"] += 1

        if "batch_size" in sim:
            grouped[bp]["batch_sizes"].append(sim["batch_size"])

        if "empty_buckets" in sim:
            grouped[bp]["empty_buckets"].append(sim["empty_buckets"])

        grouped[bp]["algs"].add(sim.get("alg", "unknown"))

    aggregated = []

    for bp, data in grouped.items():
        success_values = data["success_values"]
        failed_values = data["failed_values"]
        failed_batches_percent_values = data["failed_batches_percent_values"]

        aggregated.append({
            "bastard_percentage": bp,
            "success_shreds_avg": statistics.mean(success_values) if success_values else 0,
            "success_shreds_median": statistics.median(success_values) if success_values else 0,
            "failed_shreds_avg": statistics.mean(failed_values) if failed_values else 0,
            "failed_shreds_median": statistics.median(failed_values) if failed_values else 0,
            "failed_batches_percent_avg": (
                statistics.mean(failed_batches_percent_values)
                if failed_batches_percent_values else 0
            ),
            "simulations_count": data["simulations_count"],
            "batch_size_avg": statistics.mean(data["batch_sizes"]) if data["batch_sizes"] else 0,
            "empty_buckets_avg": statistics.mean(data["empty_buckets"]) if data["empty_buckets"] else 0,
            "algs": sorted(data["algs"]),
        })

    aggregated.sort(key=lambda x: x["bastard_percentage"])
    return aggregated


def print_table(aggregated: list[dict]) -> None:
    for row in aggregated:
        print(
            f"bastard_percentage={row['bastard_percentage']:>3} | "
            f"success_avg={row['success_shreds_avg']:.2f} | "
            f"success_median={row['success_shreds_median']:.2f} | "
            f"failed_avg={row['failed_shreds_avg']:.2f} | "
            f"failed_median={row['failed_shreds_median']:.2f} | "
            f"failed_batches_avg_percent={row['failed_batches_percent_avg']:.2f}% | "
            f"simulations={row['simulations_count']} | "
            f"algs={','.join(row['algs'])}"
        )


def plot_stats(aggregated: list[dict]) -> None:
    x = [item["bastard_percentage"] for item in aggregated]

    success_avg = [item["success_shreds_avg"] for item in aggregated]
    success_median = [item["success_shreds_median"] for item in aggregated]
    failed_avg = [item["failed_shreds_avg"] for item in aggregated]
    failed_median = [item["failed_shreds_median"] for item in aggregated]
    failed_batches_percent_avg = [
        item["failed_batches_percent_avg"] for item in aggregated
    ]

    fig, axes = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    axes[0].plot(x, success_avg, marker="o", label="success_shreds_avg")
    axes[0].plot(x, success_median, marker="o", label="success_shreds_median")
    axes[0].plot(x, failed_avg, marker="o", label="failed_shreds_avg")
    axes[0].plot(x, failed_median, marker="o", label="failed_shreds_median")
    axes[0].set_ylabel("value")
    axes[0].set_title("Simulation statistics grouped by bastard_percentage")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()

    axes[1].plot(
        x,
        failed_batches_percent_avg,
        marker="o",
        label="failed_batches_avg_percent"
    )
    axes[1].set_xlabel("bastard_percentage")
    axes[1].set_ylabel("failed_batches, %")
    axes[1].set_title("Average failed batches percentage by bastard_percentage")
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()

    plt.tight_layout()
    plt.show()


def main() -> None:
    results = load_results_jsonl("results.jsonl")
    aggregated = aggregate_by_bastard_percentage(results)

    print_table(aggregated)
    plot_stats(aggregated)


if __name__ == "__main__":
    main()