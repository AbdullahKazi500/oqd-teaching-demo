"""
quantum.py
──────────
Pure quantum-mechanics helpers.

All functions are stateless and operate
only on (theta, phi) Bloch-sphere angles, making them trivially testable.
"""

from __future__ import annotations
import math
import random

from config import GATE_LASER_PATTERNS, GATE_TRAP_MOTION, DEFAULT_LASER_PATTERN, DEFAULT_TRAP_MOTION


# ─────────────────────────────────────────────────────────────────────────────
# PROBABILITY AMPLITUDES
# ─────────────────────────────────────────────────────────────────────────────

def prob_zero(theta: float) -> float:
    """Probability of measuring |0⟩ given polar angle θ."""
    return math.cos(theta / 2) ** 2


def prob_one(theta: float) -> float:
    """Probability of measuring |1⟩ given polar angle θ."""
    return math.sin(theta / 2) ** 2


# ─────────────────────────────────────────────────────────────────────────────
# GATE APPLICATION
# ─────────────────────────────────────────────────────────────────────────────

def apply_gate(gate: str, theta: float, phi: float) -> tuple[float, float]:
    """
    Apply a named single-qubit gate and return the new (theta, phi).

    Supported gates
    ───────────────
    H  – Hadamard
    X  – Pauli-X  (NOT)
    Y  – Pauli-Y
    Z  – Pauli-Z  (phase flip)
    S  – S gate   (π/2 phase)
    T  – T gate   (π/4 phase)
    M  – Measurement (stochastic collapse via Born rule)
    """
    if gate == "H":
        if abs(theta) < 0.05:
            return math.pi / 2, 0.0
        if abs(theta - math.pi / 2) < 0.05 and abs(phi) < 0.05:
            return 0.0, 0.0
        return math.pi - theta, phi + math.pi

    if gate == "X":
        return math.pi - theta, phi + math.pi

    if gate == "Y":
        return math.pi - theta, -phi

    if gate == "Z":
        return theta, phi + math.pi

    if gate == "S":
        return theta, phi + math.pi / 2

    if gate == "T":
        return theta, phi + math.pi / 4

    if gate == "M":
        if random.random() < prob_zero(theta):
            return 0.0, 0.0   # collapsed to |0⟩
        return math.pi, 0.0   # collapsed to |1⟩

    # Unknown gate – leave state unchanged
    return theta, phi


# ─────────────────────────────────────────────────────────────────────────────
# STATE LABELLING
# ─────────────────────────────────────────────────────────────────────────────

def state_label(theta: float, phi: float) -> str:
    """Return a human-readable Dirac label for the current Bloch-sphere state."""
    p0 = prob_zero(theta)
    p1 = prob_one(theta)

    if abs(theta) < 0.05:
        return "|ψ⟩ = |0⟩"
    if abs(theta - math.pi) < 0.05:
        return "|ψ⟩ = |1⟩"
    if abs(theta - math.pi / 2) < 0.05:
        if abs(phi) < 0.05:
            return "|ψ⟩ = |+⟩ = (|0⟩+|1⟩)/√2"
        if abs(abs(phi) - math.pi) < 0.05:
            return "|ψ⟩ = |−⟩ = (|0⟩−|1⟩)/√2"
        return "|ψ⟩ = superposition"
    return f"|ψ⟩ = {p0:.2f}|0⟩ + {p1:.2f}|1⟩"


def bloch_state_name(theta: float, phi: float) -> str:
    """Short state name used as the SVG vector label."""
    if abs(theta) < 0.05:
        return "|0⟩"
    if abs(theta - math.pi) < 0.05:
        return "|1⟩"
    if abs(theta - math.pi / 2) < 0.05:
        if abs(phi) < 0.05:
            return "|+⟩"
        if abs(abs(phi) - math.pi) < 0.05:
            return "|−⟩"
    return "|ψ⟩"


# 
# HARDWARE MAPPING HELPERS


def laser_intensities_for_gate(gate: str) -> list[float]:
    """Return the 4-channel laser intensity list for a given gate."""
    return GATE_LASER_PATTERNS.get(gate, DEFAULT_LASER_PATTERN)


def trap_motion_for_gate(gate: str) -> str:
    """Return the trap motion command string for a given gate."""
    return GATE_TRAP_MOTION.get(gate, DEFAULT_TRAP_MOTION)


#
# CHALLENGE CHECKING
# 

def challenge_passed(
    theta: float,
    phi:   float,
    target_theta: float,
    target_phi:   float,
    tol: float = 0.2,
) -> bool:
    """Return True when the qubit state is within tolerance of the target."""
    theta_ok = abs(theta - target_theta) < tol
    phi_ok   = (
        abs(phi - target_phi) < tol
        or abs(abs(phi - target_phi) - 2 * math.pi) < tol
    )
    return theta_ok and phi_ok
