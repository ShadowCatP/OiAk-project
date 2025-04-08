import math
from adders.utils import (
    prefix_operator,  # The EXACT merge: G = gR OR (pR & gL), P = pR & pL
    int_to_bin_list,
    bin_list_to_int
)

def approx_prefix_operator(g_left, p_left, g_right, p_right):
    """
    Approximate merge (AxPO) for the LSB region, as in eqn(7)-(8) in the paper:
      G_out ≈ g_right
      P_out ≈ p_right
    This essentially ignores the left side of the merge,
    so partial carries do not propagate from that side.
    """
    g_out = g_right
    p_out = p_right
    return g_out, p_out


# ---------------------------------------------------------------------------
#   1) Approximate Brent–Kung
# ---------------------------------------------------------------------------
def approx_bk_adder(a_bits, b_bits, K):
    """
    Partitions the bits [0..K-1] as approximate region,
    and bits [K..W-1] as exact region. We'll run a standard Brent–Kung
    prefix tree, but in the "forward pass" for i < K, we apply approximate
    merges rather than exact merges.

    For simplicity, we do a uniform approach:
      - Stage 0: local g/p
      - Forward pass merges: if the 'right index i' is < K, do approx operator,
        else do exact operator.
      - Then compute final c[] and sum bits.

    This is a demonstration; you can refine the partition logic further if desired.
    """
    W = len(a_bits)
    # Step 1: local generate/propagate
    g = [a_bits[i] & b_bits[i] for i in range(W)]
    p = [a_bits[i] ^ b_bits[i] for i in range(W)]

    # We'll store partial results in a 2D array across log2(W) stages:
    log_w = int(math.ceil(math.log2(W)))
    G = [[0]*W for _ in range(log_w + 1)]
    P = [[0]*W for _ in range(log_w + 1)]

    # Initialize stage 0
    for i in range(W):
        G[0][i] = g[i]
        P[0][i] = p[i]

    # Forward pass merges
    dist = 1
    stage = 1
    while dist < W:
        for i in range(W):
            j = i - dist
            if j >= 0:
                # If the "right" index i is in the approximate region (< K),
                # use approximate prefix operator
                if i < K:
                    g_out, p_out = approx_prefix_operator(
                        G[stage-1][j], P[stage-1][j],
                        G[stage-1][i], P[stage-1][i]
                    )
                else:
                    # exact operator
                    g_out, p_out = prefix_operator(
                        G[stage-1][j], P[stage-1][j],
                        G[stage-1][i], P[stage-1][i]
                    )
                G[stage][i] = g_out
                P[stage][i] = p_out
            else:
                # no merge
                G[stage][i] = G[stage-1][i]
                P[stage][i] = P[stage-1][i]
        dist <<= 1
        stage += 1

    # Step 2: c[i+1] = G[last_stage][i], then sum[i] = p[i] ^ c[i]
    c = [0]*(W+1)
    for i in range(W):
        c[i+1] = G[log_w-1][i]
    sum_bits = [(p[i] ^ c[i]) for i in range(W)]
    return sum_bits


# ---------------------------------------------------------------------------
#   2) Approximate Kogge–Stone
# ---------------------------------------------------------------------------
def approx_ks_adder(a_bits, b_bits, K):
    """
    Kogge–Stone: log2(W) stages, distance=2^(stage-1) merges.
    We approximate merges if 'i' is in LSB region, else exact merges.
    """
    W = len(a_bits)
    g = [a_bits[i] & b_bits[i] for i in range(W)]
    p = [a_bits[i] ^ b_bits[i] for i in range(W)]
    log_w = int(math.ceil(math.log2(W)))

    G_stages = [g[:]]  # stage 0
    P_stages = [p[:]]

    for stage_i in range(1, log_w+1):
        dist = 1 << (stage_i - 1)
        G_prev = G_stages[stage_i - 1]
        P_prev = P_stages[stage_i - 1]
        G_curr = [0]*W
        P_curr = [0]*W
        for i in range(W):
            j = i - dist
            if j >= 0:
                if i < K:
                    # approximate merge
                    g_out, p_out = approx_prefix_operator(
                        G_prev[j], P_prev[j],
                        G_prev[i], P_prev[i]
                    )
                else:
                    # exact merge
                    g_out, p_out = prefix_operator(
                        G_prev[j], P_prev[j],
                        G_prev[i], P_prev[i]
                    )
                G_curr[i] = g_out
                P_curr[i] = p_out
            else:
                G_curr[i] = G_prev[i]
                P_curr[i] = P_prev[i]
        G_stages.append(G_curr)
        P_stages.append(P_curr)

    # final carry c[i+1] = G_stages[log_w][i]
    c = [0]*(W+1)
    for i in range(W):
        c[i+1] = G_stages[log_w][i]

    sum_bits = [(p[i] ^ c[i]) for i in range(W)]
    return sum_bits


