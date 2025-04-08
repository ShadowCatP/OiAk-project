import math

# ----------------------------------------------------------------------------
#  EXACT BRENT–KUNG ADDER
# ----------------------------------------------------------------------------
def bk_adder(a_bits, b_bits):
    """
    Brent–Kung Adder (exact).
    A straightforward way:
      1) Build bitwise generate (g) and propagate (p).
      2) forward reduce passes
      3) backward compute passes
      4) final sum
    The code below is somewhat "textbook style."
    """

    W = len(a_bits)
    # Step 1: Preprocessing
    g = [a_bits[i] & b_bits[i] for i in range(W)]
    p = [a_bits[i] ^ b_bits[i] for i in range(W)]

    # For Brent–Kung, the idea is a "tree" with ~2*log2(W)-1 stages:
    # We will store intermediate G/P in arrays to pass forward/backward.

    # forward generation: compute group generate/propagate for spans of 2^k bits
    log_w = int(math.ceil(math.log2(W)))
    # forward pass
    g_fwd = [[0]*W for _ in range(log_w)]  # g_fwd[k][i] = G for stage k, bit i
    p_fwd = [[0]*W for _ in range(log_w)]  # p_fwd[k][i] = P for stage k, bit i

    # stage 0: local bits
    for i in range(W):
        g_fwd[0][i] = g[i]
        p_fwd[0][i] = p[i]

    dist = 1
    lvl = 1
    while dist < W:
        for i in range(W):
            # We'll combine this bit i with i-dist if valid
            j = i - dist
            if j >= 0:
                # prefix operator
                g_fwd[lvl][i], p_fwd[lvl][i] = prefix_operator(
                    g_fwd[lvl-1][j],
                    p_fwd[lvl-1][j],
                    g_fwd[lvl-1][i],
                    p_fwd[lvl-1][i],
                )
            else:
                # no change from previous level
                g_fwd[lvl][i] = g_fwd[lvl-1][i]
                p_fwd[lvl][i] = p_fwd[lvl-1][i]
        dist <<= 1
        lvl += 1

    # g_fwd[log_w-1][i] has the forward group generate. Next do the "back" pass.
    # But for Brent–Kung, we do something slightly more explicit.

    # We'll define c[i] as carry-in to bit i
    c = [0]* (W+1)
    c[0] = 0
    # We can compute c[i+1] = G_fwd[lvl-1][i], but we only need log passes to get them.
    # Alternatively, we can do a direct pass from left to right using BK's approach:

    # The final group generate for bit i is the carry into bit i+1.
    for i in range(W):
        c[i+1] = g_fwd[log_w-1][i]

    # Step 3: Summation
    sum_bits = [ (p[i] ^ c[i]) for i in range(W)]

    return sum_bits


# ----------------------------------------------------------------------------
#  EXACT KOGGE–STONE ADDER
# ----------------------------------------------------------------------------
def ks_adder(a_bits, b_bits):
    """
    Kogge–Stone Adder (exact).
    Implementation of the standard KS prefix tree:
      * log2(W) stages
      * In each stage i, the distance is 2^i
      * G/P are computed by combining pairs at that distance
    """

    W = len(a_bits)
    # Step 1: Preprocessing
    g = [a_bits[i] & b_bits[i] for i in range(W)]
    p = [a_bits[i] ^ b_bits[i] for i in range(W)]

    log_w = int(math.ceil(math.log2(W)))
    G = [g[:]]  # G[0] is the local generates
    P = [p[:]]  # P[0] is the local propagates

    # Step 2: prefix computations
    for stage in range(1, log_w+1):
        dist = 1 << (stage-1)
        G_curr = [0]*W
        P_curr = [0]*W
        G_prev = G[stage-1]
        P_prev = P[stage-1]
        for i in range(W):
            if i - dist >= 0:
                # prefix operator
                g_out, p_out = prefix_operator(
                    G_prev[i-dist], P_prev[i-dist],
                    G_prev[i],      P_prev[i]
                )
                G_curr[i] = g_out
                P_curr[i] = p_out
            else:
                # no combination
                G_curr[i] = G_prev[i]
                P_curr[i] = P_prev[i]
        G.append(G_curr)
        P.append(P_curr)

    # Step 3: carry-out (c[i+1]) = G[log_w][i]
    # sum[i] = p[i] ^ c[i]
    c = [0]*(W+1)
    for i in range(W):
        c[i+1] = G[log_w][i]

    # Step 4: sum
    sum_bits = [(p[i] ^ c[i]) for i in range(W)]
    return sum_bits


# ----------------------------------------------------------------------------
#  EXACT SKLANSKY ADDER
# ----------------------------------------------------------------------------
def sk_adder(a_bits, b_bits):
    """
    Sklansky adder (divide-and-conquer).
    Another standard PPA structure:
      * In stage i, combine in groups of size 2^i, but reduce fan-out in final expansions
    Implementation is similar to Kogge–Stone except the "fan-out" is bigger in each stage,
    merging more signals each time. The difference is we do bigger merges in fewer lines
    but with potential high fan-out.
    """

    W = len(a_bits)
    g = [a_bits[i] & b_bits[i] for i in range(W)]
    p = [a_bits[i] ^ b_bits[i] for i in range(W)]

    log_w = int(math.ceil(math.log2(W)))

    G_stages = [g[:]]
    P_stages = [p[:]]

    for stage in range(1, log_w+1):
        dist = 1 << (stage-1)
        G_prev = G_stages[stage-1]
        P_prev = P_stages[stage-1]
        G_curr = [0]*W
        P_curr = [0]*W

        # We combine in a "Sklansky" pattern: every 2^stage block merges all from left half
        i = 0
        while i < W:
            block_end = min(i + dist, W)
            # bits i..(i+dist-1) remain same
            for j in range(i, block_end):
                G_curr[j] = G_prev[j]
                P_curr[j] = P_prev[j]

            # bits block_end..(i+2*dist-1) combine with the block_end-1
            # if block_end < W
            j2 = block_end
            while j2 < i + 2*dist and j2 < W:
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

    # final carry out
    G_final = G_stages[-1]
    c = [0]*(W+1)
    for i in range(W):
        c[i+1] = G_final[i]
    sum_bits = [p[i] ^ c[i] for i in range(W)]
    return sum_bits


# ----------------------------------------------------------------------------
#  EXACT LADNER–FISCHER ADDER
# ----------------------------------------------------------------------------
def lf_adder(a_bits, b_bits):
    """
    Ladner–Fischer Adder (exact).
    Architecture is a bit of a middle ground between Kogge–Stone and Sklansky.
    We'll do a standard implementation using a known pattern.
    """

    W = len(a_bits)
    g = [a_bits[i] & b_bits[i] for i in range(W)]
    p = [a_bits[i] ^ b_bits[i] for i in range(W)]

    log_w = int(math.ceil(math.log2(W)))
    G_stages = [g[:]]
    P_stages = [p[:]]

    # "Ladner–Fischer" merges pairs in a pattern that tries to keep fan-out and wiring low
    # Similar to Sklansky but merges in a different tree pattern.

    for stage in range(1, log_w+1):
        dist = 1 << (stage-1)
        G_prev = G_stages[stage-1]
        P_prev = P_stages[stage-1]
        G_curr = G_prev[:]
        P_curr = P_prev[:]

        step = dist
        while step < 2*dist and step < W:
            i = step
            while i < W:
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
    sum_bits = [p[i] ^ c[i] for i in range(W)]
    return sum_bits
