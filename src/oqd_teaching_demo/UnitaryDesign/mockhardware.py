"""
mock_hardware.py
────────────────
A self-contained OQD hardware mock that faithfully replicates the interface
of the real Device / Lasers / Trap / Camera stack used on the Raspberry Pi.

This module is used when:
  - MOCK = True  AND  the `oqd_teaching_demo` package is not installed
  - You want richer state-tracking / logging than the bare _StubDevice

All hardware calls are no-ops on the physical level but:
  • Record full call history for debugging/testing
  • Log every action with timestamps
  • Emit observable state so the UI can reflect what "would" happen
  • Faithfully implement the Program execution loop used by digital_shor,
    digital_random, analog_ising, and analog_all_to_all

The mock follows the same singleton pattern as the real Board class in
the original OQD main.py.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Callable

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# OBSERVABLE STATE  (subscribers can hook in for UI refresh)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class LaserState:
    """Current intensity of every laser channel."""
    intensities: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0])

    def set(self, idx: int, intensity: float) -> None:
        if 0 <= idx < len(self.intensities):
            self.intensities[idx] = max(0.0, min(1.0, float(intensity)))

    def all_on(self) -> None:
        self.intensities = [1.0] * len(self.intensities)

    def all_off(self) -> None:
        self.intensities = [0.0] * len(self.intensities)

    def __repr__(self) -> str:
        bars = " ".join(f"L{i}={v:.2f}" for i, v in enumerate(self.intensities))
        return f"LaserState({bars})"


@dataclass
class TrapState:
    """Current trap motion mode."""
    current_mode: str = "stop"   # "left" | "right" | "stop"

    def __repr__(self) -> str:
        return f"TrapState(mode={self.current_mode!r})"


@dataclass
class CameraState:
    """Simulated camera — tracks capture count."""
    captures: int = 0
    last_capture_time: float = 0.0


# ─────────────────────────────────────────────────────────────────────────────
# CALL-HISTORY ENTRY
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class HardwareEvent:
    timestamp: float
    component: str        # "lasers" | "trap" | "camera" | "device"
    action:    str
    payload:   dict


# ─────────────────────────────────────────────────────────────────────────────
# MOCK LASERS
# ─────────────────────────────────────────────────────────────────────────────

class MockLasers:
    """
    Mirrors oqd_teaching_demo.control.device.Lasers.

    Attributes
    ──────────
    channels : list[int]   channel indices (matches real hardware)
    state    : LaserState  observable current intensities
    """

    def __init__(self, num_channels: int = 4, history: list | None = None) -> None:
        self.channels: list[int] = list(range(num_channels))
        self.state    = LaserState(intensities=[0.0] * num_channels)
        self._history = history if history is not None else []
        self._subscribers: list[Callable] = []

    # ── public API (mirrors real Lasers) ─────────────────────────────────────

    def set_intensity(self, idx: int, intensity: float) -> None:
        """Set a single channel's intensity (0.0 – 1.0)."""
        clamped = max(0.0, min(1.0, float(intensity)))
        self.state.set(idx, clamped)
        logger.debug("MockLasers.set_intensity  idx=%d  intensity=%.3f", idx, clamped)
        self._record("set_intensity", {"idx": idx, "intensity": clamped})
        self._notify()

    def set_all(self, intensity: float) -> None:
        """Set all channels to the same intensity."""
        for idx in self.channels:
            self.set_intensity(idx, intensity)

    # ── observer subscription ─────────────────────────────────────────────────

    def subscribe(self, callback: Callable) -> None:
        """Register a callback invoked on every state change."""
        self._subscribers.append(callback)

    def _notify(self) -> None:
        for cb in self._subscribers:
            try:
                cb(self.state)
            except Exception as exc:
                logger.warning("MockLasers subscriber raised: %s", exc)

    # ── internal ──────────────────────────────────────────────────────────────

    def _record(self, action: str, payload: dict) -> None:
        self._history.append(HardwareEvent(
            timestamp=time.monotonic(),
            component="lasers",
            action=action,
            payload=payload,
        ))


# ─────────────────────────────────────────────────────────────────────────────
# MOCK TRAP
# ─────────────────────────────────────────────────────────────────────────────

