"""
widgets/gate_buttons.py
───────────────────────
Reusable NiceGUI components for gate-button rows and palettes.
"""

from __future__ import annotations
from typing import Callable

from nicegui import ui
from config import QUICK_GATES, GATE_INFO


# ─────────────────────────────────────────────────────────────────────────────
# SHARED BUTTON STYLE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

_QUICK_BTN_STYLE = (
    "font-family:var(--font-mono)!important;"
    "background:var(--bg2)!important;color:var(--accent)!important;"
    "border:1px solid var(--border)!important;"
    "width:48px!important;height:48px!important;"
    "border-radius:8px!important;font-size:0.95rem!important;"
    "font-weight:700!important;min-height:unset!important"
)

_SMALL_BTN_STYLE = (
    "font-family:var(--font-head)!important;font-size:0.7rem!important;"
    "background:var(--bg2)!important;color:var(--text-dim)!important;"
    "border:1px solid var(--border)!important;border-radius:6px!important;"
    "padding:8px 14px!important;min-height:unset!important"
)

_DANGER_BTN_STYLE = (
    "font-family:var(--font-head)!important;font-size:0.7rem!important;"
    "background:var(--red)!important;color:#fff!important;"
    "border:none!important;border-radius:6px!important;"
    "padding:8px 14px!important;min-height:unset!important"
)

_ACCENT_BTN_STYLE = (
    "font-family:var(--font-head)!important;font-size:0.7rem!important;"
    "background:var(--accent2)!important;color:#fff!important;"
    "border:none!important;border-radius:6px!important;"
    "padding:8px 14px!important;min-height:unset!important"
)


# ─────────────────────────────────────────────────────────────────────────────
# COMPONENTS
# ─────────────────────────────────────────────────────────────────────────────

def quick_gate_row(
    on_gate: Callable[[str], None],
    gates: list[str] | None = None,
) -> None:
    """
    Render a horizontal row of compact gate buttons.

    Parameters
    ----------
    on_gate : callback(gate_name: str)
    gates   : list of gate names to show; defaults to QUICK_GATES
    """
    gates = gates or QUICK_GATES
    with ui.row().style("flex-wrap:wrap;gap:4px;margin-top:6px"):
        for g in gates:
            ui.button(g, on_click=lambda g=g: on_gate(g)).style(_QUICK_BTN_STYLE)


def gate_palette(on_gate: Callable[[str], None]) -> None:
    """
    Render the full gate palette used in the circuit builder.

    Each tile shows the gate symbol, name, and short description.
    Clicking fires on_gate(gate_name).
    """
    with ui.row().style("flex-wrap:wrap;gap:8px;margin-bottom:16px"):
        for gate, (name, desc) in GATE_INFO.items():
            with ui.card().style(
                "background:var(--bg2);border:1px solid var(--border);"
                "border-radius:10px;padding:10px 14px;cursor:pointer;"
                "transition:all 0.15s;width:130px"
            ).on("click", lambda g=gate: on_gate(g)):
                ui.label(gate).style(
                    "font-family:var(--font-mono);font-size:1.3rem;"
                    "color:var(--accent);font-weight:700"
                )
                ui.label(name).style(
                    "font-family:var(--font-body);font-size:0.75rem;"
                    "color:var(--text);font-weight:600"
                )
                ui.label(desc).style(
                    "font-family:var(--font-body);font-size:0.68rem;"
                    "color:var(--text-dim)"
                )


def action_button(label: str, on_click: Callable, style: str = _SMALL_BTN_STYLE):
    """Generic styled action button."""
    return ui.button(label, on_click=on_click).style(style)


def danger_button(label: str, on_click: Callable):
    return action_button(label, on_click, _DANGER_BTN_STYLE)


def accent_button(label: str, on_click: Callable):
    return action_button(label, on_click, _ACCENT_BTN_STYLE)
