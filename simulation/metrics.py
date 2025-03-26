from typing import List


def compute_mae(errors: List[int]) -> float:
    """Compute Mean Absolute Error (MAE)."""
    if not errors:
        return 0.0
    return sum(errors) / len(errors)


def compute_mred(errors: List[int], exact_values: List[int]) -> float:
    """Compute Mean Relative Error Distance (MRED)."""
    if not errors or not exact_values:
        return 0.0

    total = 0.0
    count = 0
    for e, x in zip(errors, exact_values):
        if x != 0:
            total += e / x
            count += 1

    return (total / count) if count > 0 else 0.0