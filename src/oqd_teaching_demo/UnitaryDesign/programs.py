"""
programs.py
───────────
OQD Program helpers standalone versions that don't require the full
`oqd_teaching_demo` package to be installed.

Each function returns a Program object whose interface matches
oqd_teaching_demo.program.Program so MockDevice.run() and (when available)
the real Device.run() can consume them identically.

Programs
────────
digital_shor()          Shor's Algorithm laser pattern
digital_random(n)       Random single-qubit circuit (n steps)
analog_ising(n)         Nearest-neighbour Ising model simulation
analog_all_to_all(n)    All-to-all interaction simulation
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import numpy as np

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# PROGRAM DATA CLASS
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Program:
    """
    Mirrors oqd_teaching_demo.program.Program.

    Attributes
    ──────────
    red_lasers_intensity : list of 4-tuples, one per time step.
                           Each tuple holds the intensity for channels 0–3.
    dt                   : seconds per step (float).
    camera_trigger       : optional list of ints (1 = capture at that step).
    phonon_com           : optional list (not used by mock; reserved for real hardware).
    """
    red_lasers_intensity: list[tuple]       = field(default_factory=list)
    dt:                  float              = 0.1
    camera_trigger:      list[int]  | None  = None
    phonon_com:          list[int]  | None  = None

    def __post_init__(self) -> None:
        n = len(self.red_lasers_intensity)
        if self.camera_trigger is None:
            self.camera_trigger = [0] * n
        if self.phonon_com is None:
            self.phonon_com = [0] * n
        logger.debug("Program created  steps=%d  dt=%.3f", n, self.dt)


# ─────────────────────────────────────────────────────────────────────────────
# TRY TO USE THE REAL PACKAGE FIRST
# ─────────────────────────────────────────────────────────────────────────────

def _try_import_oqd_programs():
    """
    Attempt to import program helpers from the installed oqd_teaching_demo
    package.  Returns the module or None if not available.
    """
    try:
        from oqd_teaching_demo.gui import programs as oqd_progs
        logger.info("programs.py: using oqd_teaching_demo.gui.programs")
        return oqd_progs
    except ImportError:
        logger.info("programs.py: oqd_teaching_demo not installed — using built-in programs")
        return None


_oqd = _try_import_oqd_programs()


# ─────────────────────────────────────────────────────────────────────────────
# DIGITAL PROGRAMS
# ─────────────────────────────────────────────────────────────────────────────

def digital_shor() -> Program:
    """
    Laser pattern that illustrates the gate sequence for Shor's Algorithm
    (period-finding subroutine, heavily simplified to 4 channels × 17 steps).

    If oqd_teaching_demo is installed its version is used; otherwise the
    built-in pattern is returned.
    """
    if _oqd is not None:
        return _oqd.digital_shor()

    repeats = 4
    # Each inner list = [ch0, ch1, ch2, ch3]
    pattern = [
        (1, 0, 0, 0), (1, 0, 1, 0), (1, 0, 0, 1),
        (0, 0, 1, 1), (1, 0, 0, 0), (0, 1, 0, 0),
        (0, 0, 0, 0), (0, 1, 0, 0), (1, 1, 1, 0),
        (1, 1, 0, 1), (1, 0, 0, 1), (1, 1, 0, 0),
        (1, 1, 0, 1), (0, 1, 0, 0), (1, 1, 0, 1),
        (0, 1, 0, 0), (1, 1, 1, 1),
    ]
    red_lasers_intensity = pattern * repeats
    return Program(red_lasers_intensity=red_lasers_intensity, dt=0.25)


def digital_random(n: int = 20) -> Program:
    """
    Random binary laser pattern — useful for sanity-checking hardware response.
    """
    if _oqd is not None:
        return _oqd.digital_random(n)

    rng = np.random.default_rng()
    red_lasers_intensity = [
        tuple(int(v) for v in rng.integers(0, 2, size=4))
        for _ in range(n)
    ]
    return Program(red_lasers_intensity=red_lasers_intensity, dt=0.25)


# ─────────────────────────────────────────────────────────────────────────────
# ANALOG PROGRAMS
# ─────────────────────────────────────────────────────────────────────────────

def analog_ising(n: int = 60) -> Program:
    """
    Nearest-neighbour Ising model: channels 0&1 and 2&3 are paired and driven
    with a π/2 phase offset between the pairs.
    """
    if _oqd is not None:
        return _oqd.analog_ising(n)

    t      = np.arange(n)
    dt_val = 0.1
    period = 0.1

    def _wave(phase: float) -> list[float]:
        return list((np.sin(t * dt_val / period + phase) + 1) / 2)

    ch_a = _wave(0)
    ch_b = _wave(np.pi / 2)

    red_lasers_intensity = [
        (ch_a[i], ch_a[i], ch_b[i], ch_b[i])
        for i in range(n)
    ]
    return Program(red_lasers_intensity=red_lasers_intensity, dt=dt_val)


def analog_all_to_all(n: int = 60) -> Program:
    """
    All-to-all interaction: all four channels driven in phase.
    """
    if _oqd is not None:
        return _oqd.analog_all_to_all(n)

    t      = np.arange(n)
    dt_val = 0.1
    period = 0.2

    wave = list((np.sin(t * dt_val / period) + 1) / 2)

    red_lasers_intensity = [
        (wave[i], wave[i], wave[i], wave[i])
        for i in range(n)
    ]
    return Program(red_lasers_intensity=red_lasers_intensity, dt=dt_val)