class MockTrap:
    """
    Mirrors oqd_teaching_demo.control.device.Trap.

    The real trap moves an acoustic levitator left/right via GPIO PWM.
    Here we just record the commanded mode.
    """

    VALID_MODES = {"left", "right", "stop", "shake"}

    def __init__(self, history: list | None = None) -> None:
        self.state     = TrapState()
        self._history  = history if history is not None else []
        self._subscribers: list[Callable] = []

    def mode(self, m: str) -> None:
        """Command the trap motion: 'left' | 'right' | 'stop' | 'shake'."""
        if m not in self.VALID_MODES:
            logger.warning("MockTrap.mode: unknown mode %r (ignored)", m)
            return
        self.state.current_mode = m
        logger.debug("MockTrap.mode → %r", m)
        self._record("mode", {"mode": m})
        self._notify()

    def subscribe(self, callback: Callable) -> None:
        self._subscribers.append(callback)

    def _notify(self) -> None:
        for cb in self._subscribers:
            try:
                cb(self.state)
            except Exception as exc:
                logger.warning("MockTrap subscriber raised: %s", exc)

    def _record(self, action: str, payload: dict) -> None:
        self._history.append(HardwareEvent(
            timestamp=time.monotonic(),
            component="trap",
            action=action,
            payload=payload,
        ))


# ─────────────────────────────────────────────────────────────────────────────
# MOCK CAMERA
# ─────────────────────────────────────────────────────────────────────────────

class MockCamera:
    """
    Mirrors oqd_teaching_demo.control.device.Camera.

    The real camera is a Raspberry Pi camera module streamed via Flask.
    Here we simulate capture by incrementing a counter.
    """

    def __init__(self, history: list | None = None) -> None:
        self.state    = CameraState()
        self._history = history if history is not None else []

    def capture(self) -> dict:
        """Simulate a camera capture. Returns a fake result dict."""
        self.state.captures += 1
        self.state.last_capture_time = time.monotonic()
        logger.debug("MockCamera.capture  #%d", self.state.captures)
        self._record("capture", {"capture_number": self.state.captures})
        return {"capture_number": self.state.captures, "mock": True}

    def _record(self, action: str, payload: dict) -> None:
        self._history.append(HardwareEvent(
            timestamp=time.monotonic(),
            component="camera",
            action=action,
            payload=payload,
        ))


# ─────────────────────────────────────────────────────────────────────────────
# MOCK DEVICE  (top-level — mirrors real Device)
# ─────────────────────────────────────────────────────────────────────────────

