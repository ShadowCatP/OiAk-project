import matplotlib.pyplot as plt
from typing import Dict, List


def plot_metric_vs_k(
        result_dict: Dict[str, List[dict]],
        metric: str = "mae",
        title: str = "Error Metric vs Approximated Bits",
        ylabel: str = "MAE"
):
    """
    Plot MAE or MRED versus number of approximated bits (k)
    for different adder types.
    """
    plt.figure(figsize=(10, 6))

    for adder_name, results in result_dict.items():
        ks = [entry["k"] for entry in results]
        values = [entry[metric] for entry in results]
        plt.plot(ks, values, marker='o', label=adder_name)

    plt.title(title)
    plt.xlabel("Number of Approximated Bits (k)")
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

