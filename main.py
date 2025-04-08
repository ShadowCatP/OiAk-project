import random
import matplotlib.pyplot as plt

from adders.utils import int_to_bin_list, bin_list_to_int
from adders.approxAdders import axppa_bk, axppa_ks, axppa_sk, axppa_lf
from simulation.metrics import compute_error_metrics


def compare_adders(W=16, num_tests=10000, K_values=None):
    """
    Compare the 4 approximate PPA adders for multiple K values.
    We'll measure average MRED and maximum WCE over random tests.
    """
    if K_values is None:
        K_values = [0, 4, 8, 12, 16]

    # We will store results in the form:
    # results[adder_name][K] = (avg_MRED, max_WCE)
    results = {
        "AxPPA-BK": {},
        "AxPPA-KS": {},
        "AxPPA-SK": {},
        "AxPPA-LF": {}
    }

    for K in K_values:
        sum_RED_BK, sum_RED_KS = 0, 0
        sum_RED_SK, sum_RED_LF = 0, 0
        max_WCE_BK, max_WCE_KS = 0, 0
        max_WCE_SK, max_WCE_LF = 0, 0

        for _ in range(num_tests):
            a = random.randint(0, (1 << W) - 1)
            b = random.randint(0, (1 << W) - 1)
            true_val = a + b

            a_bits = int_to_bin_list(a, W)
            b_bits = int_to_bin_list(b, W)

            # BK
            sum_bk_bits = axppa_bk(a_bits, b_bits, K)
            sum_bk_val = bin_list_to_int(sum_bk_bits)
            err_bk, red_bk = compute_error_metrics(true_val, sum_bk_val)
            sum_RED_BK += red_bk
            if err_bk > max_WCE_BK:
                max_WCE_BK = err_bk

            # KS
            sum_ks_bits = axppa_ks(a_bits, b_bits, K)
            sum_ks_val = bin_list_to_int(sum_ks_bits)
            err_ks, red_ks = compute_error_metrics(true_val, sum_ks_val)
            sum_RED_KS += red_ks
            if err_ks > max_WCE_KS:
                max_WCE_KS = err_ks

            # SK
            sum_sk_bits = axppa_sk(a_bits, b_bits, K)
            sum_sk_val = bin_list_to_int(sum_sk_bits)
            err_sk, red_sk = compute_error_metrics(true_val, sum_sk_val)
            sum_RED_SK += red_sk
            if err_sk > max_WCE_SK:
                max_WCE_SK = err_sk

            # LF
            sum_lf_bits = axppa_lf(a_bits, b_bits, K)
            sum_lf_val = bin_list_to_int(sum_lf_bits)
            err_lf, red_lf = compute_error_metrics(true_val, sum_lf_val)
            sum_RED_LF += red_lf
            if err_lf > max_WCE_LF:
                max_WCE_LF = err_lf

        # Average MRED for each architecture
        avg_MRED_BK = sum_RED_BK / num_tests
        avg_MRED_KS = sum_RED_KS / num_tests
        avg_MRED_SK = sum_RED_SK / num_tests
        avg_MRED_LF = sum_RED_LF / num_tests

        # Store results
        results["AxPPA-BK"][K] = (avg_MRED_BK, max_WCE_BK)
        results["AxPPA-KS"][K] = (avg_MRED_KS, max_WCE_KS)
        results["AxPPA-SK"][K] = (avg_MRED_SK, max_WCE_SK)
        results["AxPPA-LF"][K] = (avg_MRED_LF, max_WCE_LF)

    return results


def plot_results(results):
    """
    Generate 2 plots with matplotlib:
    1) MRED vs K
    2) WCE vs K
    """
    adders = list(results.keys())

    # 1) Plot MRED vs K
    plt.figure()
    for adder_name in adders:
        K_list = sorted(results[adder_name].keys())
        MRED_list = [results[adder_name][K][0] for K in K_list]
        plt.plot(K_list, MRED_list, marker='o', label=adder_name)
    plt.xlabel("Number of Approximate LSB Bits (K)")
    plt.ylabel("Average MRED")
    plt.title("Approximate PPAs: MRED vs. K")
    plt.grid(True)
    plt.legend()

    # 2) Plot WCE vs K
    plt.figure()
    for adder_name in adders:
        K_list = sorted(results[adder_name].keys())
        WCE_list = [results[adder_name][K][1] for K in K_list]
        plt.plot(K_list, WCE_list, marker='s', label=adder_name)
    plt.xlabel("Number of Approximate LSB Bits (K)")
    plt.ylabel("Worst-Case Error (WCE)")
    plt.title("Approximate PPAs: WCE vs. K")
    plt.grid(True)
    plt.legend()

    plt.show()


if __name__ == "__main__":
    # Example usage
    W = 16
    num_tests = 20000
    K_values = [0, 4, 8, 12, 16]

    results = compare_adders(W=W, num_tests=num_tests, K_values=K_values)
    plot_results(results)
