import random
import math
import matplotlib.pyplot as plt

from adders.utils import int_to_bin_list, bin_list_to_int
from adders.approxAdders import axppa_bk, axppa_ks, axppa_sk, axppa_lf
from simulation.metrics import compute_error_metrics

def compare_adders(W=16, num_tests=5000, K_values=None):
    """
    Compare 4 approximate PPA adders (BK, KS, SK, LF) over a range of K values.
    Returns a dict:
      results[adder_name][K] = {
         "mred": <avg MRED>,
         "wce":  <max WCE>
      }
    """
    if K_values is None:
        K_values = [0, 4, 8, 12, 16]

    results = {
        "AxPPA-BK":  {},
        "AxPPA-KS":  {},
        "AxPPA-SK":  {},
        "AxPPA-LF":  {}
    }

    for K in K_values:
        sum_RED_BK, sum_RED_KS, sum_RED_SK, sum_RED_LF = 0,0,0,0
        max_WCE_BK, max_WCE_KS, max_WCE_SK, max_WCE_LF = 0,0,0,0

        for _ in range(num_tests):
            a = random.randint(0, (1 << W) - 1)
            b = random.randint(0, (1 << W) - 1)
            true_val = a + b

            a_bits = int_to_bin_list(a, W)
            b_bits = int_to_bin_list(b, W)

            # BK
            sum_bk_bits = axppa_bk(a_bits, b_bits, K)
            sum_bk_val  = bin_list_to_int(sum_bk_bits)
            err_bk, red_bk = compute_error_metrics(true_val, sum_bk_val)
            sum_RED_BK += red_bk
            if err_bk > max_WCE_BK:
                max_WCE_BK = err_bk

            # KS
            sum_ks_bits = axppa_ks(a_bits, b_bits, K)
            sum_ks_val  = bin_list_to_int(sum_ks_bits)
            err_ks, red_ks = compute_error_metrics(true_val, sum_ks_val)
            sum_RED_KS += red_ks
            if err_ks > max_WCE_KS:
                max_WCE_KS = err_ks

            # SK
            sum_sk_bits = axppa_sk(a_bits, b_bits, K)
            sum_sk_val  = bin_list_to_int(sum_sk_bits)
            err_sk, red_sk = compute_error_metrics(true_val, sum_sk_val)
            sum_RED_SK += red_sk
            if err_sk > max_WCE_SK:
                max_WCE_SK = err_sk

            # LF
            sum_lf_bits = axppa_lf(a_bits, b_bits, K)
            sum_lf_val  = bin_list_to_int(sum_lf_bits)
            err_lf, red_lf = compute_error_metrics(true_val, sum_lf_val)
            sum_RED_LF += red_lf
            if err_lf > max_WCE_LF:
                max_WCE_LF = err_lf

        # Average MRED
        avg_MRED_BK = sum_RED_BK / num_tests
        avg_MRED_KS = sum_RED_KS / num_tests
        avg_MRED_SK = sum_RED_SK / num_tests
        avg_MRED_LF = sum_RED_LF / num_tests

        results["AxPPA-BK"][K] = {"mred": avg_MRED_BK, "wce": max_WCE_BK}
        results["AxPPA-KS"][K] = {"mred": avg_MRED_KS, "wce": max_WCE_KS}
        results["AxPPA-SK"][K] = {"mred": avg_MRED_SK, "wce": max_WCE_SK}
        results["AxPPA-LF"][K] = {"mred": avg_MRED_LF, "wce": max_WCE_LF}

    return results

def estimate_gate_count(adder_name, W, K):
    """
    Return a 'theoretical' gate count for the approximate adder with bit-width W
    and K approximate LSB bits.
    This is TOTALLY for demonstration. Use your real formulas or data.
    """
    # Let's define a hypothetical formula for each exact adder's gate count:
    #   BK: ~2*W - 2 for the prefix logic
    #   KS: ~4*W for the prefix logic
    #   SK: ~2*W (similar to BK)
    #   LF: ~3*W
    # Then we reduce proportionally to (W - K) for the "exact" portion and
    # say we do only half as many gates in the approximate portion. TOTALLY FAKE.

    if adder_name == "AxPPA-BK":
        base_exact = 2*W  # say 2*W
    elif adder_name == "AxPPA-KS":
        base_exact = 4*W
    elif adder_name == "AxPPA-SK":
        base_exact = 2*W
    else:  # "AxPPA-LF":
        base_exact = 3*W

    # Suppose the exact part is (W-K) bits → scaled proportion of base
    # The approximate part is K bits → let's say half cost
    exact_gates = base_exact * (W - K) / W
    approx_gates = (base_exact * K / W) * 0.5  # half

    total = exact_gates + approx_gates
    return total

def estimate_energy(adder_name, W, K):
    """
    Return a 'theoretical' energy measure for the approximate adder.
    Could scale with gate_count and some factor for logic depth, etc.
    We'll do something simplistic: Energy ~ gate_count * log2(W - K + 1).
    """

    gcount = estimate_gate_count(adder_name, W, K)
    # Let's do a silly formula: energy = gcount * log2( (W-K) + 1 )
    # so the fewer exact bits, the fewer logic stages in the prefix → less energy
    val = gcount * math.log2((W - K) + 1)
    return val

