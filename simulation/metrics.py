# metrics.py

def compute_error_metrics(true_val, approx_val):
    """
    Return the absolute error and a single-sample relative error (RED).
    RED = |true - approx| / |true| if true != 0, else special cases.
    """
    error = abs(true_val - approx_val)
    if true_val != 0:
        red = error / abs(true_val)
    else:
        # If the true result is zero
        red = 0 if approx_val == 0 else 1
    return error, red
