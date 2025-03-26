
from typing import List
from adders.base_adder import BaseAdder, to_bits, from_bits, bitwise_generate_propagate
from adders.axpo import axpo_generate, axpo_propagate


class AxppaBk(BaseAdder):
    def __init__(self, width: int, approx_bits: int):
        super().__init__(width)
        assert 0 <= approx_bits <= width
        self.k = approx_bits  # Number of LSB bits to approximate

    def _approx_prefix_logic(self, g: List[int], p: List[int]) -> List[int]:
        """Approximate carry computation (AxPOs) for LSB part."""
        carry = [0]  # initial carry-in is 0
        for i in range(self.k):
            # Approximate: G ≈ g[i], P ≈ p[i]
            pi = axpo_propagate(p[i])  # Actually just p[i+1] ≈ p[i]
            gi = axpo_generate(g[i])   # Actually just g[i+1] ≈ g[i]
            carry.append(gi | (pi & carry[-1]))
        return carry

    @staticmethod
    def _exact_prefix_bk(g: List[int], p: List[int]) -> List[int]:
        """Exact Brent–Kung prefix logic for MSB part."""
        n = len(g)
        g = g[:]
        p = p[:]
        logn = n.bit_length()

        # Upward (reduce) pass
        for d in range(1, logn):
            for i in range((1 << d) - 1, n, 1 << d):
                g[i] = g[i] | (p[i] & g[i - (1 << (d - 1))])
                p[i] = p[i] & p[i - (1 << (d - 1))]

        # Downward (propagate) pass
        for d in reversed(range(1, logn)):
            for i in range((1 << d) + (1 << (d - 1)) - 1, n, 1 << d):
                g[i] = g[i] | (p[i] & g[i - (1 << (d - 1))])
                p[i] = p[i] & p[i - (1 << (d - 1))]

        # Compute carries
        c = [0] * (n + 1)
        for i in range(n):
            c[i + 1] = g[i]
        return c

    def add(self, a_bits: int, b: int) -> int:
        a_bits = to_bits(a_bits, self.width)
        b_bits = to_bits(b, self.width)

        g, p = bitwise_generate_propagate(a_bits, b_bits)

        # Approximate LSB part
        approx_carry = self._approx_prefix_logic(g[:self.k], p[:self.k])
        approx_sum = [p[i] ^ approx_carry[i] for i in range(self.k)]

        # Exact MSB part
        g_msb = g[self.k:]
        p_msb = p[self.k:]

        exact_carry = self._exact_prefix_bk(g_msb, p_msb)
        # Start from carry-out of LSB part
        exact_carry[0] = approx_carry[-1]
        exact_sum = [p_msb[i] ^ exact_carry[i] for i in range(len(p_msb))]

        full_sum = approx_sum + exact_sum
        return from_bits(full_sum)
