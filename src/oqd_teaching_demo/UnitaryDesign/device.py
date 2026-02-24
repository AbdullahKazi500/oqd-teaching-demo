"""
device.py
─────────
Hardware abstraction layer.

Provides get_device() and get_stream_ip() based on the MOCK flag in
config.py.  All other modules should call these two helpers instead of
importing hardware classes directly, so swapping real ↔ mock is a one-line
change in config.py.
"""

from __future__ import annotations
from config import MOCK, STREAM_IP_MOCK, STREAM_IP_REAL


# 
# STUB CLASSES  (used when neither MockDevice nor real Device is available)


class _StubLasers:
    """No-op laser controller."""
    channels = [0, 1, 2, 3]

    def set_intensity(self, idx: int, intensity: float) -> None:
        pass


class _StubTrap:
    """No-op trap controller."""

    def mode(self, m: str) -> None:
        pass


class _StubCamera:
    """No-op camera."""
    pass


class _StubDevice:
    """Fully-stubbed device used when the OQD package is not installed."""

    def __init__(self) -> None:
        self.red_lasers = _StubLasers()
        self.trap       = _StubTrap()
        self.camera     = _StubCamera()

    def run(self, program) -> None:
        pass


# 
# PUBLIC HELPERS
#

def get_device():
    """Return an initialised device (real, mock, or stub)."""
    if MOCK:
        try:
            from oqd_teaching_demo.control.mock import MockDevice
            return MockDevice()
        except ImportError:
            return _StubDevice()
    else:
        from oqd_teaching_demo.control.device import Device
        return Device()


def get_stream_ip() -> str:
    """Return the correct camera-stream URL."""
    return STREAM_IP_REAL if not MOCK else STREAM_IP_MOCK
