def int_to_bin_list(x, W):
    """
    Convert integer x into a list of W bits (LSB first).
    Example: int_to_bin_list(6,4) -> [0,1,1,0] for 6 (0b0110).
    """
    return [(x >> i) & 1 for i in range(W)]


def bin_list_to_int(bits):
    """
    Convert a list of bits (LSB first) back into an integer.
    """
    val = 0
    for i, b in enumerate(bits):
        val |= (b << i)
    return val

def prefix_operator(g_left, p_left, g_right, p_right):
    """
    Standard prefix operator:
      G_out = g_right OR (p_right AND g_left)
      P_out = p_right AND p_left
    """
    g_out = g_right | (p_right & g_left)
    p_out = p_right & p_left
    return g_out, p_out
