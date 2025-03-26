from adders.axppabk import AxppaBk
from simulation.runner import generate_test_vectors, run_simulation
from simulation.visualization import plot_metric_vs_k


def main():
    BIT_WIDTH = 16
    TEST_VECTORS = 1000
    APPROX_BITS_RANGE = list(range(0, BIT_WIDTH + 1))

    print("[*] Generating test vectors...")
    test_data = generate_test_vectors(TEST_VECTORS, BIT_WIDTH)

    print("[*] Running AxPPA-BK simulation...")
    results = run_simulation(
        adder_factory=AxppaBk,
        name="AxPPA-BK",
        bit_width=BIT_WIDTH,
        approx_bits_list=APPROX_BITS_RANGE,
        test_vectors=test_data
    )

    print("[*] Plotting results...")
    plot_metric_vs_k(results, metric="mae", title="AxPPA-BK: MAE vs k", ylabel="Mean Absolute Error")
    plot_metric_vs_k(results, metric="mred", title="AxPPA-BK: MRED vs k", ylabel="Mean Relative Error Distance")


if __name__ == "__main__":
    main()