# ---------------------------------------------------------------------------
#   3) Approximate Sklansky
# ---------------------------------------------------------------------------
def approx_sk_adder(a_bits, b_bits, K):
    """
    Sklansky: in each stage, we combine blocks of size 2^stage.
    We'll check if the 'target index' i is < K to apply approx merges.
    """
    W = len(a_bits)
    g = [a_bits[i] & b_bits[i] for i in range(W)]
    p = [a_bits[i] ^ b_bits[i] for i in range(W)]

    log_w = int(math.ceil(math.log2(W)))
    G_stages = [g[:]]
    P_stages = [p[:]]

    for stage_i in range(1, log_w+1):
        dist = 1 << (stage_i - 1)
        G_prev = G_stages[stage_i - 1]
        P_prev = P_stages[stage_i - 1]
        G_curr = [0]*W
        P_curr = [0]*W

        i = 0
        while i < W:
            block_end = min(i + dist, W)
            # keep bits i..block_end-1 the same
            for j in range(i, block_end):
                G_curr[j] = G_prev[j]
                P_curr[j] = P_prev[j]

            # merge for j2 in [block_end.. i+2*dist-1]
            j2 = block_end
            while j2 < i + 2*dist and j2 < W:
                if j2 < K:
                    g_out, p_out = approx_prefix_operator(
                        G_curr[block_end-1], P_curr[block_end-1],
                        G_prev[j2],          P_prev[j2]
                    )
                else:
                    g_out, p_out = prefix_operator(
                        G_curr[block_end-1], P_curr[block_end-1],
                        G_prev[j2],          P_prev[j2]
                    )
                G_curr[j2] = g_out
                P_curr[j2] = p_out
                j2 += 1

            i += 2*dist

        G_stages.append(G_curr)
        P_stages.append(P_curr)

    G_final = G_stages[-1]
    c = [0]*(W+1)
    for i in range(W):
        c[i+1] = G_final[i]
    sum_bits = [(p[i] ^ c[i]) for i in range(W)]
    return sum_bits


# ---------------------------------------------------------------------------
#   4) Approximate Ladner–Fischer
# ---------------------------------------------------------------------------
def approx_lf_adder(a_bits, b_bits, K):
    """
    Ladner–Fischer approximate version: merges in partial stages,
    but if i < K, do approximate merges, else do exact merges.
    """
    W = len(a_bits)
    g = [a_bits[i] & b_bits[i] for i in range(W)]
    p = [a_bits[i] ^ b_bits[i] for i in range(W)]
    log_w = int(math.ceil(math.log2(W)))

    G_stages = [g[:]]
    P_stages = [p[:]]

    for stage_i in range(1, log_w+1):
        dist = 1 << (stage_i - 1)
        G_prev = G_stages[stage_i - 1]
        P_prev = P_stages[stage_i - 1]
        G_curr = G_prev[:]
        P_curr = P_prev[:]

        step = dist
        while step < 2*dist and step < W:
            i = step
            while i < W:
                if i < K:
                    g_out, p_out = approx_prefix_operator(
                        G_curr[i-step], P_curr[i-step],
                        G_curr[i],      P_curr[i]
                    )
                else:
                    g_out, p_out = prefix_operator(
                        G_curr[i-step], P_curr[i-step],
                        G_curr[i],      P_curr[i]
                    )
                G_curr[i] = g_out
                P_curr[i] = p_out
                i += 2*dist
            step <<= 1

        G_stages.append(G_curr)
        P_stages.append(P_curr)

    G_final = G_stages[-1]
    c = [0]*(W+1)
    for i in range(W):
        c[i+1] = G_final[i]
    sum_bits = [(p[i] ^ c[i]) for i in range(W)]
    return sum_bits


# ----------------------------------------------------------------------------
#   WRAPPERS
# ----------------------------------------------------------------------------

def axppa_bk(a_bits, b_bits, K):
    return approx_bk_adder(a_bits, b_bits, K)

def axppa_ks(a_bits, b_bits, K):
    return approx_ks_adder(a_bits, b_bits, K)

def axppa_sk(a_bits, b_bits, K):
    return approx_sk_adder(a_bits, b_bits, K)

def axppa_lf(a_bits, b_bits, K):
    return approx_lf_adder(a_bits, b_bits, K)
