"""
state.py
────────
Centralised mutable application state.

All UI tabs read and write through this single module so there is one
source of truth.  Nothing here imports from NiceGUI; it is plain Python.
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class QubitState:
    """Bloch-sphere representation of a single qubit: (θ, φ)."""
    theta: float = 0.0   # 0 = |0⟩, π = |1⟩, π/2 = superposition
    phi:   float = 0.0

    def reset(self) -> None:
        self.theta = 0.0
        self.phi   = 0.0

    def set(self, theta: float, phi: float) -> None:
        self.theta = theta
        self.phi   = phi


@dataclass
class CircuitState:
    """Gates queued in the circuit builder."""
    gates: list[str] = field(default_factory=list)

    def add(self, gate: str) -> None:
        self.gates.append(gate)

    def remove(self, idx: int) -> None:
        if 0 <= idx < len(self.gates):
            self.gates.pop(idx)

    def clear(self) -> None:
        self.gates.clear()

    def __len__(self) -> int:
        return len(self.gates)

    def __iter__(self):
        return iter(self.gates)


@dataclass
class ScoreState:
    """Player score and challenge progress."""
    total:              int = 0
    challenges_done:    int = 0
    current_challenge:  int = 0

    def add(self, points: int) -> None:
        self.total += points
        self.challenges_done += 1
        self.current_challenge += 1

    def reset(self) -> None:
        self.total             = 0
        self.challenges_done   = 0
        self.current_challenge = 0


# ─────────────────────────────────────────────────────────────────────────────
# SINGLETON INSTANCES
# ─────────────────────────────────────────────────────────────────────────────

qubit   = QubitState()
circuit = CircuitState()
score   = ScoreState()
