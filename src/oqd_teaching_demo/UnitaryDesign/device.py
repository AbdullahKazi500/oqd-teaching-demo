"""
device.py
─────────
Hardware abstraction layer.

Resolution order
────────────────
1. MOCK = False  →  use oqd_teaching_demo.control.device.Device  (real Pi hardware)
2. MOCK = True   →  try oqd_teaching_demo.control.mock.MockDevice (OQD's own mock)
3. MOCK = True   →  fall back to mock_hardware.MockDevice          (our built-in mock)

Public helpers
──────────────
    get_board()     → Board singleton (wraps the device, mirrors OQD's Board class)
    get_device()    → the Device object inside the Board
    get_stream_ip() → correct camera-stream URL for the current mode
"""

from __future__ import annotations

import atexit
import logging

from config import MOCK, STREAM_IP_MOCK, STREAM_IP_REAL

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# DEVICE FACTORY
# ─────────────────────────────────────────────────────────────────────────────

def _make_device():
    """
    Instantiate the appropriate Device based on the MOCK flag and
    what packages are actually installed.
    """
    if not MOCK:
        try:
            from oqd_teaching_demo.control.device import Device
            logger.info("device.py: using real oqd_teaching_demo Device")
            return Device()
        except ImportError as exc:
            logger.error(
                "MOCK=False but oqd_teaching_demo is not installed: %s — "
                "falling back to MockDevice.", exc
            )

    # Prefer OQD's own MockDevice if the package is installed
    try:
        from oqd_teaching_demo.control.mock import MockDevice as OqdMock
        logger.info("device.py: using oqd_teaching_demo.control.mock.MockDevice")
        return OqdMock()
    except ImportError:
        pass

    # Fallback: built-in mock that needs no external packages
    from mock_hardware import MockDevice as BuiltinMock
    logger.info("device.py: using built-in mock_hardware.MockDevice")
    return BuiltinMock()


# ─────────────────────────────────────────────────────────────────────────────
# BOARD SINGLETON
# ─────────────────────────────────────────────────────────────────────────────

class Board:
    """
    Singleton board wrapper — mirrors the Board class in the original OQD
    main.py but delegates device creation to _make_device() above.
    """

    _instance: "Board | None" = None

    def __new__(cls):
        if cls._instance is None:
            logger.info("Board: creating singleton instance")
            inst = super().__new__(cls)
            inst._device = _make_device()
            logger.info("Board: device ready -> %r", inst._device)
            cls._instance = inst
        else:
            logger.debug("Board: reusing existing instance")
        return cls._instance

    @classmethod
    def get(cls) -> "Board":
        return cls()

    @property
    def device(self):
        return self._device

    def cleanup(self) -> None:
        logger.info("Board.cleanup called")
        dev = self._device
        if dev is None:
            return
        for method_name in ("stop", "reset"):
            method = getattr(dev, method_name, None)
            if callable(method):
                try:
                    method()
                except Exception as exc:
                    logger.warning("Board.cleanup: %s() raised %s", method_name, exc)

    def __repr__(self) -> str:
        return f"Board(device={self._device!r})"


# ─────────────────────────────────────────────────────────────────────────────
# CONVENIENCE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def get_board() -> Board:
    board = Board.get()
    atexit.register(board.cleanup)
    return board


def get_device():
    return get_board().device


def get_stream_ip() -> str:
    return STREAM_IP_REAL if not MOCK else STREAM_IP_MOCK