def populate_synthesis_data(results, W):
    """
    Given the 'results' from compare_adders, fill in
    "gate_count" and "energy" for each adder and K.
    So results[adder_name][K] = {
       "mred": ...
       "wce": ...
       "gates": <something>
       "energy": <something>
    }
    """
    for adder_name in results.keys():
        for K in results[adder_name].keys():
            gcount = estimate_gate_count(adder_name, W, K)
            eng    = estimate_energy(adder_name, W, K)
            results[adder_name][K]["gates"]  = gcount
            results[adder_name][K]["energy"] = eng

def plot_mred_wce(results):
    """
    The usual MRED vs K and WCE vs K combined for all adders.
    """
    adder_names = list(results.keys())

    # MRED vs K
    plt.figure()
    for name in adder_names:
        K_list = sorted(results[name].keys())
        MRED_list = [results[name][k]["mred"] for k in K_list]
        plt.plot(K_list, MRED_list, marker='o', label=name)
    plt.xlabel("K (Approx bits)")
    plt.ylabel("Average MRED")
    plt.title("All Adders: MRED vs. K")
    plt.legend()
    plt.grid(True)

    # WCE vs K
    plt.figure()
    for name in adder_names:
        K_list = sorted(results[name].keys())
        WCE_list = [results[name][k]["wce"] for k in K_list]
        plt.plot(K_list, WCE_list, marker='s', label=name)
    plt.xlabel("K (Approx bits)")
    plt.ylabel("Worst Case Error")
    plt.title("All Adders: WCE vs. K")
    plt.legend()
    plt.grid(True)

    plt.show()


def plot_gate_energy(results):
    """
    Plot gate count vs K and energy vs K, for all adders on each plot.
    Also show "savings" if desired.
    """
    adder_names = list(results.keys())

    # 1) Gate count
    plt.figure()
    for name in adder_names:
        K_list = sorted(results[name].keys())
        gate_list = [results[name][k]["gates"] for k in K_list]
        plt.plot(K_list, gate_list, marker='o', label=name)
    plt.xlabel("K (Approx bits)")
    plt.ylabel("Gate Count (theoretical)")
    plt.title("All Adders: Gate Count vs. K")
    plt.legend()
    plt.grid(True)

    # 2) Energy
    plt.figure()
    for name in adder_names:
        K_list = sorted(results[name].keys())
        energy_list = [results[name][k]["energy"] for k in K_list]
        plt.plot(K_list, energy_list, marker='o', label=name)
    plt.xlabel("K (Approx bits)")
    plt.ylabel("Energy (theoretical units)")
    plt.title("All Adders: Energy vs. K")
    plt.legend()
    plt.grid(True)

    plt.show()


def plot_savings(results):
    """
    Optionally, produce "savings" charts relative to the EXACT version (K=0).
    For each adder, we compute savings = (1 - approximate/exact).
    We'll combine all adders on one plot for gates, another for energy.
    """
    adder_names = list(results.keys())

    # We'll build a dictionary: savings[adder_name][K] = (gate_saving, energy_saving)
    # But we only plot K>0 because K=0 is the baseline with 0% saving
    savings_dict = {}
    for name in adder_names:
        baseline_gates  = results[name][0]["gates"]  # exact version
        baseline_energy = results[name][0]["energy"]
        local = {}
        for K in sorted(results[name].keys()):
            g = results[name][K]["gates"]
            e = results[name][K]["energy"]
            gate_saving   = 1.0 - (g / baseline_gates)
            energy_saving = 1.0 - (e / baseline_energy)
            local[K] = (gate_saving, energy_saving)
        savings_dict[name] = local

    # 1) Gate savings
    plt.figure()
    for name in adder_names:
        K_list = sorted(k for k in savings_dict[name].keys())
        # convert from fraction to percentage if you like
        gate_save_list = [savings_dict[name][k][0]*100.0 for k in K_list]
        plt.plot(K_list, gate_save_list, marker='o', label=name)
    plt.xlabel("K (Approx bits)")
    plt.ylabel("Gate Savings (%) vs. Exact (K=0)")
    plt.title("Gate Savings vs. K (All Adders)")
    plt.legend()
    plt.grid(True)

    # 2) Energy savings
    plt.figure()
    for name in adder_names:
        K_list = sorted(k for k in savings_dict[name].keys())
        eng_save_list = [savings_dict[name][k][1]*100.0 for k in K_list]
        plt.plot(K_list, eng_save_list, marker='s', label=name)
    plt.xlabel("K (Approx bits)")
    plt.ylabel("Energy Savings (%) vs. Exact (K=0)")
    plt.title("Energy Savings vs. K (All Adders)")
    plt.legend()
    plt.grid(True)

    plt.show()

if __name__ == "__main__":
    W = 16
    num_tests = 2000
    K_values = [0, 4, 8, 12, 16]

    # Step A: do the typical MRED/WCE computations
    results = compare_adders(W, num_tests, K_values)

    # Step B: for each adder & K, estimate gate count + energy
    populate_synthesis_data(results, W)

    # Step C: Plot the error metrics
    plot_mred_wce(results)

    # Step D: Plot the gate count & energy
    plot_gate_energy(results)

    # Step E: Plot the "savings" vs. the EXACT design (K=0)
    plot_savings(results)