class MockDevice:
    """
    Drop-in replacement for oqd_teaching_demo.control.device.Device.

    Attributes
    ──────────
    red_lasers : MockLasers
    trap       : MockTrap
    camera     : MockCamera
    history    : list[HardwareEvent]   full ordered call log

    Methods
    ───────
    run(program)    Execute an oqd_teaching_demo Program step-by-step in a
                    background thread, mirroring the real Device.run() timing.
    stop()          Abort any running program.
    reset()         All lasers off, trap stopped.
    """

    def __init__(self, num_channels: int = 4) -> None:
        self.history: list[HardwareEvent] = []
        self.red_lasers = MockLasers(num_channels=num_channels, history=self.history)
        self.trap       = MockTrap(history=self.history)
        self.camera     = MockCamera(history=self.history)

        self._program_thread: threading.Thread | None = None
        self._stop_event = threading.Event()

        logger.info("MockDevice initialised  channels=%d", num_channels)

    # ── Program execution ─────────────────────────────────────────────────────

    def run(self, program) -> None:
        """
        Execute a Program object in a background daemon thread.

        The Program is expected to have:
            program.red_lasers_intensity  : list of tuples, one per timestep
            program.dt                    : float, seconds per step
            program.camera_trigger        : optional list[int] (1 = capture)
            program.phonon_com            : optional list (ignored in mock)

        Matches the real Device.run() signature.
        """
        # Stop any currently running program first
        self.stop()

        self._stop_event.clear()
        self._program_thread = threading.Thread(
            target=self._execute_program,
            args=(program,),
            daemon=True,
            name="MockDevice-program",
        )
        self._program_thread.start()
        logger.info("MockDevice.run  started program  steps=%d  dt=%.3fs",
                    len(program.red_lasers_intensity), program.dt)

    def stop(self) -> None:
        """Signal the program thread to stop and wait for it."""
        if self._program_thread and self._program_thread.is_alive():
            self._stop_event.set()
            self._program_thread.join(timeout=2.0)
            logger.info("MockDevice.stop  program thread joined")

    def reset(self) -> None:
        """Stop any program, turn all lasers off, stop trap."""
        self.stop()
        self.red_lasers.set_all(0.0)
        self.trap.mode("stop")
        logger.info("MockDevice.reset  lasers off, trap stopped")

    # ── internal program loop ─────────────────────────────────────────────────

    def _execute_program(self, program) -> None:
        steps    = program.red_lasers_intensity
        dt       = getattr(program, "dt", 0.1)
        triggers = getattr(program, "camera_trigger", [0] * len(steps))

        for step_idx, intensities in enumerate(steps):
            if self._stop_event.is_set():
                logger.debug("MockDevice._execute_program  aborted at step %d", step_idx)
                break

            # Set laser intensities for this step
            for ch_idx, intensity in enumerate(intensities):
                if ch_idx < len(self.red_lasers.channels):
                    self.red_lasers.set_intensity(ch_idx, intensity)

            # Trigger camera if requested
            if step_idx < len(triggers) and triggers[step_idx]:
                self.camera.capture()

            # Record program step
            self.history.append(HardwareEvent(
                timestamp=time.monotonic(),
                component="device",
                action="program_step",
                payload={"step": step_idx, "intensities": list(intensities)},
            ))

            time.sleep(dt)

        # Cleanup: lasers off, trap stopped
        if not self._stop_event.is_set():
            self.red_lasers.set_all(0.0)
            self.trap.mode("stop")
            logger.info("MockDevice._execute_program  completed %d steps", len(steps))

    # ── diagnostics ───────────────────────────────────────────────────────────

    def dump_history(self, last_n: int = 20) -> str:
        """Return a formatted string of the last N hardware events."""
        events = self.history[-last_n:]
        lines  = [f"  [{e.timestamp:.3f}] {e.component}.{e.action}  {e.payload}"
                  for e in events]
        return "\n".join(lines) if lines else "  (no events)"

    def __repr__(self) -> str:
        return (
            f"MockDevice("
            f"lasers={self.red_lasers.state}, "
            f"trap={self.trap.state}, "
            f"captures={self.camera.state.captures}, "
            f"events={len(self.history)})"
        )


# ─────────────────────────────────────────────────────────────────────────────
# BOARD SINGLETON  (mirrors the Board class in the original OQD main.py)
# ─────────────────────────────────────────────────────────────────────────────

class Board:
    """
    Singleton wrapper around the active Device (mock or real).

    This mirrors the Board class from the original oqd_teaching_demo GUI
    so existing program helpers (digital_shor, analog_ising, etc.) can call
    board.device.run(...) without knowing whether they're on real hardware.

    Usage
    ─────
        board = Board.get()          # always returns the same instance
        board.device.run(program)
        board.device.red_lasers.set_intensity(0, 1.0)
        board.cleanup()              # safe to call on exit
    """

    _instance: "Board | None" = None
    _lock = threading.Lock()

    def __new__(cls, device=None):
        with cls._lock:
            if cls._instance is None:
                inst = super().__new__(cls)
                inst._device = device
                inst._initialised = False
                cls._instance = inst
        return cls._instance

    def _ensure_init(self, device=None) -> None:
        if not self._initialised:
            self._device = device or self._device or MockDevice()
            self._initialised = True
            logger.info("Board initialised  device=%r", self._device)

    @classmethod
    def get(cls, device=None) -> "Board":
        """Return (and optionally initialise) the singleton Board."""
        inst = cls(device=device)
        inst._ensure_init(device)
        return inst

    @property
    def device(self):
        self._ensure_init()
        return self._device

    def cleanup(self) -> None:
        """Gracefully shut down the device (called via atexit)."""
        logger.info("Board.cleanup  called")
        if self._device is not None:
            try:
                self._device.stop()
                self._device.reset()
            except Exception as exc:
                logger.warning("Board.cleanup error: %s", exc)

    @classmethod
    def reset_singleton(cls) -> None:
        """Destroy the singleton (useful in tests)."""
        with cls._lock:
            cls._instance = None
