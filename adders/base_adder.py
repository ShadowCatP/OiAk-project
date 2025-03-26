from typing import List, Tuple

def bitwise_generate_propagate(a: List[int], b: List[int]) -> Tuple[List[int], List[int]]:
    """Compute generate (G) and propagate (P) signals for inputs a and b."""
    g = [ai & bi for ai, bi in zip(a, b)]
    p = [ai ^ bi for ai, bi in zip(a, b)]
    return g, p

def to_bits(value: int, width: int) -> List[int]:
    """Convert integer to a list of bits (LSB first)."""
    return [(value >> i) & 1 for i in range(width)]

def from_bits(bits: List[int]) -> int:
    """Convert list of bits (LSB first) back to integer."""
    return sum(b << i for i, b in enumerate(bits))

def full_adder(p: List[int], g: List[int], cin: int = 0) -> List[int]:
    """Basic ripple-carry adder using propagate/generate logic."""
    c = [cin]
    for i in range(len(p)):
        c.append(g[i] | (p[i] & c[-1]))
    s = [p[i] ^ c[i] for i in range(len(p))]
    return s

class BaseAdder:
    """Abstract base class for exact or approximate PPAs."""

    def __init__(self, width: int):
        self.width = width

    def add(self, a: int, b: int) -> int:
        """Override in subclasses with specific adder implementation."""
        raise NotImplementedError("Subclasses must implement `add` method.")