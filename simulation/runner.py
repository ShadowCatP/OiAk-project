import random
from typing import Callable, List, Dict, Any
from adders.base_adder import from_bits
from simulation.metrics import compute_mae, compute_mred


def generate_test_vectors(num_vectors: int, bit_width: int) -> List[tuple[int, int]]:
    """Generate pairs of random integers for testing."""
    max_val = 2 ** bit_width - 1
    return [(random.randint(0, max_val), random.randint(0, max_val)) for _ in range(num_vectors)]


def run_simulation(
        adder_factory: Callable[[int, int], Any],
        name: str,
        bit_width: int,
        approx_bits_list: List[int],
        test_vectors: List[tuple[int, int]]
) -> Dict[str, List[Dict[str, Any]]]:
    """Run simulation across various approximation levels and collect results."""
    results = []

    for k in approx_bits_list:
        adder = adder_factory(bit_width, k)
        errors = []
        accurate_results = []

        for a, b in test_vectors:
            approx_result = adder.add(a, b)
            exact_result = (a + b) & ((1 << bit_width) - 1)  # Clip to bit width
            error = abs(approx_result - exact_result)
            errors.append(error)
            accurate_results.append(exact_result)

        mae = compute_mae(errors)
        mred = compute_mred(errors, accurate_results)

        results.append({
            "adder": name,
            "k": k,
            "mae": mae,
            "mred": mred,
            "error_list": errors,
        })

    return {name: results}